import { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TagInput } from '@/components/TagInput';
import { useApp } from '@/context/AppContext';
import { User, Mail, Calendar, Users, Save, Check } from 'lucide-react';
import { userAPI } from '@/services/api';

const ALLERGIES = ['Dairy', 'Eggs', 'Fish', 'Gluten', 'Lactose', 'Nuts', 'Shellfish', 'Soy', 'Peanuts', 'Tree Nuts', 'Wheat', 'Sesame'];
const DIETS = ['regular', 'vegetarian', 'vegan', 'keto', 'gluten_free', 'low_carb', 'calorie_deficit', 'diabetic', 'paleo', 'mediterranean'];
const CONDITIONS = ['Diabetes', 'Heart Disease', 'High Cholesterol', 'Hypertension', 'Celiac Disease', 'IBS', 'Lactose Intolerance', 'GERD'];
const COMMON_DISLIKES = [
  'Cilantro', 'Olives', 'Mushrooms', 'Onions', 'Tomatoes', 'Garlic', 'Eggplant', 'Bell Peppers', 
  'Broccoli', 'Cauliflower', 'Brussels Sprouts', 'Cabbage', 'Asparagus', 'Zucchini', 'Spinach', 
  'Kale', 'Anchovies', 'Liver', 'Organ Meats', 'Lamb', 'Pork', 'Seafood', 'Fish', 'Shellfish', 
  'Tofu', 'Tempeh', 'Blue Cheese', 'Goat Cheese', 'Feta', 'Strong Cheese', 'Cottage Cheese', 
  'Cumin', 'Coriander', 'Fennel', 'Anise', 'Tarragon', 'Dill', 'Nuts', 'Seeds', 'Coconut', 
  'Raisins', 'Dates', 'Pickles', 'Capers', 'Mayonnaise', 'Mustard'
];

export default function Profile() {
  const { user, setUser } = useApp();
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [age, setAge] = useState(user?.age?.toString() || '');
  const [gender, setGender] = useState(user?.gender || '');
  const [allergies, setAllergies] = useState<string[]>(user?.allergies || []);
  const [diet, setDiet] = useState(user?.diet || 'regular');
  const [conditions, setConditions] = useState<string[]>(user?.medicalConditions || []);
  const [dislikes, setDislikes] = useState<string[]>(user?.dislikedIngredients || []);

  const handleSave = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await userAPI.updateProfile({
        name,
        age: parseInt(age),
        gender,
        allergies,
        diet,
        medicalConditions: conditions,
        dislikedIngredients: dislikes,
      });

      // Update user in context
      setUser(response.data.user);
      
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <main className="ml-64 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="font-serif text-4xl font-bold text-foreground mb-2">
              My Profile
            </h1>
            <p className="text-muted-foreground text-lg">
              Update your preferences to get better recommendations.
            </p>
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive rounded-lg px-4 py-3 mb-6 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {/* Personal Info */}
            <div className="bg-card rounded-2xl p-6 shadow-card">
              <h2 className="font-serif text-xl font-bold text-foreground mb-6">
                Personal Information
              </h2>
              
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
                      disabled={loading}
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
                      className="input-field w-full pl-12 bg-muted cursor-not-allowed"
                      disabled
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Age</label>
                    <div className="relative">
                      <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="number"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="input-field w-full pl-12"
                        disabled={loading}
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
                        disabled={loading}
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
            </div>

            {/* Dietary Info */}
            <div className="bg-card rounded-2xl p-6 shadow-card">
              <h2 className="font-serif text-xl font-bold text-foreground mb-6">
                Dietary Information
              </h2>
              
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
                    disabled={loading}
                  >
                    {DIETS.map(d => (
                      <option key={d} value={d}>
                        {d.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                <TagInput
                  tags={conditions}
                  setTags={setConditions}
                  suggestions={CONDITIONS}
                  placeholder="Search conditions..."
                  label="Medical Conditions"
                />
              </div>
            </div>

            {/* Preferences */}
            <div className="bg-card rounded-2xl p-6 shadow-card">
              <h2 className="font-serif text-xl font-bold text-foreground mb-6">
                Food Preferences
              </h2>
              
              <TagInput
                tags={dislikes}
                setTags={setDislikes}
                suggestions={COMMON_DISLIKES}
                placeholder="Search ingredients you dislike..."
                label="Disliked Ingredients"
              />
            </div>

            {/* Save Button */}
            <button
              onClick={handleSave}
              disabled={loading}
              className={`w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 transition-all ${
                saved 
                  ? 'bg-accent text-accent-foreground' 
                  : 'bg-primary text-primary-foreground shadow-soft hover:shadow-elevated disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              {loading ? (
                'Saving...'
              ) : saved ? (
                <>
                  <Check className="w-5 h-5" />
                  Saved Successfully!
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
