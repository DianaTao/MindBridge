#!/usr/bin/env python3
"""
Simple Flask server for testing MindBridge video analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add lambda function paths
sys.path.append('./lambda_functions/video_analysis')
sys.path.append('./lambda_functions/audio_analysis')
sys.path.append('./lambda_functions/emotion_fusion')
sys.path.append('./lambda_functions/dashboard')

app = Flask(__name__)
CORS(app)

# Set environment variables for local development
os.environ['EMOTIONS_TABLE'] = 'mindbridge-emotions-local'
os.environ['TIMESTREAM_DB'] = 'MindBridge-local'
os.environ['STAGE'] = 'local'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Import Lambda handlers
try:
    from lambda_functions.video_analysis import handler as video_handler
    logger.info("✅ Video handler imported successfully")
except ImportError as e:
    logger.error(f"❌ Could not import video handler: {e}")
    video_handler = None

try:
    from lambda_functions.audio_analysis import handler as audio_handler
    logger.info("✅ Audio handler imported successfully")
except ImportError as e:
    logger.error(f"❌ Could not import audio handler: {e}")
    audio_handler = None

try:
    from lambda_functions.text_analysis import handler as text_handler
    logger.info("✅ Text handler imported successfully")
except ImportError as e:
    logger.error(f"❌ Could not import text handler: {e}")
    text_handler = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'MindBridge Local Test Server',
        'handlers': {
            'video': video_handler is not None,
            'audio': audio_handler is not None,
            'text': text_handler is not None
        }
    })

@app.route('/video-analysis', methods=['POST'])
def video_analysis():
    if not video_handler:
        return jsonify({'error': 'Video handler not available'}), 500
    
    try:
        logger.info("🎬 Video analysis request received")
        logger.info(f"Request data keys: {list(request.json.keys()) if request.json else 'None'}")
        
        # Create Lambda event
        event = {
            'body': json.dumps(request.json),
            'requestContext': {'requestId': 'local-test-' + str(os.getpid())}
        }
        
        logger.info("🔄 Calling video handler...")
        result = video_handler.lambda_handler(event, None)
        logger.info(f"✅ Video analysis completed: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Video analysis error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/audio-analysis', methods=['POST'])
def audio_analysis():
    if not audio_handler:
        return jsonify({'error': 'Audio handler not available'}), 500
    
    try:
        logger.info("🎤 Audio analysis request received")
        
        event = {
            'body': json.dumps(request.json),
            'requestContext': {'requestId': 'local-test-' + str(os.getpid())}
        }
        
        result = audio_handler.lambda_handler(event, None)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Audio analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/text-analysis', methods=['POST'])
def text_analysis():
    if not text_handler:
        return jsonify({'error': 'Text handler not available'}), 500
    
    try:
        logger.info("📝 Text analysis request received")
        
        event = {
            'body': json.dumps(request.json),
            'requestContext': {'requestId': 'local-test-' + str(os.getpid())}
        }
        
        result = text_handler.lambda_handler(event, None)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Text analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'MindBridge test server is running!',
        'endpoints': [
            'GET /health',
            'POST /video-analysis',
            'POST /audio-analysis', 
            'POST /text-analysis'
        ]
    })

if __name__ == '__main__':
    logger.info("🚀 Starting MindBridge test server...")
    logger.info("📍 Server will be available at: http://localhost:3002")
    logger.info("🔍 Health check: http://localhost:3002/health")
    logger.info("🧪 Test endpoint: http://localhost:3002/test")
    
    app.run(host='0.0.0.0', port=3002, debug=True) 