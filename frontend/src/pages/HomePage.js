import React from 'react';
import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SummarizeIcon from '@mui/icons-material/Summarize';
import FileUpload from '../components/FileUpload';

function HomePage() {
  const features = [
    {
      icon: <UploadFileIcon />,
      title: 'PDF Upload',
      description: 'Upload PDF documents with automatic text extraction and OCR fallback'
    },
    {
      icon: <StorageIcon />,
      title: 'Metadata Storage',
      description: 'Store document metadata and content in SQL database for efficient retrieval'
    },
    {
      icon: <SmartToyIcon />,
      title: 'LLM Integration',
      description: 'Process documents using advanced language models with RAG system'
    },
    {
      icon: <SummarizeIcon />,
      title: 'Smart Summaries',
      description: 'Generate summaries, explanations, and custom responses based on your prompts'
    }
  ];

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Welcome to Dartos
      </Typography>
      <Typography variant="h6" color="text.secondary" align="center" paragraph>
        Agentic Automated Info Services - Transform your documents into intelligent insights
      </Typography>

      <Grid container spacing={4} sx={{ mt: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Upload Your Documents
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Start by uploading PDF documents. Our system will automatically extract text,
              store metadata, and prepare your documents for intelligent analysis.
            </Typography>
            <FileUpload />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Typography variant="h5" gutterBottom>
            Features
          </Typography>
          <Grid container spacing={2}>
            {features.map((feature, index) => (
              <Grid item xs={12} key={index}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                      <Box sx={{ mr: 2, color: 'primary.main' }}>
                        {feature.icon}
                      </Box>
                      <Box>
                        <Typography variant="h6" component="h3">
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {feature.description}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>

      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom>
          How It Works
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <Typography variant="h6" color="primary">1.</Typography>
            </ListItemIcon>
            <ListItemText
              primary="Upload PDF Documents"
              secondary="Drag and drop or select PDF files to upload to the system"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Typography variant="h6" color="primary">2.</Typography>
            </ListItemIcon>
            <ListItemText
              primary="Automatic Processing"
              secondary="Text extraction with OCR fallback, content analysis, and metadata storage"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Typography variant="h6" color="primary">3.</Typography>
            </ListItemIcon>
            <ListItemText
              primary="Intelligent Analysis"
              secondary="RAG system processes content and prepares it for LLM analysis"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Typography variant="h6" color="primary">4.</Typography>
            </ListItemIcon>
            <ListItemText
              primary="Custom Outputs"
              secondary="Generate summaries, explanations, or custom responses using the dashboard"
            />
          </ListItem>
        </List>
      </Box>
    </Box>
  );
}

export default HomePage;