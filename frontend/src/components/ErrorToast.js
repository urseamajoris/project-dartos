import React from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Stack,
  Box,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useError } from '../contexts/ErrorContext';

const ErrorToast = () => {
  const { errors, dismissError } = useError();

  if (errors.length === 0) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80, // Below the AppBar
        right: 16,
        zIndex: 2000, // Above MUI Dialog default (1300)
        maxWidth: 400,
        width: '100%',
      }}
    >
      <Stack spacing={1}>
        {errors.map((error) => (
          <Snackbar
            key={error.id}
            open={true}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            sx={{ position: 'relative', top: 0, right: 0 }}
          >
            <Alert
              severity={error.severity}
              variant="filled"
              sx={{ width: '100%', maxWidth: 400 }}
              action={
                <IconButton
                  size="small"
                  aria-label="close"
                  color="inherit"
                  onClick={() => dismissError(error.id)}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              }
            >
              <AlertTitle>
                {getErrorTitle(error.type, error.severity)}
              </AlertTitle>
              <Typography variant="body2">
                {error.message}
              </Typography>
            </Alert>
          </Snackbar>
        ))}
      </Stack>
    </Box>
  );
};

// Helper function to get appropriate error titles
const getErrorTitle = (type, severity) => {
  if (severity === 'warning') {
    if (type === 'client') return 'Warning';
    return 'Notice';
  }
  
  if (type === 'server') return 'Server Error';
  if (type === 'client') return 'Request Error';
  
  return 'Error';
};

export default ErrorToast;