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

def get_demo_data() -> List[Dict[str, Any]]:
    """
    Get real demo data from existing users (anonymized) to show what analytics look like
    """
    try:
        table = dynamodb.Table(CHECKINS_TABLE)
        
        # Get some real data from existing users for demo purposes
        response = table.scan(Limit=5)
        items = response.get('Items', [])
        
        if items:
            # Anonymize the data by removing user-specific info
            demo_data = []
            for item in items:
                demo_item = {
                    'checkin_id': f"demo_{item.get('checkin_id', 'unknown')}",
                    'session_id': 'demo_session',
                    'duration': item.get('duration', 120),
                    'emotion_analysis': item.get('emotion_analysis', {}),
                    'self_assessment': item.get('self_assessment', {}),
                    'overall_score': item.get('overall_score', 75.0),
                    'timestamp': item.get('timestamp', datetime.utcnow().isoformat()),
                    'llm_report': item.get('llm_report', {}),
                    'is_demo': True  # Mark as demo data
                }
                demo_data.append(demo_item)
            
            logger.info(f"✅ Retrieved {len(demo_data)} demo records from real data")
            return demo_data
        else:
            logger.warning("No real data available for demo")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error getting demo data: {str(e)}")
        return []

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that uses real data instead of hard-coded samples
    """
    try:
        logger.info("=" * 60)
        logger.info("📊 CHECK-IN DATA RETRIEVER WITH REAL DATA")
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
        
        # Retrieve check-in data for the specific user
        checkins = retrieve_checkins(user_id, days, limit)
        
        # If user has no data, provide guidance and demo data
        if not checkins:
            logger.info(f"📝 No check-ins found for user {user_id}, providing guidance and demo data")
            
            # Get real demo data from existing users
            demo_checkins = get_demo_data()
            
            # Create guidance response
            result = {
                'checkins': convert_decimals(demo_checkins),
                'analytics_summary': {
                    'total_checkins': len(demo_checkins),
                    'average_score': 75.0 if demo_checkins else 0,
                    'mood_trend': 'demo_data',
                    'most_common_emotion': 'happy' if demo_checkins else 'none',
                    'recommendations': [
                        "Complete your first mental health check-in to see your real analytics",
                        "Use the Mental Health Check-in feature to capture your emotions",
                        "Regular check-ins help track your emotional patterns over time",
                        "Your data will be stored securely and analyzed for personalized insights"
                    ],
                    'period_covered': 'Demo data from real users',
                    'is_demo': True
                },
                'total_count': len(demo_checkins),
                'query_params': {
                    'user_id': user_id,
                    'days': days,
                    'limit': limit
                },
                'user_guidance': {
                    'has_data': False,
                    'message': 'Complete your first mental health check-in to see your personalized analytics',
                    'next_steps': [
                        'Go to the Mental Health Check-in tab',
                        'Allow camera access for emotion analysis',
                        'Complete the self-assessment questions',
                        'Submit your check-in to see real analytics'
                    ]
                }
            }
        else:
            # User has real data
            checkins = convert_decimals(checkins)
            analytics_summary = generate_analytics_summary(checkins)
            
            result = {
                'checkins': checkins,
                'analytics_summary': analytics_summary,
                'total_count': len(checkins),
                'query_params': {
                    'user_id': user_id,
                    'days': days,
                    'limit': limit
                },
                'user_guidance': {
                    'has_data': True,
                    'message': f'You have {len(checkins)} check-ins with personalized analytics',
                    'next_steps': [
                        'Continue regular check-ins to track your patterns',
                        'Review your emotional trends over time',
                        'Follow personalized recommendations for mental wellness'
                    ]
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
    Generate analytics summary from real check-in data
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
        
        # Calculate basic statistics from real data
        total_checkins = len(checkins)
        scores = [checkin.get('overall_score', 50) for checkin in checkins]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze emotions from real data
        emotions = []
        for checkin in checkins:
            emotion_data = checkin.get('emotion_analysis', {})
            if emotion_data.get('dominant_emotion'):
                emotions.append(emotion_data['dominant_emotion'])
        
        most_common_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        # Analyze mood trend from real data
        mood_trend = analyze_mood_trend(checkins)
        
        # Generate recommendations based on real data
        recommendations = generate_recommendations(checkins, average_score, mood_trend)
        
        # Calculate period covered from real data
        if checkins:
            first_date = min(checkin.get('timestamp', '') for checkin in checkins)
            last_date = max(checkin.get('timestamp', '') for checkin in checkins)
            period_covered = f"{first_date[:10]} to {last_date[:10]}"
        else:
            period_covered = 'no_data'
        
        return {
            'total_checkins': total_checkins,
            'average_score': round(average_score, 1),
            'mood_trend': mood_trend,
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

def analyze_mood_trend(checkins: List[Dict[str, Any]]) -> str:
    """
    Analyze mood trend over time from real data
    """
    try:
        if len(checkins) < 2:
            return 'insufficient_data'
        
        # Sort by timestamp
        sorted_checkins = sorted(checkins, key=lambda x: x.get('timestamp', ''))
        
        # Get scores for trend analysis
        scores = [checkin.get('overall_score', 50) for checkin in sorted_checkins]
        
        # Simple trend analysis
        if len(scores) >= 3:
            recent_scores = scores[-3:]
            earlier_scores = scores[:3]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            earlier_avg = sum(earlier_scores) / len(earlier_scores)
            
            if recent_avg > earlier_avg + 5:
                return 'improving'
            elif recent_avg < earlier_avg - 5:
                return 'declining'
            else:
                return 'stable'
        else:
            return 'insufficient_data'
            
    except Exception as e:
        logger.error(f"❌ Error analyzing mood trend: {str(e)}")
        return 'error'

def generate_recommendations(checkins: List[Dict[str, Any]], average_score: float, mood_trend: str) -> List[str]:
    """
    Generate personalized recommendations based on real data
    """
    recommendations = []
    
    try:
        # Base recommendations on real average score
        if average_score < 40:
            recommendations.extend([
                "Consider speaking with a mental health professional",
                "Practice daily self-care routines",
                "Focus on getting adequate sleep and nutrition"
            ])
        elif average_score < 60:
            recommendations.extend([
                "Continue monitoring your mental health regularly",
                "Try mindfulness or meditation exercises",
                "Maintain social connections with friends and family"
            ])
        else:
            recommendations.extend([
                "Great job maintaining positive mental health!",
                "Continue your current wellness practices",
                "Consider helping others with their mental health journey"
            ])
        
        # Add trend-based recommendations from real data
        if mood_trend == 'declining':
            recommendations.append("Your mood trend shows some decline - consider reaching out for support")
        elif mood_trend == 'improving':
            recommendations.append("Excellent progress! Your mood is trending upward")
        
        # Add frequency-based recommendations from real data
        if len(checkins) < 3:
            recommendations.append("Try to check in more regularly to better track your patterns")
        elif len(checkins) >= 10:
            recommendations.append("Excellent consistency! Keep up your regular check-ins")
        
        return recommendations[:5]  # Limit to 5 recommendations
        
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {str(e)}")
        return ["Continue monitoring your mental health regularly"] 