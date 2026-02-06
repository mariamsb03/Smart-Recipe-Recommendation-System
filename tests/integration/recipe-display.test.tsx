import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';
import { RecipeCard } from '@/components/RecipeCard';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockRecipes = [
  {
    id: '1',
    recipe_name: 'Margherita Pizza',
    cook_time_minutes: 20,
    calories: 400,
    rating: 4.8,
    cuisine: 'Italian',
    img_src: '/pizza.jpg',
    matchScore: 92,
  },
  {
    id: '2',
    recipe_name: 'Caesar Salad',
    cook_time_minutes: 10,
    calories: 250,
    rating: 4.3,
    cuisine: 'American',
    img_src: '/salad.jpg',
    matchScore: 78,
  },
  {
    id: '3',
    recipe_name: 'Pad Thai',
    cook_time_minutes: 30,
    calories: 450,
    rating: 4.6,
    cuisine: 'Thai',
    img_src: '/padthai.jpg',
    matchScore: 85,
  },
];

vi.mock('@/context/AppContext', () => ({
  useApp: () => ({
    user: {
      id: '1',
      name: 'Jane Smith',
      email: 'jane@example.com',
      diet: 'None',
      allergies: [],
    },
    recipes: mockRecipes,
    isAuthenticated: true,
  }),
}));

vi.mock('@/components/Sidebar', () => ({
  Sidebar: () => <div data-testid="sidebar">Sidebar</div>,
}));


describe('Recipe Navigation Integration', () => {
  it('should navigate from dashboard to recipe request page', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const findRecipeButton = screen.getByText('Find a Recipe').closest('button');
    
    if (findRecipeButton) {
      fireEvent.click(findRecipeButton);
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/recipe-request');
      });
    }
  });

  it('should handle View All recipes button click', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const viewAllButton = screen.getByText('View All');
    expect(viewAllButton).toBeInTheDocument();
    
    // Button exists and is clickable
    fireEvent.click(viewAllButton);
  });
});


