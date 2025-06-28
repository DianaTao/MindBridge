import axios from 'axios';

class ApiService {
  constructor() {
    // Use localhost for development, production API for deployment
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    // For CloudFront deployment, you can update this URL
    // Replace 'your-cloudfront-domain' with your actual CloudFront domain
    // Example: 'https://d1234567890abc.cloudfront.net'
    const baseURL = isLocalhost ? 'http://localhost:3002' : (process.env.REACT_APP_API_URL || 'https://axvcqofzug.execute-api.us-east-1.amazonaws.com/prod/');
    
    console.log('🔧 ApiService Configuration:');
    console.log('  - Hostname:', window.location.hostname);
    console.log('  - Is localhost:', isLocalhost);
    console.log('  - Environment API URL:', process.env.REACT_APP_API_URL);
    console.log('  - Final baseURL:', baseURL);
    
    this.client = axios.create({
      baseURL: baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
        console.log('🌐 Full URL:', `${config.baseURL}${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ Response error:', error);
        console.error('Error details:', {
          message: error.message,
          status: error.response?.status,
          url: error.config?.url
        });
        return Promise.reject(error);
      }
    );
  }

  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  async testConnection() {
    try {
      const response = await this.client.get('/health');
      return {
        status: 'connected',
        models_loaded: response.data.models_loaded || false,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error('API connection failed: ' + error.message);
    }
  }

  async analyzeVideo(request) {
    console.log('🎬 FRONTEND: Video analysis request started');
    console.log('📤 Request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      frame_data_length: request.frame_data.length,
      frame_data_preview: request.frame_data.substring(0, 50) + '...'
    });
    
    try {
      const response = await this.client.post('/video-analysis', request);
      console.log('✅ FRONTEND: Video analysis response received');
      console.log('📥 Response status:', response.status);
      console.log('📥 Response data:', response.data);
      
      // Handle both direct response and Lambda function response format
      let result;
      if (response.data.body) {
        console.log('🔄 FRONTEND: Parsing Lambda response body');
        result = JSON.parse(response.data.body);
      } else {
        console.log('🔄 FRONTEND: Using direct response data');
        result = response.data;
      }
      
      console.log('🎯 FRONTEND: Final result:', {
        faces_detected: result.faces_detected,
        primary_emotion: result.primary_emotion,
        confidence: result.confidence,
        debug_info: result.debug_info
      });
      
      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Video analysis request failed');
      console.error('Error details:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      
      // Provide detailed error information
      let errorMessage = 'Video analysis failed';
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        errorMessage = 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error occurred. The video analysis service is temporarily unavailable.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Video analysis endpoint not found. Please contact support.';
      } else if (error.response?.status === 413) {
        errorMessage = 'Image too large. Please try again with a smaller image.';
      } else if (error.response?.status === 400) {
        errorMessage = 'Invalid image format. Please try again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Access denied. Please check your permissions.';
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Throw error with detailed message
      const enhancedError = new Error(errorMessage);
      enhancedError.originalError = error;
      enhancedError.statusCode = error.response?.status;
      enhancedError.isNetworkError = error.code === 'NETWORK_ERROR' || error.message.includes('Network Error');
      
      throw enhancedError;
    }
  }

  async stopVideoAnalysis(request) {
    console.log('⏹️ FRONTEND: Stopping video analysis');
    console.log('📤 Stop request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      status: request.status
    });
    
    try {
      const response = await this.client.post('/video-analysis/stop', request);
      console.log('✅ FRONTEND: Video analysis stop response received');
      console.log('📥 Response status:', response.status);
      console.log('📥 Response data:', response.data);
      
      // Handle both direct response and Lambda function response format
      let result;
      if (response.data.body) {
        console.log('🔄 FRONTEND: Parsing Lambda response body');
        result = JSON.parse(response.data.body);
      } else {
        console.log('🔄 FRONTEND: Using direct response data');
        result = response.data;
      }
      
      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Video analysis stop request failed');
      console.error('Error details:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      throw error;
    }
  }

  async analyzeAudio(request) {
    console.log('🎙️ FRONTEND: Audio analysis request started');
    console.log('📤 Request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      audio_data_length: request.audio_data ? request.audio_data.length : 0
    });
    
    try {
      const response = await this.client.post('/audio-analysis', request);
      console.log('✅ FRONTEND: Audio analysis response received');
      console.log('📥 Response status:', response.status);
      console.log('📥 Response data:', response.data);
      
      // Handle both direct response and Lambda function response format
      let result;
      if (response.data.body) {
        console.log('🔄 FRONTEND: Parsing Lambda response body');
        result = JSON.parse(response.data.body);
      } else {
        console.log('🔄 FRONTEND: Using direct response data');
        result = response.data;
      }
      
      console.log('🎯 FRONTEND: Final result:', {
        primary_emotion: result.primary_emotion,
        confidence: result.confidence,
        transcript: result.transcript,
        debug_info: result.debug_info
      });
      
      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Audio analysis request failed');
      console.error('Error details:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      
      // Provide detailed error information
      let errorMessage = 'Audio analysis failed';
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        errorMessage = 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error occurred. The audio analysis service is temporarily unavailable.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Audio analysis endpoint not found. Please contact support.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Access denied. Please check your permissions.';
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Throw error with detailed message
      const enhancedError = new Error(errorMessage);
      enhancedError.originalError = error;
      enhancedError.statusCode = error.response?.status;
      enhancedError.isNetworkError = error.code === 'NETWORK_ERROR' || error.message.includes('Network Error');
      
      throw enhancedError;
    }
  }

  async fuseEmotions(request) {
    const response = await this.client.post('/emotion-fusion', request);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async getDashboardAnalytics(params) {
    const response = await this.client.post('/dashboard/analytics', params);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async getSessionData(sessionId) {
    const response = await this.client.get(`/dashboard/session/${sessionId}`);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  // Utility method to convert file to base64
  static async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result;
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }

  // Utility method to convert canvas to base64
  static canvasToBase64(canvas) {
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);
    // Remove the data URL prefix
    return dataURL.split(',')[1];
  }

  // Utility method to convert audio blob to base64
  static async blobToBase64(blob) {
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
  }

  // Generate session data
  static generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static generateUserId() {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static getCurrentSession() {
    return {
      sessionId: this.generateSessionId(),
      userId: this.generateUserId(),
      timestamp: new Date().toISOString()
    };
  }

  // Static methods for direct API calls
  static async analyzeVideo(data) {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost ? 'http://localhost:3002' : (process.env.REACT_APP_API_URL || 'https://axvcqofzug.execute-api.us-east-1.amazonaws.com/prod/');
    
    try {
      console.log('🔍 Attempting to call video API at:', `${baseURL}/video-analysis`);
      
      const response = await fetch(`${baseURL}/video-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Handle Lambda response format
      if (result.body) {
        return JSON.parse(result.body);
      }
      
      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Static video analysis failed:', error);
      console.error('Error details:', {
        message: error.message,
        type: error.name,
        stack: error.stack
      });
      
      // Check if it's a network error
      if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        console.warn('Network error detected, using mock video analysis');
        return this.mockVideoAnalysis(data);
      }
      
      throw error;
    }
  }

  static async stopVideoAnalysis(data) {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost ? 'http://localhost:3002' : (process.env.REACT_APP_API_URL || 'https://axvcqofzug.execute-api.us-east-1.amazonaws.com/prod/');
    
    try {
      const response = await fetch(`${baseURL}/video-analysis/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Handle Lambda response format
      if (result.body) {
        return JSON.parse(result.body);
      }
      
      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Static video analysis stop failed:', error);
      throw error;
    }
  }

  static async analyzeAudio(data) {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost ? 'http://localhost:3002' : (process.env.REACT_APP_API_URL || 'https://axvcqofzug.execute-api.us-east-1.amazonaws.com/prod/');
    
    try {
      console.log('🔍 Attempting to call audio API at:', `${baseURL}/audio-analysis`);
      
      const response = await fetch(`${baseURL}/audio-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Handle Lambda response format
      if (result.body) {
        return JSON.parse(result.body);
      }
      
      return result;
    } catch (error) {
      console.error('Audio analysis error:', error);
      console.error('Error details:', {
        message: error.message,
        type: error.name,
        stack: error.stack
      });
      
      // Check if it's a network error
      if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        console.warn('Network error detected, using mock audio analysis');
        return this.mockAudioAnalysis(data);
      }
      
      throw error;
    }
  }

  static async analyzeText(data) {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost ? 'http://localhost:3002' : (process.env.REACT_APP_API_URL || 'https://axvcqofzug.execute-api.us-east-1.amazonaws.com/prod/');
    
    try {
      console.log('🔍 Attempting to call API at:', `${baseURL}/text-analysis`);
      
      const response = await fetch(`${baseURL}/text-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        // If the endpoint doesn't exist, fall back to mock analysis
        if (response.status === 403 || response.status === 404) {
          console.warn('Text analysis endpoint not available, using mock analysis');
          return this.mockTextAnalysis(data);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Handle Lambda response format
      if (result.body) {
        return JSON.parse(result.body);
      }
      
      return result;
    } catch (error) {
      console.error('Text analysis error:', error);
      console.error('Error details:', {
        message: error.message,
        type: error.name,
        stack: error.stack
      });
      
      // Check if it's a network error
      if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        console.warn('Network error detected, using mock text analysis');
        return this.mockTextAnalysis(data);
      }
      
      // Fall back to mock analysis if there's any error
      console.warn('Falling back to mock text analysis');
      return this.mockTextAnalysis(data);
    }
  }

  static mockTextAnalysis(data) {
    const text = data.text || data.text_data || '';
    const words = text.toLowerCase().split(/\s+/);
    
    // Simple emotion detection based on keywords
    const emotionKeywords = {
      happy: ['happy', 'joy', 'excited', 'great', 'awesome', 'love', 'wonderful', 'amazing', 'fantastic'],
      sad: ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'awful', 'terrible', 'bad'],
      angry: ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'irritated'],
      surprised: ['surprised', 'shocked', 'amazed', 'wow', 'incredible', 'unbelievable'],
      fear: ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous'],
      calm: ['calm', 'peaceful', 'relaxed', 'serene', 'quiet', 'tranquil'],
    };
    
    let detectedEmotions = [];
    let maxScore = 0;
    let primaryEmotion = 'neutral';
    
    for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
      const matches = words.filter(word => keywords.includes(word)).length;
      if (matches > 0) {
        const confidence = Math.min(matches / words.length * 10, 1.0);
        detectedEmotions.push({
          Type: emotion,
          Confidence: confidence
        });
        
        if (confidence > maxScore) {
          maxScore = confidence;
          primaryEmotion = emotion;
        }
      }
    }
    
    // If no emotions detected, return neutral
    if (detectedEmotions.length === 0) {
      detectedEmotions.push({
        Type: 'neutral',
        Confidence: 0.8
      });
    }
    
    // Simple sentiment analysis
    const positiveWords = ['good', 'great', 'awesome', 'love', 'like', 'happy', 'wonderful'];
    const negativeWords = ['bad', 'awful', 'hate', 'dislike', 'sad', 'terrible', 'horrible'];
    
    const positiveCount = words.filter(word => positiveWords.includes(word)).length;
    const negativeCount = words.filter(word => negativeWords.includes(word)).length;
    
    let sentiment = 'neutral';
    if (positiveCount > negativeCount) sentiment = 'positive';
    else if (negativeCount > positiveCount) sentiment = 'negative';
    
    return {
      emotions: detectedEmotions,
      primary_emotion: primaryEmotion,
      confidence: maxScore || 0.8,
      sentiment: sentiment,
      keywords: words.slice(0, 5), // First 5 words as keywords
      timestamp: new Date().toISOString(),
      debug_info: {
        analysis_method: 'mock_frontend',
        text_length: text.length,
        environment: 'frontend_fallback'
      }
    };
  }

  static mockAudioAnalysis(data) {
    console.log('🎙️ FRONTEND: Using mock audio analysis (API unavailable)');
    console.log('📤 Mock request data:', {
      user_id: data.user_id,
      session_id: data.session_id,
      audio_data_length: data.audio_data ? data.audio_data.length : 0
    });
    
    // Generate realistic mock response based on audio data characteristics
    const audioSize = data.audio_data ? data.audio_data.length : 0;
    const timestamp = new Date().toISOString();
    
    // Simple heuristics based on audio size
    let primaryEmotion, confidence, transcript;
    
    if (audioSize < 1000) {
      primaryEmotion = 'neutral';
      confidence = 0.3;
      transcript = 'Audio too short for analysis';
    } else if (audioSize < 5000) {
      const emotions = ['happy', 'calm', 'neutral', 'thoughtful'];
      primaryEmotion = emotions[Math.floor(Math.random() * emotions.length)];
      confidence = 0.6;
      transcript = 'Hello, how are you today?';
    } else {
      const emotions = ['happy', 'excited', 'confident', 'calm', 'enthusiastic'];
      primaryEmotion = emotions[Math.floor(Math.random() * emotions.length)];
      confidence = 0.8;
      transcript = 'I am feeling really good about this project!';
    }
    
    const mockResult = {
      emotions: [
        {
          Type: primaryEmotion.toUpperCase(),
          Confidence: confidence * 100
        },
        {
          Type: 'NEUTRAL',
          Confidence: (1 - confidence) * 100
        }
      ],
      primary_emotion: primaryEmotion,
      confidence: confidence * 100,
      transcript: transcript,
      timestamp: timestamp,
      processing_time_ms: Math.floor(Math.random() * 1000) + 100,
      debug_info: {
        analysis_method: 'mock_fallback',
        audio_size_bytes: audioSize,
        environment: 'frontend_fallback',
        reason: 'API unavailable - using mock analysis'
      }
    };
    
    console.log('🎯 FRONTEND: Mock result:', {
      primary_emotion: mockResult.primary_emotion,
      confidence: mockResult.confidence,
      transcript: mockResult.transcript,
      debug_info: mockResult.debug_info
    });
    
    return mockResult;
  }

  static mockVideoAnalysis(data) {
    const frameData = data.frame_data || '';
    const frameLength = frameData.length;
    
    // Simple mock analysis based on frame data length
    const emotions = [
      { Type: 'HAPPY', Confidence: 85 },
      { Type: 'CALM', Confidence: 75 },
      { Type: 'NEUTRAL', Confidence: 60 }
    ];
    
    const primaryEmotion = emotions[0].Type.toLowerCase();
    
    return {
      faces_detected: 1,
      emotions: [{
        face_id: 'face_0',
        emotions: emotions,
        primary_emotion: primaryEmotion,
        confidence: 85,
        face_confidence: 85,
        bounding_box: {
          Width: 0.4,
          Height: 0.5,
          Left: 0.2,
          Top: 0.3
        },
        age_range: { Low: 25, High: 35 },
        gender: { Value: 'Unknown', Confidence: 50 },
        timestamp: new Date().toISOString(),
        user_id: data.user_id || 'mock-user',
        session_id: data.session_id || 'mock-session',
        modality: 'video'
      }],
      primary_emotion: primaryEmotion,
      confidence: 85.0,
      timestamp: new Date().toISOString(),
      debug_info: {
        analysis_method: 'mock_frontend',
        frame_data_length: frameLength,
        environment: 'frontend_fallback'
      }
    };
  }

}

// Create and export a default instance
const apiService = new ApiService();

// Export both the class and default instance
export default apiService;
export { ApiService }; 