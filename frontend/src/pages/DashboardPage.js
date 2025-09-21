import React, { useState } from 'react';
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
  Slider,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import { documentService } from '../services/api';

function DashboardPage() {
  const [query, setQuery] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [topK, setTopK] = useState(5);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
        Analysis Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Query your documents using natural language and get intelligent responses
      </Typography>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Query Configuration
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
                {processing ? 'Processing...' : 'Analyze Documents'}
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

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 400 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Results
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {!result && !error && (
              <Box sx={{ textAlign: 'center', color: 'text.secondary', mt: 4 }}>
                <Typography>
                  Enter a query and click "Analyze Documents" to see results here
                </Typography>
              </Box>
            )}

            {result && (
              <Box>
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
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;