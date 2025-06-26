import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { Videocam, VideocamOff, CameraAlt } from '@mui/icons-material';
import ApiService from '../services/ApiService.ts';

interface CameraCaptureProps {
  onEmotionDetected: (emotion: string, confidence: number, faces: number) => void;
  onError?: (error: string) => void;
  captureInterval?: number; // milliseconds between captures
}

const CameraCapture: React.FC<CameraCaptureProps> = ({
  onEmotionDetected,
  onError,
  captureInterval = 3000, // Default: analyze every 3 seconds
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastEmotion, setLastEmotion] = useState<string>('neutral');
  const [confidence, setConfidence] = useState<number>(0);
  const [facesDetected, setFacesDetected] = useState<number>(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsStreaming(true);
        
        // Start emotion analysis
        startEmotionAnalysis();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to access camera';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    stopEmotionAnalysis();
  };

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !canvasRef.current) return null;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context || video.videoWidth === 0 || video.videoHeight === 0) return null;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    return ApiService.canvasToBase64(canvas);
  }, []);

  const analyzeCurrentFrame = useCallback(async () => {
    if (!isStreaming || isAnalyzing) return;

    const frameData = captureFrame();
    if (!frameData) return;

    setIsAnalyzing(true);

    try {
      const session = ApiService.getCurrentSession();
      const response = await ApiService.analyzeVideo({
        frame_data: frameData,
        user_id: session.user_id,
        session_id: session.session_id,
      });

      setLastEmotion(response.primary_emotion);
      setConfidence(response.confidence);
      setFacesDetected(response.faces_detected);

      // Notify parent component
      onEmotionDetected(response.primary_emotion, response.confidence, response.faces_detected);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  }, [isStreaming, isAnalyzing, captureFrame, onEmotionDetected, onError]);

  const startEmotionAnalysis = () => {
    if (intervalRef.current) return;

    intervalRef.current = setInterval(() => {
      analyzeCurrentFrame();
    }, captureInterval);
  };

  const stopEmotionAnalysis = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      stopCamera();
      stopEmotionAnalysis();
    };
  }, []);

  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      happy: '#4caf50',
      sad: '#2196f3',
      angry: '#f44336',
      surprised: '#ff9800',
      fear: '#9c27b0',
      disgust: '#607d8b',
      neutral: '#78909c',
    };
    return colors[emotion.toLowerCase()] || colors.neutral;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Videocam color="primary" />
          <Typography variant="h6">Video Emotion Analysis</Typography>
          {isAnalyzing && <CircularProgress size={20} />}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box position="relative" mb={2}>
          <video
            ref={videoRef}
            style={{
              width: '100%',
              maxWidth: '640px',
              borderRadius: '8px',
              backgroundColor: '#000',
            }}
            muted
            playsInline
          />
          <canvas
            ref={canvasRef}
            style={{ display: 'none' }}
          />
          
          {isStreaming && (
            <Box
              position="absolute"
              top={8}
              right={8}
              display="flex"
              gap={1}
            >
              <Chip
                icon={<CameraAlt />}
                label="LIVE"
                color="error"
                size="small"
                variant="filled"
              />
            </Box>
          )}
        </Box>

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Button
            variant={isStreaming ? "outlined" : "contained"}
            color={isStreaming ? "secondary" : "primary"}
            startIcon={isStreaming ? <VideocamOff /> : <Videocam />}
            onClick={isStreaming ? stopCamera : startCamera}
          >
            {isStreaming ? 'Stop Camera' : 'Start Camera'}
          </Button>

          {isStreaming && (
            <Box display="flex" gap={1}>
              <Chip
                label={`${facesDetected} face${facesDetected !== 1 ? 's' : ''}`}
                size="small"
                variant="outlined"
              />
              <Chip
                label={lastEmotion}
                size="small"
                style={{
                  backgroundColor: getEmotionColor(lastEmotion),
                  color: 'white'
                }}
              />
              <Chip
                label={`${Math.round(confidence)}%`}
                size="small"
                variant="outlined"
              />
            </Box>
          )}
        </Box>

        <Typography variant="body2" color="text.secondary">
          {isStreaming
            ? `Analyzing frames every ${captureInterval/1000} seconds`
            : 'Click "Start Camera" to begin emotion detection'
          }
        </Typography>
      </CardContent>
    </Card>
  );
};

export default CameraCapture; 