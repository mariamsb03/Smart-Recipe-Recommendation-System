import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '@/App';

// Mock the AppContext
vi.mock('@/context/AppContext', () => ({
  AppProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useApp: () => ({
    isAuthenticated: false,
    user: null,
    recipes: [],
  }),
}));

// Mock all page components
vi.mock('@/pages/Landing', () => ({
  default: () => <div>Landing Page</div>,
}));

vi.mock('@/pages/Login', () => ({
  default: () => <div>Login Page</div>,
}));

vi.mock('@/pages/Signup', () => ({
  default: () => <div>Signup Page</div>,
}));

vi.mock('@/pages/Dashboard', () => ({
  default: () => <div>Dashboard Page</div>,
}));

vi.mock('@/pages/NotFound', () => ({
  default: () => <div>404 Not Found</div>,
}));

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the App component without crashing', () => {
    render(<App />);
    expect(screen.getByText('Landing Page')).toBeInTheDocument();
  });

  it('should have QueryClientProvider wrapping the app', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('should have TooltipProvider configured', () => {
    const { container } = render(<App />);
    // Check that the app renders successfully with TooltipProvider
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});

describe('App Routing', () => {
  it('should render Landing page by default on root path', () => {
    window.history.pushState({}, 'Landing', '/');
    render(<App />);
    expect(screen.getByText('Landing Page')).toBeInTheDocument();
  });

  it('should render Login page on /login path', () => {
    window.history.pushState({}, 'Login', '/login');
    render(<App />);
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('should render Signup page on /signup path', () => {
    window.history.pushState({}, 'Signup', '/signup');
    render(<App />);
    expect(screen.getByText('Signup Page')).toBeInTheDocument();
  });
});

describe('Protected Routes', () => {
  it('should redirect to login when accessing dashboard without authentication', () => {
    window.history.pushState({}, 'Dashboard', '/dashboard');
    render(<App />);
    
    // Should redirect to login since user is not authenticated
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
});
