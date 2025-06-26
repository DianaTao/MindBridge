import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  Fab,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import {
  Face,
  Mic,
  TextFields,
  Psychology,
  Analytics,
  Settings,
  Menu,
  Dashboard,
  History,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import EmotionVisualization from './components/EmotionVisualization.tsx';
import WebSocketService from './services/WebSocketService.ts';
import CameraCapture from './components/CameraCapture.tsx';
import ApiService from './services/ApiService.ts';
import { EmotionState, RecommendationData } from './types/emotions';
import './App.css';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#64b5f6',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
});

interface AnalysisState {
  video: {
    active: boolean;
    emotion: string;
    confidence: number;
  };
  audio: {
    active: boolean;
    emotion: string;
    confidence: number;
  };
  text: {
    active: boolean;
    sentiment: string;
    confidence: number;
  };
  unified: EmotionState | null;
}

function App() {
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    video: { active: false, emotion: 'neutral', confidence: 0 },
    audio: { active: false, emotion: 'neutral', confidence: 0 },
    text: { active: false, sentiment: 'neutral', confidence: 0 },
    unified: null,
  });

  const [recommendations] = useState<RecommendationData | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');

  useEffect(() => {
    // Check API health first
    const checkApiHealth = async () => {
      try {
        const health = await ApiService.healthCheck();
        console.log('✅ API Health:', health);
        setApiStatus('connected');
        setConnectionStatus('connected');
      } catch (error) {
        console.error('❌ API Health Check Failed:', error);
        setApiStatus('disconnected');
        setConnectionStatus('disconnected');
      }
    };

    checkApiHealth();

    // Initialize WebSocket connection (comment out for now since we're using HTTP)
    // WebSocketService.connect();

    // Set up event handlers
    // WebSocketService.onConnect(() => {
    //   setConnectionStatus('connected');
    //   console.log('Connected to MindBridge WebSocket');
    // });

    // WebSocketService.onDisconnect(() => {
    //   setConnectionStatus('disconnected');
    //   console.log('Disconnected from MindBridge WebSocket');
    // });

    // WebSocketService.onEmotionUpdate((data) => {
    //   if (data.action === 'current_state') {
    //     setAnalysisState(prev => ({
    //       ...prev,
    //       unified: data.data.emotion_state
    //     }));
    //     setRecommendations(data.data.recommendations);
    //   }
    // });

    return () => {
      // WebSocketService.disconnect();
    };
  }, []);

  const handleVideoEmotion = (emotion: string, confidence: number) => {
    setAnalysisState(prev => ({
      ...prev,
      video: { active: true, emotion, confidence }
    }));
  };

  const handleAudioEmotion = (emotion: string, confidence: number) => {
    setAnalysisState(prev => ({
      ...prev,
      audio: { active: true, emotion, confidence }
    }));
  };

  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      happy: '#4caf50',
      sad: '#2196f3',
      angry: '#f44336',
      surprised: '#ff9800',
      fear: '#9c27b0',
      disgust: '#607d8b',
      neutral: '#78909c',
      excited: '#e91e63',
      stressed: '#ff5722',
    };
    return colors[emotion.toLowerCase()] || colors.neutral;
  };

  const getConnectionIcon = () => {
    switch (apiStatus) {
      case 'connected':
        return <Chip icon={<Psychology />} label="API Connected" color="success" size="small" />;
      case 'checking':
        return <Chip icon={<Psychology />} label="Checking..." color="warning" size="small" />;
      default:
        return <Chip icon={<Psychology />} label="API Disconnected" color="error" size="small" />;
    }
  };

  const renderDashboard = () => (
    <Grid container spacing={3}>
      {/* Real-time Emotion Visualization */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🧠 Real-Time Emotion Analysis
            </Typography>
            <EmotionVisualization 
              emotion={analysisState.unified?.unified_emotion || 'neutral'}
              intensity={analysisState.unified?.intensity || 5}
              confidence={analysisState.unified?.confidence || 0}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* Camera Capture */}
      <Grid item xs={12} md={4}>
        <CameraCapture
          onEmotionDetected={handleVideoEmotion}
          onError={(error) => console.error('Camera error:', error)}
          captureInterval={5000} // Analyze every 5 seconds
        />
      </Grid>

      {/* Multi-Modal Analysis Status */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📊 Analysis Sources
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Box display="flex" alignItems="center">
                  <Face sx={{ mr: 1, color: getEmotionColor(analysisState.video.emotion) }} />
                  <Typography variant="body2">Video</Typography>
                </Box>
                <Chip 
                  label={analysisState.video.emotion} 
                  size="small"
                  sx={{ backgroundColor: getEmotionColor(analysisState.video.emotion) }}
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={analysisState.video.confidence * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Box display="flex" alignItems="center">
                  <Mic sx={{ mr: 1, color: getEmotionColor(analysisState.audio.emotion) }} />
                  <Typography variant="body2">Audio</Typography>
                </Box>
                <Chip 
                  label={analysisState.audio.emotion} 
                  size="small"
                  sx={{ backgroundColor: getEmotionColor(analysisState.audio.emotion) }}
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={analysisState.audio.confidence * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Box display="flex" alignItems="center">
                  <TextFields sx={{ mr: 1, color: getEmotionColor(analysisState.text.sentiment) }} />
                  <Typography variant="body2">Text</Typography>
                </Box>
                <Chip 
                  label={analysisState.text.sentiment} 
                  size="small"
                  sx={{ backgroundColor: getEmotionColor(analysisState.text.sentiment) }}
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={analysisState.text.confidence * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Real-time Chart */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📈 Emotion Timeline
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Emotion timeline chart will be displayed here
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Recommendations */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              💡 Recommendations
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered recommendations will be displayed here
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Camera and Audio Capture */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📹 Video Analysis
            </Typography>
            <CameraCapture onEmotionDetected={handleVideoEmotion} />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🎙️ Audio Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Audio capture functionality will be implemented here
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAnalytics = () => (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          📊 Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Historical emotion analytics and insights will be displayed here.
          This section can include emotion trends, patterns, and detailed reports.
        </Typography>
      </CardContent>
    </Card>
  );

  const renderContent = () => {
    switch (currentView) {
      case 'analytics':
        return renderAnalytics();
      case 'dashboard':
      default:
        return renderDashboard();
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar position="sticky" sx={{ backgroundColor: 'rgba(26, 26, 26, 0.95)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => setDrawerOpen(true)}>
            <Menu />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            🧠 MindBridge AI
          </Typography>
          {getConnectionIcon()}
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 280, pt: 2 }}>
          <List>
            <ListItem button onClick={() => { setCurrentView('dashboard'); setDrawerOpen(false); }}>
              <ListItemIcon><Dashboard /></ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button onClick={() => { setCurrentView('analytics'); setDrawerOpen(false); }}>
              <ListItemIcon><Analytics /></ListItemIcon>
              <ListItemText primary="Analytics" />
            </ListItem>
            <ListItem button>
              <ListItemIcon><History /></ListItemIcon>
              <ListItemText primary="History" />
            </ListItem>
            <ListItem button>
              <ListItemIcon><Settings /></ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {connectionStatus === 'disconnected' && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            Not connected to MindBridge AI. Attempting to reconnect...
          </Alert>
        )}

        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </Container>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => {
          // Refresh API health check
          ApiService.healthCheck().then(() => {
            console.log('✅ API refreshed');
          }).catch((error) => {
            console.error('❌ API refresh failed:', error);
          });
        }}
      >
        <Psychology />
      </Fab>
    </ThemeProvider>
  );
}

export default App; 