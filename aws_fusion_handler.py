"""
Production-Ready Multi-Modal Emotion Fusion Lambda Function
Deploy this to AWS Lambda to replace the basic template
"""

import json
import boto3
import logging
import os
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
try:
    bedrock = boto3.client('bedrock-runtime')
except:
    bedrock = None
    logger.warning("Bedrock client not available")

dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    🚀 MAIN LAMBDA HANDLER FOR EMOTION FUSION
    
    This function combines video, audio, and text emotion analysis into unified insights
    with AI-powered recommendations and risk assessment.
    """
    try:
        request_id = context.aws_request_id if context else 'local-test'
        logger.info(f"🚀 EMOTION FUSION STARTED - Request: {request_id}")
        logger.info(f"📥 Input Event: {json.dumps(event, default=str)}")
        
        # Process the fusion request
        result = process_fusion_request(event, context)
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Emotion fusion completed successfully',
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': request_id,
                'fusion_result': result
            })
        }
        
    except Exception as e:
        logger.error(f"❌ FUSION ERROR: {str(e)}")
        import traceback
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': context.aws_request_id if context else 'unknown'
            })
        }

def process_fusion_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Core fusion processing logic"""
    try:
        # Extract user/session info from different event sources
        user_id, session_id = extract_user_session(event)
        
        logger.info(f"👤 Processing fusion for user: {user_id}, session: {session_id}")
        
        # Step 1: Collect recent emotion data
        recent_emotions = collect_recent_emotions(user_id, session_id)
        
        if not recent_emotions:
            logger.info("ℹ️ No recent emotion data - creating baseline response")
            return create_baseline_response(user_id, session_id)
        
        logger.info(f"📈 Collected {len(recent_emotions)} emotion records for fusion")
        
        # Step 2: Advanced Multi-Modal Fusion
        unified_emotion = perform_advanced_fusion(recent_emotions)
        
        # Step 3: Generate Smart Recommendations
        recommendations = generate_recommendations(unified_emotion, recent_emotions)
        
        # Step 4: Store Results
        store_results(unified_emotion, recommendations, user_id, session_id)
        
        # Step 5: Handle High-Risk Situations
        handle_risk_alerts(unified_emotion, recommendations, user_id, session_id)
        
        # Step 6: Prepare Response
        response = {
            'unified_emotion': unified_emotion,
            'recommendations': recommendations,
            'user_id': user_id,
            'session_id': session_id,
            'processing_time': datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ FUSION COMPLETE: {unified_emotion.get('primary_emotion', 'unknown')}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in fusion processing: {str(e)}")
        raise

def extract_user_session(event: Dict[str, Any]) -> tuple:
    """Extract user_id and session_id from various event formats"""
    user_id = 'anonymous'
    session_id = 'default'
    
    # EventBridge event format
    if 'detail' in event:
        detail = event['detail']
        user_id = detail.get('user_id', user_id)
        session_id = detail.get('session_id', session_id)
    
    # API Gateway format
    elif 'body' in event:
        try:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
            user_id = body.get('user_id', user_id)
            session_id = body.get('session_id', session_id)
        except:
            pass
    
    # Direct invocation format
    else:
        user_id = event.get('user_id', user_id)
        session_id = event.get('session_id', session_id)
    
    return user_id, session_id

def collect_recent_emotions(user_id: str, session_id: str, window_minutes: int = 5) -> List[Dict[str, Any]]:
    """Collect recent emotion data from all modalities within time window"""
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        # Calculate time window
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        logger.info(f"🔍 Querying emotions from {window_start.strftime('%H:%M:%S')} to {now.strftime('%H:%M:%S')}")
        
        # Query for recent emotions
        response = table.query(
            KeyConditionExpression='user_id = :uid',
            FilterExpression='session_id = :sid AND #ts BETWEEN :start AND :end',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':uid': user_id,
                ':sid': session_id,
                ':start': window_start.isoformat(),
                ':end': now.isoformat()
            },
            ScanIndexForward=False,
            Limit=100
        )
        
        emotions = response.get('Items', [])
        logger.info(f"📈 Found {len(emotions)} emotion records")
        
        return emotions
        
    except Exception as e:
        logger.error(f"❌ Error collecting emotions: {str(e)}")
        return []

def perform_advanced_fusion(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Advanced multi-modal emotion fusion algorithm"""
    try:
        logger.info("🔬 Starting advanced multi-modal fusion")
        
        # Separate emotions by modality
        modalities = defaultdict(list)
        for item in emotion_data:
            modality = item.get('modality', 'unknown')
            if modality in ['video', 'audio', 'text']:
                modalities[modality].append(item)
        
        logger.info(f"📈 Modality breakdown: {dict((k, len(v)) for k, v in modalities.items())}")
        
        # Analyze each modality
        modality_insights = {}
        for modality, data in modalities.items():
            modality_insights[modality] = analyze_modality(data, modality)
        
        # Apply weighted fusion
        fusion_result = apply_weighted_fusion(modality_insights)
        
        # Add temporal analysis
        fusion_result = add_temporal_analysis(fusion_result, emotion_data)
        
        # Add risk assessment
        fusion_result = add_risk_assessment(fusion_result, modality_insights)
        
        # Enhance with AI (if available and sufficient data)
        if bedrock and len(emotion_data) >= 3:
            fusion_result = enhance_with_ai(fusion_result, emotion_data)
        
        logger.info(f"✨ Fusion complete: {fusion_result.get('primary_emotion')} (confidence: {fusion_result.get('confidence', 0):.2f})")
        return fusion_result
        
    except Exception as e:
        logger.error(f"❌ Fusion algorithm error: {str(e)}")
        return create_fallback_fusion(emotion_data)

def analyze_modality(data: List[Dict[str, Any]], modality: str) -> Dict[str, Any]:
    """Analyze emotion data for a specific modality"""
    if not data:
        return {
            'emotions': [],
            'primary_emotion': 'neutral',
            'confidence': 0.0,
            'stability': 1.0,
            'data_points': 0
        }
    
    # Extract emotions and confidences
    all_emotions = []
    all_confidences = []
    
    for item in data:
        emotion_data_item = item.get('emotion_data', {})
        
        # Handle different emotion data formats
        emotions = emotion_data_item.get('emotions', [])
        if isinstance(emotions, list) and emotions:
            all_emotions.extend(emotions)
        
        # Extract confidence
        confidence = emotion_data_item.get('confidence', 0.0)
        if confidence > 0:
            all_confidences.append(confidence)
        
        # Also check for primary_emotion directly
        primary = emotion_data_item.get('primary_emotion')
        if primary and primary != 'neutral':
            all_emotions.append({'name': primary, 'confidence': confidence})
    
    # Determine primary emotion
    if all_emotions:
        emotion_names = [e.get('name', 'neutral') for e in all_emotions if isinstance(e, dict)]
        if emotion_names:
            emotion_counter = Counter(emotion_names)
            primary_emotion = emotion_counter.most_common(1)[0][0]
        else:
            primary_emotion = 'neutral'
    else:
        primary_emotion = 'neutral'
    
    # Calculate average confidence
    avg_confidence = np.mean(all_confidences) if all_confidences else 0.0
    
    # Calculate emotional stability
    stability = calculate_stability(all_emotions)
    
    result = {
        'emotions': all_emotions,
        'primary_emotion': primary_emotion,
        'confidence': float(avg_confidence),
        'stability': stability,
        'data_points': len(data),
        'modality': modality
    }
    
    logger.info(f"📊 {modality.upper()} analysis: {primary_emotion} (conf: {avg_confidence:.2f}, stability: {stability:.2f})")
    return result

def calculate_stability(emotions: List[Dict[str, Any]]) -> float:
    """Calculate emotional stability (consistency) within a modality"""
    if len(emotions) < 2:
        return 1.0
    
    emotion_names = [e.get('name', 'neutral') for e in emotions if isinstance(e, dict)]
    if not emotion_names:
        return 1.0
    
    # Calculate entropy as measure of consistency
    emotion_counts = Counter(emotion_names)
    total = len(emotion_names)
    
    if total == 0:
        return 1.0
    
    entropy = 0
    for count in emotion_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)
    
    # Normalize entropy to 0-1 scale (1 = most stable)
    max_entropy = np.log2(len(emotion_counts)) if len(emotion_counts) > 1 else 1
    stability = 1 - (entropy / max_entropy) if max_entropy > 0 else 1.0
    
    return float(stability)

def apply_weighted_fusion(modality_insights: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Apply weighted fusion across modalities with dynamic weight adjustment"""
    # Base weights based on modality reliability
    base_weights = {
        'audio': 0.4,    # Voice patterns often most authentic
        'video': 0.35,   # Facial expressions important but can be controlled
        'text': 0.25     # Text can be deliberately filtered
    }
    
    # Adjust weights based on data quality
    adjusted_weights = {}
    total_weight = 0
    
    for modality, insights in modality_insights.items():
        if modality in base_weights:
            # Quality factor combines confidence and stability
            confidence = insights.get('confidence', 0.0)
            stability = insights.get('stability', 0.0)
            data_points = insights.get('data_points', 0)
            
            # Quality factor: more data points, higher confidence, higher stability = better quality
            quality_factor = min(1.0, (confidence * stability * min(data_points/3, 1)) ** 0.5)
            
            adjusted_weight = base_weights[modality] * quality_factor
            adjusted_weights[modality] = adjusted_weight
            total_weight += adjusted_weight
    
    # Normalize weights
    if total_weight > 0:
        for modality in adjusted_weights:
            adjusted_weights[modality] /= total_weight
    
    logger.info(f"⚖️ Fusion weights: {dict((k, round(v, 3)) for k, v in adjusted_weights.items())}")
    
    # Calculate weighted emotion scores
    emotion_scores = defaultdict(float)
    overall_confidence = 0
    
    for modality, insights in modality_insights.items():
        if modality in adjusted_weights:
            weight = adjusted_weights[modality]
            primary_emotion = insights.get('primary_emotion', 'neutral')
            confidence = insights.get('confidence', 0.0)
            
            emotion_scores[primary_emotion] += weight * confidence
            overall_confidence += weight * confidence
    
    # Determine unified emotion
    if emotion_scores:
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = emotion_scores[primary_emotion]
    else:
        primary_emotion = 'neutral'
        confidence = 0.0
    
    # Calculate intensity (1-10 scale)
    intensity = min(10, max(1, int(confidence * 10) + 1))
    
    return {
        'primary_emotion': primary_emotion,
        'confidence': float(confidence),
        'intensity': intensity,
        'fusion_weights': adjusted_weights,
        'modality_insights': modality_insights,
        'emotion_scores': dict(emotion_scores),
        'fusion_method': 'weighted_multi_modal',
        'timestamp': datetime.utcnow().isoformat()
    }

def add_temporal_analysis(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add temporal pattern analysis to understand emotion changes over time"""
    try:
        # Sort emotions by timestamp
        sorted_emotions = sorted(emotion_data, key=lambda x: x.get('timestamp', ''))
        
        if len(sorted_emotions) < 2:
            fusion_result['temporal_analysis'] = {
                'trend': 'stable',
                'volatility': 'low',
                'pattern': 'insufficient_data'
            }
            return fusion_result
        
        # Extract emotion sequence
        emotion_sequence = []
        for item in sorted_emotions:
            emotion_data_item = item.get('emotion_data', {})
            primary_emotion = emotion_data_item.get('primary_emotion', 'neutral')
            emotion_sequence.append(primary_emotion)
        
        # Analyze trends and patterns
        trend = analyze_emotion_trend(emotion_sequence)
        volatility = calculate_volatility(emotion_sequence)
        pattern = detect_patterns(emotion_sequence)
        
        temporal_analysis = {
            'trend': trend,
            'volatility': volatility,
            'pattern': pattern,
            'sequence_length': len(emotion_sequence),
            'unique_emotions': len(set(emotion_sequence)),
            'time_span_minutes': 5
        }
        
        fusion_result['temporal_analysis'] = temporal_analysis
        logger.info(f"⏱️ Temporal analysis: {trend} trend, {volatility} volatility, {pattern} pattern")
        
        return fusion_result
        
    except Exception as e:
        logger.error(f"❌ Temporal analysis error: {str(e)}")
        fusion_result['temporal_analysis'] = {'error': str(e)}
        return fusion_result

def analyze_emotion_trend(emotion_sequence: List[str]) -> str:
    """Analyze overall trend in emotional valence"""
    if len(emotion_sequence) < 3:
        return 'stable'
    
    # Map emotions to valence scores (-3 to +4)
    valence_map = {
        'happy': 4, 'joy': 4, 'excited': 3, 'calm': 2, 'neutral': 1,
        'surprised': 0, 'confused': 0, 'sad': -1, 'angry': -2, 
        'fear': -2, 'disgusted': -2, 'stressed': -3
    }
    
    # Convert to valence scores
    valences = [valence_map.get(emotion.lower(), 0) for emotion in emotion_sequence]
    
    # Calculate trend using simple linear regression
    n = len(valences)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(valences) / n
    
    numerator = sum((x[i] - x_mean) * (valences[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 'stable'
    
    slope = numerator / denominator
    
    if slope > 0.2:
        return 'improving'
    elif slope < -0.2:
        return 'declining'
    else:
        return 'stable'

def calculate_volatility(emotion_sequence: List[str]) -> str:
    """Calculate emotional volatility (how much emotions change)"""
    if len(emotion_sequence) < 2:
        return 'low'
    
    # Count emotion changes
    changes = sum(1 for i in range(1, len(emotion_sequence)) 
                  if emotion_sequence[i] != emotion_sequence[i-1])
    
    change_rate = changes / (len(emotion_sequence) - 1)
    
    if change_rate > 0.6:
        return 'high'
    elif change_rate > 0.3:
        return 'medium'
    else:
        return 'low'

def detect_patterns(emotion_sequence: List[str]) -> str:
    """Detect patterns in emotion sequence"""
    if len(emotion_sequence) < 3:
        return 'insufficient_data'
    
    # Check for constant emotion
    if len(set(emotion_sequence)) == 1:
        return 'constant'
    
    # Check for alternating pattern
    if len(emotion_sequence) >= 4:
        alternating = all(emotion_sequence[i] == emotion_sequence[i+2] 
                         for i in range(len(emotion_sequence)-2))
        if alternating and emotion_sequence[0] != emotion_sequence[1]:
            return 'alternating'
    
    return 'variable'

def add_risk_assessment(fusion_result: Dict[str, Any], modality_insights: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Comprehensive risk assessment for emotional state"""
    primary_emotion = fusion_result.get('primary_emotion', 'neutral')
    confidence = fusion_result.get('confidence', 0.0)
    intensity = fusion_result.get('intensity', 1)
    
    # Emotion-based risk levels
    high_risk_emotions = ['angry', 'fear', 'disgusted', 'stressed']
    medium_risk_emotions = ['sad', 'confused', 'surprised']
    
    # Base risk score
    if primary_emotion.lower() in high_risk_emotions:
        risk_score = 3.0
    elif primary_emotion.lower() in medium_risk_emotions:
        risk_score = 2.0
    else:
        risk_score = 1.0
    
    # Intensity adjustment
    if intensity >= 8:
        risk_score += 1.5
    elif intensity >= 6:
        risk_score += 0.5
    
    # Confidence adjustment
    if confidence >= 0.8:
        risk_score += 0.5
    elif confidence >= 0.6:
        risk_score += 0.25
    
    # Final risk level
    if risk_score >= 5:
        risk_level = 'critical'
    elif risk_score >= 4:
        risk_level = 'high'
    elif risk_score >= 2.5:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    risk_assessment = {
        'level': risk_level,
        'score': float(risk_score),
        'factors': {
            'emotion_severity': primary_emotion.lower() in high_risk_emotions,
            'high_intensity': intensity >= 7,
            'high_confidence': confidence >= 0.7
        }
    }
    
    fusion_result['risk_assessment'] = risk_assessment
    logger.info(f"🚨 Risk assessment: {risk_level} (score: {risk_score:.1f})")
    
    return fusion_result

def enhance_with_ai(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhance fusion with AI analysis using Amazon Bedrock Claude"""
    try:
        if not bedrock:
            logger.warning("⚠️ Bedrock not available for AI enhancement")
            return fusion_result
        
        # Prepare context for AI
        context = {
            'primary_emotion': fusion_result.get('primary_emotion'),
            'confidence': fusion_result.get('confidence'),
            'intensity': fusion_result.get('intensity'),
            'risk_level': fusion_result.get('risk_assessment', {}).get('level'),
            'modality_count': len(fusion_result.get('modality_insights', {})),
            'data_points': len(emotion_data)
        }
        
        prompt = f"""
        You are an expert emotional intelligence AI. Analyze this multi-modal emotion fusion result:

        Context: {json.dumps(context, indent=2)}

        Please provide enhancement insights in JSON format with these exact fields:
        {{
            "confidence_adjustment": <number between -0.3 and +0.3>,
            "contextual_insights": "<brief insight in 1-2 sentences>",
            "intervention_priority": "<low|medium|high|critical>"
        }}
        """
        
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 300,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        try:
            ai_insights = json.loads(ai_response)
            
            # Apply confidence adjustment
            if 'confidence_adjustment' in ai_insights:
                adj = float(ai_insights['confidence_adjustment'])
                fusion_result['confidence'] = max(0.0, min(1.0, 
                    fusion_result['confidence'] + adj))
            
            # Store AI insights
            fusion_result['ai_insights'] = ai_insights
            fusion_result['ai_enhanced'] = True
            
            logger.info("🤖 Successfully enhanced with AI insights")
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse AI response")
        
    except Exception as e:
        logger.error(f"❌ AI enhancement error: {str(e)}")
    
    return fusion_result

def generate_recommendations(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate personalized recommendations based on fusion results"""
    primary_emotion = fusion_result.get('primary_emotion', 'neutral')
    intensity = fusion_result.get('intensity', 1)
    risk_level = fusion_result.get('risk_assessment', {}).get('level', 'low')
    
    recommendations = {
        'immediate': [],
        'short_term': [],
        'long_term': [],
        'priority': 'low',
        'reasoning': ''
    }
    
    # High-risk immediate interventions
    if risk_level in ['high', 'critical']:
        recommendations['immediate'].extend([
            "Take 5 deep, slow breaths to activate your parasympathetic nervous system",
            "Step away from current stressors if possible",
            "Practice the 5-4-3-2-1 grounding technique"
        ])
        recommendations['priority'] = 'high'
        recommendations['reasoning'] = f"High-risk {primary_emotion} emotion detected with {intensity}/10 intensity"
    
    # Emotion-specific recommendations
    emotion_strategies = {
        'angry': {
            'immediate': ["Count to 10 slowly", "Clench and release your fists 3 times"],
            'short_term': ["Identify anger triggers", "Practice assertive communication"],
            'long_term': ["Consider anger management techniques", "Regular physical exercise"]
        },
        'sad': {
            'immediate': ["Listen to uplifting music", "Reach out to a supportive friend"],
            'short_term': ["Engage in activities you enjoy", "Practice gratitude journaling"],
            'long_term': ["Build stronger social connections", "Consider counseling if persistent"]
        },
        'stressed': {
            'immediate': ["Progressive muscle relaxation", "Take a 5-minute walk"],
            'short_term': ["Prioritize tasks and delegate", "Practice time management"],
            'long_term': ["Develop stress management skills", "Improve work-life balance"]
        },
        'happy': {
            'immediate': ["Share your joy with others", "Savor this positive moment"],
            'short_term': ["Plan activities that maintain this mood", "Express gratitude"],
            'long_term': ["Identify what contributes to happiness", "Build positive habits"]
        }
    }
    
    if primary_emotion.lower() in emotion_strategies:
        strategies = emotion_strategies[primary_emotion.lower()]
        recommendations['immediate'].extend(strategies.get('immediate', []))
        recommendations['short_term'].extend(strategies.get('short_term', []))
        recommendations['long_term'].extend(strategies.get('long_term', []))
    
    # Intensity-based adjustments
    if intensity >= 8:
        recommendations['immediate'].insert(0, "URGENT: Intense emotions detected - prioritize immediate relief")
        recommendations['priority'] = 'critical'
    
    # Remove duplicates and limit length
    for category in ['immediate', 'short_term', 'long_term']:
        recommendations[category] = list(dict.fromkeys(recommendations[category]))[:4]
    
    if not recommendations['reasoning']:
        recommendations['reasoning'] = f"Moderate {primary_emotion} emotion with {intensity}/10 intensity"
    
    logger.info(f"💡 Generated {recommendations['priority']} priority recommendations")
    return recommendations

def create_baseline_response(user_id: str, session_id: str) -> Dict[str, Any]:
    """Create baseline response when no emotion data is available"""
    return {
        'unified_emotion': {
            'primary_emotion': 'neutral',
            'confidence': 0.5,
            'intensity': 1,
            'fusion_method': 'baseline',
            'timestamp': datetime.utcnow().isoformat(),
            'risk_assessment': {'level': 'low', 'score': 1.0},
            'temporal_analysis': {'trend': 'stable', 'volatility': 'low', 'pattern': 'baseline'}
        },
        'recommendations': {
            'immediate': ["Take a moment to check in with yourself"],
            'short_term': ["Consider starting emotion tracking"],
            'long_term': ["Build emotional awareness practices"],
            'priority': 'low',
            'reasoning': 'No recent emotion data available'
        },
        'user_id': user_id,
        'session_id': session_id
    }

def create_fallback_fusion(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create fallback fusion when advanced processing fails"""
    if not emotion_data:
        return {
            'primary_emotion': 'neutral',
            'confidence': 0.0,
            'intensity': 1,
            'fusion_method': 'fallback_empty'
        }
    
    # Simple majority vote fallback
    emotions = []
    confidences = []
    
    for item in emotion_data:
        emotion_item = item.get('emotion_data', {})
        primary = emotion_item.get('primary_emotion', 'neutral')
        confidence = emotion_item.get('confidence', 0.0)
        
        emotions.append(primary)
        confidences.append(confidence)
    
    # Most common emotion
    emotion_counter = Counter(emotions)
    primary_emotion = emotion_counter.most_common(1)[0][0] if emotions else 'neutral'
    
    # Average confidence
    avg_confidence = np.mean(confidences) if confidences else 0.0
    
    return {
        'primary_emotion': primary_emotion,
        'confidence': float(avg_confidence),
        'intensity': min(10, max(1, int(avg_confidence * 10))),
        'fusion_method': 'fallback_majority_vote',
        'timestamp': datetime.utcnow().isoformat(),
        'data_points': len(emotion_data)
    }

def store_results(fusion_result: Dict[str, Any], recommendations: Dict[str, Any], 
                 user_id: str, session_id: str) -> None:
    """Store fusion results in DynamoDB for historical analysis"""
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        item = {
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id,
            'modality': 'fusion',
            'emotion_data': fusion_result,
            'recommendations': recommendations,
            'type': 'unified_emotion_state'
        }
        
        table.put_item(Item=item)
        logger.info("💾 Stored fusion results successfully")
        
    except Exception as e:
        logger.error(f"❌ Error storing results: {str(e)}")

def handle_risk_alerts(fusion_result: Dict[str, Any], recommendations: Dict[str, Any], 
                      user_id: str, session_id: str) -> None:
    """Handle high-risk emotional states with immediate alerts"""
    try:
        risk_level = fusion_result.get('risk_assessment', {}).get('level', 'low')
        
        if risk_level in ['high', 'critical']:
            # Send high-priority EventBridge event for real-time alerts
            eventbridge.put_events(
                Entries=[
                    {
                        'Source': 'mindbridge.emotion-fusion',
                        'DetailType': f'High Risk Emotional State Detected',
                        'Detail': json.dumps({
                            'user_id': user_id,
                            'session_id': session_id,
                            'risk_level': risk_level,
                            'primary_emotion': fusion_result.get('primary_emotion'),
                            'intensity': fusion_result.get('intensity'),
                            'confidence': fusion_result.get('confidence'),
                            'immediate_recommendations': recommendations.get('immediate', []),
                            'timestamp': datetime.utcnow().isoformat(),
                            'requires_intervention': risk_level == 'critical'
                        })
                    }
                ]
            )
            
            logger.info(f"🚨 HIGH RISK ALERT: {risk_level} level emotion detected for {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling risk alerts: {str(e)}")
