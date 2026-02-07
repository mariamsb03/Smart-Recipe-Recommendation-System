"""
Shared pytest configuration and fixtures
"""
import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests - test individual components in isolation"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests - test multiple components together"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests - test complete user workflows"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )


@pytest.fixture(scope="session")
def test_user_data():
    """Sample user data for testing across all test suites"""
    return {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'hashed_password_123',
        'age': 25,
        'gender': 'female',
        'allergies': ['peanuts', 'shellfish'],
        'diet': 'vegetarian',
        'medical_conditions': ['diabetes'],
        'disliked_ingredients': ['cilantro', 'mushrooms'],
        'liked_recipes': [],
        'disliked_recipes': []
    }


@pytest.fixture(scope="session")
def test_recipes_data():
    """Sample recipe data for testing across all test suites"""
    return [
        {
            'id': 1,
            'recipe_name': 'Vegetarian Pasta',
            'ingredients_list': "['pasta', 'tomatoes', 'basil', 'garlic', 'olive oil']",
            'cuisine': 'Italian',
            'cook_time_minutes': 25,
            'calories': 450,
            'servings': 4,
            'rating': 4.5,
            'diet': 'vegetarian',
            'url': 'http://example.com/recipe1',
            'img_src': 'http://example.com/img1.jpg',
            'directions': 'Cook pasta. Make sauce. Combine.',
            'timing': 'dinner'
        },
        {
            'id': 2,
            'recipe_name': 'Greek Salad',
            'ingredients_list': "['lettuce', 'tomatoes', 'cucumber', 'feta', 'olives']",
            'cuisine': 'Greek',
            'cook_time_minutes': 15,
            'calories': 300,
            'servings': 2,
            'rating': 4.8,
            'diet': 'vegetarian',
            'url': 'http://example.com/recipe2',
            'img_src': 'http://example.com/img2.jpg',
            'directions': 'Chop vegetables. Add cheese. Toss.',
            'timing': 'lunch'
        },
        {
            'id': 3,
            'recipe_name': 'Quinoa Bowl',
            'ingredients_list': "['quinoa', 'avocado', 'chickpeas', 'tahini']",
            'cuisine': 'Mediterranean',
            'cook_time_minutes': 30,
            'calories': 550,
            'servings': 2,
            'rating': 4.6,
            'diet': 'vegan',
            'url': 'http://example.com/recipe3',
            'img_src': 'http://example.com/img3.jpg',
            'directions': 'Cook quinoa. Prepare toppings. Assemble.',
            'timing': 'lunch'
        }
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    env_vars = {
        'FLASK_SECRET_KEY': 'test-secret-key-12345',
        'FLASK_ENV': 'testing',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-supabase-key',
        'MLFLOW_TRACKING_URI': 'https://test.mlflow.com',
        'MLFLOW_MODEL_NAME': 'test-model',
        'MLFLOW_EXPERIMENT_NAME': 'test-experiment',
        'MLFLOW_MODEL_VERSION': '1',
        'MLFLOW_TRACKING_USERNAME': 'testuser',
        'MLFLOW_TRACKING_PASSWORD': 'testpass'
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars