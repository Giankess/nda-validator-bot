import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';

const FeedbackForm = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await axios.post('http://localhost:8000/feedback', {
        document_id: documentId,
        feedback_text: feedback,
      });

      // Navigate back to review with updated suggestions
      navigate(`/review/${documentId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while submitting feedback');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/review/${documentId}`);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          Back to Review
        </Button>

        <Typography variant="h4" component="h1" gutterBottom>
          Provide Feedback
        </Typography>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Please provide your feedback on the AI suggestions. Your input helps improve the system.
        </Typography>

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            label="Your Feedback"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Please provide detailed feedback about the suggestions..."
            sx={{ mb: 3 }}
          />

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              startIcon={<SendIcon />}
              disabled={loading || !feedback.trim()}
            >
              {loading ? (
                <>
                  <CircularProgress size={24} sx={{ mr: 1 }} />
                  Submitting...
                </>
              ) : (
                'Submit Feedback'
              )}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default FeedbackForm; 