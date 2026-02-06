from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import bcrypt
import jwt
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("WARNING: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    supabase = None
else:
    supabase: Client = create_client(supabase_url, supabase_key)

# ============= HELPER FUNCTIONS =============

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        'user_id': str(user_id),  # Convert to string for consistency
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def parse_ingredients_list(ingredients_str):
    """Parse ingredients list from string to array"""
    if not ingredients_str:
        return []
    
    # If it's already a list, return it
    if isinstance(ingredients_str, list):
        return ingredients_str
    
    try:
        # Try to parse as JSON array
        if ingredients_str.startswith('['):
            parsed = json.loads(ingredients_str.replace("'", '"'))
            return parsed if isinstance(parsed, list) else []
    except:
        pass
    
    # Fallback: split by comma
    return [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]

def format_recipe(recipe):
    """Format recipe data for response"""
    if not recipe:
        return None
    
    return {
        'id': recipe['id'],
        'recipe_name': recipe.get('recipe_name', 'Unknown Recipe'),
        'ingredients_list': parse_ingredients_list(recipe.get('ingredients_list', [])),
        'cuisine': recipe.get('cuisine', 'Various'),
        'cook_time_minutes': recipe.get('cook_time_minutes', 30),
        'timing': recipe.get('timing', ''),
        'calories': recipe.get('calories', 0),
        'servings': recipe.get('servings', 4),
        'rating': float(recipe.get('rating', 4.0)),
        'url': recipe.get('url', ''),
        'img_src': recipe.get('img_src', ''),
        'directions': recipe.get('directions', '')
    }

# ============= AUTH ROUTES =============

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create a new user account"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'age', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        existing_user = supabase.table('users').select('*').eq('email', data['email']).execute()
        if existing_user.data:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Create user
        user_data = {
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'age': data['age'],
            'gender': data['gender'],
            'allergies': data.get('allergies', []),
            'diet': data.get('diet', 'regular'),
            'medical_conditions': data.get('medicalConditions', []),
            'disliked_ingredients': data.get('dislikedIngredients', []),
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            token = generate_token(user['id'], user['email'])
            
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user': {
                    'id': str(user['id']),
                    'name': user['name'],
                    'email': user['email'],
                    'age': user['age'],
                    'gender': user['gender'],
                    'allergies': user['allergies'],
                    'diet': user['diet'],
                    'medicalConditions': user['medical_conditions'],
                    'dislikedIngredients': user['disliked_ingredients']
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user by email
        result = supabase.table('users').select('*').eq('email', data['email']).execute()
        
        if not result.data:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(data['password'], user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['id']),
                'name': user['name'],
                'email': user['email'],
                'age': user['age'],
                'gender': user['gender'],
                'allergies': user['allergies'],
                'diet': user['diet'],
                'medicalConditions': user['medical_conditions'],
                'dislikedIngredients': user['disliked_ingredients']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============= USER ROUTES =============

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        # Get token from header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user
        result = supabase.table('users').select('*').eq('id', payload['user_id']).execute()
        
        if not result.data:
            return jsonify({'error': 'User not found'}), 404
        
        user = result.data[0]
        
        return jsonify({
            'user': {
                'id': str(user['id']),
                'name': user['name'],
                'email': user['email'],
                'age': user['age'],
                'gender': user['gender'],
                'allergies': user['allergies'],
                'diet': user['diet'],
                'medicalConditions': user['medical_conditions'],
                'dislikedIngredients': user['disliked_ingredients']
            }
        }), 200
        
    except Exception as e:
        print(f"Get profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        # Get token from header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get update data
        data = request.json
        
        # Update user
        update_data = {
            'name': data.get('name'),
            'age': data.get('age'),
            'gender': data.get('gender'),
            'allergies': data.get('allergies', []),
            'diet': data.get('diet', 'regular'),
            'medical_conditions': data.get('medicalConditions', []),
            'disliked_ingredients': data.get('dislikedIngredients', []),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = supabase.table('users').update(update_data).eq('id', payload['user_id']).execute()
        
        if result.data:
            user = result.data[0]
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': str(user['id']),
                    'name': user['name'],
                    'email': user['email'],
                    'age': user['age'],
                    'gender': user['gender'],
                    'allergies': user['allergies'],
                    'diet': user['diet'],
                    'medicalConditions': user['medical_conditions'],
                    'dislikedIngredients': user['disliked_ingredients']
                }
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        print(f"Update profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============= RECIPE ROUTES =============

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get recipes with optional filters"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        # Get query parameters
        cuisine = request.args.get('cuisine')
        max_time = request.args.get('maxTime', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Build query
        query = supabase.table('recipes').select('*')
        
        if cuisine and cuisine != 'Any':
            query = query.eq('cuisine', cuisine)
        
        if max_time:
            query = query.lte('cook_time_minutes', max_time)
        
        result = query.limit(limit).execute()
        
        # Format recipes
        formatted_recipes = [format_recipe(recipe) for recipe in result.data]
        
        return jsonify({
            'recipes': formatted_recipes
        }), 200
        
    except Exception as e:
        print(f"Get recipes error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get single recipe by ID"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        result = supabase.table('recipes').select('*').eq('id', recipe_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Recipe not found'}), 404
        
        return jsonify({
            'recipe': format_recipe(result.data[0])
        }), 200
        
    except Exception as e:
        print(f"Get recipe error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============= RECIPE INTERACTIONS =============

@app.route('/api/recipes/<int:recipe_id>/like', methods=['POST'])
def like_recipe(recipe_id):
    """Like a recipe"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if already liked
        existing = supabase.table('recipe_likes').select('*').eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
        
        if existing.data:
            # Unlike
            supabase.table('recipe_likes').delete().eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
            return jsonify({'message': 'Recipe unliked', 'liked': False}), 200
        else:
            # Like
            results = supabase.table('recipe_likes').insert({
                'user_id': payload['user_id'],
                'recipe_id': recipe_id,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            print(results)

            
            # Remove dislike if exists
            supabase.table('recipe_dislikes').delete().eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
            
            return jsonify({'message': 'Recipe liked', 'liked': True}), 200
        
    except Exception as e:
        print(f"Like recipe error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>/dislike', methods=['POST'])
def dislike_recipe(recipe_id):
    """Dislike a recipe"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if already disliked
        existing = supabase.table('recipe_dislikes').select('*').eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
        
        if existing.data:
            # Remove dislike
            supabase.table('recipe_dislikes').delete().eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
            return jsonify({'message': 'Recipe undisliked', 'disliked': False}), 200
        else:
            # Dislike
            supabase.table('recipe_dislikes').insert({
                'user_id': payload['user_id'],
                'recipe_id': recipe_id,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            # Remove like if exists
            supabase.table('recipe_likes').delete().eq('user_id', payload['user_id']).eq('recipe_id', recipe_id).execute()
            
            return jsonify({'message': 'Recipe disliked', 'disliked': True}), 200
        
    except Exception as e:
        print(f"Dislike recipe error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/liked-recipes', methods=['GET'])
def get_liked_recipes():
    """Get user's liked recipes"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        result = supabase.table('recipe_likes').select('recipe_id').eq('user_id', payload['user_id']).execute()
        
        recipe_ids = [item['recipe_id'] for item in result.data]
        
        return jsonify({
            'likedRecipes': recipe_ids
        }), 200
        
    except Exception as e:
        print(f"Get liked recipes error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/disliked-recipes', methods=['GET'])
def get_disliked_recipes():
    """Get user's disliked recipes"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
            
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        result = supabase.table('recipe_dislikes').select('recipe_id').eq('user_id', payload['user_id']).execute()
        
        recipe_ids = [item['recipe_id'] for item in result.data]
        
        return jsonify({
            'dislikedRecipes': recipe_ids
        }), 200
        
    except Exception as e:
        print(f"Get disliked recipes error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if supabase else 'not configured'
    }), 200

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'FlavorFit API',
        'version': '1.0.0',
        'endpoints': {
            'auth': ['/api/auth/signup', '/api/auth/login'],
            'user': ['/api/user/profile'],
            'recipes': ['/api/recipes', '/api/recipes/<id>'],
            'interactions': ['/api/recipes/<id>/like', '/api/recipes/<id>/dislike'],
            'health': '/api/health'
        }
    }), 200

# ============= RUN APP =============

if __name__ == '__main__':
    print("=" * 50)
    print("FlavorFit Backend Starting...")
    print("=" * 50)
    if supabase:
        print("✓ Supabase connected")
    else:
        print("✗ Supabase not configured - check .env file")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)