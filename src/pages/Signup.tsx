import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ChefHat, ArrowLeft, ArrowRight, User, Mail, Lock, Calendar, Users } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { ProgressBar } from '@/components/ProgressBar';
import { TagInput } from '@/components/TagInput';

const ALLERGIES = ['dairy', 'eggs', 'fish', 'gluten', 'lactose', 'nuts', 'shellfish', 'soy'];
const DIETS = ['regular', 'vegetarian', 'vegan', 'keto', 'gluten_free', 'low_carb', 'calorie_deficit', 'diabetic'];
const CONDITIONS = ['diabetes', 'heart_disease', 'high_cholesterol', 'hypertension'];
const COMMON_DISLIKES = [
  // Vegetables
  'Cilantro', 'Olives', 'Mushrooms', 'Onions', 'Tomatoes', 'Garlic', 'Eggplant', 'Bell Peppers', 'Broccoli', 'Cauliflower', 'Brussels Sprouts', 'Cabbage', 'Asparagus', 'Zucchini', 'Spinach', 'Kale',
  // Proteins
  'Anchovies', 'Liver', 'Organ Meats', 'Lamb', 'Pork', 'Seafood', 'Fish', 'Shellfish', 'Tofu', 'Tempeh',
  // Dairy & Cheese
  'Blue Cheese', 'Goat Cheese', 'Feta', 'Strong Cheese', 'Cottage Cheese',
  // Spices & Herbs
  'Cumin', 'Coriander', 'Fennel', 'Anise', 'Tarragon', 'Dill',
  // Other
  'Nuts', 'Seeds', 'Coconut', 'Raisins', 'Dates', 'Pickles', 'Capers', 'Mayonnaise', 'Mustard'
];

export default function Signup() {
  const navigate = useNavigate();
  const { setUser, setIsAuthenticated } = useApp();
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  // Step 1 - Account
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Step 2 - Demographics
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');

  // Step 3 - Dietary
  const [allergies, setAllergies] = useState<string[]>([]);
  const [diet, setDiet] = useState('regular');
  const [conditions, setConditions] = useState<string[]>([]);

  // Step 4 - Dislikes
  const [dislikes, setDislikes] = useState<string[]>([]);

  const stepLabels = ['Account', 'About You', 'Dietary', 'Preferences'];

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      // Complete signup
      setUser({
        id: '1',
        name,
        email,
        age: parseInt(age) || 25,
        gender,
        allergies,
        diet,
        medicalConditions: conditions,
        dislikedIngredients: dislikes,
      });
      setIsAuthenticated(true);
      navigate('/dashboard');
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return name && email && password;
      case 2:
        return age && gender;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-2/5 bg-gradient-hero items-center justify-center p-12">
        <div className="max-w-sm text-center">
          <div className="w-20 h-20 rounded-full bg-accent/20 backdrop-blur-sm flex items-center justify-center mx-auto mb-8">
            <ChefHat className="w-10 h-10 text-accent-foreground" />
          </div>
          <h2 className="font-serif text-3xl font-bold text-primary-foreground mb-4">
            Join FlavorFit
          </h2>
          <p className="text-primary-foreground/80 text-lg leading-relaxed">
            Tell us about yourself so we can personalize your recipe recommendations.
          </p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex flex-col p-8 lg:p-12">
        <div className="lg:hidden flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
            <ChefHat className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl font-semibold text-foreground">FlavorFit</span>
        </div>

        <div className="flex-1 max-w-xl mx-auto w-full">
          {/* Progress Bar */}
          <div className="mb-10">
            <ProgressBar currentStep={step} totalSteps={totalSteps} labels={stepLabels} />
          </div>

          {/* Step Content */}
          <div className="animate-fade-in">
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <h1 className="font-serif text-3xl font-bold text-foreground mb-2">
                    Create Your Account
                  </h1>
                  <p className="text-muted-foreground">
                    Let's start with the basics.
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="input-field w-full pl-12"
                        placeholder="John Doe"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Email Address</label>
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
                    <label className="block text-sm font-medium text-foreground mb-2">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field w-full pl-12"
                        placeholder="Create a password"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6">
                <div>
                  <h1 className="font-serif text-3xl font-bold text-foreground mb-2">
                    Tell Us About Yourself
                  </h1>
                  <p className="text-muted-foreground">
                    This helps us tailor recipes to your needs.
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Age</label>
                    <div className="relative">
                      <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="number"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="input-field w-full pl-12"
                        placeholder="25"
                        min="1"
                        max="120"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Gender</label>
                    <div className="relative">
                      <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <select
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        className="input-field w-full pl-12 appearance-none cursor-pointer"
                      >
                        <option value="">Select...</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="prefer-not-to-say">Prefer not to say</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6">
                <div>
                  <h1 className="font-serif text-3xl font-bold text-foreground mb-2">
                    Dietary Information
                  </h1>
                  <p className="text-muted-foreground">
                    Help us keep you safe and healthy.
                  </p>
                </div>

                <div className="space-y-6">
                  <TagInput
                    tags={allergies}
                    setTags={setAllergies}
                    suggestions={ALLERGIES}
                    placeholder="Search allergies..."
                    label="Allergies"
                  />

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Diet Type</label>
                    <select
                      value={diet}
                      onChange={(e) => setDiet(e.target.value)}
                      className="input-field w-full appearance-none cursor-pointer"
                    >
                      {DIETS.map(d => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>

                  <TagInput
                    tags={conditions}
                    setTags={setConditions}
                    suggestions={CONDITIONS}
                    placeholder="Search conditions..."
                    label="Medical Conditions (optional)"
                  />
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-6">
                <div>
                  <h1 className="font-serif text-3xl font-bold text-foreground mb-2">
                    Food Preferences
                  </h1>
                  <p className="text-muted-foreground">
                    What ingredients do you prefer to avoid?
                  </p>
                </div>

                <TagInput
                  tags={dislikes}
                  setTags={setDislikes}
                  suggestions={COMMON_DISLIKES}
                  placeholder="Search ingredients you dislike..."
                  label="Disliked Ingredients"
                />

                <p className="text-sm text-muted-foreground">
                  We'll try to avoid these ingredients in your recommendations.
                </p>
              </div>
            )}
          </div>

          {/* Navigation */}
          <div className="flex justify-between mt-10">
            <button
              onClick={handleBack}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
                step === 1 
                  ? 'opacity-0 pointer-events-none' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>

            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex items-center gap-2 px-8 py-3 bg-primary text-primary-foreground rounded-xl font-semibold shadow-soft hover:shadow-elevated transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {step === totalSteps ? 'Complete Setup' : 'Continue'}
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>

          <p className="text-center mt-8 text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
