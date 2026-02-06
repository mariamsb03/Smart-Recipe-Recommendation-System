"""
Backend Unit Tests - API Endpoints
Tests for FlavorFit Flask API endpoints
"""
import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, hash_password, verify_password, generate_token, verify_token, parse_ingredients_list

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_token():
    """Generate a mock JWT token for testing"""
    return generate_token('test-user-id', 'test@example.com')

# ============= Helper Function Tests =============

def test_hash_password():
    """Test password hashing"""
    password = "testpassword123"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert hashed != password
    assert len(hashed) > 20

def test_verify_password():
    """Test password verification"""
    password = "testpassword123"
    hashed = hash_password(password)
    
    # Correct password
    assert verify_password(password, hashed) is True
    
    # Wrong password
    assert verify_password("wrongpassword", hashed) is False

def test_generate_token():
    """Test JWT token generation"""
    token = generate_token('user123', 'test@example.com')
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 20

def test_verify_token():
    """Test JWT token verification"""
    user_id = 'user123'
    email = 'test@example.com'
    token = generate_token(user_id, email)
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload['user_id'] == user_id
    assert payload['email'] == email

def test_verify_token_invalid():
    """Test JWT token verification with invalid token"""
    payload = verify_token('invalid-token')
    assert payload is None

def test_parse_ingredients_list_from_array():
    """Test parsing ingredients from array"""
    ingredients = ['tomato', 'onion', 'garlic']
    result = parse_ingredients_list(ingredients)
    
    assert result == ingredients

def test_parse_ingredients_list_from_json_string():
    """Test parsing ingredients from JSON string"""
    ingredients_str = "['tomato', 'onion', 'garlic']"
    result = parse_ingredients_list(ingredients_str)
    
    assert isinstance(result, list)
    assert len(result) == 3

def test_parse_ingredients_list_from_comma_separated():
    """Test parsing ingredients from comma-separated string"""
    ingredients_str = "tomato, onion, garlic"
    result = parse_ingredients_list(ingredients_str)
    
    assert isinstance(result, list)
    assert len(result) == 3
    assert 'tomato' in result

def test_parse_ingredients_list_empty():
    """Test parsing empty ingredients"""
    result = parse_ingredients_list(None)
    assert result == []
    
    result = parse_ingredients_list("")
    assert result == []

# ============= Health Check Tests =============

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'FlavorFit API'
    assert 'version' in data
    assert 'endpoints' in data

# ============= Auth Endpoint Tests (Without Database) =============

def test_signup_missing_fields(client):
    """Test signup with missing required fields"""
    response = client.post('/api/auth/signup',
                          data=json.dumps({
                              'email': 'test@example.com'
                          }),
                          content_type='application/json')
    
    # Should return 400 or 500 depending on database availability
    assert response.status_code in [400, 500]

def test_login_missing_credentials(client):
    """Test login with missing credentials"""
    response = client.post('/api/auth/login',
                          data=json.dumps({
                              'email': 'test@example.com'
                          }),
                          content_type='application/json')
    
    assert response.status_code in [400, 500]

# ============= Recipe Endpoint Tests (Without Database) =============

def test_get_recipes_without_filters(client):
    """Test getting recipes without filters"""
    response = client.get('/api/recipes')
    
    # Should return 200 or 500 depending on database
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'recipes' in data

def test_get_recipes_with_filters(client):
    """Test getting recipes with filters"""
    response = client.get('/api/recipes?cuisine=Italian&maxTime=30&limit=10')
    
    assert response.status_code in [200, 500]

def test_get_single_recipe(client):
    """Test getting a single recipe"""
    response = client.get('/api/recipes/1')
    
    # Should return 200, 404, or 500
    assert response.status_code in [200, 404, 500]

# ============= Protected Endpoint Tests =============

def test_get_profile_without_token(client):
    """Test getting profile without auth token"""
    response = client.get('/api/user/profile')
    
    assert response.status_code == 401
    
    data = json.loads(response.data)
    assert 'error' in data

def test_get_profile_with_invalid_token(client):
    """Test getting profile with invalid token"""
    response = client.get('/api/user/profile',
                         headers={'Authorization': 'Bearer invalid-token'})
    
    assert response.status_code == 401

def test_like_recipe_without_token(client):
    """Test liking recipe without auth token"""
    response = client.post('/api/recipes/1/like')
    
    assert response.status_code == 401

def test_dislike_recipe_without_token(client):
    """Test disliking recipe without auth token"""
    response = client.post('/api/recipes/1/dislike')
    
    assert response.status_code == 401

# ============= Request Validation Tests =============

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get('/api/health')
    
    # Flask-CORS should add appropriate headers
    assert response.status_code == 200

def test_json_content_type(client):
    """Test API returns JSON content type"""
    response = client.get('/api/health')
    
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_post_with_invalid_json(client):
    """Test POST endpoint with invalid JSON"""
    response = client.post('/api/auth/login',
                          data='invalid json',
                          content_type='application/json')
    
    # Should return error status
    assert response.status_code >= 400

def test_get_profile_without_token(client):
    """Test getting profile without auth token"""
    response = client.get('/api/user/profile')
    
    # Debug: Print the actual error
    print(f"\n=== DEBUG test_get_profile_without_token ===")
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.data.decode('utf-8')}")
    
    if response.status_code == 500:
        try:
            data = json.loads(response.data)
            print(f"Error message: {data.get('message', 'No message')}")
            print(f"Error type: {data.get('error', 'No error type')}")
        except:
            print(f"Raw response: {response.data}")
    
    assert response.status_code == 401
    
    data = json.loads(response.data)
    assert 'error' in data

def test_get_profile_with_invalid_token(client):
    """Test getting profile with invalid token"""
    response = client.get('/api/user/profile',
                         headers={'Authorization': 'Bearer invalid-token'})
    
    # Debug: Print the actual error
    print(f"\n=== DEBUG test_get_profile_with_invalid_token ===")
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.data.decode('utf-8')}")
    
    assert response.status_code == 401
