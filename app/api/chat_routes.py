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
chat_request_schema = ChatRequestSchema()
chat_response_schema = ChatResponseSchema()

# Initialize service
chat_service = ChatService()


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint
    
    Request body:
    {
        "message": "Hello, how are you?",
        "user_id": "user123",
        "conversation_id": "conv456" (optional)
    }
    
    Response:
    {
        "response": "I'm doing well, thank you!",
        "conversation_id": "conv456",
        "timestamp": "2024-01-15T10:30:00"
    }
    """
    try:
        # Validate request
        data = chat_request_schema.load(request.json)
        
        # Process chat message
        result = chat_service.process_message(
            message=data['message'],
            user_id=data['user_id'],
            conversation_id=data.get('conversation_id')
        )
        
        # Validate and return response
        response = chat_response_schema.dump(result)
        return jsonify(response), 200
        
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({'error': 'Invalid request', 'details': err.messages}), 400
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Get conversation history
    """
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
    """
    Get all conversations for a user
    """
    try:
        conversations = chat_service.get_user_conversations(user_id)
        return jsonify({
            'user_id': user_id,
            'conversations': conversations
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user conversations: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500