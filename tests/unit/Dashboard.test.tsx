import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import React, { useState } from 'react';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockUser = {
  id: '1',
  name: 'Jane Smith',
  email: 'jane@example.com',
  diet: 'vegetarian',
  allergies: ['Peanuts', 'Shellfish'],
};

const createMockRecipes = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: (i + 1).toString(),
    recipe_name: `Recipe ${i + 1}`,
    cook_time_minutes: 20,
    calories: 300,
    rating: 4.5,
    cuisine: 'Italian',
    img_src: `/recipe.jpg`,
    servings: 4,
    ingredients_list: [],
    directions: '',
    url: '',
  }));
};

// Mock the context ONCE at the module level
const mockUseApp = vi.fn();
vi.mock('@/context/AppContext', () => ({
  useApp: () => mockUseApp(),
}));

vi.mock('@/components/Sidebar', () => ({
  Sidebar: () => <div data-testid="sidebar">Sidebar</div>,
}));

vi.mock('@/components/RecipeCard', () => ({
  RecipeCard: ({ recipe }: any) => (
    <div data-testid={`recipe-card-${recipe.id}`}>
      {recipe.recipe_name}
    </div>
  ),
}));

// Import Dashboard AFTER all mocks are set up
import Dashboard from '@/pages/Dashboard';

describe('Dashboard - Basic Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render with user greeting', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Hi, Jane/i)).toBeInTheDocument();
  });

  it('should show welcome message', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Ready to discover something delicious/i)).toBeInTheDocument();
  });

  it('should render sidebar', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
  });
});

describe('Dashboard - Quick Actions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display Find a Recipe button and navigate', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const button = screen.getByText('Find a Recipe');
    expect(button).toBeInTheDocument();
    
    fireEvent.click(button.closest('button')!);
    expect(mockNavigate).toHaveBeenCalledWith('/recipe-request');
  });

  it('should display Your Profile section', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Your Profile')).toBeInTheDocument();
  });
});

describe('Dashboard - Recipe Display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display Recommended for You heading', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: createMockRecipes(3),
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Recommended for You')).toBeInTheDocument();
  });

  it('should show loading state when no recipes', () => {
    mockUseApp.mockReturnValue({
      user: mockUser,
      recipes: [],
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Loading recipes/i)).toBeInTheDocument();
  });
});
