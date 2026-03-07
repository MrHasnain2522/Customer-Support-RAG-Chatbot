"""
Chat API routes
"""
from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService
from app.schemas.chat_schema import ChatRequestSchema, ChatResponseSchema
from marshmallow import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)
chat_bp = Blueprint('chat', __name__)

# Initialize schemas
chat_request_schema  = ChatRequestSchema()
chat_response_schema = ChatResponseSchema()

# Initialize service
chat_service = ChatService()


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Text chat endpoint

    Request body:
    {
        "message": "Hello, how are you?",
        "user_id": "user123",
        "conversation_id": "conv456" (optional)
    }
    """
    try:
        data = chat_request_schema.load(request.json)

        result = chat_service.process_message(
            message=data['message'],
            user_id=data['user_id'],
            conversation_id=data.get('conversation_id')
        )

        response = chat_response_schema.dump(result)
        return jsonify(response), 200

    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({'error': 'Invalid request', 'details': err.messages}), 400

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/chat/voice', methods=['POST'])
def voice_chat():
    """
    🔥 NEW: Voice → STT → RAG → Response

    POST /api/chat/voice
    Form Data:
        audio           : Audio file (mp3/wav/ogg/m4a)
        user_id         : User identifier
        conversation_id : Optional existing conversation
        model_type      : whisper or wav2vec2 (default: whisper)
        model_size      : tiny/base/small/medium (default: base)
        language        : english/urdu/arabic etc (default: english)

    Response:
    {
        "transcript":      "what is RAG?",
        "response":        "RAG stands for...",
        "conversation_id": "abc-123",
        "model_used":      "openai/whisper-large-v3-turbo",
        "status":          "success"
    }
    """
    try:
        # ── Validate audio file ───────────────────
        if "audio" not in request.files:
            return jsonify({
                "error": "No audio file provided.",
                "hint":  "Use form-data key: 'audio'"
            }), 400

        audio_file = request.files["audio"]

        if not audio_file.filename:
            return jsonify({
                "error": "Empty filename.",
                "hint":  "Make sure a file is selected."
            }), 400

        # ── Get optional params ───────────────────
        user_id         = request.form.get("user_id",         "default_user")
        conversation_id = request.form.get("conversation_id", None)
        model_type      = request.form.get("model_type",      "whisper")
        model_size      = request.form.get("model_size",      "base")
        language        = request.form.get("language",        "english")

        # ── Process voice → STT → RAG ─────────────
        result = chat_service.voice_chat(
            audio_file=audio_file,
            user_id=user_id,
            conversation_id=conversation_id,
            model_type=model_type,
            model_size=model_size,
            language=language,
        )

        if result["status"] == "error":
            return jsonify(result), 500

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"Voice chat route error: {e}")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation history."""
    try:
        history = chat_service.get_conversation_history(conversation_id)
        return jsonify({
            'conversation_id': conversation_id,
            'messages': history
        }), 200

    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversation'}), 500


@chat_bp.route('/conversations/user/<user_id>', methods=['GET'])
def get_user_conversations(user_id):
    """Get all conversations for a user."""
    try:
        conversations = chat_service.get_user_conversations(user_id)
        return jsonify({
            'user_id': user_id,
            'conversations': conversations
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user conversations: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500
