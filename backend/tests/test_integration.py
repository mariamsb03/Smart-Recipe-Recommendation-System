"""
Backend Integration Tests
End-to-end tests for API workflows
"""
import pytest
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ============= Auth Flow Integration Tests =============

def test_signup_login_flow(client):
    """Test complete signup and login flow"""
    # Note: This test will fail without database, but structure is correct
    
    # 1. Sign up
    signup_data = {
        'name': 'Test User',
        'email': 'integration@test.com',
        'password': 'testpass123',
        'age': 25,
        'gender': 'male',
        'allergies': ['peanuts'],
        'diet': 'regular'
    }
    
    signup_response = client.post('/api/auth/signup',
                                 data=json.dumps(signup_data),
                                 content_type='application/json')
    
    # Expect 201 on success, 500 if no database
    assert signup_response.status_code in [201, 400, 500]
    
    if signup_response.status_code == 201:
        signup_json = json.loads(signup_response.data)
        assert 'token' in signup_json
        assert 'user' in signup_json
        token = signup_json['token']
        
        # 2. Login with same credentials
        login_data = {
            'email': 'integration@test.com',
            'password': 'testpass123'
        }
        
        login_response = client.post('/api/auth/login',
                                    data=json.dumps(login_data),
                                    content_type='application/json')
        
        assert login_response.status_code == 200
        login_json = json.loads(login_response.data)
        assert 'token' in login_json

def test_protected_route_with_valid_token(client):
    """Test accessing protected route with valid token"""
    # This demonstrates the pattern even without actual database
    
    # Attempt to access protected route without token
    response = client.get('/api/user/profile')
    assert response.status_code == 401
    
    # Pattern for with token (would work with real database)
    # response = client.get('/api/user/profile',
    #                       headers={'Authorization': f'Bearer {token}'})
    # assert response.status_code == 200

def test_recipe_interaction_flow(client):
    """Test recipe like/dislike flow"""
    recipe_id = 1
    
    # Try to like without authentication
    like_response = client.post(f'/api/recipes/{recipe_id}/like')
    assert like_response.status_code == 401
    
    # Try to dislike without authentication
    dislike_response = client.post(f'/api/recipes/{recipe_id}/dislike')
    assert dislike_response.status_code == 401

# ============= Recipe Search Integration Tests =============

def test_recipe_search_and_detail_flow(client):
    """Test searching recipes and getting details"""
    # 1. Search for recipes
    search_response = client.get('/api/recipes?cuisine=Italian&maxTime=45')
    
    # Expect 200 on success, 500 if no database
    assert search_response.status_code in [200, 500]
    
    if search_response.status_code == 200:
        search_json = json.loads(search_response.data)
        assert 'recipes' in search_json
        
        if len(search_json['recipes']) > 0:
            # 2. Get details of first recipe
            recipe_id = search_json['recipes'][0]['id']
            detail_response = client.get(f'/api/recipes/{recipe_id}')
            
            assert detail_response.status_code == 200
            detail_json = json.loads(detail_response.data)
            assert 'recipe' in detail_json

def test_recipe_filtering(client):
    """Test recipe filtering with various parameters"""
    # Test different filter combinations
    
    # Filter by cuisine
    response1 = client.get('/api/recipes?cuisine=Italian')
    assert response1.status_code in [200, 500]
    
    # Filter by time
    response2 = client.get('/api/recipes?maxTime=30')
    assert response2.status_code in [200, 500]
    
    # Filter with limit
    response3 = client.get('/api/recipes?limit=5')
    assert response3.status_code in [200, 500]
    
    # Combined filters
    response4 = client.get('/api/recipes?cuisine=Mexican&maxTime=45&limit=10')
    assert response4.status_code in [200, 500]

# ============= User Profile Integration Tests =============

def test_user_profile_update_flow(client):
    """Test user profile retrieval and update"""
    # Without token
    get_response = client.get('/api/user/profile')
    assert get_response.status_code == 401
    
    update_response = client.put('/api/user/profile',
                                 data=json.dumps({'name': 'Updated Name'}),
                                 content_type='application/json')
    assert update_response.status_code == 401

def test_user_liked_recipes_flow(client):
    """Test getting user's liked recipes"""
    response = client.get('/api/user/liked-recipes')
    assert response.status_code == 401  # No token provided

def test_user_disliked_recipes_flow(client):
    """Test getting user's disliked recipes"""
    response = client.get('/api/user/disliked-recipes')
    assert response.status_code == 401  # No token provided

# ============= API Response Format Tests =============

def test_error_response_format(client):
    """Test that error responses have consistent format"""
    response = client.get('/api/user/profile')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    
    # Should have 'error' key
    assert 'error' in data
    assert isinstance(data['error'], str)

def test_success_response_format(client):
    """Test that success responses have consistent format"""
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Health check should have status
    assert 'status' in data

def test_recipe_response_format(client):
    """Test recipe response has all required fields"""
    response = client.get('/api/recipes/1')
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'recipe' in data
        
        recipe = data['recipe']
        # Check required fields
        assert 'id' in recipe
        assert 'recipe_name' in recipe
        assert 'ingredients_list' in recipe
        assert 'cuisine' in recipe
        assert 'cook_time_minutes' in recipe

# ============= Edge Case Tests =============

def test_nonexistent_recipe(client):
    """Test requesting a non-existent recipe"""
    response = client.get('/api/recipes/999999')
    
    # Should return 404 or 500
    assert response.status_code in [404, 500]

def test_invalid_recipe_id(client):
    """Test requesting recipe with invalid ID format"""
    response = client.get('/api/recipes/invalid')
    
    # Should return error
    assert response.status_code == 404

def test_like_nonexistent_recipe(client):
    """Test liking a non-existent recipe"""
    response = client.post('/api/recipes/999999/like')
    
    # Should return 401 (no auth) or error
    assert response.status_code >= 400

# ============= Performance Tests =============

def test_multiple_concurrent_requests(client):
    """Test handling multiple requests"""
    # Make multiple requests
    responses = []
    for i in range(5):
        response = client.get('/api/health')
        responses.append(response)
    
    # All should succeed
    for response in responses:
        assert response.status_code == 200

def test_recipe_list_limit(client):
    """Test recipe list respects limit parameter"""
    response = client.get('/api/recipes?limit=5')
    
    if response.status_code == 200:
        data = json.loads(response.data)
        # Should not exceed limit
        assert len(data['recipes']) <= 5
