import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """Simple health check and API info endpoint"""
    
    # Debug: Log the event to understand the structure
    print(f"Event received: {json.dumps(event, default=str)}")
    
    # Get the path from different possible locations in the event
    path = event.get('path', '')
    resource = event.get('resource', '')
    path_parameters = event.get('pathParameters', {})
    
    # Determine if this is a health check or root endpoint
    is_health_endpoint = (
        path == '/health' or 
        path == '/prod/health' or 
        resource == '/health' or
        '/health' in path
    )
    
    print(f"Path: {path}, Resource: {resource}, Is health: {is_health_endpoint}")
    
    if is_health_endpoint:
        # Health check response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'MindBridge AI',
                'version': '1.0.0',
                'path': path,
                'resource': resource
            })
        }
    else:
        # Root endpoint - API information
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Welcome to MindBridge AI API',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'path': path,
                'resource': resource,
                'endpoints': {
                    'health': 'GET /health',
                    'video_analysis': 'POST /video-analysis',
                    'audio_analysis': 'POST /audio-analysis',
                    'emotion_fusion': 'POST /emotion-fusion',
                    'dashboard': 'GET /dashboard',
                    'dashboard_post': 'POST /dashboard'
                },
                'description': 'Real-time emotional intelligence platform using multi-modal AI analysis'
            })
        }
    
    print(f"Returning response: {json.dumps(response, default=str)}")
    return response 