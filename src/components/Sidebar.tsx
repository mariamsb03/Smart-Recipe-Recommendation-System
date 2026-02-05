import { Home, Search, User, LogOut, ChefHat } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '@/context/AppContext';

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setIsAuthenticated, setUser, user } = useApp();

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUser(null);
    navigate('/');
  };

  const links = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/recipe-request', icon: Search, label: 'Find Recipes' },
    { path: '/profile', icon: User, label: 'My Profile' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-sidebar flex flex-col z-50">
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-sidebar-primary flex items-center justify-center">
            <ChefHat className="w-5 h-5 text-sidebar-primary-foreground" />
          </div>
          <span className="font-serif text-xl font-semibold text-sidebar-foreground">FlavorFit</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {links.map(({ path, icon: Icon, label }) => (
          <button
            key={path}
            onClick={() => navigate(path)}
            className={`sidebar-link w-full ${
              location.pathname === path ? 'sidebar-link-active' : ''
            }`}
          >
            <Icon className="w-5 h-5" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 px-4 py-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-sidebar-accent flex items-center justify-center">
            <span className="text-sidebar-foreground font-medium">
              {user?.name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">
              {user?.name || 'User'}
            </p>
            <p className="text-xs text-sidebar-foreground/60 truncate">
              {user?.email || 'user@example.com'}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="sidebar-link w-full text-sidebar-foreground/70 hover:text-sidebar-foreground"
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
