import axios from 'axios';

// FastAPI API Backend URL
export const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' ? 'http://localhost:8000/api/v1' : `${window.location.protocol}//${window.location.host}/api/v1`)
  : 'http://localhost:8000/api/v1';

export const WS_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' ? 'ws://localhost:8000/api/v1' : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1`)
  : 'ws://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject JWT Bearer token into requests
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
