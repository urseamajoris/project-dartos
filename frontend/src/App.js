import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import DocumentsPage from './pages/DocumentsPage';
import DashboardPage from './pages/DashboardPage';
import Navigation from './components/Navigation';
import { ErrorProvider, useError } from './contexts/ErrorContext';
import ErrorBoundary from './components/ErrorBoundary';
import ErrorToast from './components/ErrorToast';

// Inner App component that uses the error context
function AppContent() {
  const { showError } = useError();

  const handleError = (error) => {
    showError(error);
  };

  return (
    <ErrorBoundary onError={handleError}>
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Dartos - Agentic Info Services
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Navigation />
          
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </Container>

          <ErrorToast />
        </Box>
      </Router>
    </ErrorBoundary>
  );
}

// Main App component with error provider
function App() {
  return (
    <ErrorProvider>
      <AppContent />
    </ErrorProvider>
  );
}

export default App;