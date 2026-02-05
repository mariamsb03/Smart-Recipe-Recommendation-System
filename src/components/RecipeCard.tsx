import { Clock, Flame, Star } from 'lucide-react';
import { Recipe } from '@/types/recipe';
import { useNavigate } from 'react-router-dom';

interface RecipeCardProps {
  recipe: Recipe;
  showMatchScore?: boolean;
}

export function RecipeCard({ recipe, showMatchScore }: RecipeCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/recipe/${recipe.id}`);
  };

  return (
    <div 
      onClick={handleClick}
      className="card-recipe cursor-pointer group bg-card"
    >
      <div className="relative h-48 overflow-hidden">
        <img 
          src={recipe.img_src || '/placeholder.svg'} 
          alt={recipe.recipe_name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/placeholder.svg';
          }}
        />
        {showMatchScore && recipe.matchScore !== undefined && (
          <div className="absolute top-3 right-3 bg-accent text-accent-foreground px-3 py-1 rounded-full text-sm font-semibold">
            {recipe.matchScore}% Match
          </div>
        )}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-foreground/60 to-transparent h-20" />
      </div>
      
      <div className="p-4">
        <h3 className="font-serif text-lg font-semibold text-foreground line-clamp-2 mb-3 group-hover:text-primary transition-colors">
          {recipe.recipe_name}
        </h3>
        
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{recipe.cook_time_minutes} min</span>
          </div>
          <div className="flex items-center gap-1">
            <Flame className="w-4 h-4" />
            <span>{recipe.calories} cal</span>
          </div>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-accent text-accent" />
            <span>{recipe.rating.toFixed(1)}</span>
          </div>
        </div>
        
        {recipe.cuisine && (
          <div className="mt-3">
            <span className="tag text-xs">{recipe.cuisine}</span>
          </div>
        )}
      </div>
    </div>
  );
}
