from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import bcrypt
import jwt
from datetime import datetime, timedelta
import json
import mlflow
import mlflow.pyfunc
import pandas as pd
from model_loader import load_production_model 

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

MLFLOW_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5001')
MLFLOW_EXPERIMENT = os.getenv('MLFLOW_EXPERIMENT', 'FlavorFit-Recommendation')

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT)

# ================= LOAD MODEL ==================
try:
    ml_model = load_production_model()
    print("✓ ML model loaded successfully")
except Exception as e:
    ml_model = None
    print(f"✗ ML model failed to load: {e}")

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


# ============= ML HELPER FUNCTIONS =============
def compute_recipe_features(user_prefs, recipe):
    """
    Compute the 5 features needed by the model
    (Same as the working test version)
    
    Args:
        user_prefs: dict with user preferences
        recipe: dict with recipe details
    
    Returns:
        dict with the 5 computed features
    """
    # Feature 1: User preference - max cooking time
    max_cooking_time = user_prefs.get('max_cooking_time', 60)
    
    # Feature 2: Recipe attribute - cook time
    recipe_cook_time = recipe.get('cook_time_minutes', 30)
    
    # Feature 3: Difference in cooking time
    cook_time_diff = abs(recipe_cook_time - max_cooking_time)
    
    # Feature 4: Ingredient overlap ratio
    # Calculate how many ingredients user can eat vs total ingredients
    user_allergies = set(user_prefs.get('allergies', []))
    user_dislikes = set(user_prefs.get('disliked_ingredients', []))
    recipe_ingredients = set(parse_ingredients_list(recipe.get('ingredients_list', [])))
    
    blocked_ingredients = user_allergies | user_dislikes
    usable_ingredients = recipe_ingredients - blocked_ingredients
    ingredient_overlap_ratio = len(usable_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0
    
    # Feature 5: Cuisine similarity
    # 1.0 if recipe cuisine matches user preference, 0.0 otherwise
    user_cuisines = user_prefs.get('preferred_cuisine', [])
    if isinstance(user_cuisines, str):
        user_cuisines = [user_cuisines]
    user_cuisines = set([c.lower().strip() for c in user_cuisines])
    recipe_cuisine = str(recipe.get('cuisine', '')).lower().strip()
    cuisine_similarity = 1.0 if recipe_cuisine in user_cuisines else 0.0
    
    return {
        'max_cooking_time': max_cooking_time,
        'recipe_cook_time': recipe_cook_time,
        'cook_time_diff': cook_time_diff,
        'ingredient_overlap_ratio': ingredient_overlap_ratio,
        'cuisine_similarity': cuisine_similarity
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

# ============= ML RECOMMENDATION ROUTE ============
@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Recommend recipes based on ML model with ingredient search filtering"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not configured'}), 500
        if not ml_model:
            return jsonify({'error': 'ML model not loaded'}), 500

        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400

        # Get search ingredients from request
        search_ingredients = data.get('search_ingredients', [])  # e.g., ['chicken']
        if isinstance(search_ingredients, str):
            search_ingredients = [search_ingredients]
        search_ingredients = set([ing.lower().strip() for ing in search_ingredients if ing])

        # ---------------- Fetch user -----------------
        user_result = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user_result.data:
            return jsonify({'error': 'User not found'}), 404
        user = user_result.data[0]

        allergies = set(user.get('allergies', []))
        disliked = set(user.get('disliked_ingredients', []))
        diet = user.get('diet', 'regular')

        user_prefs = {
            'preferred_cuisine': data.get('preferred_cuisine', []),
            'max_cooking_time': data.get('max_cooking_time', 60),
            'allergies': list(allergies),
            'disliked_ingredients': list(disliked),
            'diet': diet
        }

        # ---------------- Fetch recipes ----------------
        recipes_result = supabase.table('recipes').select('*').execute()
        recipes = recipes_result.data

        # ---------------- Hard rules filter ----------------
        # Get preferred cuisines
        preferred_cuisines = user_prefs.get('preferred_cuisine', [])
        if isinstance(preferred_cuisines, str):
            preferred_cuisines = [preferred_cuisines]
        preferred_cuisines = set([c.lower().strip() for c in preferred_cuisines if c])
        
        # Map cuisine categories to actual database cuisines
        CUISINE_MAPPING = {
            'mediterranean': {'greek', 'moroccan', 'spanish', 'middle eastern', 'turkish', 'lebanese'},
            'asian': {'chinese', 'japanese', 'thai', 'vietnamese', 'korean', 'asian'},
            'european': {'french', 'italian', 'german', 'british', 'english', 'spanish', 'polish', 'dutch', 'austrian', 'scandinavian', 'hungarian', 'irish'}
        }
        
        # Expand preferred cuisines based on mapping
        expanded_cuisines = set()
        for pref in preferred_cuisines:
            if pref in CUISINE_MAPPING:
                # Add all related cuisines
                expanded_cuisines.update(CUISINE_MAPPING[pref])
            else:
                # Keep the original cuisine
                expanded_cuisines.add(pref)
        
        # Use expanded cuisines for filtering
        filter_cuisines = expanded_cuisines if expanded_cuisines else set()
        
        filtered = []
        for r in recipes:
            ingredients = set(parse_ingredients_list(r.get('ingredients_list')))
            
            # Skip if contains allergies
            if allergies & ingredients:
                continue
            
            # Skip if contains disliked ingredients
            if disliked & ingredients:
                continue
            
            # Skip if diet doesn't match
            if diet != 'regular' and r.get('diet') != diet:
                continue
            
            # **HARD FILTER: Skip if cuisine doesn't match (when user specified one)**
            if filter_cuisines:
                recipe_cuisine = str(r.get('cuisine', '')).lower().strip()
                if recipe_cuisine not in filter_cuisines:
                    continue
            
            # **If user searched for specific ingredients, only include recipes that contain them**
            if search_ingredients:
                # Convert recipe ingredients to lowercase for comparison
                recipe_ingredients_lower = set([ing.lower().strip() for ing in ingredients])
                
                # Check if ANY of the searched ingredients are in the recipe
                # Use partial matching (e.g., "chicken" matches "chicken breast")
                if not any(
                    search_ing in recipe_ing 
                    for search_ing in search_ingredients 
                    for recipe_ing in recipe_ingredients_lower
                ):
                    continue
            
            filtered.append(r)

        if not filtered:
            message = 'No recipes found with these ingredients' if search_ingredients else 'No recipes match your preferences'
            return jsonify({'recipes': [], 'message': message, 'total_candidates': 0, 'total_scored': 0})

        # ---------------- ML scoring with boosting ----------------
        scored = []
        with mlflow.start_run(run_name=f"user_{user_id}_inference"):
            # ---- SAFE PARAMS ----
            mlflow.log_param("user_id", user_id)
            mlflow.log_param("num_candidates", len(filtered))

            if search_ingredients:
                mlflow.log_param(
                    "search_ingredients",
                    ",".join(sorted(search_ingredients))  # ✅ stringify
                )

            if preferred_cuisines:
                mlflow.log_param(
                    "preferred_cuisines",
                    ",".join(sorted(preferred_cuisines))  # ✅ stringify
                )

            for recipe in filtered:
                features = compute_recipe_features(user_prefs, recipe)
                input_df = pd.DataFrame([features])
                
                try:
                    # Get base ML score
                    base_score = float(ml_model.predict(input_df)[0])
                    
                    # Apply boosting to make scores more meaningful
                    boosted_score = base_score
                    
                    # BOOST 1: Ingredient search match (0.2 bonus per matching ingredient)
                    if search_ingredients:
                        recipe_ingredients = set([ing.lower().strip() for ing in parse_ingredients_list(recipe.get('ingredients_list', []))])
                        matches = sum(1 for search_ing in search_ingredients 
                                    if any(search_ing in recipe_ing for recipe_ing in recipe_ingredients))
                        if matches > 0:
                            ingredient_boost = matches * 0.2
                            boosted_score += ingredient_boost
                            mlflow.log_metric(f"recipe_{recipe['id']}_ingredient_boost", ingredient_boost)
                    
                    # BOOST 2: Perfect/near-perfect cooking time match
                    cook_time = recipe.get('cook_time_minutes', 60)
                    max_time = user_prefs.get('max_cooking_time', 60)
                    time_diff = abs(cook_time - max_time)
                    if time_diff <= 5:
                        time_boost = 0.15  # Within 5 minutes
                        boosted_score += time_boost
                    elif time_diff <= 15:
                        time_boost = 0.10  # Within 15 minutes
                        boosted_score += time_boost
                    elif time_diff <= 30:
                        time_boost = 0.05  # Within 30 minutes
                        boosted_score += time_boost
                    
                    # BOOST 3: Cuisine match (already filtered, but boost for logging)
                    if preferred_cuisines:
                        recipe_cuisine = str(recipe.get('cuisine', '')).lower().strip()
                        if recipe_cuisine in preferred_cuisines:
                            cuisine_boost = 0.1
                            boosted_score += cuisine_boost
                    
                    # Cap the score at 1.0 (100%)
                    final_score = min(1.0, boosted_score)
                    
                    mlflow.log_metric(f"recipe_{recipe['id']}_base_score", base_score)
                    mlflow.log_metric(f"recipe_{recipe['id']}_final_score", final_score)
                    
                except Exception as e:
                    final_score = 0.0
                    print(f"ML prediction error for recipe {recipe['id']}: {e}")
                    print(f"Features were: {features}")
                
                scored.append((recipe, final_score))

            scored.sort(key=lambda x: x[1], reverse=True)
            if scored:
                mlflow.log_param('top_recipe', scored[0][0]['recipe_name'])
                mlflow.log_metric('top_score', scored[0][1])

        # ---------------- Build response ----------------
        response = []
        for r, score in scored:
            item = format_recipe(r)
            item['ml_score'] = round(score, 4)
            response.append(item)

        return jsonify({
            'recipes': response,
            'total_candidates': len(filtered),
            'total_scored': len(scored),
            'search_ingredients': list(search_ingredients) if search_ingredients else []
        })

    except Exception as e:
        print(f"Recommendation error: {e}")
        import traceback
        traceback.print_exc()
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

# ============= SERVE FRONTEND =============

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React frontend"""
    # Skip API routes
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Serve static files or index.html
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    return send_from_directory(app.static_folder, 'index.html')

# ============= RUN APP =============

if __name__ == '__main__':
    print("=" * 50)
    print("FlavorFit Backend Starting...")
    print("=" * 50)
    if supabase:
        print("✓ Supabase connected")
    else:
        print("✗ Supabase not configured - check .env file")
    if ml_model:
        print("✓ ML model loaded")
    else:
        print("✗ ML model not loaded")
    print("=" * 50)
    port = int(os.getenv('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
