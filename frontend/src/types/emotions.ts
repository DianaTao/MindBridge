export interface EmotionState {
  unified_emotion: string;
  intensity: number;
  confidence: number;
  contributing_factors: string[];
  trend: 'improving' | 'declining' | 'stable';
  context: string;
  risk_level: 'low' | 'medium' | 'high';
  analysis_timestamp: string;
  data_points_analyzed: number;
  ai_model: string;
}

export interface RecommendationData {
  immediate_actions: string[];
  breathing_exercise: string;
  environment_changes: string[];
  activity_suggestions: string[];
  when_to_seek_help: string;
  positive_affirmations: string[];
  priority_level: 'low' | 'medium' | 'high';
  generated_at: string;
}

export interface EmotionDataPoint {
  timestamp: string;
  emotion: string;
  intensity: number;
  confidence: number;
}

export interface WebSocketMessage {
  action: string;
  data?: any;
  user_id?: string;
  session_id?: string;
  timeframe?: string;
}

export interface AnalyticsData {
  emotion_distribution: Array<{
    emotion: string;
    frequency: number;
    avg_intensity: number;
    avg_confidence: number;
  }>;
  emotion_trends: Array<{
    time_bucket: string;
    avg_intensity: number;
    dominant_emotion: string;
  }>;
  insights: {
    dominant_emotion: string;
    emotion_variability: string;
    average_intensity: number;
    recommendations: string[];
  };
} 