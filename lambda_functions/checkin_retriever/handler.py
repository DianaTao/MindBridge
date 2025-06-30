import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
import urllib.parse
import ssl
import certifi

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
CHECKINS_TABLE = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins-dev')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# Initialize AWS clients
try:
    # Initialize DynamoDB client
    dynamodb = boto3.client('dynamodb')
    logger.info("✅ AWS DynamoDB client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize DynamoDB: {str(e)}")
    dynamodb = None

try:
    # Initialize Bedrock for LLM analytics with SSL configuration
    # Create a custom SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Initialize Bedrock client with custom config
    bedrock = boto3.client(
        'bedrock-runtime',
        config=boto3.session.Config(
            retries={'max_attempts': 3},
            connect_timeout=30,
            read_timeout=60
        )
    )
    logger.info("✅ AWS Bedrock client initialized successfully with SSL configuration")
except Exception as e:
    logger.error(f"❌ Failed to initialize Bedrock: {str(e)}")
    bedrock = None

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

def convert_dynamodb_item(item):
    """
    Convert DynamoDB client response format to regular dict
    """
    result = {}
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = float(value['N'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'M' in value:
            result[key] = convert_dynamodb_item(value['M'])
        elif 'L' in value:
            result[key] = [convert_dynamodb_item({'item': v})['item'] for v in value['L']]
        else:
            result[key] = str(value)
    return result

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized success response with CORS headers
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://d8zwp3hg28702.cloudfront.net',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data, default=str)
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Comprehensive check-in retriever with real data only
    """
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'https://d8zwp3hg28702.cloudfront.net',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({})
        }

    try:
        logger.info("🚀 COMPREHENSIVE CHECKIN RETRIEVER WITH LLM ANALYTICS")
        
        # Extract user ID from query parameters
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('user_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': 'https://d8zwp3hg28702.cloudfront.net',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Credentials': 'true',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'user_id parameter required'})
            }
        
        # URL decode the user_id in case it's encoded
        try:
            from urllib.parse import unquote
            user_id = unquote(user_id)
        except:
            pass
        
        logger.info(f"🔍 User: {user_id}")
        logger.info(f"📊 Table: {CHECKINS_TABLE}")
        
        # First attempt: Try to retrieve real data from DynamoDB
        real_checkins = []
        try:
            logger.info("🔍 Attempting to retrieve real data from DynamoDB...")
            
            response = dynamodb.query(
                TableName=CHECKINS_TABLE,
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={
                    ':user_id': {'S': user_id}
                },
                ScanIndexForward=False,  # Most recent first
                Limit=50
            )
            
            raw_items = response.get('Items', [])
            for item in raw_items:
                converted_item = convert_dynamodb_item(item)
                real_checkins.append(converted_item)
            
            if real_checkins:
                logger.info(f"✅ Retrieved {len(real_checkins)} real check-ins from DynamoDB")
            else:
                logger.info("ℹ️ No real check-ins found in DynamoDB")
                
        except Exception as e:
            logger.error(f"❌ DynamoDB query error: {str(e)}")
            logger.info("🔄 Falling back to demo data...")
            
        # Use real data if available, otherwise return empty list
        if real_checkins:
            checkins = real_checkins
            data_source = "real_database"
            logger.info(f"📊 Using {len(checkins)} real check-ins for analysis")
        else:
            checkins = []
            data_source = "real_database"
            logger.info("📊 No check-ins found for user")
            return create_success_response({
                'checkins': [],
                'analytics_summary': {
                    'total_checkins': 0,
                    'average_score': 0,
                    'mood_trend': 'no_data',
                    'most_common_emotion': 'none',
                    'data_source': 'real_database',
                    'has_real_data': False,
                    'period_covered': 'No data available'
                },
                'total_count': 0,
                'user_guidance': {
                    'has_data': False,
                    'message': 'No check-in data available yet. Complete your first check-in to see analytics.'
                }
            })
        
        # Always attempt LLM analytics first (for both real and demo data)
        logger.info("🤖 Attempting LLM-powered analytics...")
        analytics_summary = generate_llm_analytics(checkins, user_id)
        
        # Add metadata about data source and LLM usage
        analytics_summary['data_source'] = data_source
        analytics_summary['has_real_data'] = len(real_checkins) > 0
        
        # Prepare final response
            result = {
                'checkins': checkins,
                'analytics_summary': analytics_summary,
                'total_count': len(checkins),
                'user_guidance': {
                    'has_data': True,
                'message': f"{'Real' if data_source == 'real_database' else 'Demo'} analytics for {len(checkins)} check-ins with {'AI insights' if analytics_summary.get('llm_generated', False) else 'fallback analysis'}"
                }
            }
        
        logger.info("✅ SUCCESS - returning comprehensive result with LLM analytics")
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"❌ Error in retrieval: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def generate_llm_analytics(checkins: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """
    Generate comprehensive analytics using Bedrock LLM with enhanced SSL handling
    """
    try:
        if not bedrock:
            logger.info("🔄 Bedrock client not available, using fallback analytics")
            return generate_fallback_analytics(checkins)
        
        # Prepare data for LLM analysis
        analysis_context = prepare_analytics_context(checkins, user_id)
        
        # Create prompt for comprehensive analytics
        prompt = create_analytics_prompt(analysis_context)
        
        logger.info("🤖 Attempting LLM analytics with Bedrock...")
        
        # Call Bedrock LLM with enhanced error handling
        try:
            response = bedrock.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 2000,
                    'temperature': 0.7,
                    'top_p': 0.9
                })
            )
            
            # Parse LLM response
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            logger.info("✅ LLM analytics generated successfully")
        
            # Parse and structure the analytics
            return parse_analytics_response(llm_output, analysis_context)
            
        except Exception as llm_error:
            logger.error(f"❌ LLM call failed: {str(llm_error)}")
            
            # Check if it's an SSL issue
            if 'SSL' in str(llm_error) or 'certificate' in str(llm_error).lower():
                logger.warning("🔒 SSL certificate issue detected, using fallback analytics")
                fallback_analytics = generate_fallback_analytics(checkins)
                fallback_analytics['ssl_issue'] = True
                fallback_analytics['llm_error'] = str(llm_error)
                return fallback_analytics
            else:
                # Other LLM errors
                logger.error(f"❌ Non-SSL LLM error: {str(llm_error)}")
                return generate_fallback_analytics(checkins)
        
    except Exception as e:
        logger.error(f"❌ General LLM analytics error: {str(e)}")
        return generate_fallback_analytics(checkins)

def prepare_analytics_context(checkins: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """
    Prepare comprehensive context for LLM analytics
    """
    total_checkins = len(checkins)
    
    # Calculate trends
    scores = [c.get('overall_score', 0) for c in checkins]
    average_score = sum(scores) / len(scores) if scores else 0
    
    # Emotion analysis
    emotions = []
    for checkin in checkins:
        emotion_data = checkin.get('emotion_analysis', {})
        if emotion_data.get('primary_emotion'):
            emotions.append(emotion_data['primary_emotion'])
    
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Time-based analysis
    timestamps = [c.get('timestamp', '') for c in checkins if c.get('timestamp')]
    
    return {
        'user_id': user_id,
        'total_checkins': total_checkins,
        'average_score': average_score,
        'score_trend': scores,
        'emotion_distribution': emotion_counts,
        'checkins_data': checkins,
        'time_period': f"Last {total_checkins} check-ins",
        'latest_checkin': checkins[0] if checkins else None
    }

def create_analytics_prompt(context: Dict[str, Any]) -> str:
    """
    Create comprehensive analytics prompt for LLM
    """
    prompt = f"""You are an expert mental health data analyst and AI counselor. Analyze the following comprehensive mental health check-in data and provide detailed insights and recommendations.

USER ANALYTICS DATA:
- User ID: {context['user_id']}
- Total Check-ins: {context['total_checkins']}
- Average Wellbeing Score: {context['average_score']:.1f}/100
- Score Progression: {context['score_trend']}
- Emotion Distribution: {json.dumps(context['emotion_distribution'], indent=2)}

DETAILED CHECK-IN DATA:
{json.dumps(context['checkins_data'], indent=2)}

ANALYSIS REQUIREMENTS:
Please provide a comprehensive JSON response with the following structure:

1. overall_trend_analysis: Detailed analysis of score trends and patterns
2. emotional_insights: Deep insights into emotional patterns and changes
3. personalized_recommendations: 5-7 specific, actionable recommendations
4. risk_assessment: Assessment of any concerning patterns (low/medium/high)
5. positive_indicators: Highlights of positive mental health indicators
6. areas_for_improvement: Specific areas that need attention
7. professional_guidance: Whether professional help is recommended
8. trend_prediction: Predicted trend based on current data
9. comparative_analysis: How this user compares to healthy baselines
10. llm_confidence: Your confidence level in this analysis (high/medium/low)

Focus on:
- Evidence-based insights from the data patterns
- Actionable and specific recommendations
- Supportive and encouraging tone
- Professional mental health best practices
- Data-driven trend analysis

Respond ONLY with valid JSON format."""
    
    return prompt

def parse_analytics_response(llm_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse LLM analytics response and structure it
    """
    try:
        # Try to extract JSON
        import re
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            llm_analytics = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in LLM response")
        
        # Structure the final analytics
        return {
            'total_checkins': context['total_checkins'],
            'average_score': round(context['average_score'], 1),
            'mood_trend': determine_mood_trend(context['score_trend']),
            'most_common_emotion': max(context['emotion_distribution'].items(), key=lambda x: x[1])[0] if context['emotion_distribution'] else 'neutral',
            'recommendations': llm_analytics.get('personalized_recommendations', ['Continue regular check-ins']),
            'period_covered': context['time_period'],
            'llm_insights': llm_analytics.get('overall_trend_analysis', 'Comprehensive analysis completed'),
            'emotional_insights': llm_analytics.get('emotional_insights', 'Emotional patterns analyzed'),
            'risk_assessment': llm_analytics.get('risk_assessment', 'low'),
            'positive_indicators': llm_analytics.get('positive_indicators', []),
            'areas_for_improvement': llm_analytics.get('areas_for_improvement', []),
            'professional_guidance': llm_analytics.get('professional_guidance', False),
            'trend_prediction': llm_analytics.get('trend_prediction', 'stable'),
            'llm_confidence': llm_analytics.get('llm_confidence', 'high'),
            'llm_generated': True
        }
        
    except Exception as e:
        logger.error(f"❌ Error parsing LLM analytics: {str(e)}")
        return generate_fallback_analytics(context['checkins_data'])

def determine_mood_trend(scores: List[float]) -> str:
    """Determine mood trend from score progression"""
    if len(scores) < 2:
        return 'insufficient_data'
    
    recent_avg = sum(scores[:2]) / 2 if len(scores) >= 2 else scores[0]
    older_avg = sum(scores[2:]) / len(scores[2:]) if len(scores) > 2 else scores[-1]
    
    if recent_avg > older_avg + 5:
        return 'improving'
    elif recent_avg < older_avg - 5:
        return 'declining'
    else:
        return 'stable'

def generate_fallback_analytics(checkins: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate fallback analytics without LLM"""
        if not checkins:
            return {
                'total_checkins': 0,
                'average_score': 0,
                'mood_trend': 'no_data',
                'most_common_emotion': 'none',
            'recommendations': ['Complete your first check-in'],
                'period_covered': 'no_data',
            'llm_generated': False
            }
        
        total_checkins = len(checkins)
    scores = [c.get('overall_score', 0) for c in checkins]
        average_score = sum(scores) / len(scores) if scores else 0
        
    # Find most common emotion
        emotions = []
        for checkin in checkins:
            emotion_data = checkin.get('emotion_analysis', {})
        if emotion_data.get('primary_emotion'):
            emotions.append(emotion_data['primary_emotion'])
    
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'neutral'
        
        return {
            'total_checkins': total_checkins,
            'average_score': round(average_score, 1),
        'mood_trend': determine_mood_trend(scores),
            'most_common_emotion': most_common_emotion,
        'recommendations': [
            f'You have completed {total_checkins} check-ins with an average score of {average_score:.1f}',
            'Your most common emotion is ' + most_common_emotion,
            'Continue regular mental health monitoring',
            'Consider professional guidance if scores decline'
        ],
        'period_covered': f'Last {total_checkins} check-ins',
        'llm_generated': False
    } 