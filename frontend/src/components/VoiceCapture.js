import React, { useState, useRef, useCallback, useEffect } from 'react';
import ApiService from '../services/ApiService';

const VoiceCapture = ({ onEmotionDetected, onProcessingChange, className = '' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordingTime, setRecordingTime] = useState(0);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const microphoneRef = useRef(null);
  const animationFrameRef = useRef(null);
  const recordingTimerRef = useRef(null);

  // Check browser support
  useEffect(() => {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      setIsSupported(false);
      setError('Voice recording is not supported in this browser');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording]);

  const analyzeAudio = async (audioBlob) => {
    try {
      console.log('🔍 Analyzing audio...');
      
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
      
      const result = await ApiService.analyzeAudio({
        audio_data: base64Audio,
        user_id: `demo-user-${Math.random().toString(36).substr(2, 9)}`,
        session_id: `session-${Date.now()}`
      });

      console.log('✅ Audio analysis result:', result);
      return result;
    } catch (error) {
      console.error('❌ Audio analysis failed:', error);
      
      // Check if it's a network error and provide fallback
      if (error.isNetworkError || error.message.includes('Network Error') || error.message.includes('Server error')) {
        console.log('🔄 Using mock audio analysis as fallback');
        
        // Use mock analysis as fallback
        const mockResult = ApiService.mockAudioAnalysis({
          audio_data: 'mock_audio_data',
          user_id: `demo-user-${Math.random().toString(36).substr(2, 9)}`,
          session_id: `session-${Date.now()}`
        });
        
        // Add a note that this is a fallback result
        mockResult.debug_info = {
          ...mockResult.debug_info,
          fallback_reason: error.message,
          original_error: error.message
        };
        
        return mockResult;
      }
      
      // For other errors, throw with enhanced message
      let errorMessage = 'Audio analysis failed';
      if (error.message.includes('Network Error')) {
        errorMessage = 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.message.includes('Server error')) {
        errorMessage = 'Server error occurred. The audio analysis service is temporarily unavailable.';
      } else if (error.message.includes('Access denied')) {
        errorMessage = 'Access denied. Please check your permissions.';
      } else {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  };

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      setIsAnalyzing(false);
      setLastResult(null);
      audioChunksRef.current = [];
      setRecordingTime(0);
      onProcessingChange?.(true);

      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });

      // Set up audio analysis for visualization
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      microphoneRef.current = audioContextRef.current.createMediaStreamSource(stream);
      microphoneRef.current.connect(analyserRef.current);

      // Start audio level monitoring
      const updateAudioLevel = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average);
        }
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      };
      updateAudioLevel();

      // Set up MediaRecorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        setIsRecording(false);
        setAudioLevel(0);
        
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        
        if (recordingTimerRef.current) {
          clearInterval(recordingTimerRef.current);
        }

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());

        // Analyze the recorded audio
        if (audioChunksRef.current.length > 0) {
          setIsAnalyzing(true);
          onProcessingChange?.(true);
          try {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            const result = await analyzeAudio(audioBlob);
            setLastResult(result);
            
            if (onEmotionDetected) {
              onEmotionDetected(result);
            }
          } catch (err) {
            setError('Failed to analyze audio: ' + err.message);
          } finally {
            setIsAnalyzing(false);
            onProcessingChange?.(false);
          }
        } else {
          onProcessingChange?.(false);
        }
      };

      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);
      onProcessingChange?.(false);

      // Start recording timer
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      console.log('🎙️ Voice recording started');

    } catch (err) {
      console.error('❌ Failed to start recording:', err);
      setError('Failed to start recording: ' + err.message);
      setIsRecording(false);
      onProcessingChange?.(false);
    }
  }, [onEmotionDetected, onProcessingChange]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      console.log('🛑 Voice recording stopped');
    }
  }, [isRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEmotionColor = (emotion) => {
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
      neutral: '#9CA3AF'
    };
    return colors[emotion.toLowerCase()] || '#9CA3AF';
  };

  if (!isSupported) {
    return (
      <div className="text-center p-8">
        <div className="text-red-500 text-6xl mb-4">🎤</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Voice Recording Not Supported</h3>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Recording Interface */}
      <div className="text-center">
        <div className="relative inline-block">
          {/* Audio Level Visualization */}
          <div className="w-32 h-32 rounded-full border-4 border-gray-200 flex items-center justify-center mb-4 relative">
            {isRecording && (
              <div 
                className="absolute inset-0 rounded-full bg-gradient-to-r from-green-400 to-blue-500 opacity-20 animate-pulse"
                style={{ 
                  transform: `scale(${1 + (audioLevel / 255) * 0.5})`,
                  transition: 'transform 0.1s ease-out'
                }}
              />
            )}
            
            <div className="text-4xl">
              {isRecording ? '🎙️' : '🎤'}
            </div>
            
            {isRecording && (
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full animate-pulse" />
            )}
          </div>
          
          {/* Recording Time */}
          {isRecording && (
            <div className="text-2xl font-mono font-bold text-gray-900">
              {formatTime(recordingTime)}
            </div>
          )}
        </div>

        {/* Status Messages */}
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {isAnalyzing && (
          <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg">
            <p className="text-blue-700">🔍 Analyzing audio patterns...</p>
          </div>
        )}

        {/* Controls */}
        <div className="mt-6 space-x-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={isAnalyzing}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Stop Recording
            </button>
          )}
        </div>
      </div>

      {/* Results Display */}
      {lastResult && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
          
          {/* Fallback Warning */}
          {lastResult.debug_info?.fallback_reason && (
            <div className="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
              <div className="flex items-center">
                <span className="text-yellow-800 mr-2">⚠️</span>
                <p className="text-yellow-800 text-sm">
                  <strong>Demo Mode:</strong> Using fallback analysis due to network issues. 
                  Real analysis will be available when the service is restored.
                </p>
              </div>
            </div>
          )}
          
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

            {/* All Emotions */}
            {lastResult.emotions && lastResult.emotions.length > 0 && (
              <div className="p-3 bg-white rounded-lg border">
                <span className="font-medium block mb-2">All Detected Emotions:</span>
                <div className="flex flex-wrap gap-2">
                  {lastResult.emotions.map((emotion, index) => {
                    // Handle both mock structure (Type/Confidence) and real API structure (emotion/confidence)
                    const emotionName = emotion.emotion || emotion.Type || 'unknown';
                    const emotionConfidence = emotion.confidence || emotion.Confidence || 0;
                    
                    return (
                      <span
                        key={index}
                        className="px-2 py-1 rounded text-xs text-white"
                        style={{ backgroundColor: getEmotionColor(emotionName) }}
                      >
                        {emotionName} ({Math.round(emotionConfidence * 100)}%)
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Transcript */}
            {lastResult.transcript && (
              <div className="p-3 bg-white rounded-lg border">
                <span className="font-medium block mb-2">Transcript:</span>
                <p className="text-gray-700 italic">"{lastResult.transcript}"</p>
              </div>
            )}

            {/* Sentiment */}
            {lastResult.sentiment && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
                <span className="font-medium">Sentiment:</span>
                <span className="font-semibold capitalize">{lastResult.sentiment}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceCapture; 