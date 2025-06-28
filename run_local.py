#!/usr/bin/env python3
"""
Simple Flask server to run MindBridge Lambda functions locally
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add lambda function paths to Python path
sys.path.insert(0, './lambda_functions/video_analysis')
sys.path.insert(0, './lambda_functions/audio_analysis')
sys.path.insert(0, './lambda_functions/emotion_fusion')
sys.path.insert(0, './lambda_functions/dashboard')

# Set environment variables for local development
os.environ['EMOTIONS_TABLE'] = 'mindbridge-emotions-local'
os.environ['TIMESTREAM_DB'] = 'MindBridge-local'
os.environ['TIMESTREAM_TABLE'] = 'emotions'
os.environ['STAGE'] = 'local'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Mock context for local testing
class MockContext:
    def get_remaining_time_in_millis(self):
        return 300000  # 5 minutes

    @property
    def function_name(self):
        return 'local-function'
    
    @property
    def function_version(self):
        return '$LATEST'
    
    @property
    def invoked_function_arn(self):
        return 'arn:aws:lambda:us-east-1:123456789012:function:local-function'
    
    @property
    def memory_limit_in_mb(self):
        return 128
    
    @property
    def aws_request_id(self):
        return 'local-request-id'

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# Try to import Lambda handlers
video_handler = None
audio_handler = None
fusion_handler = None
dashboard_handler = None

try:
    import handler as video_handler
    logger.info("✅ Video analysis handler imported")
except ImportError as e:
    logger.warning(f"⚠️ Could not import video handler: {e}")

try:
    sys.path.insert(0, './lambda_functions/audio_analysis')
    import handler as audio_handler
    logger.info("✅ Audio analysis handler imported")
except ImportError as e:
    logger.warning(f"⚠️ Could not import audio handler: {e}")

try:
    sys.path.insert(0, './lambda_functions/emotion_fusion')
    import handler as fusion_handler
    logger.info("✅ Emotion fusion handler imported")
except ImportError as e:
    logger.warning(f"⚠️ Could not import fusion handler: {e}")

try:
    sys.path.insert(0, './lambda_functions/dashboard')
    import handler as dashboard_handler
    logger.info("✅ Dashboard handler imported")
except ImportError as e:
    logger.warning(f"⚠️ Could not import dashboard handler: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MindBridge Local Development Server',
        'handlers': {
            'video': video_handler is not None,
            'audio': audio_handler is not None,
            'fusion': fusion_handler is not None,
            'dashboard': dashboard_handler is not None
        }
    })

@app.route('/video-analysis', methods=['POST'])
def video_analysis():
    """Video analysis endpoint"""
    if not video_handler:
        return jsonify({'error': 'Video handler not available'}), 500
    
    event = {
        'body': json.dumps(request.json),
        'requestContext': {'requestId': 'local-test'},
        'httpMethod': 'POST',
        'path': '/video-analysis'
    }
    
    try:
        result = video_handler.lambda_handler(event, MockContext())
        logger.info(f"Video analysis result: {result}")
        
        # Handle Lambda response format
        if isinstance(result, dict) and 'body' in result:
            # Extract body from Lambda response
            body_data = json.loads(result['body'])
            logger.info(f"Parsed body data: {body_data}")
            return jsonify(body_data)
        else:
            # Direct response
            logger.info(f"Direct response: {result}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/audio-analysis', methods=['POST'])
def audio_analysis():
    """Audio analysis endpoint"""
    if not audio_handler:
        return jsonify({'error': 'Audio handler not available'}), 500
    
    event = {
        'body': json.dumps(request.json),
        'requestContext': {'requestId': 'local-test'},
        'httpMethod': 'POST',
        'path': '/audio-analysis'
    }
    
    try:
        result = audio_handler.lambda_handler(event, MockContext())
        
        # Handle Lambda response format
        if isinstance(result, dict) and 'body' in result:
            # Extract body from Lambda response
            body_data = json.loads(result['body'])
            return jsonify(body_data)
        else:
            # Direct response
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Audio analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/emotion-fusion', methods=['POST'])
def emotion_fusion():
    """Emotion fusion endpoint"""
    if not fusion_handler:
        return jsonify({'error': 'Fusion handler not available'}), 500
    
    event = {
        'body': json.dumps(request.json),
        'requestContext': {'requestId': 'local-test'},
        'httpMethod': 'POST',
        'path': '/emotion-fusion'
    }
    
    try:
        result = fusion_handler.lambda_handler(event, MockContext())
        
        # Handle Lambda response format
        if isinstance(result, dict) and 'body' in result:
            # Extract body from Lambda response
            body_data = json.loads(result['body'])
            return jsonify(body_data)
        else:
            # Direct response
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Emotion fusion error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dashboard(path):
    """Dashboard endpoints"""
    if not dashboard_handler:
        return jsonify({'error': 'Dashboard handler not available'}), 500
    
    event = {
        'body': json.dumps(request.json) if request.json else '{}',
        'pathParameters': {'proxy': path},
        'requestContext': {'requestId': 'local-test'},
        'httpMethod': request.method,
        'path': f'/dashboard/{path}'
    }
    
    try:
        result = dashboard_handler.lambda_handler(event, MockContext())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'MindBridge Lambda Functions are running locally!',
        'endpoints': [
            'GET /health - Health check',
            'POST /video-analysis - Video emotion analysis',
            'POST /audio-analysis - Audio emotion analysis', 
            'POST /emotion-fusion - Multi-modal emotion fusion',
            'GET|POST /dashboard/<path> - Dashboard and analytics'
        ]
    })

if __name__ == '__main__':
    print("🧠 Starting MindBridge Local Development Server...")
    print("📡 Available endpoints:")
    print("  - GET  http://localhost:3001/health")
    print("  - GET  http://localhost:3001/test")
    print("  - POST http://localhost:3001/video-analysis")
    print("  - POST http://localhost:3001/audio-analysis")
    print("  - POST http://localhost:3001/emotion-fusion")
    print("  - ANY  http://localhost:3001/dashboard/<path>")
    print("🚀 Starting server on http://localhost:3001")
    
    app.run(host='0.0.0.0', port=3001, debug=True) 