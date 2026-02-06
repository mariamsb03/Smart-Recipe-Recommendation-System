import { Sidebar } from '@/components/Sidebar';
import { RecipeCard } from '@/components/RecipeCard';
import { useApp } from '@/context/AppContext';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, recipes } = useApp();
  const [showAll, setShowAll] = useState(false);

  // Get recommended recipes - show 6 initially, all when "View All" is clicked
  const recommendedRecipes = showAll ? recipes : recipes.slice(0, 6);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <main className="ml-64 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Greeting */}
          <div className="mb-10">
            <h1 className="font-serif text-4xl font-bold text-foreground mb-2">
              Hi, {user?.name?.split(' ')[0] || 'Chef'} 👋
            </h1>
            <p className="text-muted-foreground text-lg">
              Ready to discover something delicious today?
            </p>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <button
              onClick={() => navigate('/recipe-request')}
              className="group bg-gradient-hero p-6 rounded-2xl text-left transition-all hover:shadow-elevated hover:-translate-y-1"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-accent/20 backdrop-blur-sm flex items-center justify-center">
                  <Search className="w-7 h-7 text-accent-foreground" />
                </div>
                <div>
                  <h3 className="font-serif text-xl font-semibold text-primary-foreground mb-1">
                    Find a Recipe
                  </h3>
                  <p className="text-primary-foreground/70">
                    Tell us what you have and we'll find the perfect dish
                  </p>
                </div>
              </div>
            </button>

            <div className="bg-card p-6 rounded-2xl border border-border">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-secondary flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-primary" />
                </div>
                <div>
                  <h3 className="font-serif text-xl font-semibold text-foreground mb-1">
                    Your Profile
                  </h3>
                  <p className="text-muted-foreground">
                    {user?.diet && user.diet !== 'regular' ? user.diet.replace(/_/g, ' ') : 'No diet restrictions'} 
                    {user?.allergies?.length ? ` • ${user.allergies.length} allergies` : ''}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recommended Recipes */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-serif text-2xl font-bold text-foreground">
                Recommended for You
              </h2>
              {!showAll && recipes.length > 6 && (
                <button 
                  onClick={() => setShowAll(true)}
                  className="text-primary font-medium hover:underline"
                >
                  View All
                </button>
              )}
            </div>

            {recommendedRecipes.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendedRecipes.map(recipe => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-card rounded-2xl">
                <p className="text-muted-foreground">Loading recipes...</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
