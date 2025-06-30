import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
try:
    dynamodb = boto3.resource('dynamodb')
    logger.info("✅ AWS clients initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AWS clients: {str(e)}")

# Environment variables
CHECKINS_TABLE = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins')

def convert_decimals(obj):
    """
    Convert Decimal types to JSON serializable types
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

def create_simple_sample_data(user_id: str) -> bool:
    """
    Create simple sample data for a user
    """
    try:
        logger.info(f"📝 Creating simple sample data for user: {user_id}")
        
        table = dynamodb.Table(CHECKINS_TABLE)
        
        # Create one sample check-in
        sample_record = {
            'user_id': str(user_id),
            'timestamp': datetime.utcnow().isoformat(),
            'checkin_id': f'sample_checkin_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
            'session_id': 'sample_session',
            'duration': 120,
            'emotion_analysis': {
                'dominant_emotion': 'happy',
                'confidence': 0.85,
                'intensity': 75
            },
            'self_assessment': {
                'mood_score': 8,
                'energy_level': 7,
                'stress_level': 3
            },
            'overall_score': Decimal('75.0'),
            'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
        }
        
        table.put_item(Item=sample_record)
        logger.info(f"✅ Created sample data for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {str(e)}")
        return False

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler with simple auto sample creation
    """
    try:
        logger.info("=" * 60)
        logger.info("📊 CHECK-IN DATA RETRIEVER WITH SIMPLE AUTO SAMPLE")
        logger.info("=" * 60)
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': ''
            }
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'anonymous')
        days = int(query_params.get('days', 30))
        limit = int(query_params.get('limit', 50))
        
        logger.info(f"🔍 Requesting data for user: {user_id}")
        
        # Retrieve check-in data
        checkins = retrieve_checkins(user_id, days, limit)
        
        # If no check-ins found, create simple sample data
        if not checkins:
            logger.info(f"📝 No check-ins found for user {user_id}, creating sample data...")
            sample_created = create_simple_sample_data(user_id)
            if sample_created:
                # Retrieve again after creating sample data
                checkins = retrieve_checkins(user_id, days, limit)
                logger.info(f"✅ Retrieved {len(checkins)} check-ins after creating sample data")
        
        # Convert Decimal types to JSON serializable types
        checkins = convert_decimals(checkins)
        
        # Generate analytics summary
        analytics_summary = generate_analytics_summary(checkins)
        
        result = {
            'checkins': checkins,
            'analytics_summary': analytics_summary,
            'total_count': len(checkins),
            'query_params': {
                'user_id': user_id,
                'days': days,
                'limit': limit
            }
        }
        
        logger.info(f"✅ SUCCESS: Retrieved {len(checkins)} check-ins")
        logger.info("=" * 60)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR in check-in retrieval: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'error': f"Check-in retrieval failed: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def retrieve_checkins(user_id: str, days: int, limit: int) -> List[Dict[str, Any]]:
    """
    Retrieve check-in data from DynamoDB
    """
    try:
        table = dynamodb.Table(CHECKINS_TABLE)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"🔍 Querying for user_id: {user_id}")
        
        # Query directly using partition key (user_id) and sort key (timestamp)
        response = table.query(
            KeyConditionExpression='user_id = :user_id AND #ts BETWEEN :start_date AND :end_date',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':start_date': start_date.isoformat(),
                ':end_date': end_date.isoformat()
            },
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        
        checkins = response.get('Items', [])
        logger.info(f"✅ Direct query returned {len(checkins)} check-ins")
        
        # If no results from direct query, try scan as fallback
        if not checkins:
            logger.info("No results from direct query, trying scan fallback...")
            checkins = scan_checkins_with_filter(user_id, start_date, end_date, limit)
        
        logger.info(f"✅ Retrieved {len(checkins)} check-ins for user {user_id}")
        return checkins
        
    except Exception as e:
        logger.error(f"❌ Error retrieving check-ins: {str(e)}")
        return []

def scan_checkins_with_filter(user_id: str, start_date: datetime, end_date: datetime, limit: int) -> List[Dict[str, Any]]:
    """
    Fallback method to scan check-ins with filter
    """
    try:
        table = dynamodb.Table(CHECKINS_TABLE)
        
        response = table.scan(
            FilterExpression='user_id = :user_id AND #ts BETWEEN :start_date AND :end_date',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':start_date': start_date.isoformat(),
                ':end_date': end_date.isoformat()
            },
            Limit=limit
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        logger.error(f"❌ Error in scan fallback: {str(e)}")
        return []

def generate_analytics_summary(checkins: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate analytics summary from check-in data
    """
    try:
        if not checkins:
            return {
                'total_checkins': 0,
                'average_score': 0,
                'mood_trend': 'no_data',
                'most_common_emotion': 'none',
                'recommendations': ['Start with your first mental health check-in'],
                'period_covered': 'no_data'
            }
        
        # Calculate basic statistics
        total_checkins = len(checkins)
        scores = [checkin.get('overall_score', 50) for checkin in checkins]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze emotions
        emotions = []
        for checkin in checkins:
            emotion_data = checkin.get('emotion_analysis', {})
            if emotion_data.get('dominant_emotion'):
                emotions.append(emotion_data['dominant_emotion'])
        
        most_common_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        # Simple recommendations
        recommendations = [
            "Great job maintaining positive mental health!",
            "Continue your current wellness practices",
            "Consider helping others with their mental health journey"
        ]
        
        # Calculate period covered
        if checkins:
            first_date = min(checkin.get('timestamp', '') for checkin in checkins)
            last_date = max(checkin.get('timestamp', '') for checkin in checkins)
            period_covered = f"{first_date[:10]} to {last_date[:10]}"
        else:
            period_covered = 'no_data'
        
        return {
            'total_checkins': total_checkins,
            'average_score': round(average_score, 1),
            'mood_trend': 'stable',
            'most_common_emotion': most_common_emotion,
            'recommendations': recommendations,
            'period_covered': period_covered,
            'score_range': {
                'min': min(scores) if scores else 0,
                'max': max(scores) if scores else 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating analytics summary: {str(e)}")
        return {
            'total_checkins': 0,
            'average_score': 0,
            'mood_trend': 'error',
            'most_common_emotion': 'unknown',
            'recommendations': ['Unable to generate recommendations'],
            'period_covered': 'error'
        } 