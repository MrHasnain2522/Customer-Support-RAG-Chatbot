"""
Tests for database models
"""
import pytest
from app import db
from app.models import User, Conversation, Message, Greeting


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, app):
        """Test user creation"""
        with app.app_context():
            user = User(user_id='test_user_123', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.user_id == 'test_user_123'
            assert user.username == 'testuser'
    
    def test_user_to_dict(self, app):
        """Test user to_dict method"""
        with app.app_context():
            user = User(user_id='test_user_123', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            assert 'id' in user_dict
            assert 'user_id' in user_dict
            assert user_dict['user_id'] == 'test_user_123'


class TestConversationModel:
    """Test Conversation model"""
    
    def test_create_conversation(self, app):
        """Test conversation creation"""
        with app.app_context():
            user = User(user_id='test_user_123')
            db.session.add(user)
            db.session.commit()
            
            conversation = Conversation(
                conversation_id='conv_123',
                user_id=user.id,
                title='Test Conversation'
            )
            db.session.add(conversation)
            db.session.commit()
            
            assert conversation.id is not None
            assert conversation.conversation_id == 'conv_123'
            assert conversation.user_id == user.id
    
    def test_conversation_to_dict(self, app):
        """Test conversation to_dict method"""
        with app.app_context():
            user = User(user_id='test_user_123')
            db.session.add(user)
            db.session.commit()
            
            conversation = Conversation(
                conversation_id='conv_123',
                user_id=user.id
            )
            db.session.add(conversation)
            db.session.commit()
            
            conv_dict = conversation.to_dict()
            assert 'id' in conv_dict
            assert 'conversation_id' in conv_dict
            assert conv_dict['conversation_id'] == 'conv_123'


class TestMessageModel:
    """Test Message model"""
    
    def test_create_user_message(self, app):
        """Test user message creation"""
        with app.app_context():
            user = User(user_id='test_user_123')
            db.session.add(user)
            db.session.commit()
            
            conversation = Conversation(
                conversation_id='conv_123',
                user_id=user.id
            )
            db.session.add(conversation)
            db.session.commit()
            
            message = Message.create_user_message(
                conversation_id=conversation.id,
                user_id=user.id,
                content='Hello!'
            )
            db.session.add(message)
            db.session.commit()
            
            assert message.id is not None
            assert message.role == 'user'
            assert message.content == 'Hello!'
    
    def test_create_assistant_message(self, app):
        """Test assistant message creation"""
        with app.app_context():
            user = User(user_id='test_user_123')
            db.session.add(user)
            db.session.commit()
            
            conversation = Conversation(
                conversation_id='conv_123',
                user_id=user.id
            )
            db.session.add(conversation)
            db.session.commit()
            
            message = Message.create_assistant_message(
                conversation_id=conversation.id,
                user_id=user.id,
                content='Hi there!',
                context='Some context'
            )
            db.session.add(message)
            db.session.commit()
            
            assert message.id is not None
            assert message.role == 'assistant'
            assert message.content == 'Hi there!'
            assert message.context_used == 'Some context'


class TestGreetingModel:
    """Test Greeting model"""
    
    def test_create_greeting(self, app):
        """Test greeting creation"""
        with app.app_context():
            greeting = Greeting(
                text='Hello!',
                language='en',
                category='casual'
            )
            db.session.add(greeting)
            db.session.commit()
            
            assert greeting.id is not None
            assert greeting.text == 'Hello!'
            assert greeting.language == 'en'
            assert greeting.category == 'casual'
    
    def test_greeting_to_dict(self, app):
        """Test greeting to_dict method"""
        with app.app_context():
            greeting = Greeting(text='Hello!', language='en')
            db.session.add(greeting)
            db.session.commit()
            
            greeting_dict = greeting.to_dict()
            assert 'id' in greeting_dict
            assert 'text' in greeting_dict
            assert greeting_dict['text'] == 'Hello!'