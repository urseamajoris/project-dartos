import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import DescriptionIcon from '@mui/icons-material/Description';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { documentService } from '../services/api';
import FileUpload from '../components/FileUpload';

function DashboardPage() {
  const [query, setQuery] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [topK, setTopK] = useState(5);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Document management state
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (err) {
      setError(`Failed to load documents: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (uploadedDocs) => {
    // Refresh document list after upload
    loadDocuments();
  };

  const handleViewDocument = async (doc) => {
    try {
      const fullDoc = await documentService.getDocument(doc.id);
      setSelectedDoc(fullDoc);
      setDialogOpen(true);
    } catch (err) {
      setError(`Failed to load document: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setProcessing(true);
      setError(null);
      const response = await documentService.processDocument(
        query,
        customPrompt || null,
        topK
      );
      setResult(response);
    } catch (err) {
      setError(`Processing failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const exampleQueries = [
    "Summarize the main points of the document",
    "What are the key findings or conclusions?",
    "Extract important dates and events",
    "List the main topics discussed",
    "Identify any recommendations or action items"
  ];

  const handleExampleClick = (example) => {
    setQuery(example);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dartos - Document Analysis Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload documents and query them using AI-powered analysis
      </Typography>

      <Grid container spacing={4}>
        {/* File Upload Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Upload PDF files to analyze them with AI
            </Typography>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </Paper>
        </Grid>

        {/* Documents List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Documents ({documents.length})
            </Typography>

            {loading ? (
              <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
                <CircularProgress size={24} />
                <Typography sx={{ ml: 2 }}>Loading...</Typography>
              </Box>
            ) : documents.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No documents uploaded yet. Upload a PDF above to get started.
              </Typography>
            ) : (
              <List dense>
                {documents.slice(0, 5).map((doc) => (
                  <ListItem
                    key={doc.id}
                    secondaryAction={
                      <Button
                        size="small"
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
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
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
                        <Typography variant="caption" color="text.secondary" noWrap>
                          {doc.content_preview?.substring(0, 80)}...
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
                {documents.length > 5 && (
                  <ListItem>
                    <Typography variant="body2" color="text.secondary">
                      ... and {documents.length - 5} more documents
                    </Typography>
                  </ListItem>
                )}
              </List>
            )}
          </Paper>
        </Grid>

        {/* Query Interface */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              AI Analysis Query
            </Typography>
            
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your Question or Query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask anything about your uploaded documents..."
                sx={{ mb: 3 }}
              />

              <Accordion sx={{ mb: 3 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Advanced Options</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Custom Prompt (Optional)"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="Provide specific instructions for how to analyze or respond..."
                    sx={{ mb: 3 }}
                  />
                  
                  <Typography gutterBottom>
                    Number of relevant chunks to retrieve: {topK}
                  </Typography>
                  <Slider
                    value={topK}
                    onChange={(e, newValue) => setTopK(newValue)}
                    min={1}
                    max={10}
                    marks
                    valueLabelDisplay="auto"
                  />
                </AccordionDetails>
              </Accordion>

              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={!query.trim() || processing}
                startIcon={processing ? <CircularProgress size={20} /> : <SendIcon />}
                sx={{ mb: 2 }}
              >
                {processing ? 'Analyzing...' : 'Analyze Documents'}
              </Button>
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Example Queries:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {exampleQueries.map((example, index) => (
                  <Chip
                    key={index}
                    label={example}
                    variant="outlined"
                    clickable
                    onClick={() => handleExampleClick(example)}
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Analysis Results */}
        {result && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Analysis Results
              </Typography>

              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Query:
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {result.query}
                  </Typography>
                  
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Response:
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {result.response}
                  </Typography>
                </CardContent>
              </Card>

              {result.relevant_chunks && result.relevant_chunks.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle2">
                      Relevant Document Sections ({result.relevant_chunks.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {result.relevant_chunks.map((chunk, index) => (
                      <Card key={index} sx={{ mb: 2 }}>
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">
                            Section {index + 1}:
                          </Typography>
                          <Typography variant="body2">
                            {chunk}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}
            </Paper>
          </Grid>
        )}

        {/* Error Display */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error">
              {error}
            </Alert>
          </Grid>
        )}
      </Grid>

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

export default DashboardPage;