import json
import logging
import os
import boto3
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
    dynamodb = None

# Environment variables
CHECKINS_TABLE = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Basic handler that stores full check-in data without LLM generation
    """
    try:
        logger.info("🔍 BASIC HANDLER STARTED")
        
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
        
        # Extract data
        logger.info("🔍 Step 2: Extracting data")
        checkin_id = request_data.get('checkin_id', f"checkin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        user_id = request_data.get('user_id', 'anonymous')
        session_id = request_data.get('session_id', 'default')
        duration = request_data.get('duration', 0)
        emotion_analysis = request_data.get('emotion_analysis', {})
        self_assessment = request_data.get('self_assessment', {})
        timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Data extracted: user_id={user_id}, session_id={session_id}, duration={duration}")
        
        # Store check-in data
        logger.info("🔍 Step 3: Storing check-in data")
        try:
            if dynamodb is None:
                raise Exception("DynamoDB client not available")
            
            table = dynamodb.Table(CHECKINS_TABLE)
            logger.info(f"📋 Using table: {CHECKINS_TABLE}")
            
            # Create record with full data
            record = {
                'user_id': user_id,
                'timestamp': timestamp,
                'checkin_id': checkin_id,
                'session_id': session_id,
                'duration': duration,
                'emotion_analysis': emotion_analysis if emotion_analysis else {},
                'self_assessment': self_assessment if self_assessment else {},
                'overall_score': calculate_overall_score(emotion_analysis, self_assessment),
                'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
            }
            
            # Test JSON serialization
            try:
                json.dumps(record)
                logger.info(f"📝 Record is JSON serializable")
            except Exception as e:
                logger.warning(f"⚠️ Record not JSON serializable, cleaning up: {str(e)}")
                record = {
                    'user_id': str(user_id),
                    'timestamp': str(timestamp),
                    'checkin_id': str(checkin_id),
                    'session_id': str(session_id),
                    'duration': int(duration) if isinstance(duration, (int, float)) else 0,
                    'emotion_analysis': {},
                    'self_assessment': {},
                    'overall_score': 50.0,
                    'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
                }
            
            logger.info(f"📝 Storing record: {json.dumps(record, default=str)}")
            table.put_item(Item=record)
            logger.info("✅ Record stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Storage error: {str(e)}")
            return create_error_response(500, f"Storage failed: {str(e)}")
        
        # Create simple fallback report
        logger.info("🔍 Step 4: Creating fallback report")
        fallback_report = {
            "emotional_summary": "Mental health check-in completed successfully.",
            "key_insights": ["Check-in data recorded", "Baseline established"],
            "recommendations": ["Continue regular check-ins", "Monitor patterns"],
            "trend_analysis": "Initial data point",
            "overall_assessment": "Good engagement with mental health monitoring",
            "mood_score": 7,
            "confidence_level": "medium",
            "fallback_generated": True
        }
        
        # Store the report
        logger.info("🔍 Step 5: Storing report")
        try:
            table.update_item(
                Key={'user_id': user_id, 'timestamp': timestamp},
                UpdateExpression='SET llm_report = :report',
                ExpressionAttributeValues={':report': fallback_report}
            )
            logger.info("✅ Report stored successfully")
        except Exception as e:
            logger.warning(f"⚠️ Report storage failed: {str(e)}")
        
        # Success response
        response_data = {
            'status': 'completed',
            'checkin_id': checkin_id,
            'llm_report': fallback_report,
            'timestamp': timestamp,
            'message': 'Check-in processed successfully with fallback report'
        }
        
        logger.info("✅ BASIC HANDLER COMPLETED SUCCESSFULLY")
        
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
        logger.error(f"❌ BASIC HANDLER ERROR: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return create_error_response(500, f"Basic handler failed: {str(e)}")

def calculate_overall_score(emotion_analysis: Dict[str, Any], self_assessment: Dict[str, Any]) -> float:
    """
    Calculate overall wellness score with defensive programming
    """
    try:
        # Emotion analysis score (0-100)
        emotion_score = 50.0
        if emotion_analysis and isinstance(emotion_analysis, dict):
            emotion_score = emotion_analysis.get('average_wellbeing', 50.0)
            if not isinstance(emotion_score, (int, float)):
                emotion_score = 50.0
        
        # Self-assessment score (0-100)
        assessment_score = 50.0
        if self_assessment and isinstance(self_assessment, dict):
            try:
                scores = []
                score_fields = ['overall_mood', 'energy_level', 'stress_level', 'sleep_quality', 'social_connection', 'motivation']
                
                for field in score_fields:
                    value = self_assessment.get(field, 5)
                    if isinstance(value, (int, float)):
                        scores.append(float(value) * 10)
                    else:
                        scores.append(50.0)
                
                if scores:
                    assessment_score = sum(scores) / len(scores)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error calculating assessment score: {str(e)}, using default")
                assessment_score = 50.0
        
        # Weighted average (60% emotion, 40% self-assessment)
        overall_score = (emotion_score * 0.6) + (assessment_score * 0.4)
        return round(overall_score, 1)
        
    except Exception as e:
        logger.error(f"❌ Error calculating overall score: {str(e)}")
        return 50.0

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