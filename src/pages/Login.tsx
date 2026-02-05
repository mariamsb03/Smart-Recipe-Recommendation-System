import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ChefHat, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export default function Login() {
  const navigate = useNavigate();
  const { setIsAuthenticated, setUser } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    // Dummy login - accept any credentials
    setUser({
      id: '1',
      name: 'Alex Johnson',
      email: email,
      age: 28,
      gender: 'prefer-not-to-say',
      allergies: ['peanuts', 'shellfish'],
      diet: 'vegetarian',
      medicalConditions: [],
      dislikedIngredients: ['cilantro', 'olives'],
    });
    setIsAuthenticated(true);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-hero items-center justify-center p-12">
        <div className="max-w-md text-center">
          <div className="w-20 h-20 rounded-full bg-accent/20 backdrop-blur-sm flex items-center justify-center mx-auto mb-8">
            <ChefHat className="w-10 h-10 text-accent-foreground" />
          </div>
          <h2 className="font-serif text-4xl font-bold text-primary-foreground mb-4">
            Welcome Back!
          </h2>
          <p className="text-primary-foreground/80 text-lg leading-relaxed">
            Your personalized recipes are waiting. Sign in to discover new dishes tailored just for you.
          </p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden text-center mb-8">
            <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mx-auto mb-4">
              <ChefHat className="w-8 h-8 text-primary" />
            </div>
            <h1 className="font-serif text-2xl font-bold text-foreground">FlavorFit</h1>
          </div>

          <h1 className="font-serif text-3xl font-bold text-foreground mb-2">Sign In</h1>
          <p className="text-muted-foreground mb-8">
            Enter your credentials to access your account
          </p>

          {error && (
            <div className="bg-destructive/10 text-destructive rounded-lg px-4 py-3 mb-6 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field w-full pl-12"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field w-full pl-12 pr-12"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-semibold text-lg shadow-soft hover:shadow-elevated transition-all duration-300"
            >
              Sign In
            </button>
          </form>

          <p className="text-center mt-8 text-muted-foreground">
            Don't have an account?{' '}
            <Link to="/signup" className="text-primary font-medium hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
