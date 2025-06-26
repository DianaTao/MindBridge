import axios, { AxiosInstance } from 'axios';

export interface VideoAnalysisRequest {
  frame_data: string;
  user_id: string;
  session_id: string;
}

export interface VideoAnalysisResponse {
  faces_detected: number;
  emotions: any[];
  primary_emotion: string;
  confidence: number;
  timestamp: string;
}

export interface AudioAnalysisRequest {
  audio_data: string;
  user_id: string;
  session_id: string;
}

export interface AudioAnalysisResponse {
  emotions: any[];
  primary_emotion: string;
  confidence: number;
  transcript?: string;
  timestamp: string;
}

export interface EmotionFusionRequest {
  user_id: string;
  session_id: string;
  emotions?: any[];
}

export interface EmotionFusionResponse {
  unified_emotion: {
    emotion: string;
    confidence: number;
    intensity: number;
  };
  recommendations: {
    primary: string;
    actions: string[];
    wellness_score: number;
  };
  timestamp: string;
}

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use((config) => {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    });

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
        return Promise.reject(error);
      }
    );
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async analyzeVideo(request: VideoAnalysisRequest): Promise<VideoAnalysisResponse> {
    const response = await this.client.post('/video-analysis', request);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async analyzeAudio(request: AudioAnalysisRequest): Promise<AudioAnalysisResponse> {
    const response = await this.client.post('/audio-analysis', request);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async fuseEmotions(request: EmotionFusionRequest): Promise<EmotionFusionResponse> {
    const response = await this.client.post('/emotion-fusion', request);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async getDashboardAnalytics(params: {
    user_id: string;
    session_id: string;
    time_range?: string;
  }): Promise<any> {
    const response = await this.client.post('/dashboard/analytics', params);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  async getSessionData(sessionId: string): Promise<any> {
    const response = await this.client.get(`/dashboard/session/${sessionId}`);
    
    // Handle both direct response and Lambda function response format
    if (response.data.body) {
      return JSON.parse(response.data.body);
    }
    return response.data;
  }

  // Utility method to convert file to base64
  static async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }

  // Utility method to convert canvas to base64
  static canvasToBase64(canvas: HTMLCanvasElement): string {
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);
    // Remove the data URL prefix
    return dataURL.split(',')[1];
  }

  // Utility method to convert audio blob to base64
  static async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }

  // Get current user and session IDs (for demo purposes)
  static getCurrentSession() {
    return {
      user_id: `demo-user-${Math.random().toString(36).substr(2, 9)}`,
      session_id: `session-${Date.now()}`
    };
  }
}

export default new ApiService(); 