import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import DocumentUpload from './components/DocumentUpload';
import DocumentReview from './components/DocumentReview';
import FeedbackForm from './components/FeedbackForm';

// Hubersuhner corporate colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#003366', // Hubersuhner blue
      light: '#004d99',
      dark: '#002244',
    },
    secondary: {
      main: '#ff6600', // Hubersuhner orange
      light: '#ff8533',
      dark: '#cc5200',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Helvetica Neue", Arial, sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static" color="primary">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                NDA Validator AI Assistant
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
            <Routes>
              <Route path="/" element={<DocumentUpload />} />
              <Route path="/review/:documentId" element={<DocumentReview />} />
              <Route path="/feedback/:documentId" element={<FeedbackForm />} />
            </Routes>
          </Container>
          
          <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', backgroundColor: 'primary.main' }}>
            <Container maxWidth="sm">
              <Typography variant="body2" color="white" align="center">
                © {new Date().getFullYear()} Hubersuhner NDA Validator
              </Typography>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 