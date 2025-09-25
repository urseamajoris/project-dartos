import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import HomePage from './pages/HomePage';
import DocumentsPage from './pages/DocumentsPage';
import DashboardPage from './pages/DashboardPage';
import Navigation from './components/Navigation';

function App() {
  return (
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
      </Box>
    </Router>
  );
}

export default App;