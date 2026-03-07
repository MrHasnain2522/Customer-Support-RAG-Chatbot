"""
Chat Service with JSON storage for PostgreSQL
Enhanced with source deduplication + STT voice chat
"""
import uuid
import re
from datetime import datetime
from app import db
from app.models.user import User
from app.models.conversation import Conversation
from app.rag.retriever import RAGRetriever
from app.rag.generator import ResponseGenerator
from app.stt.stt_service import STTService                  # ← NEW
from app.stt.audio_processor import save_audio_file         # ← NEW
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for handling chat operations with JSON storage"""

    def __init__(self):
        self.retriever  = RAGRetriever()
        self.generator  = ResponseGenerator()
        self.stt        = STTService()                      # ← NEW


    def voice_chat(
        self,
        audio_file,
        user_id: str,
        conversation_id: str = None,
        model_type: str = "whisper",
        model_size: str = "base",
        language: str = "english",
    ) -> dict:
        """
        🔥 NEW: Voice → STT → RAG → Response
        
        Flow:
          Audio file
            ↓
          STT (HuggingFace Whisper)
            ↓
          Transcript text
            ↓
          RAG pipeline
            ↓
          AI response

        Args:
            audio_file       : Uploaded audio file object
            user_id          : User identifier
            conversation_id  : Optional conversation ID
            model_type       : STT model type (whisper/wav2vec2)
            model_size       : STT model size (tiny/base/small etc)
            language         : Audio language

        Returns:
            dict with transcript, response, conversation_id, status
        """
        try:
            # ── Step 1: Save audio file ───────────────
            audio_path = save_audio_file(audio_file)
            logger.info(f"Voice chat started → file saved: {audio_path}")

            # ── Step 2: Transcribe audio → text ───────
            stt_result = self.stt.transcribe(
                audio_path=audio_path,
                model_type=model_type,
                model_size=model_size,
                language=language,
            )

            # Handle STT failure
            if stt_result["status"] == "error":
                return {
                    "transcript":       "",
                    "response":         "",
                    "conversation_id":  conversation_id,
                    "status":           "error",
                    "error":            f"STT failed: {stt_result['error']}",
                }

            transcript = stt_result["transcript"]
            logger.info(f"Transcript: '{transcript}'")

            # Handle empty transcript (silent audio)
            if not transcript.strip():
                return {
                    "transcript":       "",
                    "response":         "I could not hear anything. Please speak clearly and try again.",
                    "conversation_id":  conversation_id,
                    "status":           "success",
                    "error":            None,
                }

            # ── Step 3: Send transcript to RAG ────────
            chat_result = self.process_message(
                user_id=user_id,
                message=transcript,
                conversation_id=conversation_id,
            )

            # ── Step 4: Return combined result ────────
            return {
                "transcript":       transcript,
                "response":         chat_result["response"],
                "conversation_id":  chat_result["conversation_id"],
                "model_used":       stt_result["model_used"],
                "language":         stt_result["language"],
                "context_used":     chat_result["context_used"],
                "timestamp":        chat_result["timestamp"],
                "status":           "success",
                "error":            None,
            }

        except Exception as e:
            logger.error(f"Voice chat error: {e}")
            return {
                "transcript":       "",
                "response":         "",
                "conversation_id":  conversation_id,
                "status":           "error",
                "error":            str(e),
            }


    def process_message(self, user_id: str, message: str, conversation_id: str = None):
        """
        Process chat message with JSON storage and deduplicated sources
        """
        try:
            # Get or create user
            user = self._get_or_create_user(user_id)

            # Get or create conversation
            if conversation_id:
                conversation = Conversation.query.filter_by(
                    conversation_id=conversation_id
                ).first()
                if not conversation:
                    conversation = self._create_conversation(user_id)
            else:
                conversation = self._create_conversation(user_id)

            # Add user message to JSON
            conversation.add_message(
                role='user',
                content=message,
                context_used=False,
                sources=[]
            )

            # Get conversation history
            history = conversation.get_last_n_messages(10)

            # Retrieve context from RAG
            context = self.retriever.retrieve(message, history)

            logger.debug(f"RAW CONTEXT SAMPLE: {str(context)[:300] if context else 'None'}")

            # Extract and deduplicate sources
            sources = []
            if context:
                sources = self._extract_and_deduplicate_sources(context)

            # Generate response
            response = self.generator.generate(message, context, history)

            # Add assistant message
            conversation.add_message(
                role='assistant',
                content=response,
                context_used=bool(context),
                sources=sources
            )

            # Update title if first exchange
            if len(conversation.get_messages()) == 2:
                conversation.title = message[:50]
                db.session.commit()

            current_time = datetime.utcnow()

            logger.info(f"Processed message for conversation {conversation.conversation_id}")

            return {
                'response':         response,
                'conversation_id':  conversation.conversation_id,
                'timestamp':        current_time,
                'context_used':     bool(context)
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def _extract_and_deduplicate_sources(self, context: str):
        """Extract and deduplicate sources by filename."""
        if not context:
            return []

        pattern = r'\[Source \d+: (.+?) \(Relevance: ([\d.]+)\)\]'
        matches = re.findall(pattern, context)

        seen_files = {}
        for filename, relevance in matches:
            filename = filename.strip()
            relevance_score = float(relevance)
            if filename not in seen_files:
                seen_files[filename] = relevance_score
            else:
                if relevance_score > seen_files[filename]:
                    seen_files[filename] = relevance_score

        sources = [
            {'filename': filename, 'relevance': relevance}
            for filename, relevance in seen_files.items()
        ]

        sources = sorted(sources, key=lambda x: x['relevance'], reverse=True)[:3]
        logger.info(f"Deduplicated {len(matches)} sources to {len(sources)} unique sources")
        return sources

    def _extract_sources(self, context: str):
        """DEPRECATED: Use _extract_and_deduplicate_sources instead."""
        return self._extract_and_deduplicate_sources(context)

    def get_conversation_history(self, conversation_id: str):
        """Get full conversation history."""
        try:
            conversation = Conversation.query.filter_by(
                conversation_id=conversation_id
            ).first()
            if not conversation:
                return {'error': 'Conversation not found'}
            return conversation.to_json()
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise

    def get_user_conversations(self, user_id: str):
        """Get all user conversations."""
        try:
            conversations = Conversation.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(Conversation.updated_at.desc()).all()
            return [conv.to_json() for conv in conversations]
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise

    def _get_or_create_user(self, user_id: str):
        """Get or create user."""
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id)
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {user_id}")
        return user

    def _create_conversation(self, user_id: str):
        """Create new conversation."""
        conversation = Conversation(
            conversation_id=str(uuid.uuid4()),
            user_id=user_id,
            messages_json=[],
            metadata_json={}
        )
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"Created conversation: {conversation.conversation_id}")
        return conversation