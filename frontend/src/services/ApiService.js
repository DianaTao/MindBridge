import axios from 'axios';

class ApiService {
  constructor() {
    // Use localhost for development, production API for deployment
    const isLocalhost =
      window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    // Hardcoded correct API Gateway URL - no environment variable dependency
    const baseURL = isLocalhost
      ? 'http://localhost:8000'
      : 'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/';

    console.log('🔧 ApiService Configuration:');
    console.log('  - Version: 3.0.0-FINAL-CACHE-BUSTER-' + Date.now());
    console.log('  - DEPLOYED: ' + new Date().toISOString());
    console.log('  - API URL FIXED: wome1vjyzb (NOT axvcqofzug)');
    console.log('  - Hostname:', window.location.hostname);
    console.log('  - Is localhost:', isLocalhost);
    console.log('  - Final baseURL:', baseURL);
    console.log('  - User Agent:', navigator.userAgent);
    console.log('  - Online Status:', navigator.onLine);

    this.client = axios.create({
      baseURL: baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      config => {
        console.log(
          `🌐 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`
        );
        console.log('🌐 Full URL:', `${config.baseURL}${config.url}`);
        console.log('🌐 Request Headers:', config.headers);
        console.log('🌐 Request Data:', config.data);
        return config;
      },
      error => {
        console.error('❌ Request error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      response => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        console.log('✅ Response Headers:', response.headers);
        console.log('✅ Response Data:', response.data);
        return response;
      },
      error => {
        console.error('❌ Response error:', error);
        console.error('Error details:', {
          message: error.message,
          status: error.response?.status,
          url: error.config?.url,
          code: error.code,
          name: error.name,
          stack: error.stack,
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
        timestamp: new Date().toISOString(),
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
      frame_data_preview: request.frame_data.substring(0, 50) + '...',
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
        debug_info: result.debug_info,
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
        errorMessage =
          'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.status === 500) {
        errorMessage =
          'Server error occurred. The video analysis service is temporarily unavailable.';
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
      enhancedError.isNetworkError =
        error.code === 'NETWORK_ERROR' || error.message.includes('Network Error');

      throw enhancedError;
    }
  }

  async stopVideoAnalysis(request) {
    console.log('⏹️ FRONTEND: Stopping video analysis');
    console.log('📤 Stop request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      status: request.status,
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
    // Try to get existing user ID from localStorage
    let userId = localStorage.getItem('mindbridge_user_id');

    // If no user ID exists, create one and store it
    if (!userId) {
      userId = `user_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('mindbridge_user_id', userId);
      console.log('🆔 Generated new user ID:', userId);
    } else {
      console.log('🆔 Using existing user ID:', userId);
    }

    return userId;
  }

  static getCurrentSession() {
    return {
      sessionId: this.generateSessionId(),
      userId: this.generateUserId(),
      timestamp: new Date().toISOString(),
    };
  }

  // Static methods for direct API calls
  static async analyzeVideo(data) {
    const isLocalhost =
      window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost
      ? 'http://localhost:8000'
      : 'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/';

    try {
      console.log('🔍 Attempting to call video API at:', `${baseURL}/video-analysis`);

      const response = await fetch(`${baseURL}/video-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
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
        stack: error.stack,
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
    const isLocalhost =
      window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost
      ? 'http://localhost:8000'
      : 'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/';

    try {
      const response = await fetch(`${baseURL}/video-analysis/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
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

  static async analyzeText(data) {
    const isLocalhost =
      window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const baseURL = isLocalhost
      ? 'http://localhost:8000'
      : 'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/';

    try {
      console.log('�� Attempting to call API at:', `${baseURL}/text-analysis`);

      const response = await fetch(`${baseURL}/text-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
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
        stack: error.stack,
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
      happy: [
        'happy',
        'joy',
        'excited',
        'great',
        'awesome',
        'love',
        'wonderful',
        'amazing',
        'fantastic',
      ],
      sad: ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'awful', 'terrible', 'bad'],
      angry: ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'irritated'],
      surprised: ['surprised', 'shocked', 'amazed', 'wow', 'incredible', 'unbelievable'],
      fear: ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous'],
      calm: ['calm', 'peaceful', 'relaxed', 'serene', 'quiet', 'tranquil'],
    };

    const detectedEmotions = [];
    let maxScore = 0;
    let primaryEmotion = 'neutral';

    for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
      const matches = words.filter(word => keywords.includes(word)).length;
      if (matches > 0) {
        const confidence = Math.min((matches / words.length) * 10, 1.0);
        detectedEmotions.push({
          Type: emotion,
          Confidence: confidence,
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
        Confidence: 0.8,
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
        environment: 'frontend_fallback',
      },
    };
  }

  static mockVideoAnalysis(data) {
    const frameData = data.frame_data || '';
    const frameLength = frameData.length;

    // Simple mock analysis based on frame data length
    const emotions = [
      { Type: 'HAPPY', Confidence: 85 },
      { Type: 'CALM', Confidence: 75 },
      { Type: 'NEUTRAL', Confidence: 60 },
    ];

    const primaryEmotion = emotions[0].Type.toLowerCase();

    return {
      faces_detected: 1,
      emotions: [
        {
          face_id: 'face_0',
          emotions: emotions,
          primary_emotion: primaryEmotion,
          confidence: 85,
          face_confidence: 85,
          bounding_box: {
            Width: 0.4,
            Height: 0.5,
            Left: 0.2,
            Top: 0.3,
          },
          age_range: { Low: 25, High: 35 },
          gender: { Value: 'Unknown', Confidence: 50 },
          timestamp: new Date().toISOString(),
          user_id: data.user_id || 'mock-user',
          session_id: data.session_id || 'mock-session',
          modality: 'video',
        },
      ],
      primary_emotion: primaryEmotion,
      confidence: 85.0,
      timestamp: new Date().toISOString(),
      debug_info: {
        analysis_method: 'mock_frontend',
        frame_data_length: frameLength,
        environment: 'frontend_fallback',
      },
    };
  }

  async analyzeText(request) {
    console.log('📝 FRONTEND: Text analysis request started');
    console.log('📤 Request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      text_length: request.text ? request.text.length : 0,
    });

    try {
      const response = await this.client.post('/text-analysis', request);
      console.log('✅ FRONTEND: Text analysis response received');
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

      console.log('🎯 FRONTEND: Final text analysis result:', {
        sentiment: result.sentiment,
        emotions: result.emotions,
        confidence: result.confidence,
        debug_info: result.debug_info,
      });

      return result;
    } catch (error) {
      console.error('❌ FRONTEND: Text analysis request failed');
      console.error('Error details:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }

      // Provide detailed error information
      let errorMessage = 'Text analysis failed';
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        errorMessage =
          'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.status === 500) {
        errorMessage =
          'Server error occurred. The text analysis service is temporarily unavailable.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Text analysis endpoint not found. Please contact support.';
      } else if (error.response?.status === 400) {
        errorMessage = 'Invalid text format. Please try again.';
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
      enhancedError.isNetworkError =
        error.code === 'NETWORK_ERROR' || error.message.includes('Network Error');

      throw enhancedError;
    }
  }

  async analyzeCallReview(request) {
    console.log('📞 FRONTEND: Call review analysis request started');
    console.log('📤 Request data:', {
      user_id: request.user_id,
      session_id: request.session_id,
      audio_url: request.audio_url,
    });

    try {
      const response = await this.client.post('/call-review', request);
      console.log('✅ FRONTEND: Call review analysis response received');
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
      console.error('❌ FRONTEND: Call review analysis request failed');
      console.error('Error details:', error);
      throw error;
    }
  }

  async submitCheckin(checkinData) {
    console.log('🧠 FRONTEND: Submitting mental health check-in');
    console.log('📤 Check-in data:', {
      user_id: checkinData.user_id,
      session_id: checkinData.session_id,
      duration: checkinData.duration,
      has_emotion_analysis: !!checkinData.emotion_analysis,
      has_self_assessment: !!checkinData.self_assessment,
    });

    try {
      const response = await this.client.post('/checkin-processor', checkinData);
      console.log('✅ FRONTEND: Check-in submission response received');
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
      console.error('❌ FRONTEND: Check-in submission failed');
      console.error('Error details:', error);
      throw error;
    }
  }

  async getCheckinData(params = {}) {
    console.log('📊 FRONTEND: Getting check-in data with params:', params);

    try {
      const response = await this.client.get('/checkin-data', { params });
      console.log('✅ FRONTEND: Check-in data response received');
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
      console.error('❌ FRONTEND: Failed to get check-in data');
      console.error('Error details:', error);

      // Return empty data structure for graceful degradation
      return {
        checkins: [],
        analytics_summary: {
          total_checkins: 0,
          average_score: 0,
          mood_trend: 'stable',
          most_common_emotion: 'neutral',
          period_covered: 'No data available',
          recommendations: [],
          llm_insights: [],
        },
      };
    }
  }

  async getHRWellnessData(params = {}) {
    console.log('🏢 FRONTEND: Getting HR wellness data with params:', params);

    try {
      const response = await this.client.get('/hr-wellness-data', { params });
      console.log('✅ FRONTEND: HR wellness data response received');
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
      console.error('❌ FRONTEND: Failed to get HR wellness data');
      console.error('Error details:', error);

      // Return null to indicate no data available
      return null;
    }
  }
}

// Create and export a default instance
const apiService = new ApiService();

// Export both the class and default instance
export default apiService;
export { ApiService };

export async function sendRealTimeAudioChunk(audioBlob) {
  const isLocalhost =
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const baseURL = isLocalhost
    ? 'http://localhost:8000'
    : 'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/';

  try {
    console.log('🎤 Sending audio chunk to AWS for analysis...');
    console.log('🎤 Audio blob size:', audioBlob.size, 'bytes');
    console.log('🎤 Audio blob type:', audioBlob.type);

    // Convert blob to base64
    const base64Data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1]; // Remove data URL prefix
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(audioBlob);
    });

    // Send as JSON with base64 audio data
    const requestData = {
      audio_chunk: base64Data,
      content_type: audioBlob.type,
      size: audioBlob.size,
    };

    const response = await fetch(`${baseURL}/realtime-call-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      console.warn(`🎤 AWS analysis failed with status ${response.status}, using fallback`);
      throw new Error(`AWS analysis failed: ${response.status}`);
    }

    const result = await response.json();
    console.log('🎤 AWS analysis successful:', result);
    return result;
  } catch (error) {
    console.warn('🎤 Using fallback analysis due to AWS error:', error.message);

    // Fallback analysis when AWS is not available
    const fallbackAnalysis = {
      emotion: ['happy', 'neutral', 'calm', 'focused'][Math.floor(Math.random() * 4)],
      emotion_confidence: 0.6 + Math.random() * 0.3,
      sentiment: Math.random() > 0.5 ? 'positive' : 'neutral',
      sentiment_score: 0.3 + Math.random() * 0.7,
      sentiment_trend: Math.random() > 0.5 ? 'improving' : 'stable',
      call_type: 'general',
      call_intensity: 20 + Math.random() * 60,
      speaking_rate: 120 + Math.random() * 80,
      key_phrases: ['conversation', 'communication'],
      processing_time_ms: 1000,
      timestamp: new Date().toISOString(),
      debug_info: {
        analysis_method: 'fallback_frontend',
        audio_size_bytes: audioBlob.size,
        environment: 'fallback_mode',
        error: error.message,
      },
    };

    console.log('🎤 Fallback analysis result:', fallbackAnalysis);
    return fallbackAnalysis;
  }
}
