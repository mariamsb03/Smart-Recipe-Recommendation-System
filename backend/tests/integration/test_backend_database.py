"""
Integration Test: Backend + Supabase Database
Tests actual database CRUD operations with Supabase
"""
import pytest
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import bcrypt
from datetime import datetime

# Load environment variables
load_dotenv()


@pytest.fixture(scope='module')
def supabase_client():
    """Create Supabase client for testing"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        pytest.skip("Supabase credentials not configured")
    
    client = create_client(supabase_url, supabase_key)
    yield client
    
    # Cleanup: Delete test users created during testing
    # (Only if using a test database, be careful with production data!)


@pytest.fixture
def test_user_data():
    """Generate test user data"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return {
        'name': f'Test User {timestamp}',
        'email': f'test{timestamp}@example.com',
        'password': 'testpassword123',
        'age': 25,
        'gender': 'male',
        'allergies': ['nuts', 'dairy'],
        'diet': 'vegetarian',
        'medical_conditions': ['diabetes'],
        'disliked_ingredients': ['cilantro', 'olives']
    }


class TestSupabaseCRUD:
    """Test suite for Supabase database operations"""
    
    def test_database_connection(self, supabase_client):
        """Test that we can connect to Supabase"""
        # Act - Try to query the users table
        result = supabase_client.table('users').select('id').limit(1).execute()
        
        # Assert
        assert result is not None
        assert hasattr(result, 'data')
    
    def test_create_user(self, supabase_client, test_user_data):
        """Test creating a new user in the database"""
        # Arrange
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender'],
            'allergies': test_user_data['allergies'],
            'diet': test_user_data['diet'],
            'medical_conditions': test_user_data['medical_conditions'],
            'disliked_ingredients': test_user_data['disliked_ingredients'],
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Act
        result = supabase_client.table('users').insert(user_data).execute()
        
        # Assert
        assert result.data is not None
        assert len(result.data) > 0
        created_user = result.data[0]
        assert created_user['email'] == test_user_data['email']
        assert created_user['name'] == test_user_data['name']
        assert 'id' in created_user
        
        # Cleanup
        supabase_client.table('users').delete().eq('id', created_user['id']).execute()
    
    def test_read_user_by_email(self, supabase_client, test_user_data):
        """Test reading user data by email"""
        # Arrange - Create a user first
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender'],
            'allergies': test_user_data['allergies'],
            'diet': test_user_data['diet']
        }
        
        created = supabase_client.table('users').insert(user_data).execute()
        user_id = created.data[0]['id']
        
        # Act
        result = supabase_client.table('users').select('*').eq('email', test_user_data['email']).execute()
        
        # Assert
        assert result.data is not None
        assert len(result.data) > 0
        retrieved_user = result.data[0]
        assert retrieved_user['email'] == test_user_data['email']
        assert retrieved_user['name'] == test_user_data['name']
        assert retrieved_user['allergies'] == test_user_data['allergies']
        
        # Cleanup
        supabase_client.table('users').delete().eq('id', user_id).execute()
    
    def test_update_user_profile(self, supabase_client, test_user_data):
        """Test updating user profile information"""
        # Arrange - Create a user first
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender']
        }
        
        created = supabase_client.table('users').insert(user_data).execute()
        user_id = created.data[0]['id']
        
        # Act - Update user data
        updated_data = {
            'age': 30,
            'allergies': ['shellfish'],
            'diet': 'vegan'
        }
        
        result = supabase_client.table('users').update(updated_data).eq('id', user_id).execute()
        
        # Assert
        assert result.data is not None
        assert len(result.data) > 0
        updated_user = result.data[0]
        assert updated_user['age'] == 30
        assert updated_user['allergies'] == ['shellfish']
        assert updated_user['diet'] == 'vegan'
        
        # Cleanup
        supabase_client.table('users').delete().eq('id', user_id).execute()
    
    def test_delete_user(self, supabase_client, test_user_data):
        """Test deleting a user from the database"""
        # Arrange - Create a user first
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender']
        }
        
        created = supabase_client.table('users').insert(user_data).execute()
        user_id = created.data[0]['id']
        
        # Act - Delete the user
        delete_result = supabase_client.table('users').delete().eq('id', user_id).execute()
        
        # Assert - User should be deleted
        assert delete_result is not None
        
        # Verify user is gone
        check_result = supabase_client.table('users').select('*').eq('id', user_id).execute()
        assert len(check_result.data) == 0
    
    def test_query_recipes(self, supabase_client):
        """Test querying recipes from the database"""
        # Act
        result = supabase_client.table('recipes').select('*').limit(5).execute()
        
        # Assert
        assert result is not None
        assert result.data is not None
        # We expect at least some recipes in the database
        if len(result.data) > 0:
            recipe = result.data[0]
            assert 'id' in recipe
            assert 'recipe_name' in recipe
            assert 'ingredients_list' in recipe
    
    def test_like_recipe(self, supabase_client, test_user_data):
        """Test liking a recipe (creating user-recipe interaction)"""
        # Arrange - Create a test user
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender']
        }
        
        created_user = supabase_client.table('users').insert(user_data).execute()
        user_id = created_user.data[0]['id']
        
        # Get a recipe to like
        recipes = supabase_client.table('recipes').select('id').limit(1).execute()
        
        if len(recipes.data) > 0:
            recipe_id = recipes.data[0]['id']
            
            # Act - Create a "like" interaction
            like_data = {
                'user_id': user_id,
                'recipe_id': recipe_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Use the correct table name from your app
            result = supabase_client.table('recipe_likes').insert(like_data).execute()
            
            # Assert
            assert result.data is not None
            assert len(result.data) > 0
            like = result.data[0]
            assert like['user_id'] == user_id
            assert like['recipe_id'] == recipe_id
            
            # Cleanup
            supabase_client.table('recipe_likes').delete().eq('id', like['id']).execute()
        
        # Cleanup user
        supabase_client.table('users').delete().eq('id', user_id).execute()
    
    def test_duplicate_email_constraint(self, supabase_client, test_user_data):
        """Test that duplicate emails are prevented"""
        # Arrange - Create first user
        hashed_password = bcrypt.hashpw(
            test_user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_data = {
            'name': test_user_data['name'],
            'email': test_user_data['email'],
            'password': hashed_password,
            'age': test_user_data['age'],
            'gender': test_user_data['gender']
        }
        
        first_user = supabase_client.table('users').insert(user_data).execute()
        user_id = first_user.data[0]['id']
        
        # Act & Assert - Try to create duplicate
        try:
            supabase_client.table('users').insert(user_data).execute()
            # If we get here, the duplicate was allowed (should not happen)
            pytest.fail("Duplicate email was allowed")
        except Exception as e:
            # Expected - duplicate should be rejected
            assert 'duplicate' in str(e).lower() or 'unique' in str(e).lower()
        
        # Cleanup
        supabase_client.table('users').delete().eq('id', user_id).execute()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])