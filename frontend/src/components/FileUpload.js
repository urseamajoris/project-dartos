import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { documentService } from '../services/api';
import { useError } from '../contexts/ErrorContext';

function FileUpload({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResults, setUploadResults] = useState([]);
  const [processingStatus, setProcessingStatus] = useState({});
  const { showError } = useError();

  // Poll for document processing status
  const pollDocumentStatus = useCallback(async (documentId) => {
    try {
      const status = await documentService.getDocumentStatus(documentId);
      setProcessingStatus(prev => ({
        ...prev,
        [documentId]: status
      }));

      // Continue polling if still processing
      if (status.status === 'uploaded' || status.status === 'processing') {
        setTimeout(() => pollDocumentStatus(documentId), 2000);
      }
    } catch (err) {
      console.error('Error polling status:', err);
    }
  }, []);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    // Handle rejected files (too large, wrong type, etc.)
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(file => {
        const error = file.errors[0];
        if (error.code === 'file-too-large') {
          return `${file.file.name}: File is too large. Maximum size is 50MB.`;
        } else if (error.code === 'file-invalid-type') {
          return `${file.file.name}: Only PDF files are allowed.`;
        } else {
          return `${file.file.name}: ${error.message}`;
        }
      });
      showError(`Upload failed: ${errors.join(' ')}`);
      return;
    }

    setUploading(true);
    setUploadResults([]);
    setUploadProgress(0);

    try {
      const results = [];
      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];
        console.log(`Uploading file ${i + 1}/${acceptedFiles.length}: ${file.name}`);
        
        const result = await documentService.uploadDocument(file, (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        });
        
        results.push(result);
        
        // Start polling for processing status
        if (result.id) {
          pollDocumentStatus(result.id);
        }
      }
      
      setUploadResults(results);
      if (onUploadSuccess) {
        onUploadSuccess(results);
      }
    } catch (err) {
      console.error('Upload error:', err);
      if (err.code === 'ECONNABORTED') {
        showError('Upload timeout - your file may be too large or the network is slow. Please try again with a smaller file.');
      } else {
        showError(err);
      }
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [onUploadSuccess, showError, pollDocumentStatus]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 50 * 1024 * 1024, // 50MB to match backend
    multiple: true
  });

  const getStatusIcon = (result) => {
    const status = processingStatus[result.id];
    if (!status) {
      return <CircularProgress size={24} />;
    }

    switch (status.status) {
      case 'indexed':
      case 'processed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'processing':
      case 'uploaded':
        return <CircularProgress size={24} />;
      default:
        return <DescriptionIcon color="primary" />;
    }
  };

  const getStatusText = (result) => {
    const status = processingStatus[result.id];
    if (!status) {
      return 'Uploading...';
    }
    return status.progress || status.status;
  };

  return (
    <Box>
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the files here...' : 'Drag & drop PDF files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          or click to select files (max 50MB per file)
        </Typography>
        <Button variant="outlined" sx={{ mt: 2 }}>
          Select Files
        </Button>
      </Paper>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography>Uploading... {uploadProgress}%</Typography>
          </Box>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      {uploadResults.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Upload Results:
          </Typography>
          <List>
            {uploadResults.map((result, index) => {
              const status = processingStatus[result.id];
              return (
                <ListItem key={index}>
                  <ListItemIcon>
                    {getStatusIcon(result)}
                  </ListItemIcon>
                  <ListItemText
                    primary={result.filename}
                    secondary={
                      <>
                        <Typography component="span" variant="body2">
                          {getStatusText(result)}
                        </Typography>
                        {status?.error_message && (
                          <Alert severity="error" sx={{ mt: 1 }}>
                            {status.error_message}
                          </Alert>
                        )}
                      </>
                    }
                  />
                </ListItem>
              );
            })}
          </List>
        </Box>
      )}
    </Box>
  );
}

export default FileUpload;