import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';

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

// Auth APIs
export const authAPI = {
  signup: (userData) => api.post('/auth/signup', userData),
  login: (credentials) => api.post('/auth/login', credentials),
};

// User APIs
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  getLikedRecipes: () => api.get('/user/liked-recipes'),
};

// Recipe APIs
export const recipeAPI = {
  getRecipes: (params) => api.get('/recipes', { params }),
  getRecipe: (id) => api.get(`/recipes/${id}`),
  likeRecipe: (id) => api.post(`/recipes/${id}/like`),
  dislikeRecipe: (id) => api.post(`/recipes/${id}/dislike`),
};

export default api;
