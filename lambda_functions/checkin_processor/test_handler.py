"""
Simplified test handler to debug the 500 error
"""

import json
import boto3
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
try:
    dynamodb = boto3.resource('dynamodb')
    logger.info("✅ DynamoDB client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize DynamoDB client: {str(e)}")

# Environment variables
CHECKINS_TABLE = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins-dev')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simplified test handler
    """
    try:
        logger.info("🧪 TEST HANDLER STARTED")
        logger.info(f"Event: {json.dumps(event, default=str)}")
        logger.info(f"Environment variables: CHECKINS_TABLE={CHECKINS_TABLE}")
        
        # Test 1: Check if we can access DynamoDB table
        try:
            table = dynamodb.Table(CHECKINS_TABLE)
            logger.info(f"✅ Successfully accessed table: {CHECKINS_TABLE}")
        except Exception as e:
            logger.error(f"❌ Failed to access table {CHECKINS_TABLE}: {str(e)}")
            return create_error_response(500, f"Table access failed: {str(e)}")
        
        # Test 2: Check if we can parse the request body
        try:
            body = event.get('body', '')
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            request_data = json.loads(body)
            logger.info(f"✅ Successfully parsed request data: {json.dumps(request_data, default=str)}")
        except Exception as e:
            logger.error(f"❌ Failed to parse request body: {str(e)}")
            return create_error_response(400, f"Invalid request body: {str(e)}")
        
        # Test 3: Try to store a simple record
        try:
            test_record = {
                'user_id': request_data.get('user_id', 'test_user'),
                'timestamp': datetime.utcnow().isoformat(),
                'test_data': 'This is a test record',
                'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
            }
            
            table.put_item(Item=test_record)
            logger.info("✅ Successfully stored test record")
        except Exception as e:
            logger.error(f"❌ Failed to store test record: {str(e)}")
            return create_error_response(500, f"Storage failed: {str(e)}")
        
        # Success response
        return create_success_response({
            'status': 'test_successful',
            'message': 'All tests passed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Unexpected error: {str(e)}")

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    } 