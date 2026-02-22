"""
Greeting schema
"""
from marshmallow import Schema, fields, validate


class GreetingSchema(Schema):
    """Schema for greeting validation"""
    
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    language = fields.Str(required=False, validate=validate.Length(max=10))
    category = fields.Str(required=False, validate=validate.Length(max=50))
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(required=False)


class GreetingListSchema(Schema):
    """Schema for list of greetings"""
    
    greetings = fields.List(fields.Nested(GreetingSchema))
    total = fields.Int()