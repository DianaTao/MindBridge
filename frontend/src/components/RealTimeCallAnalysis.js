import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import {
  Mic,
  MicOff,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  MessageSquare,
  Users,
} from 'lucide-react';
import { sendRealTimeAudioChunk } from '../services/ApiService';

const RealTimeCallAnalysis = ({ userEmail }) => {
  // Check browser compatibility
  const isMediaRecorderSupported = typeof MediaRecorder !== 'undefined';
  const isGetUserMediaSupported = navigator.mediaDevices && navigator.mediaDevices.getUserMedia;

  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [callData, setCallData] = useState({
    duration: 0,
    callType: null,
    sentiment: 'neutral',
    sentimentScore: 0,
    emotions: [],
    keyPhrases: [],
    issues: [],
    quality: 0,
    participants: 0,
  });
  const [liveMetrics, setLiveMetrics] = useState({
    currentEmotion: 'neutral',
    emotionConfidence: 0,
    sentimentTrend: 'stable',
    callIntensity: 0,
    speakingRate: 0,
  });
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const analysisIntervalRef = useRef(null);
  const durationIntervalRef = useRef(null);

  // Use email as user identifier
  const userId = userEmail || 'anonymous';

  console.log('🔍 RealTimeCallAnalysis using user email:', userId);

  // Process audio chunk for real-time analysis
  const processAudioChunk = useCallback(
    async audioBlob => {
      try {
        console.log('🎤 Processing audio chunk for real-time analysis...');
        setIsAnalyzing(true);

        // Check audio quality
        if (audioBlob.size < 1000) {
          console.warn('🎤 Audio chunk too small, skipping analysis');
          return;
        }

        const analysis = await sendRealTimeAudioChunk(audioBlob);
        console.log('🎤 AWS Real-time Analysis Result:', analysis);

        if (!analysis) {
          console.warn('🎤 No analysis result received from AWS');
          return;
        }

        // Validate analysis results
        const isValidAnalysis =
          analysis.emotion && analysis.sentiment && analysis.emotion_confidence > 0;

        if (!isValidAnalysis) {
          console.warn('🎤 Invalid analysis results received');
          return;
        }

        // Update live metrics and call data with backend response
        setLiveMetrics({
          currentEmotion: analysis.emotion,
          emotionConfidence: analysis.emotion_confidence,
          sentimentTrend: analysis.sentiment_trend,
          callIntensity: analysis.call_intensity,
          speakingRate: analysis.speaking_rate,
        });

        setCallData(prev => ({
          ...prev,
          sentiment: analysis.sentiment,
          sentimentScore: analysis.sentiment_score,
          callType: analysis.call_type || prev.callType,
        }));

        setAnalysisHistory(prev => [
          ...prev.slice(-9),
          {
            timestamp: new Date().toISOString(),
            emotion: analysis.emotion,
            sentiment: analysis.sentiment,
            intensity: analysis.call_intensity,
            keyPhrases: analysis.key_phrases || [],
            confidence: analysis.emotion_confidence,
          },
        ]);

        console.log('🎤 Real-time analysis completed successfully');
      } catch (err) {
        console.error('❌ Live analysis failed:', err);
        // Don't show error to user for real-time analysis, just log it
      } finally {
        setIsAnalyzing(false);
      }
    },
    [isRecording]
  );

  // Initialize audio recording
  const initializeRecording = useCallback(async () => {
    try {
      console.log('🎤 Initializing high-quality audio recording...');

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100,
          channelCount: 1,
          volume: 1.0,
        },
      });

      console.log('🎤 Audio stream obtained:', stream.getAudioTracks()[0].getSettings());

      // Try different MIME types in order of preference
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus',
        'audio/wav',
      ];

      let mediaRecorder = null;
      let selectedMimeType = null;

      for (const mimeType of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mimeType)) {
          try {
            mediaRecorder = new MediaRecorder(stream, {
              mimeType,
              audioBitsPerSecond: 128000, // Higher quality
            });
            selectedMimeType = mimeType;
            console.log(`✅ Using MIME type: ${mimeType} with 128kbps`);
            break;
          } catch (e) {
            console.warn(`⚠️ Failed to create MediaRecorder with ${mimeType}:`, e);
            continue;
          }
        }
      }

      // Fallback: create MediaRecorder without specifying MIME type
      if (!mediaRecorder) {
        console.log('🔄 Using default MediaRecorder without MIME type specification');
        mediaRecorder = new MediaRecorder(stream);
        selectedMimeType = mediaRecorder.mimeType || 'audio/webm';
      }

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          console.log('🎤 Audio chunk received, size:', event.data.size, 'bytes');
          audioChunksRef.current.push(event.data);

          // Process the audio chunk for real-time analysis
          if (isRecording) {
            processAudioChunk(event.data);
          }
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: selectedMimeType });
        console.log(
          '🎤 Recording stopped, total blob size:',
          audioBlob.size,
          'MIME type:',
          selectedMimeType
        );
      };

      mediaRecorder.onerror = event => {
        console.error('🎤 MediaRecorder error:', event.error);
        setError(`Recording error: ${event.error.name}`);
      };

      mediaRecorder.onstart = () => {
        console.log('✅ MediaRecorder started successfully');
        setError(null);
      };

      return true;
    } catch (error) {
      console.error('Failed to initialize recording:', error);
      if (error.name === 'NotAllowedError') {
        setError(
          'Microphone access denied. Please allow microphone permissions and refresh the page.'
        );
      } else if (error.name === 'NotFoundError') {
        setError('No microphone found. Please connect a microphone and try again.');
      } else if (error.name === 'NotSupportedError') {
        setError(
          'MediaRecorder not supported in this browser. Please use a modern browser like Chrome, Firefox, or Safari.'
        );
      } else {
        setError(`Recording initialization failed: ${error.message}`);
      }
      return false;
    }
  }, [isRecording, processAudioChunk]);

  // Perform real-time analysis using AWS audio analysis
  const performRealTimeAnalysis = useCallback(async () => {
    try {
      console.log('🎤 Performing real-time audio analysis...');
      console.log('🎤 Available audio chunks:', audioChunksRef.current.length);

      // Get the latest audio chunk for analysis
      if (audioChunksRef.current.length === 0) {
        console.log('🎤 No audio chunks available for analysis - waiting for audio data');
        return;
      }

      // Use the most recent audio chunk
      const latestAudioChunk = audioChunksRef.current[audioChunksRef.current.length - 1];
      console.log('🎤 Analyzing audio chunk, size:', latestAudioChunk.size, 'bytes');

      // Check if audio chunk is large enough for meaningful analysis
      if (latestAudioChunk.size < 1000) {
        console.log('🎤 Audio chunk too small, waiting for more audio data');
        return;
      }

      // Send to AWS for real analysis
      const analysis = await sendRealTimeAudioChunk(latestAudioChunk);
      console.log('🎤 AWS Audio Analysis Result:', analysis);

      if (!analysis) {
        console.warn('🎤 No analysis result received from AWS');
        return;
      }

      // Validate analysis results
      const isValidAnalysis =
        analysis.emotion && analysis.sentiment && analysis.emotion_confidence > 0;

      if (!isValidAnalysis) {
        console.warn('🎤 Invalid analysis results received');
        return;
      }

      // Update live metrics with real AWS data
      setLiveMetrics({
        currentEmotion: analysis.emotion || 'neutral',
        emotionConfidence: analysis.emotion_confidence || 0,
        sentimentTrend: analysis.sentiment_trend || 'stable',
        callIntensity: analysis.call_intensity || 0,
        speakingRate: analysis.speaking_rate || 0,
      });

      // Update call data with real sentiment analysis
      setCallData(prev => ({
        ...prev,
        sentiment: analysis.sentiment || 'neutral',
        sentimentScore: analysis.sentiment_score || 0,
        callType: analysis.call_type || prev.callType,
      }));

      // Add real analysis to history
      setAnalysisHistory(prev => [
        ...prev.slice(-9),
        {
          timestamp: new Date().toISOString(),
          emotion: analysis.emotion || 'neutral',
          sentiment: analysis.sentiment || 'neutral',
          intensity: analysis.call_intensity || 0,
          keyPhrases: analysis.key_phrases || [],
          confidence: analysis.emotion_confidence,
        },
      ]);

      console.log('🎤 Real-time analysis completed successfully');
    } catch (error) {
      console.error('❌ Real-time analysis failed:', error);
      // Don't show error to user for real-time analysis, just log it
    }
  }, []);

  // Detect call type based on real analysis data
  const detectCallType = useCallback(() => {
    // Use analysis history to determine call type
    if (analysisHistory.length === 0) {
      // Default to general if no analysis data yet
      setCallData(prev => ({
        ...prev,
        callType: 'general',
      }));
      return;
    }

    // Analyze recent history to determine call type
    const recentAnalyses = analysisHistory.slice(-3); // Last 3 analyses
    const keyPhrases = recentAnalyses
      .filter(entry => entry.keyPhrases && entry.keyPhrases.length > 0)
      .flatMap(entry => entry.keyPhrases)
      .join(' ')
      .toLowerCase();

    // Determine call type based on key phrases and sentiment patterns
    let callType = 'general';

    if (
      keyPhrases.includes('customer') ||
      keyPhrases.includes('support') ||
      keyPhrases.includes('help')
    ) {
      callType = 'customer_support';
    } else if (
      keyPhrases.includes('sale') ||
      keyPhrases.includes('buy') ||
      keyPhrases.includes('purchase')
    ) {
      callType = 'sales';
    } else if (
      keyPhrases.includes('technical') ||
      keyPhrases.includes('bug') ||
      keyPhrases.includes('error')
    ) {
      callType = 'technical';
    }

    // Also consider sentiment patterns
    const negativeCount = recentAnalyses.filter(entry => entry.sentiment === 'negative').length;
    if (negativeCount > recentAnalyses.length * 0.6) {
      // High negative sentiment might indicate customer support
      if (callType === 'general') {
        callType = 'customer_support';
      }
    }

    setCallData(prev => ({
      ...prev,
      callType: callType,
    }));

    console.log('🎤 Detected call type:', callType, 'based on analysis history');
  }, [analysisHistory]);

  // Start call analysis
  const startCallAnalysis = useCallback(async () => {
    try {
      console.log('🎤 Starting call analysis...');
      setIsRecording(true);
      setIsAnalyzing(true);
      setError(null);
      setAnalysisHistory([]);
      setCallData({
        duration: 0,
        callType: 'general',
        quality: 0,
        emotions: [],
        keyPhrases: [],
        issues: [],
        participants: 1,
      });
      setLiveMetrics({
        callIntensity: 0,
        sentimentTrend: 'neutral',
        emotionStability: 0,
      });

      // Initialize recording first
      console.log('🎤 Initializing recording...');
      await initializeRecording();

      // Start the MediaRecorder
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.start(5000); // Capture chunks every 5 seconds
        console.log('🎤 MediaRecorder started with 5-second chunks');
      }

      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setCallData(prev => ({
          ...prev,
          duration: prev.duration + 1,
        }));
      }, 1000);

      // Start periodic analysis after a delay to allow first audio chunk
      setTimeout(() => {
        analysisIntervalRef.current = setInterval(() => {
          performRealTimeAnalysis();
        }, 6000); // Analyze every 6 seconds (after chunk is captured)
        console.log('🎤 Analysis interval started (6-second intervals)');
      }, 3000); // Wait 3 seconds for first audio chunk

      // Initial call type detection
      setTimeout(() => {
        detectCallType();
      }, 5000);

      console.log('🎤 Call analysis started successfully');
    } catch (error) {
      console.error('❌ Error starting call analysis:', error);
      setError(`Failed to start call analysis: ${error.message}`);
      setIsRecording(false);
      setIsAnalyzing(false);
    }
  }, [initializeRecording, performRealTimeAnalysis, detectCallType]);

  // Calculate standard deviation
  const calculateStandardDeviation = values => {
    if (values.length < 2) return 0;

    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length;

    return Math.sqrt(variance);
  };

  // Perform final analysis when call ends
  const performFinalAnalysis = useCallback(() => {
    if (analysisHistory.length === 0) {
      console.log('🎤 No analysis history available for final analysis');
      return;
    }

    console.log('🎤 Performing final call analysis...');

    // Calculate sentiment scores from history
    const sentimentScores = analysisHistory
      .map(entry => {
        // Map sentiment to numeric score
        switch (entry.sentiment) {
          case 'positive':
            return 0.8;
          case 'negative':
            return 0.2;
          default:
            return 0.5;
        }
      })
      .filter(score => score !== null);

    // Calculate emotion distribution
    const emotionCounts = {};
    analysisHistory.forEach(entry => {
      const emotion = entry.emotion || 'neutral';
      emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    });

    const totalEntries = analysisHistory.length;
    const emotions = Object.entries(emotionCounts)
      .map(([emotion, count]) => ({
        emotion,
        score: Math.round((count / totalEntries) * 100),
      }))
      .sort((a, b) => b.score - a.score);

    // Calculate overall quality based on sentiment trend and consistency
    const avgSentiment =
      sentimentScores.length > 0
        ? sentimentScores.reduce((sum, score) => sum + score, 0) / sentimentScores.length
        : 0.5;

    const sentimentConsistency =
      sentimentScores.length > 1 ? 1 - (calculateStandardDeviation(sentimentScores) || 0) : 0.8;

    const quality = Math.round((avgSentiment * 0.6 + sentimentConsistency * 0.4) * 100);

    // Extract key phrases from recent analyses (if available)
    const recentAnalyses = analysisHistory.slice(-5); // Last 5 analyses
    const phrases = recentAnalyses
      .filter(entry => entry.keyPhrases && entry.keyPhrases.length > 0)
      .flatMap(entry => entry.keyPhrases)
      .slice(0, 5); // Top 5 phrases

    // Identify potential issues based on negative sentiment patterns
    const issues = [];
    const negativeCount = sentimentScores.filter(score => score < 0.3).length;
    const totalCount = sentimentScores.length;

    if (negativeCount > totalCount * 0.3) {
      issues.push('frequent negative sentiment');
    }

    if (callData.duration > 300) {
      // 5 minutes
      issues.push('long call duration');
    }

    if (liveMetrics.callIntensity > 80) {
      issues.push('high call intensity');
    }

    // Estimate participants based on call type and duration
    const participants = callData.callType === 'customer_support' ? 2 : 1;

    setCallData(prev => ({
      ...prev,
      quality: Math.max(quality, 20), // Minimum 20% quality
      emotions: emotions.length > 0 ? emotions : [{ emotion: 'neutral', score: 50 }],
      keyPhrases: phrases,
      issues: issues,
      participants: participants,
    }));
  }, [analysisHistory, callData.duration, callData.callType, liveMetrics.callIntensity]);

  // Stop call analysis
  const stopCallAnalysis = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }

    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
    }

    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }

    setIsRecording(false);
    setIsAnalyzing(false);

    // Final analysis
    performFinalAnalysis();
  }, [isRecording, performFinalAnalysis]);

  // Format duration
  const formatDuration = seconds => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get call type icon
  const getCallTypeIcon = type => {
    switch (type) {
      case 'customer_support':
        return <Users className="w-4 h-4" />;
      case 'sales':
        return <TrendingUp className="w-4 h-4" />;
      case 'technical':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <MessageSquare className="w-4 h-4" />;
    }
  };

  // Get sentiment color
  const getSentimentColor = sentiment => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get emotion color
  const getEmotionColor = emotion => {
    const colors = {
      happy: 'bg-yellow-100 text-yellow-800',
      excited: 'bg-orange-100 text-orange-800',
      calm: 'bg-blue-100 text-blue-800',
      frustrated: 'bg-red-100 text-red-800',
      neutral: 'bg-gray-100 text-gray-800',
    };
    return colors[emotion] || colors.neutral;
  };

  useEffect(() => {
    return () => {
      if (analysisIntervalRef.current) {
        clearInterval(analysisIntervalRef.current);
      }
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stream?.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Show compatibility error if browser doesn't support required APIs
  if (!isMediaRecorderSupported || !isGetUserMediaSupported) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Real-Time Call Analysis</h2>
            <p className="text-gray-600">Live recording and sentiment analysis during calls</p>
          </div>
        </div>

        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-700">
              <XCircle className="w-5 h-5" />
              <div>
                <p className="font-semibold">Browser Not Supported</p>
                <p className="text-sm">
                  Your browser doesn&apos;t support the required APIs for real-time audio recording.
                  Please use a modern browser like Chrome, Firefox, or Safari.
                </p>
                {!isMediaRecorderSupported && (
                  <p className="text-xs mt-1">• MediaRecorder API not supported</p>
                )}
                {!isGetUserMediaSupported && (
                  <p className="text-xs mt-1">• getUserMedia API not supported</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Real-Time Call Analysis</h2>
          <p className="text-gray-600">Live recording and sentiment analysis during calls</p>
        </div>
        <div className="flex items-center space-x-4">
          {callData.callType && (
            <Badge className="flex items-center space-x-1">
              {getCallTypeIcon(callData.callType)}
              <span className="capitalize">{callData.callType.replace('_', ' ')}</span>
            </Badge>
          )}
          <Badge className={getSentimentColor(callData.sentiment)}>
            {callData.sentiment} sentiment
          </Badge>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-700">
              <XCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Control Panel */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-gray-500" />
                <span className="text-lg font-mono">{formatDuration(callData.duration)}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity
                  className={`w-4 h-4 ${isRecording ? 'text-red-500 animate-pulse' : 'text-gray-400'}`}
                />
                <span className={isRecording ? 'text-red-500' : 'text-gray-500'}>
                  {isRecording ? 'Recording' : 'Idle'}
                </span>
              </div>
            </div>

            <div className="flex space-x-3">
              {!isRecording ? (
                <Button
                  onClick={startCallAnalysis}
                  className="bg-green-600 hover:bg-green-700"
                  disabled={isAnalyzing}
                >
                  <Mic className="w-4 h-4 mr-2" />
                  Start Call Analysis
                </Button>
              ) : (
                <Button onClick={stopCallAnalysis} variant="destructive" disabled={!isRecording}>
                  <MicOff className="w-4 h-4 mr-2" />
                  End Call
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Live Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Analysis Status Note */}
        <div className="col-span-full mb-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm font-medium text-blue-800">Real AWS Analysis Active</p>
                <p className="text-xs text-blue-600">
                  Using AWS Transcribe & Comprehend for live sentiment analysis. Speak clearly for
                  best accuracy.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Fallback Analysis Note - shown when AWS is not available */}
        {analysisHistory.length > 0 &&
          analysisHistory[analysisHistory.length - 1]?.debug_info?.analysis_method ===
            'fallback_frontend' && (
            <div className="col-span-full mb-4">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-orange-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-orange-800">Fallback Analysis Mode</p>
                    <p className="text-xs text-orange-600">
                      AWS services temporarily unavailable. Using local analysis for demonstration.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Current Emotion</p>
                <p className="text-2xl font-bold">{liveMetrics.currentEmotion}</p>
                {isAnalyzing && (
                  <div className="flex items-center mt-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2"></div>
                    <span className="text-xs text-blue-600">Analyzing...</span>
                  </div>
                )}
                {isRecording && !isAnalyzing && audioChunksRef.current.length === 0 && (
                  <div className="flex items-center mt-1">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-2"></div>
                    <span className="text-xs text-orange-600">Waiting for audio...</span>
                  </div>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Confidence</p>
                <p className="text-lg font-semibold">
                  {Math.round(liveMetrics.emotionConfidence * 100)}%
                </p>
                {liveMetrics.emotionConfidence > 0.8 && (
                  <span className="text-xs text-green-600">High Accuracy</span>
                )}
                {liveMetrics.emotionConfidence < 0.5 && liveMetrics.emotionConfidence > 0 && (
                  <span className="text-xs text-orange-600">Low Confidence</span>
                )}
                {liveMetrics.emotionConfidence === 0 && (
                  <span className="text-xs text-gray-500">No data yet</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sentiment Trend</p>
                <p className="text-2xl font-bold capitalize">{liveMetrics.sentimentTrend}</p>
              </div>
              <div className="text-right">
                {liveMetrics.sentimentTrend === 'improving' ? (
                  <TrendingUp className="w-6 h-6 text-green-500" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-red-500" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Call Intensity</p>
              <p className="text-2xl font-bold">{Math.round(liveMetrics.callIntensity)}%</p>
              <Progress value={liveMetrics.callIntensity} className="mt-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Speaking Rate</p>
              <p className="text-2xl font-bold">{Math.round(liveMetrics.speakingRate)} wpm</p>
              <p className="text-xs text-gray-500 mt-1">words per minute</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis History */}
      <Card>
        <CardHeader>
          <CardTitle>Live Analysis History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analysisHistory.map((entry, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <Badge className={getEmotionColor(entry.emotion)}>{entry.emotion}</Badge>
                  <Badge className={getSentimentColor(entry.sentiment)}>{entry.sentiment}</Badge>
                  <span className="text-sm text-gray-600">
                    Intensity: {Math.round(entry.intensity)}%
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
            {analysisHistory.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Activity className="w-8 h-8 mx-auto mb-2" />
                <p>Start recording to see live analysis</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Call Summary (shown after call ends) */}
      {!isRecording && callData.quality > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Call Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Call Quality</h4>
                <div className="flex items-center space-x-3">
                  <Progress value={callData.quality} className="flex-1" />
                  <span className="font-bold">{callData.quality}%</span>
                </div>
                <div className="mt-3">
                  <p className="text-sm text-gray-600">Participants: {callData.participants}</p>
                  <p className="text-sm text-gray-600">
                    Duration: {formatDuration(callData.duration)}
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-3">Key Emotions</h4>
                <div className="space-y-2">
                  {callData.emotions.map((emotion, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="capitalize">{emotion.emotion}</span>
                      <span className="font-semibold">{Math.round(emotion.score)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {callData.keyPhrases.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold mb-3">Key Phrases</h4>
                <div className="flex flex-wrap gap-2">
                  {callData.keyPhrases.map((phrase, index) => (
                    <Badge key={index} variant="outline">
                      {phrase}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {callData.issues.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold mb-3">Issues Identified</h4>
                <div className="space-y-2">
                  {callData.issues.map((issue, index) => (
                    <div key={index} className="flex items-center space-x-2 text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span>{issue}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RealTimeCallAnalysis;
