#!/usr/bin/env python3
"""
Simple Flask test server for MindBridge video analysis
Uses actual emotion detection instead of mock data
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Add the lambda_functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda_functions'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Set environment variables for AWS Rekognition
os.environ['STAGE'] = 'production'
os.environ['AWS_ACCESS_KEY_ID'] = 'your_actual_aws_access_key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_actual_aws_secret_key'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['EMOTIONS_TABLE'] = 'mindbridge-emotions'
os.environ['FUSION_LAMBDA_ARN'] = ''

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'mindbridge-video-analysis',
        'version': '1.0.0'
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify server is running"""
    return jsonify({
        'message': 'MindBridge Video Analysis Server is running!',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/health',
            'video_analysis': '/video-analysis'
        }
    })

@app.route('/video-analysis', methods=['POST'])
def video_analysis():
    """Video analysis endpoint using actual emotion detection"""
    try:
        logger.info("🎬 Video analysis request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Request data keys: {list(data.keys())}")
        
        # Call the actual video handler
        logger.info("🔄 Calling video handler...")
        
        # Import the handler from the virtual environment
        try:
            from lambda_functions.video_analysis import handler as video_handler
            logger.info("✅ Video handler imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import video handler: {e}")
            return jsonify({'error': 'Video handler not available'}), 500
        
        # Create event structure for Lambda handler
        event = {
            'body': json.dumps(data),
            'requestContext': {
                'requestId': f'local-test-{int(datetime.utcnow().timestamp())}'
            }
        }
        
        # Call the handler
        response = video_handler.lambda_handler(event, None)
        
        logger.info(f"✅ Video analysis completed: {response}")
        
        # Return the response body
        if response['statusCode'] == 200:
            return json.loads(response['body']), 200
        else:
            return json.loads(response['body']), response['statusCode']
            
    except Exception as e:
        logger.error(f"❌ Error in video analysis: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/video-analysis/stop', methods=['POST'])
def video_analysis_stop():
    """Video analysis stop endpoint"""
    try:
        logger.info("⏹️ Video analysis stop request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Stop request data: {data}")
        
        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Video analysis stopped successfully',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': data.get('user_id'),
            'session_id': data.get('session_id')
        }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in video analysis stop: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/audio-analysis', methods=['POST'])
def audio_analysis():
    """Audio analysis endpoint"""
    try:
        logger.info("🎵 Audio analysis request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Audio request data keys: {list(data.keys())}")
        
        # Return mock audio analysis response
        return jsonify({
            'status': 'success',
            'primary_emotion': 'neutral',
            'confidence': 0.85,
            'emotions': [
                {'emotion': 'neutral', 'confidence': 0.85},
                {'emotion': 'calm', 'confidence': 0.10},
                {'emotion': 'focused', 'confidence': 0.05}
            ],
            'sentiment': 'neutral',
            'transcript': 'Audio analysis completed',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in audio analysis: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/emotion-fusion', methods=['POST'])
def emotion_fusion():
    """Emotion fusion endpoint"""
    try:
        logger.info("🧠 Emotion fusion request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Fusion request data keys: {list(data.keys())}")
        
        # Return mock fusion response
        return jsonify({
            'status': 'success',
            'fused_emotion': 'neutral',
            'confidence': 0.90,
            'modalities': ['video', 'audio'],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in emotion fusion: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/dashboard/analytics', methods=['POST'])
def dashboard_analytics():
    """Dashboard analytics endpoint"""
    try:
        logger.info("📊 Dashboard analytics request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Analytics request data keys: {list(data.keys())}")
        
        # Return mock analytics response
        return jsonify({
            'status': 'success',
            'total_sessions': 1,
            'total_detections': 5,
            'average_confidence': 0.87,
            'dominant_emotion': 'neutral',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in dashboard analytics: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/dashboard/session/<session_id>', methods=['GET'])
def get_session_data(session_id):
    """Get session data endpoint"""
    try:
        logger.info(f"📋 Session data request received for session: {session_id}")
        
        # Return mock session data
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'detections': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'emotion': 'neutral',
                    'confidence': 0.85,
                    'modality': 'video'
                }
            ],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"❌ Error in session data: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting MindBridge video test server...")
    logger.info("📍 Server will be available at: http://localhost:3001")
    logger.info("🔍 Health check: http://localhost:3001/health")
    logger.info("🧪 Test endpoint: http://localhost:3001/test")
    
    # Run the server
    app.run(host='0.0.0.0', port=3001, debug=True) 