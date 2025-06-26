# 🛠️ MindBridge Local Development Guide

## Overview
This guide explains how to run the MindBridge AI backend locally for development and testing purposes. The backend consists of Lambda functions that can be run locally using AWS SAM or serverless-offline.

## 🏗️ Architecture Summary

### Lambda Functions
1. **Video Analysis Lambda** - Facial emotion detection using Rekognition
2. **Audio Analysis Lambda** - Voice pattern and sentiment analysis
3. **Emotion Fusion Lambda** - Multi-modal AI fusion using Bedrock
4. **Dashboard Lambda** - WebSocket handling and analytics

### API Endpoints

#### WebSocket API (Real-time)
- **Connection**: `wss://localhost:3001`
- **Routes**:
  - `$connect` - WebSocket connection establishment
  - `$disconnect` - WebSocket disconnection
  - `$default` - Default message handling
  - `video-analysis` - Real-time video frame analysis
  - `audio-analysis` - Real-time audio stream analysis

#### HTTP API (REST)
- **Base URL**: `http://localhost:3000`
- **Routes**:
  - `GET /dashboard/health` - Health check
  - `POST /dashboard/analytics` - Get emotion analytics
  - `GET /dashboard/session/{sessionId}` - Get session data
  - `POST /dashboard/query` - Custom analytics queries

## 🚀 Quick Setup

### Prerequisites
```bash
# Install required tools
npm install -g aws-cdk aws-sam-cli serverless
pip install aws-sam-cli

# Verify installations
sam --version
cdk --version
serverless --version
```

### Option 1: Using AWS SAM Local (Recommended)

1. **Install SAM Template**
```bash
# Create SAM template
cat > template.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: MindBridge Local Development

Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
    Environment:
      Variables:
        EMOTIONS_TABLE: mindbridge-emotions-local
        TIMESTREAM_DB: MindBridge-local
        TIMESTREAM_TABLE: emotions
        STAGE: local

Resources:
  VideoAnalysisFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/video_analysis/
      Handler: handler.lambda_handler
      Events:
        VideoAnalysis:
          Type: Api
          Properties:
            Path: /video-analysis
            Method: post

  AudioAnalysisFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/audio_analysis/
      Handler: handler.lambda_handler
      Events:
        AudioAnalysis:
          Type: Api
          Properties:
            Path: /audio-analysis
            Method: post

  EmotionFusionFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/emotion_fusion/
      Handler: handler.lambda_handler
      Timeout: 120

  DashboardFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda_functions/dashboard/
      Handler: handler.lambda_handler
      Events:
        Dashboard:
          Type: Api
          Properties:
            Path: /dashboard/{proxy+}
            Method: any
        WebSocket:
          Type: Api
          Properties:
            Path: /ws/{proxy+}
            Method: any

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Stage/"
EOF
```

2. **Start Local Development**
```bash
# Install dependencies for all Lambda functions
for dir in lambda_functions/*/; do
    if [ -f "$dir/requirements.txt" ]; then
        echo "Installing dependencies for $dir"
        pip install -r "$dir/requirements.txt" -t "$dir"
    fi
done

# Start SAM local API
sam local start-api --port 3000

# In another terminal, start WebSocket (if needed)
sam local start-lambda --port 3001
```

### Option 2: Using Serverless Framework

1. **Install Serverless Config**
```bash
# Create serverless.yml
cat > serverless.yml << 'EOF'
service: mindbridge-local

provider:
  name: aws
  runtime: python3.9
  stage: local
  region: us-east-1
  environment:
    EMOTIONS_TABLE: mindbridge-emotions-local
    TIMESTREAM_DB: MindBridge-local
    STAGE: local

functions:
  videoAnalysis:
    handler: lambda_functions/video_analysis/handler.lambda_handler
    events:
      - http:
          path: video-analysis
          method: post
          cors: true

  audioAnalysis:
    handler: lambda_functions/audio_analysis/handler.lambda_handler
    events:
      - http:
          path: audio-analysis
          method: post
          cors: true

  emotionFusion:
    handler: lambda_functions/emotion_fusion/handler.lambda_handler
    timeout: 120

  dashboard:
    handler: lambda_functions/dashboard/handler.lambda_handler
    events:
      - http:
          path: dashboard/{proxy+}
          method: any
          cors: true
      - websocket:
          route: $connect
      - websocket:
          route: $disconnect
      - websocket:
          route: $default

plugins:
  - serverless-offline
  - serverless-python-requirements

custom:
  serverless-offline:
    httpPort: 3000
    websocketPort: 3001
EOF

# Install serverless plugins
npm install serverless-offline serverless-python-requirements

# Start offline mode
serverless offline start
```

### Option 3: Direct Python Execution (Development Only)

1. **Create Local Test Server**
```bash
# Create local_server.py
cat > local_server.py << 'EOF'
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import os
import json

# Add lambda function paths
sys.path.append('./lambda_functions/video_analysis')
sys.path.append('./lambda_functions/audio_analysis')
sys.path.append('./lambda_functions/emotion_fusion')
sys.path.append('./lambda_functions/dashboard')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Import Lambda handlers
try:
    from lambda_functions.video_analysis import handler as video_handler
    from lambda_functions.audio_analysis import handler as audio_handler
    from lambda_functions.emotion_fusion import handler as fusion_handler
    from lambda_functions.dashboard import handler as dashboard_handler
except ImportError as e:
    print(f"Warning: Could not import handlers: {e}")

@app.route('/video-analysis', methods=['POST'])
def video_analysis():
    event = {
        'body': json.dumps(request.json),
        'requestContext': {'requestId': 'local-test'}
    }
    try:
        result = video_handler.lambda_handler(event, None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio-analysis', methods=['POST'])
def audio_analysis():
    event = {
        'body': json.dumps(request.json),
        'requestContext': {'requestId': 'local-test'}
    }
    try:
        result = audio_handler.lambda_handler(event, None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dashboard(path):
    event = {
        'body': json.dumps(request.json) if request.json else '{}',
        'pathParameters': {'proxy': path},
        'requestContext': {'requestId': 'local-test'}
    }
    try:
        result = dashboard_handler.lambda_handler(event, None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to MindBridge local server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('video-analysis')
def handle_video_analysis(data):
    try:
        event = {
            'body': json.dumps(data),
            'requestContext': {
                'requestId': 'local-ws-test',
                'routeKey': 'video-analysis',
                'connectionId': 'local-connection'
            }
        }
        result = video_handler.lambda_handler(event, None)
        emit('video-analysis-result', result)
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)
EOF

# Install Flask and dependencies
pip install flask flask-socketio

# Run local server
python local_server.py
```

## 🔧 Mock AWS Services

### DynamoDB Local
```bash
# Install DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local

# Create local tables
aws dynamodb create-table \
    --table-name mindbridge-emotions-local \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000
```

### S3 Local (LocalStack)
```bash
# Install and run LocalStack
docker run -p 4566:4566 localstack/localstack

# Create local S3 bucket
aws s3 mb s3://mindbridge-media-local --endpoint-url http://localhost:4566
```

## 📋 API Testing

### WebSocket Testing
```javascript
// Connect to local WebSocket
const ws = new WebSocket('ws://localhost:3001');

// Send video analysis request
ws.send(JSON.stringify({
    action: 'video-analysis',
    frame_data: 'base64_encoded_image_data',
    user_id: 'test_user',
    session_id: 'test_session'
}));

// Listen for responses
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### HTTP API Testing
```bash
# Test video analysis
curl -X POST http://localhost:3000/video-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "frame_data": "base64_image_data",
    "user_id": "test_user",
    "session_id": "test_session"
  }'

# Test audio analysis
curl -X POST http://localhost:3000/audio-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_audio_data",
    "user_id": "test_user",
    "session_id": "test_session"
  }'

# Test dashboard analytics
curl -X POST http://localhost:3000/dashboard/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "time_range": "1h"
  }'
```

## 🧪 Testing with Mock Data

### Create Test Data
```python
# test_data.py
import base64
import json
import requests

# Mock video frame data
def create_mock_frame():
    # Simple 1x1 pixel PNG (base64)
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

# Test video analysis
def test_video_analysis():
    response = requests.post('http://localhost:3000/video-analysis', json={
        'frame_data': create_mock_frame(),
        'user_id': 'test_user',
        'session_id': 'test_session'
    })
    print(f"Video Analysis: {response.json()}")

# Test audio analysis
def test_audio_analysis():
    response = requests.post('http://localhost:3000/audio-analysis', json={
        'audio_data': 'mock_audio_data',
        'user_id': 'test_user',
        'session_id': 'test_session'
    })
    print(f"Audio Analysis: {response.json()}")

if __name__ == '__main__':
    test_video_analysis()
    test_audio_analysis()
```

## 🐛 Debugging

### Enable Debug Logging
```python
# Add to Lambda handlers
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

1. **Missing AWS Credentials**
```bash
# Set local credentials
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

2. **Import Errors**
```bash
# Install dependencies in Lambda directories
cd lambda_functions/video_analysis
pip install -r requirements.txt -t .
```

3. **Port Conflicts**
```bash
# Change default ports if needed
sam local start-api --port 3002
```

## 🔄 Hot Reload Development

### Watch for Changes
```bash
# Using nodemon for auto-restart
npm install -g nodemon
nodemon --exec "sam local start-api" --ext py

# Or use entr for file watching
ls lambda_functions/**/*.py | entr -r sam local start-api
```

## 🚀 Deployment Testing

### Test Before Deploy
```bash
# Run all tests
python -m pytest tests/

# Test with real AWS services (staging)
export STAGE=staging
cdk deploy --context environment=staging
```

## 📝 Environment Variables

### Required for Local Development
```bash
export EMOTIONS_TABLE=mindbridge-emotions-local
export TIMESTREAM_DB=MindBridge-local
export TIMESTREAM_TABLE=emotions
export STAGE=local
export AWS_ENDPOINT_URL=http://localhost:4566  # For LocalStack
```

### Optional AWS Service Mocking
```bash
export REKOGNITION_ENDPOINT=http://localhost:4566
export COMPREHEND_ENDPOINT=http://localhost:4566
export TRANSCRIBE_ENDPOINT=http://localhost:4566
export BEDROCK_ENDPOINT=http://localhost:4566
```

This guide provides multiple approaches for local development, from simple direct execution to full SAM local setup. Choose the method that best fits your development workflow. 