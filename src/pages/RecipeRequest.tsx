import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from '@/components/Sidebar';
import { TagInput } from '@/components/TagInput';
import { useApp } from '@/context/AppContext';
import { Search, Clock, ChefHat, Globe } from 'lucide-react';

const COMMON_INGREDIENTS = [
  // Proteins
  'Chicken', 'Beef', 'Pork', 'Fish', 'Salmon', 'Tuna', 'Shrimp', 'Turkey', 'Lamb', 'Tofu', 'Eggs', 'Bacon', 'Sausage', 'Ground Beef', 'Chicken Breast', 'Chicken Thighs',
  // Grains & Starches
  'Rice', 'Pasta', 'Bread', 'Potatoes', 'Sweet Potatoes', 'Noodles', 'Quinoa', 'Couscous', 'Barley', 'Oats', 'Flour', 'Breadcrumbs', 'Tortillas',
  // Vegetables
  'Tomatoes', 'Onions', 'Garlic', 'Bell Peppers', 'Carrots', 'Broccoli', 'Spinach', 'Lettuce', 'Cucumber', 'Zucchini', 'Eggplant', 'Mushrooms', 'Corn', 'Peas', 'Green Beans', 'Asparagus', 'Cauliflower', 'Cabbage', 'Celery', 'Leeks', 'Shallots', 'Scallions',
  // Fruits
  'Apples', 'Bananas', 'Oranges', 'Lemons', 'Limes', 'Berries', 'Strawberries', 'Blueberries', 'Avocado', 'Mango', 'Pineapple',
  // Dairy
  'Cheese', 'Milk', 'Butter', 'Cream', 'Sour Cream', 'Yogurt', 'Cheddar', 'Mozzarella', 'Parmesan', 'Feta', 'Cream Cheese',
  // Herbs & Spices
  'Basil', 'Oregano', 'Thyme', 'Rosemary', 'Parsley', 'Cilantro', 'Ginger', 'Cumin', 'Paprika', 'Chili Powder', 'Black Pepper', 'Salt', 'Bay Leaves', 'Dill', 'Sage',
  // Oils & Condiments
  'Olive Oil', 'Vegetable Oil', 'Soy Sauce', 'Vinegar', 'Balsamic Vinegar', 'Worcestershire Sauce', 'Hot Sauce', 'Ketchup', 'Mustard', 'Mayonnaise',
  // Pantry Staples
  'Sugar', 'Brown Sugar', 'Honey', 'Maple Syrup', 'Vanilla Extract', 'Baking Powder', 'Baking Soda', 'Cornstarch', 'Chicken Broth', 'Beef Broth', 'Vegetable Broth', 'Coconut Milk', 'Tomato Paste', 'Tomato Sauce', 'Canned Tomatoes'
];

const CUISINES = ['Any', 'American', 'Italian', 'Mexican', 'Chinese', 'Japanese', 'Indian', 'Mediterranean', 'Thai', 'French'];
const DIFFICULTIES = ['Any', 'Easy', 'Medium', 'Hard'];

export default function RecipeRequest() {
  const navigate = useNavigate();
  const { recipes, setSearchResults, setLastRequest } = useApp();
  
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [cookingTime, setCookingTime] = useState(60);
  const [difficulty, setDifficulty] = useState('Any');
  const [cuisine, setCuisine] = useState('Any');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Simulate ML matching with random scores
    const results = recipes
      .filter(recipe => {
        // Filter by cooking time
        if (recipe.cook_time_minutes > cookingTime) return false;
        
        // Filter by cuisine
        if (cuisine !== 'Any' && recipe.cuisine.toLowerCase() !== cuisine.toLowerCase()) return false;
        
        return true;
      })
      .map(recipe => ({
        ...recipe,
        matchScore: Math.floor(Math.random() * 40) + 60 // Random score 60-100
      }))
      .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
      .slice(0, 12);

    setSearchResults(results);
    setLastRequest({ ingredients, cookingTime, difficulty, cuisine });
    navigate('/recipe-results');
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
              className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-semibold text-lg shadow-soft hover:shadow-elevated transition-all duration-300 flex items-center justify-center gap-2"
            >
              <Search className="w-5 h-5" />
              Find Recipes
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
