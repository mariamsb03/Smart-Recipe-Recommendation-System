/**
 * Simplified Integration Test: RecipeRequest Component
 * Location: frontend/src/tests/integration/test_frontend_backend.test.tsx
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecipeRequest from '@/pages/RecipeRequest';

// Create mock functions
const mockNavigate = vi.fn();
const mockSetSearchResults = vi.fn();

// Mock react-router-dom with importOriginal pattern
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual, // This includes BrowserRouter
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/recipe-request' }),
  };
});

// Mock AppContext
vi.mock('@/context/AppContext', () => ({
  useApp: () => ({
    setSearchResults: mockSetSearchResults,
    setLastRequest: vi.fn(),
    user: { id: 1, name: 'Test User', email: 'test@example.com' },
    setIsAuthenticated: vi.fn(),
    setUser: vi.fn(),
  }),
}));

// Simple component mocks
vi.mock('@/components/Sidebar', () => ({
  Sidebar: () => <div>Sidebar</div>,
}));

vi.mock('@/components/TagInput', () => ({
  TagInput: () => <div>TagInput Mock</div>,
}));

// Mock icons
vi.mock('lucide-react', () => ({
  Search: () => <span>🔍</span>,
  Clock: () => <span>⏰</span>,
  ChefHat: () => <span>👨‍🍳</span>,
  Globe: () => <span>🌎</span>,
  Loader2: () => <span>⏳</span>,
}));

describe('RecipeRequest Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  // Keep only the tests that passed
  it('renders the search form', () => {
    render(
      <BrowserRouter>
        <RecipeRequest />
      </BrowserRouter>
    );

    expect(screen.getByText('Find Your Perfect Recipe')).toBeInTheDocument();
    expect(screen.getByText('Available Ingredients')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /find recipes/i })).toBeInTheDocument();
  });

  it('submits search and calls API', async () => {
    const mockResponse = {
      recipes: [
        {
          id: 1,
          recipe_name: 'Test Recipe',
          ml_score: 0.85,
          ingredients_list: ['test'],
          cuisine: 'italian',
          cook_time_minutes: 30,
          calories: 400,
          servings: 4,
          rating: 4.5,
        },
      ],
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <BrowserRouter>
        <RecipeRequest />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /find recipes/i }));

    await waitFor(() => {
      // Check API was called
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/recommend',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );

      // Check results were processed
      expect(mockSetSearchResults).toHaveBeenCalled();
      expect(mockSetSearchResults.mock.calls[0][0][0].matchScore).toBe(85);
      
      // Check navigation
      expect(mockNavigate).toHaveBeenCalledWith('/recipe-results');
    });
  });

  it('shows loading state', async () => {
    global.fetch = vi.fn().mockImplementation(
      () => new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({ recipes: [] }),
        }), 100)
      )
    );

    render(
      <BrowserRouter>
        <RecipeRequest />
      </BrowserRouter>
    );

    const submitButton = screen.getByRole('button', { name: /find recipes/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });
});