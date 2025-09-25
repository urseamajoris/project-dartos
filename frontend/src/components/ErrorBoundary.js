import React from 'react';
import { Alert, AlertTitle, Box, Button, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // If there's an error context provider, use it to show the error
    if (this.props.onError) {
      this.props.onError(error);
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '50vh',
            p: 3,
          }}
        >
          <Alert 
            severity="error" 
            sx={{ maxWidth: 600, width: '100%', mb: 3 }}
          >
            <AlertTitle>Something went wrong</AlertTitle>
            <Typography variant="body2" paragraph>
              An unexpected error occurred in the application. This has been logged for investigation.
            </Typography>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" component="div" sx={{ mb: 1 }}>
                  Error Details (Development Mode):
                </Typography>
                <Typography 
                  variant="caption" 
                  component="pre" 
                  sx={{ 
                    backgroundColor: 'rgba(0,0,0,0.1)', 
                    p: 1, 
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </Typography>
              </Box>
            )}
          </Alert>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={this.handleReload}
            >
              Reload Page
            </Button>
            <Button
              variant="outlined"
              onClick={this.handleReset}
            >
              Try Again
            </Button>
          </Box>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;