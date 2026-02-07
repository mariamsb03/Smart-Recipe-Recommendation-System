import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from '@/components/Sidebar';
import { TagInput } from '@/components/TagInput';
import { useApp } from '@/context/AppContext';
import { Search, Clock, ChefHat, Globe, Loader2 } from 'lucide-react';

// Common ingredients for recipe requests
const COMMON_INGREDIENTS = [
  'Chicken', 'Beef', 'Pork', 'Fish','Butter', 'Cheese', 'Yogurt', 'Shrimp', 'Salmon', 'Tuna', 'Eggs',
  'Milk', 'Cream','Oranges', 'Lemons', 'Strawberries', 
  'Rice', 'Pasta', 'Bread', 'Flour', 'Noodles',
  'Tomatoes', 'Onions', 'Garlic', 'Potatoes', 'Carrots', 'Broccoli', 'Spinach', 'Bell Peppers', 'Mushrooms', 'Lettuce', 'Cucumber', 'Zucchini',
  'Apples', 'Bananas', 'Blueberries',
  'Olive Oil', 'Vegetable Oil', 'Soy Sauce', 'Salt', 'Pepper', 'Sugar', 'Vinegar',
  'Basil', 'Oregano', 'Thyme', 'Rosemary', 'Cilantro', 'Parsley', 'Ginger', 'Cumin', 'Paprika',
  'Beans', 'Lentils', 'Chickpeas', 'Tofu', 'Nuts', 'Almonds', 'Walnuts',
  'Honey', 'Maple Syrup', 'Chocolate', 'Vanilla', 'Cinnamon'
];

const CUISINES = [  'Any', 
  'American',
  'Mexican', 
  'Italian',
  'Mediterranean',  // Maps to Greek, Moroccan, Spanish, Middle Eastern
  'Asian',          // Maps to Chinese, Japanese, Thai, Vietnamese
  'Indian',
  'French',
  'German',
  'Caribbean',
  'British'];
const DIFFICULTIES = ['Any', 'Easy', 'Medium', 'Hard'];

// API configuration
const API_BASE_URL = 'http://localhost:5000';

export default function RecipeRequest() {
  const navigate = useNavigate();
  const { setSearchResults, setLastRequest, user } = useApp();

  const [ingredients, setIngredients] = useState<string[]>([]);
  const [cookingTime, setCookingTime] = useState(60);
  const [difficulty, setDifficulty] = useState('Any');
  const [cuisine, setCuisine] = useState('Any');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Make sure user is logged in
      if (!user || !user.id) {
        setError('Please log in to search for recipes');
        setIsLoading(false);
        return;
      }

      // Call the backend recommendation API
      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          search_ingredients: ingredients,  // ← This is the key ingredient search!
          preferred_cuisine: cuisine !== 'Any' ? [cuisine] : [],
          max_cooking_time: cookingTime,
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch recommendations');
      }

      const data = await response.json();
      
      // Transform the response to match your app's format
      const results = data.recipes.map((recipe: any) => ({
        ...recipe,
        matchScore: Math.round(recipe.ml_score * 100), // Convert 0-1 score to percentage
      }));

      setSearchResults(results);
      setLastRequest({ ingredients, cookingTime, difficulty, cuisine });
      navigate('/recipe-results');

    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'Failed to search recipes. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />

      <main className="ml-64 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="font-serif text-4xl font-bold text-foreground mb-2">
              Find Your Perfect Recipe
            </h1>
            <p className="text-muted-foreground text-lg">
              Tell us what you have and we'll suggest the best matches.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Ingredients */}
            <div className="bg-card rounded-2xl p-6 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                  <Search className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Available Ingredients</h3>
                  <p className="text-sm text-muted-foreground">What do you have on hand?</p>
                </div>
              </div>
              <TagInput
                tags={ingredients}
                setTags={setIngredients}
                suggestions={COMMON_INGREDIENTS}
                placeholder="Add ingredients..."
              />
              <p className="text-xs text-muted-foreground mt-2">
                💡 Tip: Add "Chicken" to find all chicken recipes!
              </p>
            </div>

            {/* Cooking Time */}
            <div className="bg-card rounded-2xl p-6 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                  <Clock className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Cooking Time</h3>
                  <p className="text-sm text-muted-foreground">How much time do you have?</p>
                </div>
              </div>
              <div className="space-y-4">
                <input
                  type="range"
                  min="15"
                  max="180"
                  step="15"
                  value={cookingTime}
                  onChange={(e) => setCookingTime(parseInt(e.target.value))}
                  className="w-full h-2 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>15 min</span>
                  <span className="font-semibold text-foreground">{cookingTime} minutes</span>
                  <span>3 hours</span>
                </div>
              </div>
            </div>

            {/* Difficulty & Cuisine */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-card rounded-2xl p-6 shadow-card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                    <ChefHat className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground">Difficulty</h3>
                </div>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="input-field w-full appearance-none cursor-pointer"
                >
                  {DIFFICULTIES.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div className="bg-card rounded-2xl p-6 shadow-card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                    <Globe className="w-5 h-5 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground">Cuisine</h3>
                </div>
                <select
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                  className="input-field w-full appearance-none cursor-pointer"
                >
                  {CUISINES.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-semibold text-lg shadow-soft hover:shadow-elevated transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Find Recipes
                </>
              )}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
