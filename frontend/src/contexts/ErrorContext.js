import React, { createContext, useContext, useState, useCallback } from 'react';

const ErrorContext = createContext();

// Custom hook to use the error context
export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

// Error provider component
export const ErrorProvider = ({ children }) => {
  const [errors, setErrors] = useState([]);

  // Function to show a new error
  const showError = useCallback((error, options = {}) => {
    const errorObj = {
      id: Date.now() + Math.random(), // Simple unique ID
      message: formatErrorMessage(error),
      type: getErrorType(error),
      severity: getErrorSeverity(error),
      timestamp: new Date(),
      ...options
    };

    setErrors(prev => [...prev, errorObj]);

    // Auto-dismiss after 6 seconds unless specified otherwise
    if (options.autoDismiss !== false) {
      setTimeout(() => {
        setErrors(prev => prev.filter(err => err.id !== errorObj.id));
      }, options.duration || 6000);
    }
  }, []); // Remove dismissError dependency to avoid circular dependency

  // Function to dismiss an error
  const dismissError = useCallback((id) => {
    setErrors(prev => prev.filter(error => error.id !== id));
  }, []);

  // Function to clear all errors
  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const value = {
    errors,
    showError,
    dismissError,
    clearErrors
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

// Helper function to format error messages
const formatErrorMessage = (error) => {
  if (typeof error === 'string') {
    return error;
  }

  if (error?.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Handle specific HTTP status codes
    switch (status) {
      case 413:
        return 'File too large. Please upload a smaller file (maximum 10MB).';
      case 400:
        return data?.detail || 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'Access denied. You don\'t have permission to perform this action.';
      case 404:
        return 'Resource not found. The requested item may have been deleted.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case 500:
        return 'Server error. Please try again later.';
      case 502:
      case 503:
      case 504:
        return 'Service temporarily unavailable. Please try again later.';
      default:
        return data?.detail || data?.message || `Server error (${status})`;
    }
  }

  return error?.message || 'An unexpected error occurred';
};

// Helper function to determine error type
const getErrorType = (error) => {
  if (error?.response?.status) {
    const status = error.response.status;
    if (status >= 400 && status < 500) return 'client';
    if (status >= 500) return 'server';
  }
  return 'unknown';
};

// Helper function to determine error severity
const getErrorSeverity = (error) => {
  if (error?.response?.status) {
    const status = error.response.status;
    if (status === 413 || status === 400) return 'warning';
    if (status >= 500) return 'error';
    if (status === 401 || status === 403) return 'warning';
  }
  return 'error';
};