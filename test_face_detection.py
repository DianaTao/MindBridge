#!/usr/bin/env python3
"""Test script for face detection debugging"""

import sys
import os
import json
import base64

# Add lambda function path
sys.path.insert(0, './lambda_functions/video_analysis')

# Set environment variables for local development
os.environ['EMOTIONS_TABLE'] = 'mindbridge-emotions-local'
os.environ['TIMESTREAM_DB'] = 'MindBridge-local'
os.environ['TIMESTREAM_TABLE'] = 'emotions'
os.environ['STAGE'] = 'local'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

from handler import lambda_handler

# Mock context for local testing
class MockContext:
    def get_remaining_time_in_millis(self):
        return 300000  # 5 minutes

    @property
    def function_name(self):
        return 'test-function'
    
    @property
    def function_version(self):
        return '$LATEST'
    
    @property
    def invoked_function_arn(self):
        return 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
    
    @property
    def memory_limit_in_mb(self):
        return 128
    
    @property
    def aws_request_id(self):
        return 'test-request-id'

# Create a test request
test_request = {
    'body': json.dumps({
        'frame_data': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
        'user_id': 'test-user',
        'session_id': 'test-session'
    }),
    'requestContext': {'requestId': 'test-request'},
    'httpMethod': 'POST',
    'path': '/video-analysis'
}

print("🧪 Testing face detection...")
print("=" * 50)

try:
    result = lambda_handler(test_request, MockContext())
    print("✅ Lambda handler executed successfully")
    print("Response:", json.dumps(result, indent=2))
    
    if 'body' in result:
        body = json.loads(result['body'])
        print("\n📋 Response body:", json.dumps(body, indent=2))
        print(f"\n🎭 Faces detected: {body.get('faces_detected', 'N/A')}")
        print(f"😊 Primary emotion: {body.get('primary_emotion', 'N/A')}")
        print(f"🎯 Confidence: {body.get('confidence', 'N/A')}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()