import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { documentService } from '../services/api';
import { useError } from '../contexts/ErrorContext';

function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showError } = useError();

  useEffect(() => {
    const loadInitialDocuments = async () => {
      try {
        setLoading(true);
        const docs = await documentService.getDocuments();
        setDocuments(docs);
      } catch (err) {
        showError(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialDocuments();
  }, [showError]);

  const handleViewDocument = async (doc) => {
    try {
      const fullDoc = await documentService.getDocument(doc.id);
      setSelectedDoc(fullDoc);
      setDialogOpen(true);
    } catch (err) {
      showError(err);
    }
  };



  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading documents...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Documents
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage and view your uploaded documents
      </Typography>

      {documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No documents uploaded yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Go to the Home page to upload your first document
          </Typography>
        </Paper>
      ) : (
        <Paper>
          <List>
            {documents.map((doc, index) => (
              <ListItem
                key={doc.id}
                divider={index < documents.length - 1}
                secondaryAction={
                  <Button
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    onClick={() => handleViewDocument(doc)}
                  >
                    View
                  </Button>
                }
              >
                <ListItemIcon>
                  <DescriptionIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {doc.filename}
                      </Typography>
                      <Chip
                        label={doc.status}
                        color={doc.status === 'processed' ? 'success' : 'warning'}
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Typography variant="body2" color="text.secondary">
                      {doc.content_preview}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Document View Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedDoc?.filename}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {selectedDoc?.content_preview}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DocumentsPage;