import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import FeedbackIcon from '@mui/icons-material/Feedback';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';

const DocumentReview = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [document, setDocument] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const analyzeDocument = async () => {
      try {
        const response = await axios.post(`http://localhost:8000/analyze/${documentId}`);
        setDocument(response.data);
        setSuggestions(response.data.suggestions || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'An error occurred while analyzing the document');
      } finally {
        setLoading(false);
      }
    };

    analyzeDocument();
  }, [documentId]);

  const handleAccept = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`http://localhost:8000/accept/${documentId}`);
      const cleanDocId = response.data.clean_document_id;
      
      // Download the clean document
      const docResponse = await axios.get(`http://localhost:8000/download/${cleanDocId}`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([docResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'clean_nda.docx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Navigate back to upload
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while accepting suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = () => {
    navigate(`/feedback/${documentId}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Document Review
        </Typography>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Review the AI suggestions for your NDA document
        </Typography>

        <List>
          {suggestions.map((suggestion, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" component="span">
                        Original Text:
                      </Typography>
                      <Chip
                        label="Original"
                        size="small"
                        color="default"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.primary"
                      sx={{ display: 'block', textDecoration: 'line-through' }}
                    >
                      {suggestion.original}
                    </Typography>
                  }
                />
              </ListItem>

              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" component="span">
                        Suggested Change:
                      </Typography>
                      <Chip
                        label="Suggestion"
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Typography
                      component="span"
                      variant="body2"
                      color="primary"
                      sx={{ display: 'block' }}
                    >
                      {suggestion.suggestion}
                    </Typography>
                  }
                />
              </ListItem>

              {index < suggestions.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>

        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<CheckCircleIcon />}
            onClick={handleAccept}
            disabled={loading}
          >
            Accept All Suggestions
          </Button>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<FeedbackIcon />}
            onClick={handleFeedback}
            disabled={loading}
          >
            Provide Feedback
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default DocumentReview; 