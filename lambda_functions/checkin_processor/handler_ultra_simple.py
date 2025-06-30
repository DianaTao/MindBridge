import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Ultra-simple handler that just returns success
    """
    try:
        logger.info("🔍 ULTRA SIMPLE HANDLER STARTED")
        logger.info(f"Event: {json.dumps(event, default=str)}")
        
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
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        try:
            request_data = json.loads(body)
            logger.info(f"✅ Request parsed: {list(request_data.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON error: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': f'Invalid JSON: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
        # Extract basic info
        user_id = request_data.get('user_id', 'anonymous')
        checkin_id = request_data.get('checkin_id', f"checkin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        
        # Simple success response
        response_data = {
            'status': 'ultra_simple_success',
            'message': 'Ultra simple handler completed successfully',
            'checkin_id': checkin_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'No data stored - testing only'
        }
        
        logger.info("✅ ULTRA SIMPLE HANDLER COMPLETED SUCCESSFULLY")
        
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
        logger.error(f"❌ ULTRA SIMPLE HANDLER ERROR: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': f'Ultra simple handler failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            })
        } 