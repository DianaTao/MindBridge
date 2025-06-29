import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import ApiService, { ApiService as ApiServiceClass } from '../services/ApiService';
import {
  Camera,
  CameraOff,
  Heart,
  Brain,
  Smile,
  Frown,
  Activity,
  Calendar,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  LineChart,
  Users,
  Shield,
  Zap,
  RefreshCw,
  Play,
  Pause,
  Save
} from 'lucide-react';

const MentalHealthCheckin = ({ userEmail }) => {
  // Camera and video states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [hasPermission, setHasPermission] = useState(null);
  
  // Check-in states
  const [checkinData, setCheckinData] = useState({
    sessionId: null,
    startTime: null,
    duration: 0,
    currentMood: 'neutral',
    moodHistory: [],
    emotionScores: {
      happy: 0,
      sad: 0,
      angry: 0,
      surprised: 0,
      fear: 0,
      disgusted: 0,
      calm: 0
    },
    averageWellbeing: 50,
    stressLevel: 'low',
    recommendations: [],
    insights: []
  });
  
  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const analysisIntervalRef = useRef(null);
  const durationIntervalRef = useRef(null);
  
  // Self-assessment states
  const [selfAssessment, setSelfAssessment] = useState({
    overallMood: 5,
    energyLevel: 5,
    stressLevel: 5,
    sleepQuality: 5,
    socialConnection: 5,
    motivation: 5,
    notes: ''
  });
  
  const [checkinHistory, setCheckinHistory] = useState([]);
  const [showSelfAssessment, setShowSelfAssessment] = useState(false);
  const [checkinComplete, setCheckinComplete] = useState(false);

  // Use email as user identifier
  const userId = userEmail || 'anonymous';
  
  console.log('🔍 MentalHealthCheckin using user email:', userId);

  // Initialize camera
  const initializeCamera = useCallback(async () => {
    try {
      console.log('📷 Initializing camera for mental health check-in...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 480 },
          facingMode: 'user',
          frameRate: { ideal: 30, min: 15 }
        } 
      });
      
      console.log('📷 Camera stream obtained:', stream.getVideoTracks()[0].getSettings());
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
          videoRef.current.onloadedmetadata = () => {
            console.log('📷 Video metadata loaded:', {
              videoWidth: videoRef.current.videoWidth,
              videoHeight: videoRef.current.videoHeight
            });
            resolve();
          };
        });
      }
      
      setHasPermission(true);
      setError(null);
      console.log('📷 Camera initialization successful');
    } catch (err) {
      console.error('📷 Camera access error:', err);
      setHasPermission(false);
      setError('Camera access denied. Please allow camera permissions for emotion analysis.');
    }
  }, []);

  // Update emotion data
  const updateEmotionData = useCallback((emotionResult) => {
    console.log('🧠 Mental Health: Processing emotion result:', emotionResult);
    
    const timestamp = new Date();
    
    // Handle AWS Rekognition response format
    let emotions = [];
    
    // Try multiple possible response formats
    if (emotionResult.emotions && emotionResult.emotions.length > 0) {
      // Format 1: Processed emotions from Lambda (array of face data)
      const firstFace = emotionResult.emotions[0];
      if (firstFace.emotions && Array.isArray(firstFace.emotions)) {
        emotions = firstFace.emotions.map(emotion => ({
          name: emotion.Type.toLowerCase(),
          confidence: emotion.Confidence / 100, // Convert percentage to decimal
          type: emotion.Type
        }));
        console.log('🧠 Using processed face emotions from AWS Lambda');
      } else if (Array.isArray(firstFace)) {
        // Format 2: Direct emotions array
        emotions = firstFace.map(emotion => ({
          name: emotion.Type.toLowerCase(),
          confidence: emotion.Confidence / 100,
          type: emotion.Type
        }));
        console.log('🧠 Using direct emotions array from AWS');
      }
    } else if (emotionResult.primary_emotion) {
      // Format 3: Primary emotion from top-level response
      emotions = [{
        name: emotionResult.primary_emotion.toLowerCase(),
        confidence: (emotionResult.confidence || 50) / 100,
        type: emotionResult.primary_emotion
      }];
      console.log('🧠 Using primary emotion from AWS response');
    } else if (emotionResult.faces_detected === 0) {
      // No faces detected - provide helpful feedback
      console.warn('🧠 No faces detected in the image');
      
      // Update with a gentle message instead of neutral
      setCheckinData(prev => ({
        ...prev,
        currentMood: 'no_face_detected',
        moodHistory: [...prev.moodHistory, {
          timestamp,
          emotion: 'no_face_detected',
          confidence: 0,
          allEmotions: [],
          message: 'Please ensure your face is clearly visible in the camera'
        }].slice(-20)
      }));
      return;
    } else {
      console.warn('🧠 No emotion data found in AWS response:', emotionResult);
      return; // Don't update if no emotion data
    }
    
    console.log('🧠 Mental Health: Processed emotions:', emotions);
    
    if (emotions.length === 0) {
      console.warn('🧠 No emotions processed, skipping update');
      return;
    }
    
    // Find dominant emotion
    const dominantEmotion = emotions.reduce((prev, current) => 
      (prev.confidence > current.confidence) ? prev : current
    );

    console.log('🧠 Dominant emotion:', dominantEmotion);

    setCheckinData(prev => {
      const newMoodHistory = [...prev.moodHistory, {
        timestamp,
        emotion: dominantEmotion.name,
        confidence: dominantEmotion.confidence,
        allEmotions: emotions
      }].slice(-20); // Keep last 20 entries

      // Calculate emotion scores - map AWS emotions to our emotion categories
      const newEmotionScores = { ...prev.emotionScores };
      
      // Reset all scores first
      Object.keys(newEmotionScores).forEach(key => {
        newEmotionScores[key] = 0;
      });
      
      // Map AWS emotions to our categories and accumulate scores
      emotions.forEach(emotion => {
        const emotionName = emotion.name.toLowerCase();
        const confidence = Math.round(emotion.confidence * 100);
        
        console.log(`🧠 Processing emotion: ${emotionName} = ${confidence}%`);
        
        // Map AWS emotion names to our emotion categories
        if (emotionName === 'happy') {
          newEmotionScores.happy = Math.max(newEmotionScores.happy, confidence);
        } else if (emotionName === 'sad') {
          newEmotionScores.sad = Math.max(newEmotionScores.sad, confidence);
        } else if (emotionName === 'angry') {
          newEmotionScores.angry = Math.max(newEmotionScores.angry, confidence);
        } else if (emotionName === 'surprised') {
          newEmotionScores.surprised = Math.max(newEmotionScores.surprised, confidence);
        } else if (emotionName === 'fear') {
          newEmotionScores.fear = Math.max(newEmotionScores.fear, confidence);
        } else if (emotionName === 'disgusted') {
          newEmotionScores.disgusted = Math.max(newEmotionScores.disgusted, confidence);
        } else if (emotionName === 'calm') {
          newEmotionScores.calm = Math.max(newEmotionScores.calm, confidence);
        } else if (emotionName === 'confused') {
          // Map confused to a mix of surprised and fear
          newEmotionScores.surprised = Math.max(newEmotionScores.surprised, confidence / 2);
          newEmotionScores.fear = Math.max(newEmotionScores.fear, confidence / 2);
        } else {
          // Handle unknown emotions by mapping to neutral/calm
          console.log(`🧠 Unknown emotion: ${emotionName}, mapping to calm`);
          newEmotionScores.calm = Math.max(newEmotionScores.calm, confidence);
        }
      });
      
      console.log('🧠 Mental Health: Updated emotion scores:', newEmotionScores);

      // Calculate wellbeing score
      const positiveEmotions = ['happy', 'calm', 'surprised'];
      const negativeEmotions = ['sad', 'angry', 'fear', 'disgusted'];
      
      const positiveScore = positiveEmotions.reduce((sum, emotion) => 
        sum + (newEmotionScores[emotion] || 0), 0);
      const negativeScore = negativeEmotions.reduce((sum, emotion) => 
        sum + (newEmotionScores[emotion] || 0), 0);
      
      const averageWellbeing = Math.max(10, Math.min(90, 
        50 + (positiveScore - negativeScore) / 2
      ));

      // Determine stress level
      const stressIndicators = newEmotionScores.angry + newEmotionScores.fear + newEmotionScores.disgusted;
      const stressLevel = stressIndicators > 60 ? 'high' : 
                         stressIndicators > 30 ? 'medium' : 'low';

      console.log('🧠 Final wellbeing score:', averageWellbeing, 'Stress level:', stressLevel);

      return {
        ...prev,
        currentMood: dominantEmotion.name,
        moodHistory: newMoodHistory,
        emotionScores: newEmotionScores,
        averageWellbeing,
        stressLevel
      };
    });
  }, []);

  // Utility function to convert blob to base64
  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onload = () => {
        const result = reader.result;
        // Remove the data URL prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  // Capture and analyze frame
  const captureAndAnalyzeFrame = useCallback(async () => {
    console.log('🧠 captureAndAnalyzeFrame called with state:', {
      hasVideo: !!videoRef.current,
      hasCanvas: !!canvasRef.current,
      isAnalyzing,
      isCameraActive
    });
    
    // Check current state instead of relying on closure
    if (!videoRef.current || !canvasRef.current) {
      console.log('🧠 Frame capture skipped: missing video or canvas');
      return;
    }

    try {
      console.log('🧠 Starting frame capture and analysis...');
      
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Set canvas dimensions
      canvas.width = videoRef.current.videoWidth || 640;
      canvas.height = videoRef.current.videoHeight || 480;
      
      console.log('🧠 Canvas dimensions:', canvas.width, 'x', canvas.height);
      
      // Draw current frame
      context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      
      // Convert to blob
      const blob = await new Promise((resolve, reject) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.8);
      });
      
      if (!blob) {
        console.error('🧠 Failed to create blob from canvas');
        return;
      }
      
      console.log('🧠 Blob created, size:', blob.size, 'bytes');
      
      try {
        console.log('🎭 Analyzing facial emotions for mental health check-in...');
        
        // Convert blob to base64
        const frameData = await blobToBase64(blob);
        
        // Create proper request object
        const request = {
          frame_data: frameData,
          user_id: userId,
          session_id: checkinData.sessionId || `checkin_${Date.now()}`,
          timestamp: new Date().toISOString()
        };
        
        const result = await ApiService.analyzeVideo(request);
        console.log('🎭 AWS Video Analysis Result:', result);
        
        if (result) {
          updateEmotionData(result);
        } else {
          console.warn('⚠️ No emotion data received from AWS');
        }
      } catch (error) {
        console.error('❌ Emotion analysis error:', error);
      }
    } catch (error) {
      console.error('❌ Frame capture error:', error);
    }
  }, [updateEmotionData, isAnalyzing, isCameraActive, userId]);

  // Start mental health check-in
  const startCheckin = useCallback(async () => {
    if (isAnalyzing) {
      console.log('🧠 Check-in already in progress');
      return;
    }

    try {
      console.log('🧠 Starting mental health check-in...');
      setIsAnalyzing(true);
      setError(null);
      setIsCameraActive(true);
      
      // Small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Initialize session
      const sessionId = `checkin_${Date.now()}`;
      const startTime = new Date();
      
      setCheckinData(prev => ({
        ...prev,
        sessionId,
        startTime,
        duration: 0
      }));
      
      console.log('🧠 Session initialized:', { sessionId, startTime });
      
      // Initialize camera if not already active
      if (!isCameraActive) {
        await initializeCamera();
      }
      
      // Wait for camera to be ready
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setCheckinData(prev => ({
          ...prev,
          duration: prev.duration + 1
        }));
      }, 1000);
      
      // Start emotion analysis
      analysisIntervalRef.current = setInterval(() => {
        captureAndAnalyzeFrame();
      }, 3000); // Analyze every 3 seconds
      
      // Also do an immediate analysis to get started
      setTimeout(() => {
        captureAndAnalyzeFrame();
      }, 2000); // Increased delay to ensure everything is ready
      
      console.log('🧠 Mental health check-in started successfully');
      
    } catch (error) {
      console.error('❌ Error starting check-in:', error);
      setError(`Failed to start check-in: ${error.message}`);
      setIsAnalyzing(false);
      setIsCameraActive(false);
    }
  }, [initializeCamera, captureAndAnalyzeFrame, isAnalyzing, isCameraActive, userId]);

  // Stop check-in
  const stopCheckin = useCallback(() => {
    // Stop intervals
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
    }
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
    
    // Stop camera
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    setIsCameraActive(false);
    setIsAnalyzing(false);
    
    // Generate insights and recommendations
    generateInsights();
    
    // Show self-assessment
    setShowSelfAssessment(true);
    
    console.log('🧠 Mental health check-in completed');
  }, []);

  // Generate insights and recommendations
  const generateInsights = useCallback(() => {
    setCheckinData(prev => {
      const insights = [];
      const recommendations = [];
      
      // Analyze mood patterns
      if (prev.averageWellbeing >= 70) {
        insights.push('Your emotional state appears positive and stable.');
        recommendations.push('Continue with your current wellness routine.');
      } else if (prev.averageWellbeing >= 50) {
        insights.push('Your emotional state shows some fluctuation.');
        recommendations.push('Consider mindfulness exercises or brief walks.');
      } else {
        insights.push('Your emotional state suggests you may need some self-care.');
        recommendations.push('Take time for relaxation and consider talking to someone.');
      }
      
      // Stress level insights
      if (prev.stressLevel === 'high') {
        insights.push('Elevated stress indicators detected.');
        recommendations.push('Try deep breathing exercises or meditation.');
      } else if (prev.stressLevel === 'medium') {
        insights.push('Moderate stress levels observed.');
        recommendations.push('Take short breaks and practice stress management.');
      }
      
      // Duration insights
      if (prev.duration >= 180) { // 3 minutes
        insights.push('Good session length for comprehensive analysis.');
      } else {
        insights.push('Consider longer sessions for better insights.');
      }
      
      return {
        ...prev,
        insights,
        recommendations
      };
    });
  }, []);

  // Complete check-in with self-assessment
  const completeCheckin = useCallback(async () => {
    try {
      console.log('🧠 Completing mental health check-in...');
      
      // Prepare check-in data for submission
      const checkinSubmission = {
        checkin_id: `checkin_${Date.now()}`,
        user_id: userId,
        session_id: checkinData.sessionId,
        duration: checkinData.duration,
        emotion_analysis: {
          dominant_emotion: checkinData.currentMood,
          emotion_scores: checkinData.emotionScores,
          average_wellbeing: checkinData.averageWellbeing,
          stress_level: checkinData.stressLevel,
          mood_history: checkinData.moodHistory.slice(-5), // Last 5 entries
          insights: checkinData.insights
        },
        self_assessment: {
          overall_mood: selfAssessment.overallMood,
          energy_level: selfAssessment.energyLevel,
          stress_level: selfAssessment.stressLevel,
          sleep_quality: selfAssessment.sleepQuality,
          social_connection: selfAssessment.socialConnection,
          motivation: selfAssessment.motivation,
          notes: selfAssessment.notes
        }
      };
      
      console.log('📤 Submitting check-in data:', checkinSubmission);
      
      // Submit to database
      const result = await ApiService.submitCheckin(checkinSubmission);
      
      console.log('✅ Check-in submitted successfully:', result);
      
      // Create local record for history
      const checkinRecord = {
        id: checkinData.sessionId,
        date: checkinData.startTime,
        duration: checkinData.duration,
        emotionAnalysis: checkinData,
        selfAssessment: selfAssessment,
        overallScore: Math.round((checkinData.averageWellbeing + selfAssessment.overallMood * 10) / 2),
        recommendations: checkinData.recommendations,
        llmReport: result.llm_report // Include LLM report
      };
      
      setCheckinHistory(prev => [checkinRecord, ...prev].slice(0, 10)); // Keep last 10
      setCheckinComplete(true);
      setShowSelfAssessment(false);
      
      // Reset for next session
      setTimeout(() => {
        setCheckinComplete(false);
        setCheckinData({
          sessionId: null,
          startTime: null,
          duration: 0,
          currentMood: 'neutral',
          moodHistory: [],
          emotionScores: {
            happy: 0, sad: 0, angry: 0, surprised: 0, fear: 0, disgusted: 0, calm: 0
          },
          averageWellbeing: 50,
          stressLevel: 'low',
          recommendations: [],
          insights: []
        });
        setSelfAssessment({
          overallMood: 5, energyLevel: 5, stressLevel: 5,
          sleepQuality: 5, socialConnection: 5, motivation: 5, notes: ''
        });
      }, 3000);
      
    } catch (error) {
      console.error('❌ Failed to submit check-in:', error);
      setError('Failed to save check-in data. Please try again.');
      
      // Still complete locally even if submission fails
      const checkinRecord = {
        id: checkinData.sessionId,
        date: checkinData.startTime,
        duration: checkinData.duration,
        emotionAnalysis: checkinData,
        selfAssessment: selfAssessment,
        overallScore: Math.round((checkinData.averageWellbeing + selfAssessment.overallMood * 10) / 2),
        recommendations: checkinData.recommendations
      };
      
      setCheckinHistory(prev => [checkinRecord, ...prev].slice(0, 10));
      setCheckinComplete(true);
      setShowSelfAssessment(false);
    }
  }, [checkinData, selfAssessment, userId]);

  // Format duration
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get emotion color
  const getEmotionColor = (emotion) => {
    const colors = {
      happy: 'bg-yellow-100 text-yellow-800',
      calm: 'bg-blue-100 text-blue-800',
      sad: 'bg-indigo-100 text-indigo-800',
      angry: 'bg-red-100 text-red-800',
      fear: 'bg-purple-100 text-purple-800',
      surprised: 'bg-orange-100 text-orange-800',
      disgusted: 'bg-gray-100 text-gray-800',
      neutral: 'bg-green-100 text-green-800'
    };
    return colors[emotion] || colors.neutral;
  };

  // Get wellbeing color
  const getWellbeingColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (analysisIntervalRef.current) clearInterval(analysisIntervalRef.current);
      if (durationIntervalRef.current) clearInterval(durationIntervalRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Heart className="w-8 h-8 mr-3 text-red-500" />
            Mental Health Check-in
          </h2>
          <p className="text-gray-600">AI-powered emotional wellness monitoring and self-assessment</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={`px-3 py-1 ${getWellbeingColor(checkinData.averageWellbeing)}`}>
            {checkinData.averageWellbeing}% Wellbeing
          </Badge>
          <Badge className={`px-3 py-1 ${checkinData.stressLevel === 'high' ? 'bg-red-100 text-red-800' : checkinData.stressLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
            {checkinData.stressLevel} Stress
          </Badge>
        </div>
      </div>

      {/* Camera Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Camera className="w-5 h-5 mr-2" />
            Real-time Emotion Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Camera Feed */}
          <div className="relative bg-gray-100 rounded-lg overflow-hidden">
            {isCameraActive ? (
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-64 object-cover"
                />
                <canvas
                  ref={canvasRef}
                  className="hidden"
                />
                {isAnalyzing && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="text-white text-center">
                      <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
                      <p>Analyzing emotions...</p>
                    </div>
                  </div>
                )}
                {checkinData.currentMood === 'no_face_detected' && (
                  <div className="absolute inset-0 bg-orange-500 bg-opacity-20 flex items-center justify-center">
                    <div className="text-orange-800 text-center bg-white bg-opacity-90 px-4 py-2 rounded-lg">
                      <AlertTriangle className="w-6 h-6 mx-auto mb-1" />
                      <p className="text-sm font-medium">Please position your face in the camera</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <CameraOff className="w-12 h-12 mx-auto mb-2" />
                  <p>Camera inactive</p>
                </div>
              </div>
            )}
          </div>

          {/* Camera Controls */}
          <div className="flex items-center justify-center space-x-4">
            {!isCameraActive ? (
              <Button onClick={startCheckin} className="flex items-center">
                <Play className="w-4 h-4 mr-2" />
                Start Check-in
              </Button>
            ) : (
              <Button onClick={stopCheckin} variant="destructive" className="flex items-center">
                <Pause className="w-4 h-4 mr-2" />
                Stop Check-in
              </Button>
            )}
          </div>

          {/* Session Info */}
          {isCameraActive && (
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {formatDuration(checkinData.duration)}
              </div>
              <div className="flex items-center">
                <Brain className="w-4 h-4 mr-1" />
                {checkinData.currentMood === 'no_face_detected' ? (
                  <span className="text-orange-600">No face detected</span>
                ) : (
                  checkinData.currentMood
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Emotion Analysis Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Emotion Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(checkinData.emotionScores).map(([emotion, score]) => (
              <div key={emotion} className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getEmotionColor(emotion)}`}>
                  {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                </div>
                <div className="mt-2">
                  <Progress value={score} className="h-2" />
                  <p className="text-xs text-gray-600 mt-1">{score}%</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Self Assessment */}
      {showSelfAssessment && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="w-5 h-5 mr-2" />
              Self Assessment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'overallMood', label: 'Overall Mood', icon: Smile },
                { key: 'energyLevel', label: 'Energy Level', icon: Zap },
                { key: 'stressLevel', label: 'Stress Level', icon: AlertTriangle },
                { key: 'sleepQuality', label: 'Sleep Quality', icon: Shield },
                { key: 'socialConnection', label: 'Social Connection', icon: Users },
                { key: 'motivation', label: 'Motivation', icon: TrendingUp }
              ].map(({ key, label, icon: Icon }) => (
                <div key={key} className="space-y-2">
                  <label className="flex items-center text-sm font-medium text-gray-700">
                    <Icon className="w-4 h-4 mr-2" />
                    {label}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={selfAssessment[key]}
                    onChange={(e) => setSelfAssessment(prev => ({
                      ...prev,
                      [key]: parseInt(e.target.value)
                    }))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>1</span>
                    <span>{selfAssessment[key]}</span>
                    <span>10</span>
                  </div>
                </div>
              ))}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes
              </label>
              <textarea
                value={selfAssessment.notes}
                onChange={(e) => setSelfAssessment(prev => ({
                  ...prev,
                  notes: e.target.value
                }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="How are you feeling today? Any specific concerns or positive moments?"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button onClick={() => setShowSelfAssessment(false)} variant="outline">
                Cancel
              </Button>
              <Button onClick={completeCheckin} className="flex items-center">
                <Save className="w-4 h-4 mr-2" />
                Complete Check-in
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Check-in Complete */}
      {checkinComplete && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-600" />
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Check-in Complete!
              </h3>
              <p className="text-green-700">
                Your mental health data has been recorded. Keep up the great work!
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center text-red-800">
              <AlertTriangle className="w-5 h-5 mr-2" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MentalHealthCheckin;