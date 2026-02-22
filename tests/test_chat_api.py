"""
Tests for chat API
"""
import json
import pytest


class TestChatAPI:
    """Test chat API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'database' in data
    
    def test_ping(self, client):
        """Test ping endpoint"""
        response = client.get('/api/ping')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['message'] == 'pong'
    
    def test_chat_endpoint_valid_request(self, client):
        """Test chat endpoint with valid request"""
        payload = {
            'message': 'Hello, how are you?',
            'user_id': 'test_user_123'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        assert 'conversation_id' in data
        assert 'timestamp' in data
    
    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message"""
        payload = {
            'user_id': 'test_user_123'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_endpoint_missing_user_id(self, client):
        """Test chat endpoint with missing user_id"""
        payload = {
            'message': 'Hello'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_endpoint_with_conversation_id(self, client):
        """Test chat endpoint with existing conversation"""
        # First message
        payload1 = {
            'message': 'Hello',
            'user_id': 'test_user_123'
        }
        
        response1 = client.post(
            '/api/chat',
            data=json.dumps(payload1),
            content_type='application/json'
        )
        
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        conversation_id = data1['conversation_id']
        
        # Second message in same conversation
        payload2 = {
            'message': 'How can you help me?',
            'user_id': 'test_user_123',
            'conversation_id': conversation_id
        }
        
        response2 = client.post(
            '/api/chat',
            data=json.dumps(payload2),
            content_type='application/json'
        )
        
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['conversation_id'] == conversation_id
    
    def test_get_conversation_history(self, client):
        """Test getting conversation history"""
        # Create a conversation
        payload = {
            'message': 'Hello',
            'user_id': 'test_user_123'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        conversation_id = data['conversation_id']
        
        # Get conversation history
        response = client.get(f'/api/conversations/{conversation_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'conversation_id' in data
        assert 'messages' in data
        assert len(data['messages']) >= 2  # User message + assistant response
    
    def test_get_user_conversations(self, client):
        """Test getting all user conversations"""
        user_id = 'test_user_456'
        
        # Create multiple conversations
        for i in range(3):
            payload = {
                'message': f'Message {i}',
                'user_id': user_id
            }
            
            client.post(
                '/api/chat',
                data=json.dumps(payload),
                content_type='application/json'
            )
        
        # Get user conversations
        response = client.get(f'/api/conversations/user/{user_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'user_id' in data
        assert 'conversations' in data
        assert len(data['conversations']) == 3