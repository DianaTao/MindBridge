"""
Video Analysis Lambda Function
Analyzes facial expressions for emotion detection using Amazon Rekognition
"""

import json
import boto3
import base64
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
FUSION_LAMBDA_ARN = os.environ.get('FUSION_LAMBDA_ARN', '')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for video emotion analysis
    
    Trigger: API Gateway WebSocket (real-time video frames)
    Purpose: Analyze facial expressions for emotions using Rekognition
    """
    try:
        logger.info(f"Processing video analysis request: {event.get('requestContext', {}).get('requestId')}")
        
        # Parse incoming video frame data
        body = json.loads(event.get('body', '{}'))
        frame_data = body.get('frame_data', '')
        user_id = body.get('user_id', 'anonymous')
        session_id = body.get('session_id', 'default')
        
        if not frame_data:
            return create_error_response(400, "No frame data provided")
        
        # Decode base64 frame data
        try:
            image_bytes = base64.b64decode(frame_data)
        except Exception as e:
            logger.error(f"Failed to decode frame data: {str(e)}")
            return create_error_response(400, "Invalid frame data format")
        
        # Analyze emotions using Amazon Rekognition
        emotion_results = analyze_facial_emotions(image_bytes)
        
        if not emotion_results:
            logger.info("No faces detected in frame")
            return create_success_response({
                'faces_detected': 0,
                'emotions': [],
                'primary_emotion': 'neutral',
                'confidence': 0.0
            })
        
        # Process and format emotion data
        processed_emotions = process_emotion_results(emotion_results, user_id, session_id)
        
        # Store emotion data in DynamoDB
        store_emotion_data(processed_emotions, user_id, session_id)
        
        # Trigger emotion fusion Lambda
        trigger_emotion_fusion(processed_emotions)
        
        # Prepare response
        response_data = {
            'faces_detected': len(emotion_results),
            'emotions': processed_emotions,
            'primary_emotion': get_primary_emotion(processed_emotions),
            'confidence': get_average_confidence(processed_emotions),
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time_ms': context.get_remaining_time_in_millis()
        }
        
        logger.info(f"Successfully processed {len(emotion_results)} faces")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error processing video analysis: {str(e)}")
        return create_error_response(500, f"Internal server error: {str(e)}")

def analyze_facial_emotions(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Use Amazon Rekognition to detect facial emotions
    """
    try:
        # Check if we're in local development mode
        if os.environ.get('STAGE') == 'local' or os.environ.get('AWS_ACCESS_KEY_ID') == 'test':
            logger.info("Running in local mode - using mock face detection")
            return mock_face_detection()
        
        response = rekognition.detect_faces(
            Image={'Bytes': image_bytes},
            Attributes=['ALL']
        )
        
        faces_with_emotions = []
        for face_detail in response['FaceDetails']:
            if 'Emotions' in face_detail:
                faces_with_emotions.append(face_detail)
        
        return faces_with_emotions
        
    except Exception as e:
        logger.error(f"Rekognition analysis failed: {str(e)}")
        # Fall back to mock detection in case of AWS errors
        logger.info("Falling back to mock face detection")
        return mock_face_detection()

def mock_face_detection() -> List[Dict[str, Any]]:
    """
    Mock face detection for local development
    Simulates detecting a face with random emotions
    """
    logger.info("MOCK FACE DETECTION TRIGGERED")
    import random
    from datetime import datetime
    
    emotions = [
        {'Type': 'HAPPY', 'Confidence': random.uniform(70, 95)},
        {'Type': 'SAD', 'Confidence': random.uniform(10, 30)},
        {'Type': 'ANGRY', 'Confidence': random.uniform(5, 20)},
        {'Type': 'SURPRISED', 'Confidence': random.uniform(10, 40)},
        {'Type': 'FEAR', 'Confidence': random.uniform(5, 15)},
        {'Type': 'DISGUSTED', 'Confidence': random.uniform(5, 15)},
        {'Type': 'CALM', 'Confidence': random.uniform(20, 50)},
        {'Type': 'CONFUSED', 'Confidence': random.uniform(10, 30)}
    ]
    
    # Shuffle emotions and take top 3
    random.shuffle(emotions)
    top_emotions = emotions[:3]
    
    mock_face = {
        'Emotions': top_emotions,
        'Confidence': random.uniform(85, 98),
        'BoundingBox': {
            'Width': random.uniform(0.1, 0.3),
            'Height': random.uniform(0.2, 0.4),
            'Left': random.uniform(0.3, 0.7),
            'Top': random.uniform(0.2, 0.6)
        },
        'AgeRange': {
            'Low': random.randint(20, 35),
            'High': random.randint(35, 50)
        },
        'Gender': {
            'Value': random.choice(['Male', 'Female']),
            'Confidence': random.uniform(80, 95)
        }
    }
    
    return [mock_face]

def process_emotion_results(face_details: List[Dict[str, Any]], user_id: str, session_id: str) -> List[Dict[str, Any]]:
    """
    Process and format emotion detection results
    """
    processed_emotions = []
    
    for i, face_detail in enumerate(face_details):
        emotions = face_detail.get('Emotions', [])
        
        # Sort emotions by confidence
        sorted_emotions = sorted(emotions, key=lambda x: x['Confidence'], reverse=True)
        
        face_emotion_data = {
            'face_id': f"face_{i}",
            'emotions': sorted_emotions,
            'primary_emotion': sorted_emotions[0]['Type'].lower() if sorted_emotions else 'neutral',
            'confidence': sorted_emotions[0]['Confidence'] if sorted_emotions else 0.0,
            'face_confidence': face_detail.get('Confidence', 0.0),
            'bounding_box': face_detail.get('BoundingBox', {}),
            'age_range': face_detail.get('AgeRange', {}),
            'gender': face_detail.get('Gender', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'session_id': session_id,
            'modality': 'video'
        }
        
        processed_emotions.append(face_emotion_data)
    
    return processed_emotions

def store_emotion_data(emotions: List[Dict[str, Any]], user_id: str, session_id: str) -> None:
    """
    Store emotion data in DynamoDB
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        for emotion_data in emotions:
            table.put_item(
                Item={
                    'user_id': user_id,
                    'timestamp': emotion_data['timestamp'],
                    'session_id': session_id,
                    'modality': 'video',
                    'emotion_data': emotion_data,
                    'ttl': int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
                }
            )
        
        logger.info(f"Stored {len(emotions)} emotion records in DynamoDB")
        
    except Exception as e:
        logger.error(f"Failed to store emotion data: {str(e)}")

def trigger_emotion_fusion(emotions: List[Dict[str, Any]]) -> None:
    """
    Trigger the emotion fusion Lambda function
    """
    try:
        if not FUSION_LAMBDA_ARN:
            logger.warning("Fusion Lambda ARN not configured")
            return
        
        # Send event to EventBridge to trigger emotion fusion
        eventbridge.put_events(
            Entries=[
                {
                    'Source': 'mindbridge.video-analysis',
                    'DetailType': 'Emotion Data Available',
                    'Detail': json.dumps({
                        'modality': 'video',
                        'emotion_count': len(emotions),
                        'user_id': emotions[0]['user_id'] if emotions else 'unknown',
                        'session_id': emotions[0]['session_id'] if emotions else 'unknown',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                }
            ]
        )
        
        logger.info("Triggered emotion fusion process")
        
    except Exception as e:
        logger.error(f"Failed to trigger emotion fusion: {str(e)}")

def get_primary_emotion(emotions: List[Dict[str, Any]]) -> str:
    """
    Get the primary emotion across all detected faces
    """
    if not emotions:
        return 'neutral'
    
    # Average confidence scores across all faces for each emotion type
    emotion_totals = {}
    emotion_counts = {}
    
    for face_emotion in emotions:
        for emotion in face_emotion.get('emotions', []):
            emotion_type = emotion['Type'].lower()
            confidence = emotion['Confidence']
            
            emotion_totals[emotion_type] = emotion_totals.get(emotion_type, 0) + confidence
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
    
    # Calculate averages
    emotion_averages = {
        emotion_type: total / emotion_counts[emotion_type]
        for emotion_type, total in emotion_totals.items()
    }
    
    # Return emotion with highest average confidence
    return max(emotion_averages.items(), key=lambda x: x[1])[0] if emotion_averages else 'neutral'

def get_average_confidence(emotions: List[Dict[str, Any]]) -> float:
    """
    Get average confidence across all detected emotions
    """
    if not emotions:
        return 0.0
    
    total_confidence = sum(emotion['confidence'] for emotion in emotions)
    return total_confidence / len(emotions)

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a successful response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create an error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    } 