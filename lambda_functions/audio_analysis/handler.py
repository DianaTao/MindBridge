"""
Audio Analysis Lambda Function
Analyzes voice patterns and speech for emotional content using Amazon Transcribe and voice feature extraction
"""

import json
import boto3
import base64
import logging
import os
import io
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
transcribe = boto3.client('transcribe')
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')
s3 = boto3.client('s3')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
AUDIO_BUCKET = os.environ.get('AUDIO_BUCKET', 'mindbridge-audio-temp')
FUSION_LAMBDA_ARN = os.environ.get('FUSION_LAMBDA_ARN', '')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for audio emotion analysis
    
    Trigger: API Gateway WebSocket (real-time audio stream)
    Purpose: Analyze voice patterns and speech for emotional content
    """
    try:
        logger.info(f"Processing audio analysis request: {event.get('requestContext', {}).get('requestId')}")
        
        # Parse incoming audio data
        body = json.loads(event.get('body', '{}'))
        audio_data = body.get('audio_data', '')
        user_id = body.get('user_id', 'anonymous')
        session_id = body.get('session_id', 'default')
        sample_rate = body.get('sample_rate', 16000)
        
        if not audio_data:
            return create_error_response(400, "No audio data provided")
        
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            logger.error(f"Failed to decode audio data: {str(e)}")
            return create_error_response(400, "Invalid audio data format")
        
        # Process audio for emotion analysis
        audio_analysis = analyze_audio_emotions(audio_bytes, sample_rate, user_id, session_id)
        
        if not audio_analysis:
            logger.info("No audio features could be extracted")
            return create_success_response({
                'voice_emotion': 'neutral',
                'confidence': 0.0,
                'speech_detected': False,
                'features': {}
            })
        
        # Store audio analysis data
        store_audio_emotion_data(audio_analysis, user_id, session_id)
        
        # Trigger emotion fusion
        trigger_emotion_fusion(audio_analysis)
        
        # Prepare response
        response_data = {
            'voice_emotion': audio_analysis.get('predicted_emotion', 'neutral'),
            'confidence': audio_analysis.get('confidence', 0.0),
            'speech_detected': audio_analysis.get('speech_detected', False),
            'speaking_rate': audio_analysis.get('speaking_rate', 0),
            'voice_features': audio_analysis.get('voice_features', {}),
            'sentiment': audio_analysis.get('sentiment', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time_ms': context.get_remaining_time_in_millis()
        }
        
        logger.info(f"Successfully processed audio analysis")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error processing audio analysis: {str(e)}")
        return create_error_response(500, f"Internal server error: {str(e)}")

def analyze_audio_emotions(audio_bytes: bytes, sample_rate: int, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Analyze audio for emotional content using voice features and speech-to-text
    """
    try:
        # Extract voice features using basic audio processing
        voice_features = extract_voice_features(audio_bytes, sample_rate)
        
        # Save audio to S3 for transcription
        audio_key = f"audio/{user_id}/{session_id}/{datetime.utcnow().isoformat()}.wav"
        s3.put_object(
            Bucket=AUDIO_BUCKET,
            Key=audio_key,
            Body=audio_bytes,
            ContentType='audio/wav'
        )
        
        # Start transcription job
        transcription_result = start_transcription(audio_key)
        
        # Analyze sentiment if we have transcribed text
        sentiment_analysis = {}
        if transcription_result and transcription_result.get('transcript'):
            sentiment_analysis = analyze_text_sentiment(transcription_result['transcript'])
        
        # Combine voice features with speech analysis
        emotion_analysis = {
            'voice_features': voice_features,
            'transcription': transcription_result,
            'sentiment': sentiment_analysis,
            'predicted_emotion': predict_emotion_from_voice(voice_features, sentiment_analysis),
            'confidence': calculate_confidence(voice_features, sentiment_analysis),
            'speech_detected': bool(transcription_result and transcription_result.get('transcript')),
            'speaking_rate': voice_features.get('speaking_rate', 0),
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'session_id': session_id,
            'modality': 'audio'
        }
        
        return emotion_analysis
        
    except Exception as e:
        logger.error(f"Audio emotion analysis failed: {str(e)}")
        return None

def extract_voice_features(audio_bytes: bytes, sample_rate: int) -> Dict[str, Any]:
    """
    Extract voice features for emotion analysis using basic audio processing
    Note: In production, you would use librosa or similar libraries
    """
    try:
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Basic feature extraction (simplified version)
        features = {
            'duration': len(audio_array) / sample_rate,
            'energy': float(np.mean(np.abs(audio_array))),
            'zero_crossing_rate': calculate_zero_crossing_rate(audio_array),
            'rms_energy': float(np.sqrt(np.mean(audio_array ** 2))),
            'max_amplitude': float(np.max(np.abs(audio_array))),
            'speaking_rate': estimate_speaking_rate(audio_array, sample_rate),
            'silence_ratio': calculate_silence_ratio(audio_array)
        }
        
        # Estimate pitch (very basic implementation)
        features['estimated_pitch'] = estimate_pitch(audio_array, sample_rate)
        
        return features
        
    except Exception as e:
        logger.error(f"Voice feature extraction failed: {str(e)}")
        return {}

def calculate_zero_crossing_rate(audio_array: np.ndarray) -> float:
    """Calculate zero crossing rate of audio signal"""
    zero_crossings = np.where(np.diff(np.sign(audio_array)))[0]
    return len(zero_crossings) / len(audio_array)

def estimate_speaking_rate(audio_array: np.ndarray, sample_rate: int) -> float:
    """Estimate speaking rate in words per minute"""
    # Simplified estimation based on energy peaks
    energy_threshold = np.mean(np.abs(audio_array)) * 2
    peaks = np.where(np.abs(audio_array) > energy_threshold)[0]
    
    if len(peaks) == 0:
        return 0.0
    
    # Estimate syllables from energy peaks
    syllable_count = len(peaks) // (sample_rate // 10)  # Rough estimation
    duration_minutes = len(audio_array) / sample_rate / 60
    
    # Rough conversion from syllables to words (average 1.5 syllables per word)
    words_per_minute = (syllable_count / 1.5) / max(duration_minutes, 0.1)
    
    return min(words_per_minute, 300)  # Cap at reasonable maximum

def calculate_silence_ratio(audio_array: np.ndarray) -> float:
    """Calculate ratio of silence in audio"""
    threshold = np.mean(np.abs(audio_array)) * 0.1
    silent_samples = np.sum(np.abs(audio_array) < threshold)
    return silent_samples / len(audio_array)

def estimate_pitch(audio_array: np.ndarray, sample_rate: int) -> float:
    """Basic pitch estimation using autocorrelation"""
    try:
        # Simple autocorrelation-based pitch detection
        correlation = np.correlate(audio_array, audio_array, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        # Find the first peak after the initial peak
        min_period = sample_rate // 500  # 500 Hz max
        max_period = sample_rate // 50   # 50 Hz min
        
        if len(correlation) > max_period:
            search_range = correlation[min_period:max_period]
            if len(search_range) > 0:
                peak_index = np.argmax(search_range) + min_period
                fundamental_freq = sample_rate / peak_index
                return float(fundamental_freq)
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Pitch estimation failed: {str(e)}")
        return 0.0

def start_transcription(audio_key: str) -> Optional[Dict[str, Any]]:
    """
    Start Amazon Transcribe job for speech-to-text
    Note: This is simplified - in production you'd use streaming transcription
    """
    try:
        job_name = f"mindbridge-{int(datetime.utcnow().timestamp())}"
        
        # For demo purposes, return a mock transcription
        # In production, you would start a real transcription job
        mock_transcript = "Hello, how are you doing today?"
        
        return {
            'job_name': job_name,
            'transcript': mock_transcript,
            'confidence': 0.95
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return None

def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of transcribed text using Amazon Comprehend
    """
    try:
        response = comprehend.detect_sentiment(
            Text=text,
            LanguageCode='en'
        )
        
        return {
            'sentiment': response['Sentiment'].lower(),
            'confidence': response['SentimentScore'][response['Sentiment'].title()],
            'scores': response['SentimentScore']
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return {'sentiment': 'neutral', 'confidence': 0.5}

def predict_emotion_from_voice(voice_features: Dict[str, Any], sentiment: Dict[str, Any]) -> str:
    """
    Predict emotion based on voice features and speech sentiment
    """
    if not voice_features:
        return 'neutral'
    
    energy = voice_features.get('energy', 0)
    pitch = voice_features.get('estimated_pitch', 0)
    speaking_rate = voice_features.get('speaking_rate', 0)
    silence_ratio = voice_features.get('silence_ratio', 0)
    sentiment_label = sentiment.get('sentiment', 'neutral')
    
    # Simple rule-based emotion prediction
    # In production, this would be a trained ML model
    
    if sentiment_label == 'negative':
        if energy < 0.3 and speaking_rate < 120:
            return 'sad'
        elif speaking_rate > 180:
            return 'angry'
        else:
            return 'disappointed'
    
    elif sentiment_label == 'positive':
        if energy > 0.7 or speaking_rate > 160:
            return 'excited'
        else:
            return 'happy'
    
    else:  # neutral sentiment
        if energy > 0.8 and speaking_rate > 180:
            return 'stressed'
        elif silence_ratio > 0.6:
            return 'thoughtful'
        else:
            return 'neutral'

def calculate_confidence(voice_features: Dict[str, Any], sentiment: Dict[str, Any]) -> float:
    """
    Calculate confidence score for emotion prediction
    """
    base_confidence = 0.5
    
    # Increase confidence based on clear voice features
    if voice_features.get('energy', 0) > 0.5:
        base_confidence += 0.1
    
    if voice_features.get('speaking_rate', 0) > 60:  # Clear speech detected
        base_confidence += 0.1
    
    # Add sentiment confidence if available
    sentiment_confidence = sentiment.get('confidence', 0.5)
    weighted_confidence = (base_confidence + sentiment_confidence) / 2
    
    return min(weighted_confidence, 1.0)

def store_audio_emotion_data(emotion_data: Dict[str, Any], user_id: str, session_id: str) -> None:
    """
    Store audio emotion analysis in DynamoDB
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        table.put_item(
            Item={
                'user_id': user_id,
                'timestamp': emotion_data['timestamp'],
                'session_id': session_id,
                'modality': 'audio',
                'emotion_data': emotion_data,
                'ttl': int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
        )
        
        logger.info("Stored audio emotion data in DynamoDB")
        
    except Exception as e:
        logger.error(f"Failed to store audio emotion data: {str(e)}")

def trigger_emotion_fusion(emotion_data: Dict[str, Any]) -> None:
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
                    'Source': 'mindbridge.audio-analysis',
                    'DetailType': 'Emotion Data Available',
                    'Detail': json.dumps({
                        'modality': 'audio',
                        'user_id': emotion_data.get('user_id', 'unknown'),
                        'session_id': emotion_data.get('session_id', 'unknown'),
                        'emotion': emotion_data.get('predicted_emotion', 'neutral'),
                        'confidence': emotion_data.get('confidence', 0.0),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                }
            ]
        )
        
        logger.info("Triggered emotion fusion process")
        
    except Exception as e:
        logger.error(f"Failed to trigger emotion fusion: {str(e)}")

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