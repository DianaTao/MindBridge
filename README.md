# MindBridge AI - Real-Time Mental Health Analytics Platform

![MindBridge AI](https://img.shields.io/badge/MindBridge-AI%20Powered-blue?style=for-the-badge&logo=aws)
![AWS](https://img.shields.io/badge/AWS-Cloud%20Native-orange?style=for-the-badge&logo=amazon-aws)
![React](https://img.shields.io/badge/React-Frontend-61dafb?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-Backend-3776ab?style=for-the-badge&logo=python)

## 🧠 Overview

MindBridge AI is a comprehensive mental health analytics platform that combines real-time emotion detection, AI-powered sentiment analysis, and personalized wellness recommendations. Built with AWS cloud-native architecture, it provides both real-time call analysis for customer service and personal mental health check-ins for individual wellness tracking.

## ✨ Key Features

### 🎯 Real-Time Call Analysis
- **Live Emotion Detection** - Real-time facial emotion analysis during video calls
- **Audio Sentiment Analysis** - AI-powered audio processing using AWS Bedrock LLM
- **Call Quality Metrics** - Speaking rate, confidence levels, and emotional patterns
- **Agent Performance Insights** - Detailed analytics for customer service optimization
- **Real-time Audio Chunks** - Continuous audio analysis during calls

### 🧘 Mental Health Check-ins
- **Facial Emotion Analysis** - Camera-based emotion detection using AWS Rekognition
- **Self-Assessment Integration** - Comprehensive mood and wellness questionnaires
- **AI-Powered Insights** - Personalized recommendations using AWS Bedrock Claude 3
- **Trend Analytics** - Historical pattern analysis and progress tracking
- **Session-based Tracking** - Individual check-in sessions with detailed metrics

### 🤖 AI-Powered Analytics
- **LLM-Generated Reports** - Personalized insights using AWS Bedrock Claude 3
- **Dynamic Recommendations** - Context-aware wellness advice
- **Emotional Context Analysis** - Deep understanding of emotional states
- **Predictive Insights** - Pattern recognition and trend analysis
- **Multi-modal Fusion** - Combined video, audio, and text analysis

## 🏗️ Architecture

### Frontend (React.js)
```
frontend/
├── src/
│   ├── components/
│   │   ├── RealTimeCallAnalysis.js    # Live call emotion detection
│   │   ├── MentalHealthCheckin.js     # Personal wellness check-ins
│   │   ├── TextAnalysis.js            # Text sentiment analysis
│   │   ├── EmotionAnalytics.js        # Historical analytics dashboard
│   │   ├── CameraCapture.js           # Video capture and processing
│   │   ├── AutomatedCallDashboard.js  # Call review analytics
│   │   ├── EmailAuth.js               # User authentication
│   │   └── ui/                        # Reusable UI components
│   ├── services/
│   │   ├── ApiService.js              # AWS API Gateway integration
│   │   ├── WebSocketService.js        # Real-time communication
│   │   └── index.js                   # Service exports
│   └── config.prod.js                 # Production configuration
```

### Backend (AWS Serverless)
```
infrastructure/
├── mindbridge_stack.py                # CDK infrastructure definition (Python)
├── cdk.json                           # CDK configuration
├── requirements.txt                   # Python dependencies
└── bin/

lambda_functions/
├── video_analysis/                    # Facial emotion detection
├── text_analysis/                     # LLM-powered sentiment analysis
├── checkin_processor/                 # Mental health data processing
├── checkin_retriever/                 # Analytics data retrieval
├── realtime_call_analysis/            # Live call processing
├── emotion_fusion/                    # Multi-modal emotion fusion
├── dashboard/                         # Analytics aggregation
├── user_auth/                         # User authentication
├── health_check/                      # Health monitoring
└── call_review/                       # Call review processing
```

### AWS Services Integration
- **AWS Lambda** - Serverless compute for all processing
- **AWS Bedrock** - Claude 3 LLM for AI-powered insights
- **AWS Rekognition** - Facial emotion detection
- **AWS Transcribe** - Speech-to-text conversion
- **AWS Comprehend** - Natural language processing
- **DynamoDB** - NoSQL database for data storage
- **S3** - Media storage and call recordings
- **API Gateway** - RESTful API endpoints
- **CloudFront** - CDN for frontend delivery

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm
- Python 3.9+
- AWS CDK CLI

### 1. Clone and Setup
```bash
git clone <repository-url>
cd MindBridge
npm install
```

### 2. Deploy Infrastructure
```bash
cd infrastructure
npm install
cdk bootstrap
cdk deploy --require-approval never
```

### 3. Deploy Frontend and Backend
```bash
# Deploy frontend to S3/CloudFront and backend proxy
./scripts/deploy-frontend-backend.sh
```

### 4. Deploy Lambda Functions
```bash
# Deploy all Lambda functions
./scripts/deploy-checkin-functions.sh
./scripts/deploy-automated-call-review.sh

# Or deploy individually
./scripts/deploy-checkin-processor.sh
./scripts/deploy-user-auth.sh
```

### 5. Setup AWS Resources
```bash
# Setup required AWS resources (S3, DynamoDB, IAM)
./scripts/setup-aws-resources.sh
```

## 📊 API Endpoints

### Real-Time Analysis
- `POST /video-analysis` - Facial emotion detection
- `POST /text-analysis` - LLM-powered sentiment analysis
- `POST /realtime-call-analysis` - Live call processing
- `POST /emotion-fusion` - Multi-modal emotion fusion

### Mental Health
- `POST /checkin-processor` - Process mental health check-ins
- `GET /checkin-retriever` - Retrieve analytics data
- `POST /user-auth` - User authentication

### Analytics
- `GET /dashboard` - Analytics dashboard data
- `GET /health` - Health check endpoint
- `POST /call-review` - Automated call review processing

## 🧠 AI Features

### Text Sentiment Analysis
```javascript
// Example: Analyze text emotions
const result = await ApiService.analyzeText({
  text: "I'm feeling really stressed about work lately",
  user_id: "user123",
  session_id: "session456"
});

// Returns:
{
  sentiment: "negative",
  emotions: [{ Type: "anxiety", Confidence: 0.85, Intensity: "high" }],
  llm_analysis: {
    emotional_context: "The text indicates work-related stress...",
    recommendations: "Consider stress management techniques..."
  }
}
```

### Mental Health Check-ins
```javascript
// Example: Submit check-in data
const checkinData = {
  emotion_analysis: { dominant_emotion: "calm", average_wellbeing: 75 },
  self_assessment: { overall_mood: 7, stress_level: 3 },
  duration: 120
};

const result = await ApiService.submitCheckin(checkinData);
// Returns personalized LLM-generated recommendations
```

### Real-Time Call Analysis
```javascript
// Example: Send audio chunk for analysis
const audioChunk = await ApiService.sendRealTimeAudioChunk({
  audio_data: base64AudioData,
  user_id: "user123",
  session_id: "call456",
  timestamp: Date.now()
});

// Returns real-time sentiment and emotion analysis
```

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# DynamoDB Tables
CHECKINS_TABLE=mindbridge-checkins-dev
EMOTIONS_TABLE=mindbridge-emotions-dev
USERS_TABLE=mindbridge-users-dev
CALL_REVIEWS_TABLE=mindbridge-call-reviews-dev

# S3 Buckets
MEDIA_BUCKET=mindbridge-media-dev-{account}
CALL_RECORDINGS_BUCKET=mindbridge-call-recordings-dev-{account}
AUDIO_CHUNKS_BUCKET=mindbridge-audio-chunks-dev-{account}
```

### Frontend Configuration
```javascript
// config.prod.js
const config = {
  apiUrl: 'https://your-api-gateway-url.amazonaws.com/prod/',
  websocketUrl: 'wss://your-websocket-url.amazonaws.com/prod/',
  region: 'us-east-1'
};
```

## 📈 Analytics Dashboard

### Real-Time Metrics
- **Emotion Distribution** - Real-time emotion tracking
- **Sentiment Trends** - Historical sentiment analysis
- **Call Quality Scores** - Agent performance metrics
- **Wellness Trends** - Personal mental health patterns

### LLM-Powered Insights
- **Personalized Recommendations** - AI-generated wellness advice
- **Emotional Context Analysis** - Deep understanding of emotional states
- **Trend Predictions** - Pattern recognition and forecasting
- **Actionable Insights** - Specific, personalized recommendations

### Historical Analytics
- **Session History** - Complete check-in session records
- **Emotion Patterns** - Long-term emotional trend analysis
- **Wellness Progress** - Personal growth and improvement tracking
- **Recommendation History** - Past AI-generated advice

## 🔒 Security & Privacy

### Data Protection
- **End-to-end encryption** for all data transmission
- **AWS IAM** for fine-grained access control
- **DynamoDB encryption** at rest and in transit
- **S3 bucket policies** for secure media storage

### Privacy Compliance
- **User consent** for data collection and processing
- **Data anonymization** for analytics
- **Retention policies** for automatic data cleanup
- **GDPR compliance** ready

## 🚀 Deployment

### Production Deployment
```bash
# Deploy to production
cd infrastructure
cdk deploy --context environment=production

# Deploy frontend to CloudFront
cd frontend
npm run build
npm run deploy:prod
```

### Local Development
```bash
# Start local development environment
./scripts/local-dev.sh

# Test local endpoints
./scripts/test-local.sh
```

### Monitoring & Logging
- **CloudWatch Logs** for Lambda function monitoring
- **CloudWatch Metrics** for performance tracking
- **X-Ray** for distributed tracing
- **CloudTrail** for API call auditing

## 🤝 Contributing

### Development Setup
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Run development server
cd frontend
npm start

# Run tests
npm test
```

### Code Structure
- **Frontend**: React.js with functional components and hooks
- **Backend**: Python Lambda functions with AWS SDK
- **Infrastructure**: AWS CDK with Python
- **Testing**: Jest for frontend, pytest for backend

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Architecture Guide](docs/ARCHITECTURE.md)
- [AWS Bedrock Integration](AWS_BEDROCK_LLM_INTEGRATION.md)
- [Amazon Rekognition Deployment](AMAZON_REKOGNITION_DEPLOYMENT.md)
- [Automated Call Review](AUTOMATED_CALL_REVIEW.md)

### Troubleshooting
- Check CloudWatch Logs for Lambda function errors
- Verify AWS IAM permissions for Bedrock access
- Ensure API Gateway CORS configuration is correct
- Validate DynamoDB table schemas and permissions
- Check S3 bucket policies and permissions

### Common Issues
- **500 Internal Server Errors**: Check Lambda function logs and DynamoDB permissions
- **403 Forbidden**: Verify IAM roles and API Gateway permissions
- **CORS Errors**: Ensure API Gateway CORS configuration is correct
- **Lambda Timeout**: Check function timeout settings and resource allocation

## 🎯 Roadmap

### Upcoming Features
- **Multi-language Support** - Internationalization
- **Advanced Analytics** - Machine learning insights
- **Mobile App** - React Native implementation
- **Team Analytics** - Group wellness tracking
- **Integration APIs** - Third-party service connections

### Performance Optimizations
- **Edge Computing** - Lambda@Edge for global performance
- **Caching Strategy** - Redis for frequently accessed data
- **CDN Optimization** - Advanced CloudFront configuration
- **Database Optimization** - DynamoDB performance tuning

## 📊 Current Status

### ✅ Implemented Features
- **Real-time Call Analysis** - Live audio processing and sentiment analysis
- **Mental Health Check-ins** - Camera-based emotion detection and self-assessment
- **AI-Powered Analytics** - LLM-generated insights and recommendations
- **Multi-modal Fusion** - Combined video, audio, and text analysis
- **User Authentication** - Email-based user management
- **Historical Analytics** - Session tracking and trend analysis

### 🔧 Infrastructure
- **AWS CDK Stack** - Complete infrastructure as code
- **Lambda Functions** - 8+ serverless functions deployed
- **DynamoDB Tables** - 4 tables for different data types
- **S3 Buckets** - 3 buckets for media storage
- **API Gateway** - RESTful API with CORS support
- **CloudFront** - CDN for frontend delivery

### 🚀 Deployment
- **Frontend** - Deployed to S3/CloudFront
- **Backend** - Lambda functions deployed to AWS
- **Database** - DynamoDB tables created and configured
- **Monitoring** - CloudWatch logs and metrics enabled

---

**Built with ❤️ using AWS Serverless Architecture and AI-Powered Insights** 