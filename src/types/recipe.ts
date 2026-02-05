export interface Recipe {
  id: number;
  recipe_name: string;
  ingredients_list: string[];
  cuisine: string;
  cook_time_minutes: number;
  timing: string;
  calories: number;
  servings: number;
  rating: number;
  url: string;
  img_src: string;
  directions: string;
  matchScore?: number;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  age: number;
  gender: string;
  allergies: string[];
  diet: string;
  medicalConditions: string[];
  dislikedIngredients: string[];
}

export interface RecipeRequest {
  ingredients: string[];
  cookingTime: number;
  difficulty: string;
  cuisine: string;
}
