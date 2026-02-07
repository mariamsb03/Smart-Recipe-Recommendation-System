import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Recipe, UserProfile, RecipeRequest } from '@/types/recipe';
import { recipeAPI } from '@/services/api';


interface AppContextType {
  recipes: Recipe[];
  user: UserProfile | null;
  isAuthenticated: boolean;
  setUser: (user: UserProfile | null) => void;
  setIsAuthenticated: (value: boolean) => void;
  searchResults: Recipe[];
  setSearchResults: (recipes: Recipe[]) => void;
  lastRequest: RecipeRequest | null;
  setLastRequest: (request: RecipeRequest | null) => void;
  likedRecipes: number[];
  dislikedRecipes: number[];
  toggleLike: (recipeId: number) => void;
  toggleDislike: (recipeId: number) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Parse CSV with proper handling of multi-line fields
const parseCSV = (text: string): string[][] => {
  const rows: string[][] = [];
  let currentRow: string[] = [];
  let currentField = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        // Escaped quote
        currentField += '"';
        i++; // Skip next quote
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      currentRow.push(currentField.trim());
      currentField = '';
    } else if ((char === '\n' || char === '\r') && !inQuotes) {
      // End of row (but not if we're inside quotes)
      if (currentField || currentRow.length > 0) {
        currentRow.push(currentField.trim());
        if (currentRow.some(f => f.length > 0)) {
          rows.push(currentRow);
        }
        currentRow = [];
        currentField = '';
      }
      // Skip \r\n combination
      if (char === '\r' && nextChar === '\n') {
        i++;
      }
    } else {
      currentField += char;
    }
  }

  // Add last field and row
  if (currentField || currentRow.length > 0) {
    currentRow.push(currentField.trim());
    if (currentRow.some(f => f.length > 0)) {
      rows.push(currentRow);
    }
  }

  return rows;
};

const parseIngredients = (ingredientsStr: string): string[] => {
  try {
    // Remove outer brackets and split
    const cleaned = ingredientsStr.replace(/^\[|\]$/g, '');
    const items = cleaned.split("', '").map(item =>
      item.replace(/^'|'$/g, '').trim()
    );
    return items.filter(item => item.length > 0);
  } catch {
    return [];
  }
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [searchResults, setSearchResults] = useState<Recipe[]>([]);
  const [lastRequest, setLastRequest] = useState<RecipeRequest | null>(null);
  const [likedRecipes, setLikedRecipes] = useState<number[]>([]);
  const [dislikedRecipes, setDislikedRecipes] = useState<number[]>([]);

useEffect(() => {
  recipeAPI.getRecipes()
    .then(res => {
      setRecipes(res.data.recipes); // ← REAL IDS
    })
    .catch(err => console.error('Error loading recipes:', err));
}, []);


  const toggleLike = (recipeId: number) => {
    setLikedRecipes(prev =>
      prev.includes(recipeId)
        ? prev.filter(id => id !== recipeId)
        : [...prev, recipeId]
    );
    setDislikedRecipes(prev => prev.filter(id => id !== recipeId));
  };

  const toggleDislike = (recipeId: number) => {
    setDislikedRecipes(prev =>
      prev.includes(recipeId)
        ? prev.filter(id => id !== recipeId)
        : [...prev, recipeId]
    );
    setLikedRecipes(prev => prev.filter(id => id !== recipeId));
  };

  return (
    <AppContext.Provider value={{
      recipes,
      user,
      isAuthenticated,
      setUser,
      setIsAuthenticated,
      searchResults,
      setSearchResults,
      lastRequest,
      setLastRequest,
      likedRecipes,
      dislikedRecipes,
      toggleLike,
      toggleDislike,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
