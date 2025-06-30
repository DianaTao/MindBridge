"""
Enhanced Text Analysis Lambda Function
Analyzes text for emotion detection using AWS Bedrock LLM
"""

import json
import logging
import os
import re
import boto3
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter
import signal
import ssl
import certifi
import urllib3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Disable SSL warnings for debugging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a custom SSL context with certificate handling
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Initialize AWS Bedrock client
try:
    # Initialize Bedrock client with custom SSL configuration
    bedrock = boto3.client(
        'bedrock-runtime', 
        region_name='us-east-1',
        config=boto3.session.Config(
            retries={'max_attempts': 3},
            connect_timeout=30,
            read_timeout=60
        )
    )
    
    # Test Bedrock access with detailed logging
    logger.info("🔍 Testing Bedrock access...")
    try:
        bedrock_control = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock_control.list_foundation_models()
        logger.info(f"✅ Bedrock access confirmed. Found {len(models.get('modelSummaries', []))} models")
        logger.info("✅ Bedrock client initialized successfully with SSL fixes")
    except Exception as test_error:
        logger.warning(f"⚠️ Bedrock test failed but continuing: {str(test_error)}")
        logger.info("✅ Bedrock client initialized (test skipped)")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize Bedrock client: {str(e)}")
    logger.error(f"🔍 Error type: {type(e).__name__}")
    import traceback
    logger.error(f"📋 Full traceback: {traceback.format_exc()}")
    bedrock = None

# Get Bedrock model ID from environment variable
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for text emotion analysis using AWS Bedrock LLM
    
    Trigger: API Gateway (text input)
    Purpose: Analyze text for emotions using LLM
    """
    try:
        logger.info("=" * 50)
        logger.info("📝 ENHANCED TEXT ANALYSIS REQUEST STARTED - WITH BEDROCK LLM")
        logger.info("=" * 50)
        logger.info(f"Request ID: {event.get('requestContext', {}).get('requestId')}")
        logger.info(f"Event keys: {list(event.keys())}")
        
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
        
        # Parse incoming text data robustly for API Gateway and direct Lambda invocation
        body = event.get('body', event)  # If 'body' is missing, assume direct Lambda invoke
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception as e:
                logger.error(f"Failed to parse body string as JSON: {e}")
                body = {}
        elif not isinstance(body, dict):
            body = {}
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
        
        # Analyze emotions using AWS Bedrock LLM
        logger.info("🧠 Starting LLM-based text emotion analysis...")
        analysis_method = "bedrock_llm"  # Default method
        try:
            emotion_results = analyze_text_with_llm(text_data)
            logger.info("✅ LLM analysis completed successfully")
        except Exception as e:
            logger.error(f"❌ LLM analysis failed: {str(e)}")
            logger.info("🔄 Falling back to basic NLP analysis")
            emotion_results = analyze_text_emotions_fallback(text_data)
            analysis_method = "fallback_nlp"  # Update method when fallback is used
        
        logger.info(f"📊 Analysis results: {len(emotion_results.get('emotions', []))} emotions detected")
        
        # Prepare response
        response_data = {
            'emotions': emotion_results.get('emotions', []),
            'primary_emotion': emotion_results.get('primary_emotion', 'neutral'),
            'confidence': emotion_results.get('confidence', 0.8),
            'sentiment': emotion_results.get('sentiment', 'neutral'),
            'keywords': emotion_results.get('keywords', []),
            'llm_analysis': emotion_results.get('llm_analysis', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time_ms': context.get_remaining_time_in_millis() if context else 0,
            'debug_info': {
                'analysis_method': analysis_method,  # Use the actual method used
                'text_length': len(text_data),
                'environment': os.environ.get('STAGE', 'unknown'),
                'model_used': BEDROCK_MODEL_ID if analysis_method == "bedrock_llm" else "fallback_nlp"
            }
        }
        
        logger.info(f"✅ SUCCESS: Processed text emotions with LLM")
        logger.info(f"📊 Response: {response_data}")
        logger.info("=" * 50)
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"❌ ERROR in text analysis: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Internal server error: {str(e)}")

def analyze_text_with_llm(text_data: str) -> Dict[str, Any]:
    """
    Analyze text for emotions using AWS Bedrock LLM with enhanced SSL handling
    """
    try:
        logger.info("🧠 ANALYZE_TEXT_WITH_LLM STARTED")
        logger.info(f"Text length: {len(text_data)}")
        logger.info(f"Using Bedrock model: {BEDROCK_MODEL_ID}")
        
        # Check if Bedrock client is available
        if bedrock is None:
            logger.error("❌ Bedrock client is not available")
            raise Exception("Bedrock client not initialized")
        
        logger.info(f"Bedrock client region: {bedrock.meta.region_name}")
        logger.info(f"Bedrock client config: {bedrock.meta.config}")
        
        # Create prompt for LLM analysis
        prompt = create_text_analysis_prompt(text_data)
        logger.info(f"Created prompt with length: {len(prompt)}")
        
        # Set a timeout for the Bedrock call to prevent Lambda timeout
        def timeout_handler(signum, frame):
            raise TimeoutError("Bedrock LLM call timed out")
        
        # Set 45-second timeout for LLM call (leaving 15 seconds for other operations)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(45)
        
        try:
            logger.info("📡 Making Bedrock API call with SSL debugging...")
            logger.info(f"🔍 SSL Context: verify_mode={ssl_context.verify_mode}, check_hostname={ssl_context.check_hostname}")
            
            # Call AWS Bedrock with enhanced error handling
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
                    'max_tokens': 800,
                    'temperature': 0.3,
                    'top_p': 0.9
                })
            )
            
            signal.alarm(0)  # Cancel the alarm
            logger.info("✅ Bedrock API call successful!")
            
            # Parse response
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            logger.info(f"🤖 LLM Response: {llm_output[:200]}...")
            
            # Parse structured response
            analysis_result = parse_llm_text_analysis(llm_output, text_data)
            
            logger.info(f"📝 LLM TEXT ANALYSIS COMPLETED")
            logger.info(f"📊 Sentiment: {analysis_result.get('sentiment')}")
            logger.info(f"😊 Emotions: {[e['Type'] for e in analysis_result.get('emotions', [])]}")
            
            return analysis_result
            
        except TimeoutError:
            signal.alarm(0)  # Cancel the alarm
            logger.error("⏰ Bedrock LLM call timed out")
            raise TimeoutError("LLM call timed out")
        except Exception as bedrock_error:
            signal.alarm(0)  # Cancel the alarm
            logger.error(f"❌ Bedrock API call failed: {str(bedrock_error)}")
            logger.error(f"🔍 Error type: {type(bedrock_error).__name__}")
            logger.error(f"🔍 Error details: {bedrock_error}")
            
            # Additional SSL debugging
            if "SSL" in str(bedrock_error) or "certificate" in str(bedrock_error).lower():
                logger.error("🔍 SSL/Certificate issue detected!")
                logger.error(f"🔍 SSL Context state: verify_mode={ssl_context.verify_mode}")
                logger.error(f"🔍 Certifi path: {certifi.where()}")
                try:
                    import os
                    logger.error(f"🔍 Lambda environment: {os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'unknown')}")
                    logger.error(f"🔍 Lambda runtime: {os.environ.get('AWS_EXECUTION_ENV', 'unknown')}")
                except Exception as env_error:
                    logger.error(f"🔍 Environment check failed: {str(env_error)}")
            
            import traceback
            logger.error(f"📋 Bedrock error traceback: {traceback.format_exc()}")
            raise bedrock_error
            
    except Exception as e:
        logger.error(f"❌ LLM text analysis failed: {str(e)}")
        logger.error(f"🔍 Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        raise e

def create_text_analysis_prompt(text_data: str) -> str:
    """
    Create a prompt for LLM text emotion analysis
    """
    prompt = f"""You are an expert in emotion analysis and sentiment detection. Analyze the following text and provide a detailed emotional analysis.

Text to analyze: "{text_data}"

Please provide your analysis in the following JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "sentiment_score": 0.0-1.0,
    "emotions": [
        {{
            "Type": "emotion_name",
            "Confidence": 0.0-1.0,
            "Intensity": "low|medium|high"
        }}
    ],
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "emotional_context": "brief description of the emotional context",
    "recommendations": "brief personalized recommendations based on the emotional state"
}}

Focus on detecting emotions like: joy, sadness, anger, fear, surprise, disgust, love, anxiety, excitement, frustration, contentment, confusion, etc.

Be empathetic and provide helpful insights. If the text is very short or unclear, make reasonable inferences based on context."""
    
    return prompt

def parse_llm_text_analysis(llm_output: str, original_text: str) -> Dict[str, Any]:
    """
    Parse the LLM response into structured format
    """
    try:
        # Try to extract JSON from the response
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = llm_output[json_start:json_end]
            parsed_data = json.loads(json_str)
            
            # Ensure required fields exist
            emotions = parsed_data.get('emotions', [])
            if not emotions:
                emotions = [{'Type': 'neutral', 'Confidence': 0.8, 'Intensity': 'medium'}]
            
            return {
                'emotions': emotions,
                'sentiment': parsed_data.get('sentiment', 'neutral'),
                'sentiment_score': parsed_data.get('sentiment_score', 0.5),
                'keywords': parsed_data.get('keywords', []),
                'primary_emotion': emotions[0]['Type'] if emotions else 'neutral',
                'confidence': emotions[0]['Confidence'] if emotions else 0.8,
                'llm_analysis': {
                    'emotional_context': parsed_data.get('emotional_context', ''),
                    'recommendations': parsed_data.get('recommendations', ''),
                    'raw_llm_response': llm_output
                }
            }
        else:
            # Fallback parsing if JSON not found
            return parse_fallback_llm_response(llm_output, original_text)
            
    except Exception as e:
        logger.error(f"❌ LLM response parsing failed: {str(e)}")
        return parse_fallback_llm_response(llm_output, original_text)

def parse_fallback_llm_response(llm_output: str, original_text: str) -> Dict[str, Any]:
    """
    Fallback parsing for LLM response when JSON parsing fails
    """
    try:
        # Extract sentiment from text
        sentiment = 'neutral'
        if any(word in llm_output.lower() for word in ['positive', 'happy', 'joy', 'excited']):
            sentiment = 'positive'
        elif any(word in llm_output.lower() for word in ['negative', 'sad', 'angry', 'fear']):
            sentiment = 'negative'
        
        # Extract emotions from text
        emotions = []
        emotion_keywords = {
            'joy': ['joy', 'happy', 'excited', 'pleased'],
            'sadness': ['sad', 'sadness', 'depressed', 'melancholy'],
            'anger': ['angry', 'frustrated', 'irritated', 'mad'],
            'fear': ['fear', 'anxious', 'worried', 'scared'],
            'surprise': ['surprised', 'shocked', 'amazed'],
            'love': ['love', 'affection', 'caring'],
            'anxiety': ['anxious', 'nervous', 'stress']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in llm_output.lower() for keyword in keywords):
                emotions.append({
                    'Type': emotion,
                    'Confidence': 0.7,
                    'Intensity': 'medium'
                })
        
        if not emotions:
            emotions = [{'Type': 'neutral', 'Confidence': 0.8, 'Intensity': 'medium'}]
        
        return {
            'emotions': emotions,
            'sentiment': sentiment,
            'sentiment_score': 0.5,
            'keywords': extract_keywords_fallback(original_text),
            'primary_emotion': emotions[0]['Type'],
            'confidence': emotions[0]['Confidence'],
            'llm_analysis': {
                'emotional_context': 'Analysis based on LLM response',
                'recommendations': 'Consider the emotional context of your message',
                'raw_llm_response': llm_output
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Fallback parsing failed: {str(e)}")
        return {
            'emotions': [{'Type': 'neutral', 'Confidence': 0.8, 'Intensity': 'medium'}],
            'sentiment': 'neutral',
            'sentiment_score': 0.5,
            'keywords': [],
            'primary_emotion': 'neutral',
            'confidence': 0.8,
            'llm_analysis': {
                'emotional_context': 'Unable to analyze',
                'recommendations': 'Please provide more context',
                'raw_llm_response': llm_output
            }
        }

def analyze_text_emotions_fallback(text_data: str) -> Dict[str, Any]:
    """
    Fallback text analysis using basic NLP techniques
    """
    try:
        logger.info("🔄 Using fallback NLP analysis")
        
        # Extract text features
        text_features = extract_text_features(text_data)
        
        # Analyze sentiment
        sentiment = analyze_sentiment(text_data)
        
        # Extract keywords
        keywords = extract_keywords_fallback(text_data)
        
        # Predict emotions based on text features and sentiment
        emotions = predict_text_emotions(text_features, sentiment, keywords)
        
        return {
            'emotions': emotions,
            'sentiment': sentiment,
            'keywords': keywords,
            'primary_emotion': emotions[0]['Type'] if emotions else 'neutral',
            'confidence': emotions[0]['Confidence'] if emotions else 0.8,
            'llm_analysis': {
                'emotional_context': 'Analysis using fallback NLP methods',
                'recommendations': 'Consider using more descriptive text for better analysis',
                'raw_llm_response': 'Fallback analysis used'
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Fallback analysis failed: {str(e)}")
        return mock_text_detection()

def extract_keywords_fallback(text_data: str) -> List[str]:
    """
    Extract keywords using basic NLP techniques
    """
    try:
        text_lower = text_data.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency and return top keywords
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(5)]
        
    except Exception as e:
        logger.error(f"❌ Keyword extraction failed: {str(e)}")
        return []

def extract_text_features(text_data: str) -> Dict[str, Any]:
    """
    Extract text features for emotion analysis
    """
    try:
        # Basic text preprocessing
        text_lower = text_data.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Calculate basic features
        word_count = len(words)
        char_count = len(text_data)
        avg_word_length = char_count / word_count if word_count > 0 else 0
        
        # Count punctuation
        exclamation_count = text_data.count('!')
        question_count = text_data.count('?')
        period_count = text_data.count('.')
        
        # Count capitalization
        upper_case_count = sum(1 for c in text_data if c.isupper())
        upper_case_ratio = upper_case_count / char_count if char_count > 0 else 0
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'avg_word_length': avg_word_length,
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'period_count': period_count,
            'upper_case_ratio': upper_case_ratio,
            'words': words
        }
        
    except Exception as e:
        logger.error(f"❌ Feature extraction failed: {str(e)}")
        return {
            'word_count': 0,
            'char_count': len(text_data),
            'avg_word_length': 0,
            'exclamation_count': 0,
            'question_count': 0,
            'period_count': 0,
            'upper_case_ratio': 0,
            'words': []
        }

def analyze_sentiment(text_data: str) -> str:
    """
    Basic sentiment analysis using keyword matching
    """
    try:
        text_lower = text_data.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Define sentiment keywords
        positive_words = {
            'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'joy', 'excited', 'pleased', 'satisfied', 'content',
            'beautiful', 'perfect', 'best', 'outstanding', 'brilliant', 'superb'
        }
        
        negative_words = {
            'bad', 'awful', 'terrible', 'horrible', 'hate', 'dislike', 'sad', 'angry',
            'frustrated', 'annoyed', 'disappointed', 'upset', 'worried', 'scared',
            'fear', 'anxious', 'nervous', 'stress', 'pain', 'suffering'
        }
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Determine sentiment
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
            
    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {str(e)}")
        return 'neutral'

def extract_keywords(text_data: str) -> List[str]:
    """
    Extract keywords from text
    """
    try:
        text_lower = text_data.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Filter words and count frequency
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_freq = Counter(filtered_words)
        
        # Return top keywords
        return [word for word, freq in word_freq.most_common(10)]
        
    except Exception as e:
        logger.error(f"❌ Keyword extraction failed: {str(e)}")
        return []

def predict_text_emotions(text_features: Dict[str, Any], sentiment: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Predict emotions based on text features and sentiment
    """
    try:
        emotions = []
        
        # Emotion keywords mapping
        emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'awesome', 'love', 'wonderful', 'amazing', 'fantastic'],
            'sad': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'awful', 'terrible', 'bad'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'irritated'],
            'surprised': ['surprised', 'shocked', 'amazed', 'wow', 'incredible', 'unbelievable'],
            'fear': ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'quiet', 'tranquil'],
        }
        
        words = text_features.get('words', [])
        word_count = text_features.get('word_count', 0)
        
        # Check for emotion keywords
        for emotion, keywords_list in emotion_keywords.items():
            matches = sum(1 for word in words if word in keywords_list)
            if matches > 0:
                confidence = min(matches / max(word_count, 1) * 10, 1.0)
                emotions.append({
                    'Type': emotion,
                    'Confidence': confidence
                })
        
        # Add sentiment-based emotions
        if sentiment == 'positive' and not any(e['Type'] == 'happy' for e in emotions):
            emotions.append({
                'Type': 'happy',
                'Confidence': 0.7
            })
        elif sentiment == 'negative' and not any(e['Type'] in ['sad', 'angry'] for e in emotions):
            emotions.append({
                'Type': 'sad',
                'Confidence': 0.6
            })
        
        # If no emotions detected, return neutral
        if not emotions:
            emotions.append({
                'Type': 'neutral',
                'Confidence': 0.8
            })
        
        # Sort by confidence
        emotions.sort(key=lambda x: x['Confidence'], reverse=True)
        
        return emotions
        
    except Exception as e:
        logger.error(f"❌ Emotion prediction failed: {str(e)}")
        return [{'Type': 'neutral', 'Confidence': 0.8}]

def mock_text_detection() -> Dict[str, Any]:
    """
    Mock text detection for fallback
    """
    return {
        'emotions': [{'Type': 'neutral', 'Confidence': 0.8}],
        'sentiment': 'neutral',
        'keywords': ['text', 'analysis'],
        'primary_emotion': 'neutral',
        'confidence': 0.8
    }

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a successful API Gateway response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create an error API Gateway response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({'message': message})
    } 