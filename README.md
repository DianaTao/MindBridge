# 🧠 MindBridge AI - Real-Time Emotional Intelligence Platform

## 🎯 Project Vision

**MindBridge AI** is a revolutionary real-time emotional intelligence platform that uses multi-modal AI to analyze facial expressions, voice patterns, and text sentiment to provide instant emotional insights and personalized mental wellness recommendations.

## 🚀 Key Features

- **Multi-modal AI Analysis**: Combines video, audio, and text analysis in real-time
- **Real-time Processing**: Lambda functions handle live streams with sub-second latency  
- **Local Development**: Full local development environment with mock AI services
- **AWS Integration**: Production-ready serverless architecture
- **Modern UI**: React frontend with Material-UI and real-time visualizations
- **Social Impact**: Addresses mental health crisis and remote work challenges

## 🏗️ Architecture

### System Overview
MindBridge uses a **Lambda-first serverless architecture** built on AWS with a **local development mode** for testing:

- **Frontend**: React TypeScript application with real-time WebSocket connection
- **Backend**: Python Flask server for local development, AWS Lambda for production
- **AI Services**: Amazon Rekognition, Transcribe, Comprehend, and Bedrock
- **Storage**: DynamoDB for real-time data, S3 for media storage
- **Infrastructure**: AWS CDK (Python) for infrastructure as code

### Local Development Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │  Mock AI Services│
│   (Port 3000)   │◄──►│   (Port 3001)   │◄──►│   (Local Mode)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Production Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  API Gateway    │    │  AWS Lambda     │
│   (S3/CloudFront)│◄──►│   (REST/WebSocket)│◄──►│   Functions     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   AWS AI Services│    │   DynamoDB/S3   │
                       │   (Rekognition,  │    │   (Storage)     │
                       │    Transcribe,   │    └─────────────────┘
                       │    Comprehend)   │
                       └─────────────────┘
```

## 📁 Project Structure

```
MindBridge/
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── CameraCapture.tsx    # Video capture and analysis
│   │   │   └── EmotionVisualization.tsx # Real-time emotion display
│   │   ├── services/           # API and WebSocket services
│   │   │   ├── ApiService.ts   # HTTP API client
│   │   │   └── WebSocketService.ts # WebSocket client
│   │   ├── types/              # TypeScript type definitions
│   │   └── App.tsx             # Main application component
│   ├── package.json            # Frontend dependencies
│   └── public/                 # Static assets
├── lambda_functions/           # AWS Lambda function code
│   ├── video_analysis/         # Facial emotion detection
│   │   ├── handler.py          # Main Lambda handler
│   │   ├── requirements.txt    # Python dependencies
│   │   └── [dependencies]/     # Installed packages
│   ├── audio_analysis/         # Voice pattern analysis
│   ├── emotion_fusion/         # Multi-modal AI fusion
│   └── dashboard/              # Real-time dashboard
├── infrastructure/             # AWS CDK infrastructure code
│   ├── mindbridge-stack.py     # Main CDK stack (Python)
│   ├── cdk.json               # CDK configuration
│   ├── requirements.txt       # CDK dependencies
│   └── README.md              # Infrastructure documentation
├── scripts/                   # Build and deployment scripts
│   ├── local-dev.sh          # Local development setup
│   ├── deploy.sh             # Production deployment
│   ├── deploy-aws-console.sh # AWS Console deployment
│   └── test-local.sh         # Local testing scripts
├── docs/                     # Documentation
│   └── ARCHITECTURE.md       # Detailed architecture docs
├── events/                   # Test event data
│   ├── test-video-analysis.json
│   ├── test-audio-analysis.json
│   └── test-health.json
├── run_local.py              # Local Flask development server
├── requirements.txt          # Root Python dependencies
├── requirements-simple.txt   # Simplified dependencies
├── README.md                 # This file
├── LOCAL_DEVELOPMENT.md      # Local development guide
├── AWS_SETUP.md              # AWS setup instructions
└── .gitignore               # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.8+ (Anaconda recommended)
- Node.js 18+
- Git

**Optional (for AWS deployment):**
- AWS CLI configured
- AWS CDK CLI installed

### Local Development Setup

#### 1. Clone and Setup
```bash
git clone <repository-url>
cd MindBridge

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements-simple.txt
```

#### 2. Start Backend Server
```bash
# Start the local Flask server with mock AI services
python3 run_local.py
```

**Expected Output:**
```
🧠 Starting MindBridge Local Development Server...
📡 Available endpoints:
  - GET  http://localhost:3001/health
  - GET  http://localhost:3001/test
  - POST http://localhost:3001/video-analysis
  - POST http://localhost:3001/audio-analysis
  - POST http://localhost:3001/emotion-fusion
  - ANY  http://localhost:3001/dashboard/<path>
🚀 Starting server on http://localhost:3001
```

#### 3. Start Frontend
```bash
# In a new terminal
cd frontend
npm install
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view mindbridge-frontend in the browser.
  Local:            http://localhost:3000
  On Your Network:  http://10.0.0.161:3000
```

#### 4. Test the Application
1. Open `http://localhost:3000` in your browser
2. Click "Start Camera" to begin video analysis
3. Allow camera permissions when prompted
4. You should see real-time emotion detection with mock data

### API Endpoints

**Local Development:**
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:3001`
- **Health Check**: `GET http://localhost:3001/health`
- **Video Analysis**: `POST http://localhost:3001/video-analysis`
- **Audio Analysis**: `POST http://localhost:3001/audio-analysis`
- **Emotion Fusion**: `POST http://localhost:3001/emotion-fusion`

**Test API with curl:**
```bash
# Health check
curl http://localhost:3001/health

# Video analysis (mock data)
curl -X POST http://localhost:3001/video-analysis \
  -H "Content-Type: application/json" \
  -d '{"frame_data": "test", "user_id": "test", "session_id": "test"}'
```

## 🛠️ Development Guide

### Backend Development

#### Lambda Functions
Each Lambda function follows this structure:
```python
# handler.py
def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))
        
        # Process data (with mock support for local development)
        if os.environ.get('STAGE') == 'local':
            result = mock_processing()
        else:
            result = real_aws_processing()
        
        # Return response
        return create_success_response(result)
    except Exception as e:
        return create_error_response(500, str(e))
```

#### Local Development Features
- **Mock AI Services**: Automatically uses mock data when `STAGE=local`
- **CORS Support**: Configured for frontend communication
- **Hot Reload**: Flask debug mode for instant code changes
- **Error Handling**: Comprehensive error logging and responses

### Frontend Development

#### Key Components
- **CameraCapture**: Handles video capture and real-time analysis
- **EmotionVisualization**: Displays emotion data with animations
- **ApiService**: HTTP client for backend communication
- **WebSocketService**: Real-time communication (currently disabled)

#### Development Features
- **TypeScript**: Full type safety
- **Material-UI**: Modern, responsive design
- **Real-time Updates**: Live emotion visualization
- **Error Handling**: User-friendly error messages

### Infrastructure Development

#### AWS CDK (Python)
```bash
cd infrastructure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy to AWS
cdk deploy
```

#### Infrastructure Components
- **Lambda Functions**: Serverless compute
- **API Gateway**: REST and WebSocket APIs
- **DynamoDB**: NoSQL database for emotion data
- **S3**: Media storage with lifecycle policies
- **IAM**: Secure permissions and roles

## 🔧 Troubleshooting

### Common Issues

#### 1. Camera Not Working
**Problem**: "Cannot access camera" error
**Solution**: 
- Check browser permissions
- Ensure HTTPS in production (required for camera access)
- Try refreshing the page

#### 2. API Connection Issues
**Problem**: "API Disconnected" message
**Solution**:
- Verify backend is running on port 3001
- Check CORS configuration
- Restart both frontend and backend

#### 3. Face Detection Not Working
**Problem**: Shows "0 faces detected"
**Solution**:
- In local mode, this is expected (mock data)
- Check backend logs for "MOCK FACE DETECTION TRIGGERED"
- Ensure camera is started and permissions granted

#### 4. Python Dependencies Issues
**Problem**: ModuleNotFoundError
**Solution**:
```bash
# Use Anaconda Python
/opt/anaconda3/bin/python run_local.py

# Or install dependencies in system Python
pip3 install flask flask-cors boto3
```

#### 5. Port Conflicts
**Problem**: "Address already in use"
**Solution**:
```bash
# Kill existing processes
pkill -f "python.*run_local"
pkill -f "react-scripts"

# Or change ports in configuration
```

### Debug Mode

#### Backend Logging
```bash
# Enable debug logging
export FLASK_DEBUG=1
python3 run_local.py
```

#### Frontend Debugging
- Open browser DevTools (F12)
- Check Console for errors
- Monitor Network tab for API calls

## 🚀 Production Deployment

### AWS Setup
1. **Configure AWS CLI**:
   ```bash
   aws configure
   ```

2. **Deploy Infrastructure**:
   ```bash
   cd infrastructure
   cdk bootstrap  # First time only
   cdk deploy
   ```

3. **Deploy Frontend**:
   ```bash
   cd frontend
   npm run build
   # Upload to S3/CloudFront
   ```

### Environment Variables
```bash
# Required for production
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional
STAGE=production
EMOTIONS_TABLE=mindbridge-emotions-prod
```

## 📊 AWS Services Used

- **AWS Lambda**: Serverless compute for all processing
- **Amazon Rekognition**: Facial emotion detection
- **Amazon Transcribe**: Speech-to-text conversion
- **Amazon Comprehend**: Text sentiment analysis
- **Amazon Bedrock**: Claude AI for advanced analysis
- **API Gateway**: REST and WebSocket APIs
- **DynamoDB**: NoSQL database for emotion data
- **S3**: Media storage with lifecycle policies
- **CloudWatch**: Logging and monitoring
- **IAM**: Security and permissions

## 🎯 Use Cases

1. **Personal Wellness**: Monitor emotional state during work sessions
2. **Team Collaboration**: Analyze team emotions during video calls
3. **Customer Service**: Help agents manage difficult conversations
4. **Online Learning**: Track student engagement and stress levels
5. **Mental Health**: Support therapy sessions and wellness tracking
6. **Remote Work**: Improve team communication and well-being



## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `python3 run_local.py`
5. Submit a pull request


## 🆘 Support

- **Documentation**: Check `docs/` folder for detailed guides
- **Local Development**: See `LOCAL_DEVELOPMENT.md`
- **AWS Setup**: See `AWS_SETUP.md`
- **Issues**: Create an issue on GitHub

## 🔗 Quick Links

- [Local Development Guide](LOCAL_DEVELOPMENT.md)
- [AWS Setup Instructions](AWS_SETUP.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)

---

**Built with ❤️ for better emotional intelligence and mental wellness** 