#!/bin/bash

# MindBridge Local Development Setup Script
# This script sets up and runs the MindBridge backend locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PORT=${PORT:-3000}
WS_PORT=${WS_PORT:-3001}
METHOD=${METHOD:-sam}  # sam, serverless, or flask
DOCKER_SERVICES=${DOCKER_SERVICES:-true}

echo -e "${BLUE}🧠 MindBridge Local Development Setup${NC}"
echo "================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    local missing_deps=()
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if ! command_exists pip; then
        missing_deps+=("pip")
    fi
    
    if ! command_exists node; then
        missing_deps+=("node.js")
    fi
    
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    if [[ "$METHOD" == "sam" ]] && ! command_exists sam; then
        missing_deps+=("aws-sam-cli")
    fi
    
    if [[ "$METHOD" == "serverless" ]] && ! command_exists serverless; then
        missing_deps+=("serverless")
    fi
    
    if [[ "$DOCKER_SERVICES" == "true" ]] && ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies: ${missing_deps[*]}${NC}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
}

# Function to install Python dependencies
install_python_deps() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    for dir in lambda_functions/*/; do
        if [ -f "$dir/requirements.txt" ]; then
            echo "Installing dependencies for $dir"
            pip install -r "$dir/requirements.txt" -t "$dir" --quiet
        fi
    done
    
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
}

# Function to start Docker services
start_docker_services() {
    if [[ "$DOCKER_SERVICES" != "true" ]]; then
        return
    fi
    
    echo -e "${BLUE}Starting local AWS services...${NC}"
    
    # Start DynamoDB Local
    if ! docker ps | grep -q "amazon/dynamodb-local"; then
        echo "Starting DynamoDB Local..."
        docker run -d -p 8000:8000 --name mindbridge-dynamodb amazon/dynamodb-local >/dev/null
    fi
    
    # Start LocalStack for S3, etc.
    if ! docker ps | grep -q "localstack/localstack"; then
        echo "Starting LocalStack..."
        docker run -d -p 4566:4566 --name mindbridge-localstack localstack/localstack >/dev/null
    fi
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 5
    
    # Create DynamoDB table
    aws dynamodb create-table \
        --table-name mindbridge-emotions-local \
        --attribute-definitions \
            AttributeName=user_id,AttributeType=S \
            AttributeName=timestamp,AttributeType=S \
        --key-schema \
            AttributeName=user_id,KeyType=HASH \
            AttributeName=timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --endpoint-url http://localhost:8000 \
        >/dev/null 2>&1 || echo "DynamoDB table already exists"
    
    # Create S3 bucket
    aws s3 mb s3://mindbridge-media-local \
        --endpoint-url http://localhost:4566 \
        >/dev/null 2>&1 || echo "S3 bucket already exists"
    
    echo -e "${GREEN}✅ Local AWS services started${NC}"
}

# Function to create SAM template
create_sam_template() {
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
        AWS_ENDPOINT_URL: http://localhost:4566

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

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Stage/"
EOF
}

# Function to run with SAM
run_sam() {
    echo -e "${BLUE}Setting up SAM Local...${NC}"
    create_sam_template
    
    echo -e "${BLUE}Starting SAM Local API on port $PORT...${NC}"
    echo -e "${YELLOW}API will be available at: http://localhost:$PORT${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    
    # Set environment variables
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=us-east-1
    
    sam local start-api --port "$PORT"
}

# Function to create serverless config
create_serverless_config() {
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
}

# Function to run with Serverless
run_serverless() {
    echo -e "${BLUE}Setting up Serverless Framework...${NC}"
    create_serverless_config
    
    # Install plugins if not already installed
    if [ ! -d "node_modules" ]; then
        npm install serverless-offline serverless-python-requirements
    fi
    
    echo -e "${BLUE}Starting Serverless Offline on port $PORT...${NC}"
    echo -e "${YELLOW}API will be available at: http://localhost:$PORT${NC}"
    echo -e "${YELLOW}WebSocket will be available at: ws://localhost:$WS_PORT${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    
    # Set environment variables
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=us-east-1
    
    serverless offline start
}

# Function to create Flask server
create_flask_server() {
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

# Set environment variables
os.environ['EMOTIONS_TABLE'] = 'mindbridge-emotions-local'
os.environ['TIMESTREAM_DB'] = 'MindBridge-local'
os.environ['STAGE'] = 'local'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Import Lambda handlers
try:
    from lambda_functions.video_analysis import handler as video_handler
    from lambda_functions.audio_analysis import handler as audio_handler
    from lambda_functions.emotion_fusion import handler as fusion_handler
    from lambda_functions.dashboard import handler as dashboard_handler
except ImportError as e:
    print(f"Warning: Could not import handlers: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'MindBridge Local'})

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
}

# Function to run with Flask
run_flask() {
    echo -e "${BLUE}Setting up Flask development server...${NC}"
    create_flask_server
    
    # Install Flask dependencies
    pip install flask flask-socketio
    
    echo -e "${BLUE}Starting Flask server on port $PORT...${NC}"
    echo -e "${YELLOW}API will be available at: http://localhost:$PORT${NC}"
    echo -e "${YELLOW}WebSocket will be available at: http://localhost:$PORT${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    
    python local_server.py
}

# Function to cleanup
cleanup() {
    echo -e "\n${BLUE}Cleaning up...${NC}"
    
    # Stop Docker containers
    docker stop mindbridge-dynamodb mindbridge-localstack >/dev/null 2>&1 || true
    docker rm mindbridge-dynamodb mindbridge-localstack >/dev/null 2>&1 || true
    
    # Remove temporary files
    rm -f template.yaml serverless.yml local_server.py
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --method METHOD     Development method (sam|serverless|flask) [default: sam]"
    echo "  -p, --port PORT         HTTP API port [default: 3000]"
    echo "  -w, --ws-port PORT      WebSocket port [default: 3001]"
    echo "  -d, --docker            Start Docker services [default: true]"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Start with SAM Local"
    echo "  $0 -m flask            # Start with Flask"
    echo "  $0 -m serverless -p 8080  # Start with Serverless on port 8080"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--method)
            METHOD="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--ws-port)
            WS_PORT="$2"
            shift 2
            ;;
        -d|--docker)
            DOCKER_SERVICES="true"
            shift
            ;;
        --no-docker)
            DOCKER_SERVICES="false"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Trap Ctrl+C for cleanup
trap cleanup EXIT

# Main execution
main() {
    check_prerequisites
    install_python_deps
    start_docker_services
    
    case $METHOD in
        sam)
            run_sam
            ;;
        serverless)
            run_serverless
            ;;
        flask)
            run_flask
            ;;
        *)
            echo -e "${RED}Unknown method: $METHOD${NC}"
            echo "Supported methods: sam, serverless, flask"
            exit 1
            ;;
    esac
}

# Run main function
main 