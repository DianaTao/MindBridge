"""
Emotion Fusion Lambda Function
Uses Amazon Bedrock (Claude) to fuse multi-modal emotion data and generate personalized recommendations
"""

import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-write')
eventbridge = boto3.client('events')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
TIMESTREAM_DB = os.environ.get('TIMESTREAM_DB', 'MindBridge')
TIMESTREAM_TABLE = os.environ.get('TIMESTREAM_TABLE', 'emotions')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for emotion fusion
    
    Trigger: EventBridge events from video/audio/text analysis lambdas
    Purpose: Fuse multi-modal emotion data using AI and generate recommendations
    """
    try:
        logger.info(f"Processing emotion fusion request: {context.aws_request_id}")
        
        # Handle different event types
        if 'Records' in event:
            # EventBridge event
            for record in event['Records']:
                if record.get('eventSource') == 'aws:events':
                    detail = json.loads(record.get('Sns', {}).get('Message', '{}'))
                    process_emotion_fusion_event(detail)
        else:
            # Direct invocation
            process_emotion_fusion_event(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Emotion fusion processed successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing emotion fusion: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def process_emotion_fusion_event(event_detail: Dict[str, Any]) -> None:
    """
    Process emotion fusion for a specific user/session
    """
    try:
        user_id = event_detail.get('user_id', 'anonymous')
        session_id = event_detail.get('session_id', 'default')
        
        logger.info(f"Processing emotion fusion for user: {user_id}, session: {session_id}")
        
        # Collect recent emotion data from all modalities
        recent_emotions = collect_recent_emotions(user_id, session_id)
        
        if not recent_emotions:
            logger.info("No recent emotion data found for fusion")
            return
        
        # Use Claude to fuse multi-modal data
        unified_emotion = fuse_emotions_with_ai(recent_emotions)
        
        if not unified_emotion:
            logger.warning("Failed to generate unified emotion")
            return
        
        # Generate personalized recommendations
        recommendations = generate_recommendations(unified_emotion, user_id)
        
        # Store unified emotion state
        store_unified_emotion(unified_emotion, recommendations, user_id, session_id)
        
        # Store time-series data
        store_timestream_data(unified_emotion, user_id, session_id)
        
        # Send real-time updates
        send_realtime_updates(unified_emotion, recommendations, user_id, session_id)
        
        logger.info(f"Successfully processed emotion fusion for {user_id}")
        
    except Exception as e:
        logger.error(f"Error in emotion fusion processing: {str(e)}")

def collect_recent_emotions(user_id: str, session_id: str, window_minutes: int = 2) -> List[Dict[str, Any]]:
    """
    Collect recent emotion data from all modalities within a time window
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        # Calculate time window
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Query recent emotions for this user/session
        response = table.query(
            KeyConditionExpression='user_id = :user_id AND #ts BETWEEN :start_time AND :end_time',
            FilterExpression='session_id = :session_id',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':session_id': session_id,
                ':start_time': window_start.isoformat(),
                ':end_time': now.isoformat()
            },
            ScanIndexForward=False,  # Most recent first
            Limit=50  # Limit to recent items
        )
        
        emotions = response.get('Items', [])
        logger.info(f"Collected {len(emotions)} recent emotion records")
        
        return emotions
        
    except Exception as e:
        logger.error(f"Error collecting recent emotions: {str(e)}")
        return []

def fuse_emotions_with_ai(emotion_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Use Claude to intelligently fuse multi-modal emotion data
    """
    try:
        if not emotion_data:
            return None
        
        # Prepare emotion data for AI analysis
        formatted_data = format_emotion_data_for_ai(emotion_data)
        
        prompt = f"""
        You are an expert emotional intelligence AI. Analyze these multi-modal emotion signals and provide a unified emotional assessment.

        Recent Emotion Data:
        {json.dumps(formatted_data, indent=2)}

        Analyze the data considering:
        1. Facial expressions can sometimes be masked or inconsistent
        2. Voice patterns often reveal authentic emotions
        3. Text sentiment adds cognitive/linguistic context
        4. Look for consistency and conflicts across modalities
        5. Recent data should be weighted more heavily

        Provide a JSON response with exactly this structure:
        {{
            "unified_emotion": "primary emotional state (e.g., happy, sad, stressed, excited, neutral)",
            "intensity": "scale 1-10 where 10 is most intense",
            "confidence": "how certain you are (0.0-1.0)",
            "contributing_factors": ["list of which modalities contributed most"],
            "trend": "improving, declining, or stable",
            "context": "brief explanation of the emotional state (2-3 sentences)",
            "risk_level": "low, medium, or high (for mental health concerns)"
        }}

        Focus on being helpful and accurate. If the data is inconsistent or unclear, reflect lower confidence.
        """
        
        # Call Claude via Bedrock
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        claude_response = result['content'][0]['text']
        
        # Parse Claude's JSON response
        try:
            unified_emotion = json.loads(claude_response)
            
            # Add metadata
            unified_emotion['analysis_timestamp'] = datetime.utcnow().isoformat()
            unified_emotion['data_points_analyzed'] = len(emotion_data)
            unified_emotion['ai_model'] = BEDROCK_MODEL_ID
            
            return unified_emotion
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {claude_response}")
            return None
        
    except Exception as e:
        logger.error(f"Error in AI emotion fusion: {str(e)}")
        return None

def format_emotion_data_for_ai(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format emotion data for AI analysis
    """
    formatted = {
        'video_emotions': [],
        'audio_emotions': [],
        'text_emotions': [],
        'summary': {
            'total_data_points': len(emotion_data),
            'time_span_minutes': 0,
            'modalities_present': set()
        }
    }
    
    # Group by modality and summarize
    for item in emotion_data:
        modality = item.get('modality', 'unknown')
        emotion_data_content = item.get('emotion_data', {})
        
        formatted['summary']['modalities_present'].add(modality)
        
        if modality == 'video':
            formatted['video_emotions'].append({
                'timestamp': item.get('timestamp'),
                'primary_emotion': emotion_data_content.get('primary_emotion'),
                'confidence': emotion_data_content.get('confidence'),
                'faces_detected': len(emotion_data_content.get('emotions', []))
            })
        elif modality == 'audio':
            formatted['audio_emotions'].append({
                'timestamp': item.get('timestamp'),
                'voice_emotion': emotion_data_content.get('predicted_emotion'),
                'confidence': emotion_data_content.get('confidence'),
                'speaking_rate': emotion_data_content.get('speaking_rate'),
                'sentiment': emotion_data_content.get('sentiment', {}).get('sentiment')
            })
        elif modality == 'text':
            formatted['text_emotions'].append({
                'timestamp': item.get('timestamp'),
                'sentiment': emotion_data_content.get('sentiment'),
                'confidence': emotion_data_content.get('confidence')
            })
    
    # Convert set to list for JSON serialization
    formatted['summary']['modalities_present'] = list(formatted['summary']['modalities_present'])
    
    return formatted

def generate_recommendations(emotion_state: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on emotional state
    """
    try:
        prompt = f"""
        Based on this emotional analysis, provide personalized recommendations for mental wellness and emotional support.

        Current Emotion State: {json.dumps(emotion_state)}

        Consider the emotional intensity, risk level, and context. Provide practical, actionable recommendations.

        Respond with exactly this JSON structure:
        {{
            "immediate_actions": ["2-3 specific actions to take right now"],
            "breathing_exercise": "specific breathing technique with instructions",
            "environment_changes": ["2-3 environmental adjustments"],
            "activity_suggestions": ["2-3 activities to improve mood"],
            "when_to_seek_help": "guidance on when professional help might be needed",
            "positive_affirmations": ["2-3 encouraging statements"],
            "priority_level": "low, medium, or high (how urgently to act)"
        }}

        Make recommendations:
        - Specific and actionable
        - Appropriate to the emotional intensity
        - Evidence-based where possible
        - Supportive and non-judgmental
        - Practical for immediate implementation
        """
        
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 800,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        claude_response = result['content'][0]['text']
        
        try:
            recommendations = json.loads(claude_response)
            recommendations['generated_at'] = datetime.utcnow().isoformat()
            return recommendations
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse recommendations JSON: {claude_response}")
            return generate_fallback_recommendations(emotion_state)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return generate_fallback_recommendations(emotion_state)

def generate_fallback_recommendations(emotion_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate basic fallback recommendations if AI fails
    """
    emotion = emotion_state.get('unified_emotion', 'neutral').lower()
    intensity = int(emotion_state.get('intensity', 5))
    
    base_recommendations = {
        'immediate_actions': ['Take three deep breaths', 'Check your posture'],
        'breathing_exercise': '4-7-8 breathing: Inhale for 4 counts, hold for 7, exhale for 8',
        'environment_changes': ['Adjust lighting', 'Reduce noise if possible'],
        'activity_suggestions': ['Take a short walk', 'Listen to calming music'],
        'when_to_seek_help': 'Consider professional support if feelings persist for several days',
        'positive_affirmations': ['This feeling is temporary', 'You have overcome challenges before'],
        'priority_level': 'medium' if intensity > 7 else 'low',
        'generated_at': datetime.utcnow().isoformat()
    }
    
    # Customize based on emotion
    if emotion in ['sad', 'depressed']:
        base_recommendations['activity_suggestions'] = ['Connect with a friend', 'Engage in a favorite hobby', 'Get some sunlight']
    elif emotion in ['angry', 'frustrated']:
        base_recommendations['activity_suggestions'] = ['Physical exercise', 'Write in a journal', 'Practice progressive muscle relaxation']
    elif emotion in ['anxious', 'stressed']:
        base_recommendations['activity_suggestions'] = ['Meditation or mindfulness', 'Organize your space', 'Break tasks into smaller steps']
    
    return base_recommendations

def store_unified_emotion(emotion_state: Dict[str, Any], recommendations: Dict[str, Any], 
                         user_id: str, session_id: str) -> None:
    """
    Store unified emotion analysis in DynamoDB
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        table.put_item(
            Item={
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id,
                'modality': 'unified',
                'emotion_data': {
                    'unified_emotion': emotion_state,
                    'recommendations': recommendations,
                    'fusion_type': 'ai_bedrock'
                },
                'ttl': int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
        )
        
        logger.info("Stored unified emotion data in DynamoDB")
        
    except Exception as e:
        logger.error(f"Failed to store unified emotion data: {str(e)}")

def store_timestream_data(emotion_state: Dict[str, Any], user_id: str, session_id: str) -> None:
    """
    Store emotion time-series data in Amazon TimeStream
    """
    try:
        current_time = str(int(datetime.utcnow().timestamp() * 1000))  # milliseconds
        
        records = [
            {
                'Dimensions': [
                    {'Name': 'user_id', 'Value': user_id},
                    {'Name': 'session_id', 'Value': session_id},
                    {'Name': 'emotion', 'Value': emotion_state.get('unified_emotion', 'neutral')}
                ],
                'MeasureName': 'intensity',
                'MeasureValue': str(emotion_state.get('intensity', 5)),
                'MeasureValueType': 'DOUBLE',
                'Time': current_time
            },
            {
                'Dimensions': [
                    {'Name': 'user_id', 'Value': user_id},
                    {'Name': 'session_id', 'Value': session_id},
                    {'Name': 'emotion', 'Value': emotion_state.get('unified_emotion', 'neutral')}
                ],
                'MeasureName': 'confidence',
                'MeasureValue': str(emotion_state.get('confidence', 0.5)),
                'MeasureValueType': 'DOUBLE',
                'Time': current_time
            }
        ]
        
        timestream.write_records(
            DatabaseName=TIMESTREAM_DB,
            TableName=TIMESTREAM_TABLE,
            Records=records
        )
        
        logger.info("Stored emotion data in TimeStream")
        
    except Exception as e:
        logger.error(f"Failed to store TimeStream data: {str(e)}")

def send_realtime_updates(emotion_state: Dict[str, Any], recommendations: Dict[str, Any], 
                         user_id: str, session_id: str) -> None:
    """
    Send real-time updates via EventBridge for dashboard updates
    """
    try:
        eventbridge.put_events(
            Entries=[
                {
                    'Source': 'mindbridge.emotion-fusion',
                    'DetailType': 'Unified Emotion Update',
                    'Detail': json.dumps({
                        'user_id': user_id,
                        'session_id': session_id,
                        'emotion_state': emotion_state,
                        'recommendations': recommendations,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                }
            ]
        )
        
        logger.info("Sent real-time emotion update")
        
    except Exception as e:
        logger.error(f"Failed to send real-time updates: {str(e)}") 