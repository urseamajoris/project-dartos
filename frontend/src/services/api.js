import axios from 'axios';
import { debug, info, error } from '../utils/logger';

// Determine API base URL
// Priority: REACT_APP_API_URL env var > relative path for proxy
// When REACT_APP_API_URL is set (local development), use it directly
// Otherwise, use '/api' which will be proxied by setupProxy.js (Docker)
const API_BASE_URL = process.env.REACT_APP_API_URL 
  ? `${process.env.REACT_APP_API_URL}/api`
  : '/api';

console.log('[API] Base URL configured as:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for large file uploads
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    const requestInfo = {
      url: config.url,
      method: config.method?.toUpperCase(),
      headers: config.headers,
      data: config.data,
      timestamp: new Date().toISOString(),
    };
    debug('API request start', requestInfo);
    return config;
  },
  (err) => {
    error('API request error', { error: err });
    return Promise.reject(err);
  }
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    const responseInfo = {
      url: response.config.url,
      method: response.config.method?.toUpperCase(),
      status: response.status,
      headers: response.headers,
      data: response.data,
      timestamp: new Date().toISOString(),
    };
    info('API response success', responseInfo);
    return response;
  },
  (err) => {
    const errorInfo = {
      url: err.config?.url,
      method: err.config?.method?.toUpperCase(),
      error: err.message,
      code: err.code,
      response: err.response ? {
        status: err.response.status,
        data: err.response.data,
        headers: err.response.headers,
      } : null,
      timestamp: new Date().toISOString(),
    };
    error('API response error', errorInfo);
    return Promise.reject(err);
  }
);

export const documentService = {
  // Upload a PDF document
  uploadDocument: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onUploadProgress,
      timeout: 300000, // 5 minutes for large files
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

  // Get document processing status
  getDocumentStatus: async (id) => {
    const response = await api.get(`/documents/${id}/status`);
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