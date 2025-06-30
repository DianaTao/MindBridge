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
            
            dynamodb_endpoint = os.environ.get('DYNAMODB_ENDPOINT')
            if dynamodb_endpoint:
                # Use local DynamoDB for development
                dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_endpoint)
                logger.info(f"🔗 Using local DynamoDB endpoint: {dynamodb_endpoint}")
            else:
                # Use AWS DynamoDB for production
                dynamodb = boto3.resource('dynamodb')
                logger.info("🔗 Using AWS DynamoDB service")
            table = dynamodb.Table(checkins_table)
            
            # Extract full check-in data
            emotion_analysis = request_data.get('emotion_analysis', {})
            self_assessment = request_data.get('self_assessment', {})
            
            # Create complete record with full data
            record = {
                'user_id': user_id,
                'timestamp': timestamp,
                'checkin_id': checkin_id,
                'session_id': session_id,
                'duration': duration,
                'emotion_analysis': emotion_analysis,
                'self_assessment': self_assessment,
                'overall_score': calculate_overall_score(emotion_analysis, self_assessment),
                'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
            }
            
            logger.info(f"📝 Storing full record: {json.dumps(record, default=str)}")
            table.put_item(Item=record)
            logger.info("✅ Full record stored successfully")
            
        except Exception as e:
            logger.error(f"❌ DynamoDB error: {str(e)}")
            return create_error_response(500, f"DynamoDB failed: {str(e)}")
        
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
            'message': 'Check-in processed successfully with full data'
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