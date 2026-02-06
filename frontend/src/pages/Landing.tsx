import { useNavigate } from 'react-router-dom';
import { ChefHat, Leaf, Heart, ArrowRight } from 'lucide-react';
import heroBg from '@/assets/hero-bg.jpg';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroBg})` }}
        >
          <div className="absolute inset-0 bg-gradient-hero" />
        </div>
        
        <div className="relative z-10 text-center px-6 max-w-4xl mx-auto animate-fade-in">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-14 h-14 rounded-full bg-accent/20 backdrop-blur-sm flex items-center justify-center">
              <ChefHat className="w-7 h-7 text-accent-foreground" />
            </div>
          </div>
          
          <h1 className="font-serif text-5xl md:text-7xl font-bold text-primary-foreground mb-6 leading-tight">
            Cook Smarter,<br />Eat Better
          </h1>
          
          <p className="text-xl md:text-2xl text-primary-foreground/80 mb-10 max-w-2xl mx-auto leading-relaxed">
            Personalized recipe recommendations based on your preferences, dietary needs, and what's in your kitchen.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/signup')}
              className="group px-8 py-4 bg-accent text-accent-foreground rounded-xl font-semibold text-lg shadow-elevated hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 flex items-center justify-center gap-2"
            >
              Get Started
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 bg-primary-foreground/10 backdrop-blur-sm text-primary-foreground rounded-xl font-semibold text-lg border border-primary-foreground/20 hover:bg-primary-foreground/20 transition-all duration-300"
            >
              Sign In
            </button>
          </div>
        </div>
        
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-8 h-12 rounded-full border-2 border-primary-foreground/30 flex items-start justify-center p-2">
            <div className="w-1.5 h-3 bg-primary-foreground/50 rounded-full" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6 bg-background">
        <div className="max-w-6xl mx-auto">
          <h2 className="font-serif text-4xl font-bold text-center text-foreground mb-4">
            Why FlavorFit?
          </h2>
          <p className="text-center text-muted-foreground text-lg mb-16 max-w-2xl mx-auto">
            We make healthy eating effortless by matching recipes to your unique lifestyle.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Leaf,
                title: 'Dietary Preferences',
                description: 'Whether you\'re vegan, keto, or anything in between, we\'ve got recipes that fit your diet.'
              },
              {
                icon: Heart,
                title: 'Health First',
                description: 'Filter by allergies, medical conditions, and nutritional goals for peace of mind.'
              },
              {
                icon: ChefHat,
                title: 'Smart Matching',
                description: 'Tell us what ingredients you have, and we\'ll suggest the perfect recipe.'
              }
            ].map((feature, i) => (
              <div 
                key={i}
                className="bg-card rounded-2xl p-8 shadow-card hover:shadow-elevated transition-all duration-300 hover:-translate-y-1"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="w-14 h-14 rounded-xl bg-secondary flex items-center justify-center mb-6">
                  <feature.icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="font-serif text-xl font-semibold text-foreground mb-3">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-secondary">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="font-serif text-4xl font-bold text-foreground mb-6">
            Ready to Transform Your Cooking?
          </h2>
          <p className="text-muted-foreground text-lg mb-10">
            Join thousands of home cooks who've discovered their perfect recipes.
          </p>
          <button
            onClick={() => navigate('/signup')}
            className="px-10 py-4 bg-primary text-primary-foreground rounded-xl font-semibold text-lg shadow-elevated hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
          >
            Create Free Account
          </button>
        </div>
      </section>
    </div>
  );
}
