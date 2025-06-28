import React from 'react';

const EmotionVisualization = ({ emotionHistory }) => {
  const getEmotionEmoji = (emotion) => {
    const emojiMap = {
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
      disappointed: '😞',
      calm: '😌',
      confused: '😕'
    };
    return emojiMap[emotion.toLowerCase()] || '😐';
  };

  const getEmotionColor = (emotion) => {
    const colors = {
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
      disappointed: '#795548',
      calm: '#4caf50',
      confused: '#9c27b0'
    };
    return colors[emotion.toLowerCase()] || colors.neutral;
  };

  const getModalityIcon = (modality) => {
    const icons = {
      video: '📹',
      audio: '🎤',
      text: '✍️',
      unknown: '❓'
    };
    return icons[modality] || '❓';
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: '#10B981',
      negative: '#EF4444',
      neutral: '#6B7280'
    };
    return colors[sentiment?.toLowerCase()] || '#6B7280';
  };

  // Get the most recent emotion for the main visualization
  const latestEmotion = emotionHistory[0];
  
  if (!latestEmotion) {
    return (
      <div className="text-center p-8">
        <div className="text-6xl mb-4">🤷‍♂️</div>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No Emotions Detected Yet</h3>
        <p className="text-gray-500">
          Start using the Video, Voice, or Text analysis tabs to see your emotion data here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-900 text-center">
        Emotion Analytics
      </h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Emotion Display */}
        <div className="flex flex-col items-center justify-center min-h-80 p-6 rounded-lg bg-white border shadow-lg" 
             style={{
               background: `radial-gradient(circle at center, ${getEmotionColor(latestEmotion.primary_emotion)}20 0%, transparent 70%)`
             }}>
          
          {/* Modality Icon */}
          <div className="text-3xl mb-4">
            {getModalityIcon(latestEmotion.modality)}
          </div>

          {/* Animated Emoji */}
          <div className={`text-8xl mb-4 ${(latestEmotion.confidence || 0) > 0.7 ? 'animate-bounce' : ''}`}>
            {getEmotionEmoji(latestEmotion.primary_emotion)}
          </div>

          {/* Emotion Label */}
          <h4 className="text-3xl font-bold mb-4 capitalize text-center"
              style={{ color: getEmotionColor(latestEmotion.primary_emotion) }}>
            {latestEmotion.primary_emotion}
          </h4>

          {/* Confidence Bar */}
          <div className="w-full max-w-xs">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Confidence</span>
              <span>{Math.round((latestEmotion.confidence || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min((latestEmotion.confidence || 0) * 100, 100)}%`,
                  backgroundColor: (latestEmotion.confidence || 0) > 0.7 ? '#4caf50' : 
                                 (latestEmotion.confidence || 0) > 0.4 ? '#ff9800' : '#f44336'
                }}
              />
            </div>
          </div>

          {/* Additional Info */}
          {latestEmotion.sentiment && (
            <div className="mt-4 text-center">
              <div className="text-sm text-gray-600">Sentiment:</div>
              <div className="font-medium capitalize" 
                   style={{ color: getSentimentColor(latestEmotion.sentiment) }}>
                {latestEmotion.sentiment}
              </div>
            </div>
          )}

          {latestEmotion.transcript && (
            <div className="mt-2 text-center">
              <div className="text-xs text-gray-500 italic max-w-xs">
                "{latestEmotion.transcript.substring(0, 50)}..."
              </div>
            </div>
          )}
        </div>

        {/* Emotion History Timeline */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">Recent Emotions</h4>
          <div className="max-h-80 overflow-y-auto space-y-3 pr-2">
            {emotionHistory.slice(0, 8).map((emotion, index) => (
              <div
                key={index}
                className="flex items-center p-3 bg-white border rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
              >
                {/* Timeline indicator */}
                <div className="flex-shrink-0 w-8 text-center">
                  <div className="text-lg">{getModalityIcon(emotion.modality)}</div>
                </div>

                {/* Emotion info */}
                <div className="flex-grow ml-3 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2 min-w-0">
                      <span className="text-lg flex-shrink-0">{getEmotionEmoji(emotion.primary_emotion)}</span>
                      <span className="font-medium capitalize truncate">{emotion.primary_emotion}</span>
                    </div>
                    <span className="text-sm text-gray-500 flex-shrink-0 ml-2">
                      {Math.round((emotion.confidence || 0) * 100)}%
                    </span>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.min((emotion.confidence || 0) * 100, 100)}%`,
                        backgroundColor: getEmotionColor(emotion.primary_emotion)
                      }}
                    />
                  </div>
                  
                  {/* Timestamp */}
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(emotion.timestamp).toLocaleTimeString()}
                    {emotion.sentiment && (
                      <span className="ml-2 capitalize">• {emotion.sentiment}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary Stats */}
          {emotionHistory.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">Session Summary</h5>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-blue-700">Total Analyses:</div>
                  <div className="font-semibold">{emotionHistory.length}</div>
                </div>
                <div>
                  <div className="text-blue-700">Avg Confidence:</div>
                  <div className="font-semibold">
                    {Math.round(
                      (emotionHistory.reduce((acc, e) => acc + (e.confidence || 0), 0) / emotionHistory.length) * 100
                    )}%
                  </div>
                </div>
                <div>
                  <div className="text-blue-700">Most Common:</div>
                  <div className="font-semibold capitalize">
                    {Object.entries(
                      emotionHistory.reduce((acc, e) => {
                        acc[e.primary_emotion] = (acc[e.primary_emotion] || 0) + 1;
                        return acc;
                      }, {})
                    ).sort(([, a], [, b]) => b - a)[0]?.[0] || 'none'}
                  </div>
                </div>
                <div>
                  <div className="text-blue-700">Session Duration:</div>
                  <div className="font-semibold">
                    {emotionHistory.length > 1 
                      ? Math.round((new Date(emotionHistory[0].timestamp) - new Date(emotionHistory[emotionHistory.length - 1].timestamp)) / 1000 / 60)
                      : 0} min
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmotionVisualization; 