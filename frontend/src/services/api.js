import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response || error);
    
    // Log specific error details for debugging
    if (error.response) {
      console.error('Response Status:', error.response.status);
      console.error('Response Data:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

export const documentService = {
  // Upload a PDF document
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all documents
  getDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },

  // Get a specific document
  getDocument: async (id) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  // Process document with custom query
  processDocument: async (query, customPrompt = null, topK = 5) => {
    const response = await api.post('/process', {
      query,
      custom_prompt: customPrompt,
      top_k: topK,
    });
    return response.data;
  },
};

export default api;