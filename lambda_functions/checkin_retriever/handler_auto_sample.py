import json
import boto3
import logging
import os
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
import random

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

def create_sample_data_for_user(user_id: str) -> bool:
    """
    Create sample check-in data for a user who has no data
    """
    try:
        logger.info(f"📝 Creating sample data for user: {user_id}")
        
        # Create 5 sample check-ins over the past 30 days
        sample_checkins = []
        
        for i in range(5):
            # Generate a random date within the past 30 days
            days_ago = random.randint(0, 30)
            checkin_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Generate random emotion data
            emotions = ['happy', 'excited', 'calm', 'focused', 'energetic', 'peaceful', 'motivated', 'relaxed']
            emotion = random.choice(emotions)
            confidence = round(random.uniform(0.7, 0.95), 2)
            intensity = random.randint(60, 90)
            
            # Generate random self-assessment
            mood_score = random.randint(6, 10)
            energy_level = random.randint(5, 9)
            stress_level = random.randint(1, 5)
            
            # Generate random duration
            duration = random.randint(30, 180)
            
            checkin_data = {
                'user_id': user_id,
                'session_id': f'sample_session_{i+1}',
                'duration': duration,
                'checkin_id': f'sample_checkin_{checkin_date.strftime("%Y%m%d_%H%M%S")}',
                'emotion_analysis': {
                    'dominant_emotion': emotion,
                    'confidence': confidence,
                    'intensity': intensity
                },
                'self_assessment': {
                    'mood_score': mood_score,
                    'energy_level': energy_level,
                    'stress_level': stress_level
                }
            }
            
            sample_checkins.append(checkin_data)
        
        # Store sample data directly in DynamoDB
        table = dynamodb.Table(CHECKINS_TABLE)
        success_count = 0
        
        for i, checkin_data in enumerate(sample_checkins):
            try:
                # Convert to DynamoDB format
                record = {
                    'user_id': str(checkin_data['user_id']),
                    'timestamp': str(checkin_data['checkin_id'].replace('sample_checkin_', '2025-06-29T') + ':00.000000'),
                    'checkin_id': str(checkin_data['checkin_id']),
                    'session_id': str(checkin_data['session_id']),
                    'duration': int(checkin_data['duration']),
                    'emotion_analysis': checkin_data['emotion_analysis'],
                    'self_assessment': checkin_data['self_assessment'],
                    'overall_score': Decimal('75.0'),
                    'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
                }
                
                table.put_item(Item=record)
                success_count += 1
                logger.info(f"✅ Created sample check-in {i+1}/{len(sample_checkins)}")
                
            except Exception as e:
                logger.error(f"❌ Error creating sample check-in {i+1}: {str(e)}")
        
        logger.info(f"🎉 Successfully created {success_count}/{len(sample_checkins)} sample check-ins for user {user_id}")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {str(e)}")
        return False

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for retrieving check-in data with auto sample creation
    """
    try:
        logger.info("=" * 60)
        logger.info("📊 CHECK-IN DATA RETRIEVER WITH AUTO SAMPLE CREATION")
        logger.info("=" * 60)
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return create_cors_response()
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'anonymous')
        days = int(query_params.get('days', 30))
        limit = int(query_params.get('limit', 50))
        
        logger.info(f"🔍 Requesting data for user: {user_id}")
        
        # Retrieve check-in data
        checkins = retrieve_checkins(user_id, days, limit)
        
        # If no check-ins found, create sample data for this user
        if not checkins:
            logger.info(f"📝 No check-ins found for user {user_id}, creating sample data...")
            sample_created = create_sample_data_for_user(user_id)
            if sample_created:
                # Retrieve again after creating sample data
                checkins = retrieve_checkins(user_id, days, limit)
                logger.info(f"✅ Retrieved {len(checkins)} check-ins after creating sample data")
            else:
                logger.warning("❌ Failed to create sample data")
        
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
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"❌ ERROR in check-in retrieval: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Check-in retrieval failed: {str(e)}")

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
        logger.info(f"📅 Date range: {start_date.isoformat()} to {end_date.isoformat()}")
        
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
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        
        # Analyze mood trend
        mood_trend = analyze_mood_trend(checkins)
        
        # Generate recommendations
        recommendations = generate_recommendations(checkins, average_score, mood_trend)
        
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
    Analyze mood trend over time
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
    Generate personalized recommendations
    """
    recommendations = []
    
    try:
        # Base recommendations on average score
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
        
        # Add trend-based recommendations
        if mood_trend == 'declining':
            recommendations.append("Your mood trend shows some decline - consider reaching out for support")
        elif mood_trend == 'improving':
            recommendations.append("Excellent progress! Your mood is trending upward")
        
        # Add frequency-based recommendations
        if len(checkins) < 3:
            recommendations.append("Try to check in more regularly to better track your patterns")
        elif len(checkins) >= 10:
            recommendations.append("Excellent consistency! Keep up your regular check-ins")
        
        return recommendations[:5]  # Limit to 5 recommendations
        
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {str(e)}")
        return ["Continue monitoring your mental health regularly"]

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create success response with CORS headers
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': json.dumps(data)
    }

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
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

def create_cors_response() -> Dict[str, Any]:
    """
    Create CORS preflight response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': ''
    } 