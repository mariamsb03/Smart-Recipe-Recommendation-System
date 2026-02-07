import { Sidebar } from '@/components/Sidebar';
import { RecipeCard } from '@/components/RecipeCard';
import { useApp } from '@/context/AppContext';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Search } from 'lucide-react';

export default function RecipeResults() {
  const navigate = useNavigate();
  const { searchResults, lastRequest } = useApp();

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <main className="ml-64 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => navigate('/recipe-request')}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Modify Search
            </button>
            
            <h1 className="font-serif text-4xl font-bold text-foreground mb-2">
              Recipe Results
            </h1>
            <p className="text-muted-foreground text-lg">
              Found {searchResults.length} recipes matching your criteria
            </p>
            
            {lastRequest && (
              <div className="flex flex-wrap gap-2 mt-4">
                {lastRequest.ingredients.map(ing => (
                  <span key={ing} className="tag text-xs">{ing}</span>
                ))}
                {lastRequest.cookingTime && (
                  <span className="tag text-xs">≤ {lastRequest.cookingTime} min</span>
                )}
                {lastRequest.cuisine !== 'Any' && (
                  <span className="tag text-xs">{lastRequest.cuisine}</span>
                )}
              </div>
            )}
          </div>

          {/* Results Grid */}
          {searchResults.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.map(recipe => (
                <RecipeCard key={recipe.id} recipe={recipe} showMatchScore />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 bg-card rounded-2xl">
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="font-serif text-xl font-semibold text-foreground mb-2">
                No Results Found
              </h3>
              <p className="text-muted-foreground mb-6">
                Try adjusting your search criteria for more results.
              </p>
              <button
                onClick={() => navigate('/recipe-request')}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium"
              >
                New Search
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
