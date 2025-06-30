import json
import logging
import os
import boto3
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Minimal handler to test basic functionality
    """
    try:
        logger.info("🔍 MINIMAL HANDLER STARTED")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        # Parse request body
        logger.info("🔍 Step 1: Parsing request body")
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        try:
            request_data = json.loads(body)
            logger.info(f"✅ Request body parsed successfully")
            logger.info(f"📝 Request keys: {list(request_data.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {str(e)}")
            return create_error_response(400, f"Invalid JSON: {str(e)}")
        
        # Extract basic data
        logger.info("🔍 Step 2: Extracting data")
        user_id = request_data.get('user_id', 'anonymous')
        session_id = request_data.get('session_id', 'default')
        duration = request_data.get('duration', 0)
        checkin_id = request_data.get('checkin_id', f"checkin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Data extracted: user_id={user_id}, session_id={session_id}, duration={duration}")
        
        # Test DynamoDB storage
        logger.info("🔍 Step 3: Testing DynamoDB storage")
        try:
            checkins_table = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins')
            logger.info(f"📋 Using table: {checkins_table}")
            
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(checkins_table)
            
            # Create simple record
            record = {
                'user_id': user_id,
                'timestamp': timestamp,
                'checkin_id': checkin_id,
                'session_id': session_id,
                'duration': duration,
                'test_data': 'minimal_test',
                'ttl': int(datetime.utcnow().timestamp()) + 3600
            }
            
            logger.info(f"📝 Storing record: {json.dumps(record)}")
            table.put_item(Item=record)
            logger.info("✅ Record stored successfully")
            
        except Exception as e:
            logger.error(f"❌ DynamoDB error: {str(e)}")
            return create_error_response(500, f"DynamoDB failed: {str(e)}")
        
        # Success response
        response_data = {
            'status': 'minimal_success',
            'message': 'Minimal handler completed successfully',
            'checkin_id': checkin_id,
            'user_id': user_id,
            'timestamp': timestamp,
            'table': checkins_table
        }
        
        logger.info("✅ MINIMAL HANDLER COMPLETED SUCCESSFULLY")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"❌ MINIMAL HANDLER ERROR: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return create_error_response(500, f"Minimal handler failed: {str(e)}")

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create error response with CORS headers
    """
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