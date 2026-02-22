"""
Chat request/response schemas
"""
from marshmallow import Schema, fields, validate


class ChatRequestSchema(Schema):
    """Schema for chat request validation"""
    
    message = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    conversation_id = fields.Str(required=False, allow_none=True, 
                                 validate=validate.Length(min=1, max=100))


class ChatResponseSchema(Schema):
    """Schema for chat response"""
    
    response = fields.Str(required=True)
    conversation_id = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    context_used = fields.Bool(required=False)
    sources = fields.List(fields.Dict(), required=False)


class MessageSchema(Schema):
    """Schema for individual message"""
    
    id = fields.Int(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['user', 'assistant']))
    content = fields.Str(required=True)
    created_at = fields.DateTime(required=True)


class ConversationSchema(Schema):
    """Schema for conversation"""
    
    id = fields.Int(required=True)
    conversation_id = fields.Str(required=True)
    title = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    message_count = fields.Int(required=False)