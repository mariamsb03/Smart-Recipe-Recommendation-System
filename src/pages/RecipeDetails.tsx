import { useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from '@/components/Sidebar';
import { useApp } from '@/context/AppContext';
import { ArrowLeft, Clock, Flame, Users, Star, ThumbsUp, ThumbsDown, Lightbulb, ExternalLink } from 'lucide-react';

export default function RecipeDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { recipes, likedRecipes, dislikedRecipes, toggleLike, toggleDislike, user } = useApp();

  const recipe = recipes.find(r => r.id === parseInt(id || '0'));

  if (!recipe) {
    return (
      <div className="min-h-screen bg-background">
        <Sidebar />
        <main className="ml-64 p-8 flex items-center justify-center">
          <div className="text-center">
            <h2 className="font-serif text-2xl font-bold text-foreground mb-4">Recipe Not Found</h2>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium"
            >
              Back to Dashboard
            </button>
          </div>
        </main>
      </div>
    );
  }

  const isLiked = likedRecipes.includes(recipe.id);
  const isDisliked = dislikedRecipes.includes(recipe.id);

  // Check for ingredients user dislikes
  const missingIngredients = user?.dislikedIngredients?.filter(dislike => 
    recipe.ingredients_list.some(ing => 
      ing.toLowerCase().includes(dislike.toLowerCase())
    )
  ) || [];

  // Dummy substitution suggestions
  const substitutions: Record<string, string> = {
    'cilantro': 'parsley or basil',
    'olives': 'capers or sun-dried tomatoes',
    'mushrooms': 'zucchini or eggplant',
    'onions': 'shallots or leeks',
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <main className="ml-64 p-8">
        <div className="max-w-4xl mx-auto">
          {/* Back Button */}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          {/* Hero Image */}
          <div className="relative h-80 rounded-2xl overflow-hidden mb-8">
            <img
              src={recipe.img_src || '/placeholder.svg'}
              alt={recipe.recipe_name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/placeholder.svg';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-foreground/60 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 p-8">
              <span className="tag mb-3">{recipe.cuisine}</span>
              <h1 className="font-serif text-4xl font-bold text-primary-foreground">
                {recipe.recipe_name}
              </h1>
            </div>
          </div>

          {/* Info Bar */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            {[
              { icon: Clock, label: 'Time', value: `${recipe.cook_time_minutes} min` },
              { icon: Flame, label: 'Calories', value: recipe.calories },
              { icon: Users, label: 'Servings', value: recipe.servings },
              { icon: Star, label: 'Rating', value: recipe.rating.toFixed(1) },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="bg-card rounded-xl p-4 text-center shadow-card">
                <Icon className="w-5 h-5 text-primary mx-auto mb-2" />
                <p className="text-xs text-muted-foreground mb-1">{label}</p>
                <p className="font-semibold text-foreground">{value}</p>
              </div>
            ))}
          </div>

          {/* Like/Dislike Actions */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => toggleLike(recipe.id)}
              className={`flex-1 py-4 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
                isLiked 
                  ? 'bg-accent text-accent-foreground' 
                  : 'bg-card border border-border text-foreground hover:bg-muted'
              }`}
            >
              <ThumbsUp className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
              {isLiked ? 'Liked!' : 'Like Recipe'}
            </button>
            <button
              onClick={() => toggleDislike(recipe.id)}
              className={`flex-1 py-4 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
                isDisliked 
                  ? 'bg-destructive text-destructive-foreground' 
                  : 'bg-card border border-border text-foreground hover:bg-muted'
              }`}
            >
              <ThumbsDown className={`w-5 h-5 ${isDisliked ? 'fill-current' : ''}`} />
              {isDisliked ? 'Not for me' : 'Not my taste'}
            </button>
          </div>

          {/* Missing Ingredients Warning */}
          {missingIngredients.length > 0 && (
            <div className="bg-accent/10 border border-accent/30 rounded-xl p-6 mb-8">
              <div className="flex items-start gap-3">
                <Lightbulb className="w-5 h-5 text-accent mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    Contains ingredients you dislike
                  </h3>
                  <div className="space-y-2">
                    {missingIngredients.map(ing => (
                      <p key={ing} className="text-sm text-muted-foreground">
                        <span className="font-medium text-foreground">{ing}</span>
                        {substitutions[ing.toLowerCase()] && (
                          <> → Try using {substitutions[ing.toLowerCase()]} instead</>
                        )}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Ingredients */}
            <div className="lg:col-span-1">
              <div className="bg-card rounded-2xl p-6 shadow-card sticky top-8">
                <h2 className="font-serif text-xl font-bold text-foreground mb-4">
                  Ingredients
                </h2>
                <ul className="space-y-3">
                  {recipe.ingredients_list.map((ingredient, i) => {
                    const isDislikedIngredient = missingIngredients.some(
                      d => ingredient.toLowerCase().includes(d.toLowerCase())
                    );
                    return (
                      <li 
                        key={i} 
                        className={`flex items-start gap-3 text-sm ${
                          isDislikedIngredient ? 'text-destructive' : 'text-muted-foreground'
                        }`}
                      >
                        <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                          isDislikedIngredient ? 'bg-destructive' : 'bg-accent'
                        }`} />
                        <span className="capitalize">{ingredient}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>

            {/* Directions */}
            <div className="lg:col-span-2">
              <div className="bg-card rounded-2xl p-6 shadow-card">
                <h2 className="font-serif text-xl font-bold text-foreground mb-4">
                  Directions
                </h2>
                <div className="space-y-4">
                  {recipe.directions
                    .split(/\n+/)
                    .map((step, index) => step.trim())
                    .filter(step => step.length > 0)
                    .map((step, index) => (
                      <div key={index} className="flex gap-4">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm">
                          {index + 1}
                        </div>
                        <p className="flex-1 text-muted-foreground leading-relaxed pt-1">
                          {step}
                        </p>
                      </div>
                    ))}
                </div>

                {recipe.url && (
                  <a
                    href={recipe.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 mt-6 text-primary hover:underline"
                  >
                    View original recipe
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
