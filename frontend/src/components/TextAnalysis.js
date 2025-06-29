import React, { useState, useCallback } from 'react';
import ApiService from '../services/ApiService';

const TextAnalysis = ({ onEmotionDetected, onProcessingChange, className = '' }) => {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);
  const [charCount, setCharCount] = useState(0);

  const handleTextChange = useCallback(e => {
    const newText = e.target.value;
    setText(newText);
    setCharCount(newText.length);
  }, []);

  const analyzeText = useCallback(async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    if (text.length < 10) {
      setError('Please enter at least 10 characters for better analysis');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      onProcessingChange?.(true);
      console.log('🔍 Starting text analysis...');

      const result = await ApiService.analyzeText({
        text: text.trim(),
        user_id: `demo-user-${Math.random().toString(36).substr(2, 9)}`,
        session_id: `session-${Date.now()}`,
      });

      console.log('✅ Text analysis result:', result);
      setLastResult(result);

      if (onEmotionDetected) {
        onEmotionDetected(result);
      }
    } catch (err) {
      console.error('❌ Text analysis failed:', err);
      console.error('Error details:', {
        message: err.message,
        name: err.name,
        stack: err.stack,
      });

      let errorMessage = 'Text analysis failed';
      if (err.message.includes('analyzeText is not a function')) {
        errorMessage = 'Text analysis service not available. Please try again later.';
      } else if (err.message.includes('Network Error')) {
        errorMessage = 'Network connection failed. Please check your internet connection.';
      } else {
        errorMessage = err.message || 'Text analysis failed';
      }

      setError(errorMessage);
    } finally {
      setIsAnalyzing(false);
      onProcessingChange?.(false);
    }
  }, [text, onEmotionDetected, onProcessingChange]);

  const clearText = useCallback(() => {
    setText('');
    setCharCount(0);
    setLastResult(null);
    setError(null);
  }, []);

  const getEmotionColor = emotion => {
    // Handle undefined or null emotion values
    if (!emotion || typeof emotion !== 'string') {
      return '#9CA3AF'; // Default gray color
    }

    const colors = {
      happy: '#10B981',
      sad: '#3B82F6',
      angry: '#EF4444',
      surprised: '#F59E0B',
      fear: '#8B5CF6',
      calm: '#6B7280',
      excited: '#F97316',
      confused: '#8B5CF6',
      neutral: '#9CA3AF',
    };
    return colors[emotion.toLowerCase()] || '#9CA3AF';
  };

  const getSentimentColor = sentiment => {
    // Handle undefined or null sentiment values
    if (!sentiment || typeof sentiment !== 'string') {
      return '#6B7280'; // Default gray color
    }

    const colors = {
      positive: '#10B981',
      negative: '#EF4444',
      neutral: '#6B7280',
    };
    return colors[sentiment.toLowerCase()] || '#6B7280';
  };

  const getSentimentIcon = sentiment => {
    // Handle undefined or null sentiment values
    if (!sentiment || typeof sentiment !== 'string') {
      return '😐'; // Default neutral icon
    }

    const icons = {
      positive: '😊',
      negative: '😔',
      neutral: '😐',
    };
    return icons[sentiment.toLowerCase()] || '😐';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Text Input Section */}
      <div className="space-y-4">
        <div>
          <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-2">
            Enter your text for emotion analysis:
          </label>
          <div className="relative">
            <textarea
              id="text-input"
              value={text}
              onChange={handleTextChange}
              placeholder="Type or paste your text here to analyze emotions..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={isAnalyzing}
              maxLength={1000}
            />
            <div className="absolute bottom-2 right-2 text-xs text-gray-500">{charCount}/1000</div>
          </div>
        </div>

        {/* Character count indicator */}
        <div className="flex justify-between items-center">
          <div className="text-xs text-gray-500">
            {charCount < 10 ? (
              <span className="text-orange-600">⚠️ At least 10 characters recommended</span>
            ) : charCount > 500 ? (
              <span className="text-green-600">✅ Good length for analysis</span>
            ) : (
              <span className="text-blue-600">📝 {charCount} characters</span>
            )}
          </div>
          <div className="text-xs text-gray-500">
            {charCount > 1000 && <span className="text-red-600">⚠️ Text too long</span>}
          </div>
        </div>

        {/* Controls */}
        <div className="flex space-x-4">
          <button
            onClick={analyzeText}
            disabled={isAnalyzing || text.length < 10}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {isAnalyzing ? '🔍 Analyzing...' : 'Analyze Text'}
          </button>
          <button
            onClick={clearText}
            disabled={isAnalyzing}
            className="bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Clear
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-100 border border-red-300 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Analysis Status */}
        {isAnalyzing && (
          <div className="p-3 bg-blue-100 border border-blue-300 rounded-lg">
            <p className="text-blue-700">🔍 Analyzing text patterns and emotions...</p>
          </div>
        )}
      </div>

      {/* Results Display */}
      {lastResult && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>

          <div className="space-y-4">
            {/* Primary Emotion */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
              <span className="font-medium">Primary Emotion:</span>
              <span
                className="px-3 py-1 rounded-full text-white font-semibold"
                style={{ backgroundColor: getEmotionColor(lastResult.primary_emotion) }}
              >
                {lastResult.primary_emotion}
              </span>
            </div>

            {/* Confidence */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
              <span className="font-medium">Confidence:</span>
              <span className="font-semibold text-gray-900">
                {Math.round((lastResult.confidence || 0) * 100)}%
              </span>
            </div>

            {/* Sentiment */}
            {lastResult.sentiment && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
                <span className="font-medium">Sentiment:</span>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSentimentIcon(lastResult.sentiment)}</span>
                  <span
                    className="font-semibold capitalize"
                    style={{ color: getSentimentColor(lastResult.sentiment) }}
                  >
                    {lastResult.sentiment}
                  </span>
                </div>
              </div>
            )}

            {/* All Emotions */}
            {lastResult.emotions && lastResult.emotions.length > 0 && (
              <div className="p-3 bg-white rounded-lg border">
                <span className="font-medium block mb-2">All Detected Emotions:</span>
                <div className="flex flex-wrap gap-2">
                  {lastResult.emotions.map((emotion, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 rounded text-xs text-white"
                      style={{ backgroundColor: getEmotionColor(emotion.emotion) }}
                    >
                      {emotion.emotion} ({Math.round((emotion.confidence || 0) * 100)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Keywords */}
            {lastResult.keywords && lastResult.keywords.length > 0 && (
              <div className="p-3 bg-white rounded-lg border">
                <span className="font-medium block mb-2">Key Phrases:</span>
                <div className="flex flex-wrap gap-2">
                  {lastResult.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* LLM Analysis Section */}
            {lastResult.llm_analysis && (
              <div className="space-y-3">
                {/* Emotional Context */}
                {lastResult.llm_analysis.emotional_context && (
                  <div className="p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                    <span className="font-medium block mb-2 text-purple-800">
                      🧠 AI Emotional Context:
                    </span>
                    <p className="text-purple-700 text-sm">
                      {lastResult.llm_analysis.emotional_context}
                    </p>
                  </div>
                )}

                {/* AI Recommendations */}
                {lastResult.llm_analysis.recommendations && (
                  <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                    <span className="font-medium block mb-2 text-green-800">
                      💡 AI Recommendations:
                    </span>
                    <p className="text-green-700 text-sm">
                      {lastResult.llm_analysis.recommendations}
                    </p>
                  </div>
                )}

                {/* AI Generated Badge */}
                <div className="flex items-center justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    🤖 AI Generated Analysis
                  </span>
                </div>
              </div>
            )}

            {/* Analysis Metadata */}
            <div className="text-xs text-gray-500 text-center pt-2">
              Analyzed at {new Date(lastResult.timestamp || Date.now()).toLocaleTimeString()}
              {lastResult.debug_info?.analysis_method === 'bedrock_llm' && (
                <span className="block text-blue-600">Using AWS Bedrock LLM</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TextAnalysis;
