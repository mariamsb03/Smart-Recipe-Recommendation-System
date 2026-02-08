import axios from 'axios';

// Use environment variable, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

console.log('🔗 API Base URL:', API_BASE_URL); // Debug log

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  signup: (userData: any) => api.post('/auth/signup', userData),
  login: (credentials: { email: string; password: string }) => api.post('/auth/login', credentials),
};

// User APIs
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data: any) => api.put('/user/profile', data),
  getLikedRecipes: () => api.get('/user/liked-recipes'),
};

// Recipe APIs
export const recipeAPI = {
  getRecipes: (params?: { cuisine?: string; maxTime?: number; limit?: number }) => 
    api.get('/recipes', { params }),
  getRecipe: (id: number) => api.get(`/recipes/${id}`),
  likeRecipe: (id: number) => api.post(`/recipes/${id}/like`),
  dislikeRecipe: (id: number) => api.post(`/recipes/${id}/dislike`),
  // ✅ ADD THE RECOMMEND ENDPOINT
  recommend: (data: any) => api.post('/recommend', data),
};

export default api;
