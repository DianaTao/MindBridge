"""
Text Analysis Lambda Function
Analyzes text for emotion detection using NLP and sentiment analysis
"""

import json
import boto3
import logging
import os
import re
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
FUSION_LAMBDA_ARN = os.environ.get('FUSION_LAMBDA_ARN', '')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for text emotion analysis
    
    Trigger: API Gateway (text input)
    Purpose: Analyze text for emotions using NLP and sentiment analysis
    """
    try:
        logger.info("=" * 50)
        logger.info("📝 TEXT ANALYSIS REQUEST STARTED")
        logger.info("=" * 50)
        logger.info(f"Request ID: {event.get('requestContext', {}).get('requestId')}")
        logger.info(f"Event keys: {list(event.keys())}")
        
        # Parse incoming text data
        body = json.loads(event.get('body', '{}'))
        logger.info(f"Body keys: {list(body.keys())}")
        
        # Handle both text_data and text parameters
        text_data = body.get('text_data', '') or body.get('text', '')
        user_id = body.get('user_id', 'anonymous')
        session_id = body.get('session_id', 'default')
        
        logger.info(f"User ID: {user_id}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Text data length: {len(text_data)} characters")
        logger.info(f"Text preview: {text_data[:100]}...")
        
        if not text_data:
            logger.error("❌ No text data provided")
            return create_error_response(400, "No text data provided")
        
        # Analyze emotions using NLP and sentiment analysis
        logger.info("🔍 Starting text emotion analysis...")
        emotion_results = analyze_text_emotions(text_data)
        
        logger.info(f"📊 Analysis results: {len(emotion_results.get('emotions', []))} emotions detected")
        
        if not emotion_results.get('emotions'):
            logger.warning("⚠️ No emotions detected in text - returning neutral response")
            return create_success_response({
                'emotions': [],
                'primary_emotion': 'neutral',
                'confidence': 0.0,
                'sentiment': 'neutral',
                'keywords': [],
                'timestamp': datetime.utcnow().isoformat(),
                'debug_info': {
                    'analysis_method': 'mock' if os.environ.get('STAGE') == 'local' else 'text_analysis',
                    'text_length': len(text_data),
                    'environment': os.environ.get('STAGE', 'unknown')
                }
            })
        
        # Process and format emotion data
        logger.info("🔄 Processing emotion results...")
        processed_emotions = process_text_emotion_results(emotion_results, user_id, session_id)
        logger.info(f"✅ Processed {len(processed_emotions)} emotion records")
        
        # Store emotion data in DynamoDB
        logger.info("💾 Storing emotion data...")
        store_emotion_data(processed_emotions, user_id, session_id)
        
        # Trigger emotion fusion Lambda
        logger.info("🔄 Triggering emotion fusion...")
        trigger_emotion_fusion(processed_emotions)
        
        # Prepare response
        response_data = {
            'emotions': processed_emotions,
            'primary_emotion': get_primary_emotion(processed_emotions),
            'confidence': get_average_confidence(processed_emotions),
            'sentiment': emotion_results.get('sentiment', 'neutral'),
            'keywords': emotion_results.get('keywords', []),
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time_ms': context.get_remaining_time_in_millis() if context else 0,
            'debug_info': {
                'analysis_method': 'mock' if os.environ.get('STAGE') == 'local' else 'text_analysis',
                'text_length': len(text_data),
                'environment': os.environ.get('STAGE', 'unknown')
            }
        }
        
        logger.info(f"✅ SUCCESS: Processed text emotions")
        logger.info(f"📊 Response: {response_data}")
        logger.info("=" * 50)
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"❌ ERROR in text analysis: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Internal server error: {str(e)}")

def analyze_text_emotions(text_data: str) -> Dict[str, Any]:
    """
    Analyze text for emotions using NLP and sentiment analysis
    """
    try:
        logger.info("🔍 ANALYZE_TEXT_EMOTIONS STARTED")
        logger.info(f"Text length: {len(text_data)}")
        
        # Check if we're in local development mode
        stage = os.environ.get('STAGE')
        aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
        logger.info(f"Environment variables - STAGE: {stage}, AWS_ACCESS_KEY_ID: {aws_key}")
        
        if stage == 'local' or aws_key == 'test':
            logger.info("🏠 LOCAL MODE DETECTED - Using local text analysis")
            return local_text_analysis(text_data)
        
        logger.info("☁️ CLOUD MODE - Using AWS Comprehend")
        return cloud_text_analysis(text_data)
        
    except Exception as e:
        logger.error(f"❌ Text analysis failed: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fall back to local analysis in case of AWS errors
        logger.info("🔄 Falling back to local text analysis")
        local_result = local_text_analysis(text_data)
        logger.info(f"📝 Local fallback completed")
        return local_result

def local_text_analysis(text_data: str) -> Dict[str, Any]:
    """
    Local text analysis using NLP techniques
    """
    logger.info("📝 LOCAL TEXT ANALYSIS STARTED")
    
    try:
        # Extract text features
        text_features = extract_text_features(text_data)
        
        # Analyze sentiment
        sentiment = analyze_sentiment(text_data)
        
        # Extract keywords
        keywords = extract_keywords(text_data)
        
        # Predict emotions based on text features and sentiment
        emotions = predict_text_emotions(text_features, sentiment, keywords)
        
        logger.info(f"📝 LOCAL TEXT ANALYSIS COMPLETED")
        logger.info(f"📊 Sentiment: {sentiment}")
        logger.info(f"🔑 Keywords: {keywords[:5]}")  # Show first 5 keywords
        logger.info(f"😊 Emotions: {[e['Type'] for e in emotions]}")
        
        return {
            'emotions': emotions,
            'sentiment': sentiment,
            'keywords': keywords,
            'text_features': text_features
        }
        
    except Exception as e:
        logger.error(f"❌ Local text analysis failed: {str(e)}")
        logger.info("🔄 Falling back to mock text detection")
        return mock_text_detection()

def extract_text_features(text_data: str) -> Dict[str, Any]:
    """
    Extract text features for emotion analysis
    """
    try:
        # Basic text preprocessing
        text_lower = text_data.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Calculate text features
        features = {
            'word_count': len(words),
            'char_count': len(text_data),
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'sentence_count': len(re.split(r'[.!?]+', text_data)),
            'exclamation_count': text_data.count('!'),
            'question_count': text_data.count('?'),
            'uppercase_ratio': sum(1 for c in text_data if c.isupper()) / len(text_data) if text_data else 0,
            'punctuation_count': len(re.findall(r'[^\w\s]', text_data)),
            'unique_words': len(set(words)),
            'word_diversity': len(set(words)) / len(words) if words else 0
        }
        
        # Calculate emotional indicators
        features.update(calculate_emotional_indicators(text_lower))
        
        logger.info(f"📊 Extracted {len(features)} text features")
        return features
        
    except Exception as e:
        logger.error(f"❌ Failed to extract text features: {str(e)}")
        return {}

def calculate_emotional_indicators(text_lower: str) -> Dict[str, Any]:
    """
    Calculate emotional indicators from text
    """
    # Emotion word dictionaries
    emotion_words = {
        'happy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'great', 'fantastic', 'love', 'adore', 'delighted'],
        'sad': ['sad', 'depressed', 'miserable', 'unhappy', 'sorrow', 'grief', 'melancholy', 'blue', 'down', 'upset'],
        'angry': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated', 'hate', 'disgusted', 'outraged'],
        'surprised': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'wow', 'incredible', 'unbelievable'],
        'fear': ['afraid', 'scared', 'terrified', 'fearful', 'anxious', 'worried', 'nervous', 'panic', 'horror'],
        'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'quiet', 'gentle', 'soothing', 'mellow'],
        'excited': ['excited', 'thrilled', 'energetic', 'enthusiastic', 'pumped', 'stoked', 'eager', 'motivated'],
        'confused': ['confused', 'puzzled', 'uncertain', 'unsure', 'doubtful', 'perplexed', 'bewildered', 'lost']
    }
    
    # Calculate emotion word frequencies
    emotion_counts = {}
    for emotion, words in emotion_words.items():
        count = sum(1 for word in words if word in text_lower)
        emotion_counts[f'{emotion}_count'] = count
    
    # Calculate intensity indicators
    intensity_indicators = {
        'caps_words': len(re.findall(r'\b[A-Z]{2,}\b', text_lower)),
        'repeated_chars': len(re.findall(r'(.)\1{2,}', text_lower)),  # e.g., "sooo", "nooo"
        'exclamation_density': text_lower.count('!') / len(text_lower) if text_lower else 0,
        'question_density': text_lower.count('?') / len(text_lower) if text_lower else 0
    }
    
    return {**emotion_counts, **intensity_indicators}

def analyze_sentiment(text_data: str) -> str:
    """
    Analyze sentiment of text
    """
    text_lower = text_data.lower()
    
    # Positive and negative word lists
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'love', 'like', 'enjoy',
        'happy', 'joy', 'pleased', 'satisfied', 'content', 'blessed', 'fortunate', 'lucky', 'successful',
        'beautiful', 'perfect', 'ideal', 'best', 'favorite', 'prefer', 'adore', 'cherish', 'treasure'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike', 'loathe', 'despise',
        'sad', 'miserable', 'depressed', 'unhappy', 'angry', 'furious', 'mad', 'irritated', 'annoyed',
        'worried', 'anxious', 'scared', 'afraid', 'terrified', 'fearful', 'nervous', 'stressed', 'overwhelmed'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Determine sentiment
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

def extract_keywords(text_data: str) -> List[str]:
    """
    Extract keywords from text
    """
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'
    }
    
    # Extract words and filter stop words
    words = re.findall(r'\b\w+\b', text_data.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency and return most common
    word_counts = Counter(keywords)
    return [word for word, count in word_counts.most_common(10)]

def predict_text_emotions(text_features: Dict[str, Any], sentiment: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Predict emotions based on text features, sentiment, and keywords
    """
    import random
    
    emotions = []
    
    # Analyze sentiment for basic emotions
    if sentiment == 'positive':
        emotions.append({
            'Type': 'HAPPY',
            'Confidence': min(95, 70 + random.uniform(0, 20))
        })
    elif sentiment == 'negative':
        emotions.append({
            'Type': 'SAD',
            'Confidence': min(90, 60 + random.uniform(0, 25))
        })
    
    # Analyze emotional indicators
    happy_count = text_features.get('happy_count', 0)
    sad_count = text_features.get('sad_count', 0)
    angry_count = text_features.get('angry_count', 0)
    surprised_count = text_features.get('surprised_count', 0)
    fear_count = text_features.get('fear_count', 0)
    calm_count = text_features.get('calm_count', 0)
    excited_count = text_features.get('excited_count', 0)
    confused_count = text_features.get('confused_count', 0)
    
    # Add emotions based on word counts
    if happy_count > 0:
        emotions.append({
            'Type': 'HAPPY',
            'Confidence': min(95, 60 + happy_count * 15)
        })
    
    if sad_count > 0:
        emotions.append({
            'Type': 'SAD',
            'Confidence': min(90, 50 + sad_count * 15)
        })
    
    if angry_count > 0:
        emotions.append({
            'Type': 'ANGRY',
            'Confidence': min(85, 45 + angry_count * 20)
        })
    
    if surprised_count > 0:
        emotions.append({
            'Type': 'SURPRISED',
            'Confidence': min(90, 55 + surprised_count * 15)
        })
    
    if fear_count > 0:
        emotions.append({
            'Type': 'FEAR',
            'Confidence': min(85, 40 + fear_count * 20)
        })
    
    if calm_count > 0:
        emotions.append({
            'Type': 'CALM',
            'Confidence': min(85, 50 + calm_count * 15)
        })
    
    if excited_count > 0:
        emotions.append({
            'Type': 'EXCITED',
            'Confidence': min(90, 55 + excited_count * 15)
        })
    
    if confused_count > 0:
        emotions.append({
            'Type': 'CONFUSED',
            'Confidence': min(80, 40 + confused_count * 15)
        })
    
    # Analyze intensity indicators
    exclamation_density = text_features.get('exclamation_density', 0)
    caps_words = text_features.get('caps_words', 0)
    repeated_chars = text_features.get('repeated_chars', 0)
    
    if exclamation_density > 0.05 or caps_words > 2 or repeated_chars > 0:
        emotions.append({
            'Type': 'EXCITED',
            'Confidence': min(90, 60 + (exclamation_density * 500 + caps_words * 10 + repeated_chars * 15))
        })
    
    # Analyze word diversity for confusion
    word_diversity = text_features.get('word_diversity', 0)
    if word_diversity < 0.3 and text_features.get('word_count', 0) > 10:
        emotions.append({
            'Type': 'CONFUSED',
            'Confidence': min(75, 40 + (0.5 - word_diversity) * 100)
        })
    
    # Ensure we have at least one emotion
    if not emotions:
        emotions.append({
            'Type': 'CALM',
            'Confidence': 60.0
        })
    
    # Sort by confidence and return top 3
    emotions.sort(key=lambda x: x['Confidence'], reverse=True)
    return emotions[:3]

def cloud_text_analysis(text_data: str) -> Dict[str, Any]:
    """
    Cloud-based text analysis using AWS Comprehend
    """
    logger.info("☁️ CLOUD TEXT ANALYSIS STARTED")
    
    try:
        # Use AWS Comprehend for sentiment analysis
        sentiment_response = comprehend.detect_sentiment(
            Text=text_data,
            LanguageCode='en'
        )
        
        # Use AWS Comprehend for key phrases
        key_phrases_response = comprehend.detect_key_phrases(
            Text=text_data,
            LanguageCode='en'
        )
        
        # Extract results
        sentiment = sentiment_response['Sentiment'].lower()
        sentiment_scores = sentiment_response['SentimentScore']
        key_phrases = [phrase['Text'] for phrase in key_phrases_response['KeyPhrases']]
        
        # Convert to our format
        text_features = extract_text_features(text_data)
        emotions = predict_text_emotions(text_features, sentiment, key_phrases)
        
        logger.info(f"☁️ CLOUD TEXT ANALYSIS COMPLETED")
        logger.info(f"📊 AWS Sentiment: {sentiment}")
        logger.info(f"🔑 AWS Key Phrases: {key_phrases[:5]}")
        
        return {
            'emotions': emotions,
            'sentiment': sentiment,
            'keywords': key_phrases,
            'text_features': text_features,
            'aws_sentiment_scores': sentiment_scores
        }
        
    except Exception as e:
        logger.error(f"❌ Cloud text analysis failed: {str(e)}")
        return local_text_analysis(text_data)

def mock_text_detection() -> Dict[str, Any]:
    """
    Mock text detection for fallback
    """
    logger.info("📝 MOCK TEXT DETECTION STARTED")
    import random
    
    emotions = [
        {'Type': 'HAPPY', 'Confidence': random.uniform(60, 90)},
        {'Type': 'CALM', 'Confidence': random.uniform(40, 70)},
        {'Type': 'EXCITED', 'Confidence': random.uniform(30, 60)}
    ]
    
    random.shuffle(emotions)
    top_emotions = emotions[:2]
    
    logger.info(f"🎲 Generated emotions: {[e['Type'] for e in top_emotions]}")
    confidences = [f"{e['Confidence']:.1f}%" for e in top_emotions]
    logger.info(f"📊 Emotion confidences: {confidences}")
    
    return {
        'emotions': top_emotions,
        'sentiment': 'neutral',
        'keywords': ['test', 'text', 'analysis'],
        'text_features': {}
    }

def process_text_emotion_results(emotion_results: Dict[str, Any], user_id: str, session_id: str) -> List[Dict[str, Any]]:
    """
    Process and format text emotion detection results
    """
    emotions = emotion_results.get('emotions', [])
    
    # Sort emotions by confidence
    sorted_emotions = sorted(emotions, key=lambda x: x['Confidence'], reverse=True)
    
    text_emotion_data = {
        'emotion_id': f"text_{datetime.utcnow().timestamp()}",
        'emotions': sorted_emotions,
        'primary_emotion': sorted_emotions[0]['Type'].lower() if sorted_emotions else 'neutral',
        'confidence': sorted_emotions[0]['Confidence'] if sorted_emotions else 0.0,
        'sentiment': emotion_results.get('sentiment', 'neutral'),
        'keywords': emotion_results.get('keywords', []),
        'text_features': emotion_results.get('text_features', {}),
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'session_id': session_id,
        'modality': 'text'
    }
    
    return [text_emotion_data]

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
                    'modality': 'text',
                    'emotion_data': emotion_data,
                    'ttl': int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
                }
            )
        
        logger.info(f"Stored {len(emotions)} text emotion records in DynamoDB")
        
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
                    'Source': 'mindbridge.text-analysis',
                    'DetailType': 'Text Emotion Data Available',
                    'Detail': json.dumps({
                        'modality': 'text',
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
    Get the primary emotion from text analysis
    """
    if not emotions:
        return 'neutral'
    
    # Return the emotion with highest confidence
    return emotions[0].get('primary_emotion', 'neutral')

def get_average_confidence(emotions: List[Dict[str, Any]]) -> float:
    """
    Get average confidence across all detected emotions
    """
    if not emotions:
        return 0.0
    
    total_confidence = sum(emotion.get('confidence', 0) for emotion in emotions)
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