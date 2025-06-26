import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { motion } from 'framer-motion';

interface EmotionVisualizationProps {
  emotion: string;
  intensity: number;
  confidence: number;
}

const EmotionVisualization: React.FC<EmotionVisualizationProps> = ({
  emotion,
  intensity,
  confidence
}) => {
  const getEmotionEmoji = (emotion: string) => {
    const emojiMap: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      surprised: '😲',
      fear: '😨',
      disgust: '🤢',
      neutral: '😐',
      excited: '🤩',
      stressed: '😰',
      thoughtful: '🤔',
      disappointed: '😞'
    };
    return emojiMap[emotion.toLowerCase()] || '😐';
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
      thoughtful: '#3f51b5',
      disappointed: '#795548'
    };
    return colors[emotion.toLowerCase()] || colors.neutral;
  };

  const pulseAnimation = {
    scale: [1, 1.1, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={300}
      sx={{
        background: `radial-gradient(circle at center, ${getEmotionColor(emotion)}20 0%, transparent 70%)`,
        borderRadius: 2,
        p: 3
      }}
    >
      {/* Animated Emoji */}
      <motion.div
        animate={intensity > 7 ? pulseAnimation : {}}
        style={{
          fontSize: '120px',
          marginBottom: '20px',
          filter: `brightness(${confidence * 100 + 50}%)`
        }}
      >
        {getEmotionEmoji(emotion)}
      </motion.div>

      {/* Emotion Label */}
      <Typography
        variant="h4"
        sx={{
          color: getEmotionColor(emotion),
          fontWeight: 'bold',
          textTransform: 'capitalize',
          mb: 2
        }}
      >
        {emotion}
      </Typography>

      {/* Intensity Bar */}
      <Box width="100%" maxWidth={300} mb={2}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2" color="text.secondary">
            Intensity
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {intensity}/10
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={(intensity / 10) * 100}
          sx={{
            height: 12,
            borderRadius: 6,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: getEmotionColor(emotion),
              borderRadius: 6,
            }
          }}
        />
      </Box>

      {/* Confidence Bar */}
      <Box width="100%" maxWidth={300}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2" color="text.secondary">
            Confidence
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Math.round(confidence * 100)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={confidence * 100}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: confidence > 0.7 ? '#4caf50' : confidence > 0.4 ? '#ff9800' : '#f44336',
              borderRadius: 4,
            }
          }}
        />
      </Box>

      {/* Status Indicators */}
      <Box mt={3} display="flex" gap={2}>
        {intensity > 8 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring" }}
          >
            <Typography
              variant="caption"
              sx={{
                px: 2,
                py: 0.5,
                backgroundColor: '#ff5722',
                borderRadius: 2,
                color: 'white'
              }}
            >
              High Intensity
            </Typography>
          </motion.div>
        )}
        
        {confidence < 0.3 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", delay: 0.1 }}
          >
            <Typography
              variant="caption"
              sx={{
                px: 2,
                py: 0.5,
                backgroundColor: '#ff9800',
                borderRadius: 2,
                color: 'white'
              }}
            >
              Low Confidence
            </Typography>
          </motion.div>
        )}
      </Box>
    </Box>
  );
};

export default EmotionVisualization; 