"""
Unit Test: Flask API Endpoints
Tests API endpoint logic with mocked database
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, hash_password, verify_password, generate_token, verify_token


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


class TestAuthAPI:
    """Test suite for authentication API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200"""
        # Act
        response = client.get('/api/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        # Act
        response = client.get('/')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
        assert 'auth' in data['endpoints']
    
    # Update the mocking in test_signup_success:
    @patch('app.supabase')
    def test_signup_success(self, mock_supabase, client):
        """Test successful user signup"""
        # Arrange
        # Create proper mock chain
        mock_table = Mock()
        
        # Setup chain for checking existing user - returns empty list (no existing user)
        mock_existing_check = Mock()
        mock_existing_check.data = []  # Empty list means no existing user
        
        # Setup chain for insert
        mock_insert_result = Mock()
        mock_insert_result.data = [{
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 25,
            'gender': 'male',
            'password': 'hashed_password',
            'allergies': [],
            'diet': 'regular',
            'medical_conditions': [],
            'disliked_ingredients': [],
            'created_at': '2024-01-01T00:00:00'
        }]
        
        # Mock the method chain
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.side_effect = [mock_existing_check, mock_insert_result]
        
        mock_table.insert.return_value = mock_table
        
        mock_supabase.table.return_value = mock_table
        
        signup_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'age': 25,
            'gender': 'male',
            'allergies': ['nuts'],
            'diet': 'regular'
        }
        
        # Act
        response = client.post('/api/auth/signup',
                            data=json.dumps(signup_data),
                            content_type='application/json')
        
        # Debug
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    @patch('app.supabase')
    def test_signup_missing_fields(self, mock_supabase, client):
        """Test signup fails with missing required fields"""
        # Arrange
        incomplete_data = {
            'email': 'test@example.com',
            'password': 'password123'
            # Missing name, age, gender
        }
        
        # Act
        response = client.post('/api/auth/signup',
                              data=json.dumps(incomplete_data),
                              content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required field' in data['error']
    
    @patch('app.supabase')
    def test_signup_duplicate_email(self, mock_supabase, client):
        """Test signup fails with duplicate email"""
        # Arrange - simulate existing user
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{'email': 'test@example.com'}]
        )
        
        signup_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'age': 25,
            'gender': 'male'
        }
        
        # Act
        response = client.post('/api/auth/signup',
                              data=json.dumps(signup_data),
                              content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'already registered' in data['error'].lower()
    
    # Update test_login_success similarly:
    @patch('app.supabase')
    def test_login_success(self, mock_supabase, client):
        """Test successful user login"""
        # Arrange
        hashed_pw = hash_password('password123')
        
        # Create a simpler mock setup
        mock_result = MagicMock()
        mock_result.data = [{
            'id': 1,
            'email': 'test@example.com',
            'password': hashed_pw,
            'name': 'Test User',
            'age': 25,
            'gender': 'male',
            'allergies': [],
            'diet': 'regular',
            'medical_conditions': [],
            'disliked_ingredients': []
        }]
        
        # Create a mock that can be called as a chain
        chain_mock = MagicMock()
        chain_mock.eq.return_value = chain_mock
        chain_mock.execute.return_value = mock_result
        
        # Mock the table method
        mock_table = MagicMock()
        mock_table.select.return_value = chain_mock
        
        mock_supabase.table.return_value = mock_table
        
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        # Act
        response = client.post('/api/auth/login',
                            data=json.dumps(login_data),
                            content_type='application/json')
        
        # Debug
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
    
    @patch('app.supabase')
    def test_login_invalid_credentials(self, mock_supabase, client):
        """Test login fails with invalid credentials"""
        # Arrange
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=[])
        
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }
        
        # Act
        response = client.post('/api/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data


class TestHelperFunctions:
    """Test suite for helper functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        # Act
        hashed = hash_password('mypassword123')
        
        # Assert
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != 'mypassword123'
        assert len(hashed) > 20  # Bcrypt hashes are long
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        # Arrange
        password = 'mypassword123'
        hashed = hash_password(password)
        
        # Act
        is_valid = verify_password(password, hashed)
        
        # Assert
        assert is_valid is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        # Arrange
        password = 'mypassword123'
        hashed = hash_password(password)
        
        # Act
        is_valid = verify_password('wrongpassword', hashed)
        
        # Assert
        assert is_valid is False
    
    def test_generate_token(self):
        """Test JWT token generation"""
        # Act
        token = generate_token(user_id=123, email='test@example.com')
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_verify_token_valid(self):
        """Test JWT token verification with valid token"""
        # Arrange
        user_id = 123
        email = 'test@example.com'
        token = generate_token(user_id, email)
        
        # Act
        payload = verify_token(token)
        
        # Assert
        assert payload is not None
        assert str(payload['user_id']) == str(user_id)
        assert payload['email'] == email
    
    def test_verify_token_invalid(self):
        """Test JWT token verification with invalid token"""
        # Act
        payload = verify_token('invalid.token.here')
        
        # Assert
        assert payload is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])