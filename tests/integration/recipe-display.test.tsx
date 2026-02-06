import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';

// ---------- MOCK NAVIGATION ----------
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// ---------- CREATE 8 RECIPES (IMPORTANT) ----------
const mockRecipes = Array.from({ length: 8 }, (_, i) => ({
  id: String(i),
  recipe_name: `Recipe ${i}`,
  cook_time_minutes: 20,
  calories: 300,
  rating: 4.5,
  cuisine: 'Italian',
  img_src: '/recipe.jpg',
  matchScore: 90,
}));

// ---------- MOCK CONTEXT ----------
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

// ---------- MOCK SIDEBAR ----------
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

    const findRecipeButton = screen.getByRole('button', {
      name: /find a recipe/i,
    });

    fireEvent.click(findRecipeButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/recipe-request');
    });
  });


  it('should render and click View All button when recipes > 6', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const viewAllButton = screen.getByRole('button', {
      name: /view all/i,
    });

    expect(viewAllButton).toBeInTheDocument();

    fireEvent.click(viewAllButton);
  });

});
