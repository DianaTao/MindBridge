"""
Advanced Multi-Modal Emotion Fusion Lambda Function
Combines video, audio, and text emotion analysis with AI-powered insights
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
    Processes multi-modal emotion data and generates unified insights
    """
    try:
        logger.info(f"🚀 EMOTION FUSION LAMBDA STARTED - Request ID: {context.aws_request_id}")
        logger.info(f"📥 Event: {json.dumps(event, default=str)}")
        
        # Handle different event sources
        if 'Records' in event:
            # EventBridge event from other Lambda functions
            for record in event['Records']:
                if record.get('eventSource') == 'aws:events':
                    event_detail = record.get('detail', {})
                    result = process_emotion_fusion(event_detail)
                    if result:
                        logger.info("✅ Successfully processed EventBridge event")
        
        elif 'source' in event and event['source'].startswith('mindbridge'):
            # Direct EventBridge event
            result = process_emotion_fusion(event.get('detail', {}))
            
        elif 'body' in event:
            # API Gateway invocation
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
            result = process_emotion_fusion(body)
            
        else:
            # Direct invocation with event data
            result = process_emotion_fusion(event)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Emotion fusion completed successfully',
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': context.aws_request_id
            })
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR in emotion fusion: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': context.aws_request_id if context else 'unknown'
            })
        }

def process_emotion_fusion(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core emotion fusion processing logic
    """
    try:
        user_id = event_data.get('user_id', 'anonymous')
        session_id = event_data.get('session_id', 'default')
        
        logger.info(f"🔄 Processing fusion for user: {user_id}, session: {session_id}")
        
        # Step 1: Collect recent emotion data from all modalities
        recent_emotions = collect_recent_emotions(user_id, session_id)
        
        if not recent_emotions:
            logger.info("ℹ️ No recent emotion data found - creating baseline")
            return create_baseline_fusion_result(user_id, session_id)
        
        logger.info(f"📊 Collected {len(recent_emotions)} emotion records for fusion")
        
        # Step 2: Apply advanced fusion algorithms
        unified_emotion = fuse_multi_modal_emotions(recent_emotions)
        
        if not unified_emotion:
            logger.warning("⚠️ Fusion failed - using fallback")
            unified_emotion = create_fallback_fusion(recent_emotions)
        
        # Step 3: Generate personalized recommendations
        recommendations = generate_smart_recommendations(unified_emotion, recent_emotions)
        
        # Step 4: Store results
        store_fusion_results(unified_emotion, recommendations, user_id, session_id)
        
        # Step 5: Send real-time updates
        send_realtime_notifications(unified_emotion, recommendations, user_id, session_id)
        
        logger.info(f"✅ Successfully completed fusion for {user_id}")
        return unified_emotion
        
    except Exception as e:
        logger.error(f"❌ Error in fusion processing: {str(e)}")
        raise

def collect_recent_emotions(user_id: str, session_id: str, window_minutes: int = 5) -> List[Dict[str, Any]]:
    """
    Collect recent emotion data from DynamoDB within time window
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        # Calculate time window
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        logger.info(f"🔍 Querying emotions from {window_start} to {now}")
        
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

def fuse_multi_modal_emotions(emotion_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Advanced multi-modal emotion fusion using weighted algorithms
    """
    try:
        logger.info("🧠 Starting advanced emotion fusion")
        
        # Separate by modality
        modalities = defaultdict(list)
        for item in emotion_data:
            modality = item.get('modality', 'unknown')
            if modality in ['video', 'audio', 'text']:
                modalities[modality].append(item)
        
        logger.info(f"📊 Modality distribution: {dict(modalities)}")
        
        # Calculate modality-specific insights
        modality_results = {}
        for modality, data in modalities.items():
            modality_results[modality] = analyze_modality_data(data, modality)
        
        # Apply weighted fusion
        fusion_result = apply_weighted_fusion(modality_results)
        
        # Enhance with temporal analysis
        fusion_result = add_temporal_analysis(fusion_result, emotion_data)
        
        # Add risk assessment
        fusion_result = add_risk_assessment(fusion_result, modality_results)
        
        # Enhance with AI if available
        if bedrock and len(emotion_data) >= 3:
            fusion_result = enhance_with_ai(fusion_result, emotion_data)
        
        logger.info(f"✨ Fusion complete: {fusion_result.get('primary_emotion', 'unknown')}")
        return fusion_result
        
    except Exception as e:
        logger.error(f"❌ Error in emotion fusion: {str(e)}")
        return None

def analyze_modality_data(data: List[Dict[str, Any]], modality: str) -> Dict[str, Any]:
    """
    Analyze emotion data for a specific modality
    """
    if not data:
        return {'emotions': [], 'confidence': 0.0, 'primary_emotion': 'neutral'}
    
    # Extract emotions and confidences
    all_emotions = []
    all_confidences = []
    
    for item in data:
        emotion_data = item.get('emotion_data', {})
        emotions = emotion_data.get('emotions', [])
        
        if isinstance(emotions, list):
            all_emotions.extend(emotions)
        
        confidence = emotion_data.get('confidence', 0.0)
        if confidence > 0:
            all_confidences.append(confidence)
    
    # Calculate primary emotion
    if all_emotions:
        emotion_counter = Counter([e.get('name', 'neutral') for e in all_emotions if isinstance(e, dict)])
        primary_emotion = emotion_counter.most_common(1)[0][0]
    else:
        primary_emotion = 'neutral'
    
    # Calculate average confidence
    avg_confidence = np.mean(all_confidences) if all_confidences else 0.0
    
    # Calculate stability (consistency of emotions)
    stability = calculate_emotion_stability(all_emotions)
    
    return {
        'emotions': all_emotions,
        'primary_emotion': primary_emotion,
        'confidence': float(avg_confidence),
        'stability': stability,
        'data_points': len(data),
        'modality': modality
    }

def calculate_emotion_stability(emotions: List[Dict[str, Any]]) -> float:
    """
    Calculate how stable/consistent emotions are within a modality
    """
    if len(emotions) < 2:
        return 1.0
    
    emotion_names = [e.get('name', 'neutral') for e in emotions if isinstance(e, dict)]
    if not emotion_names:
        return 1.0
    
    # Calculate entropy as a measure of consistency
    emotion_counts = Counter(emotion_names)
    total = len(emotion_names)
    
    entropy = 0
    for count in emotion_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)
    
    # Normalize entropy to 0-1 scale (1 = most stable)
    max_entropy = np.log2(len(emotion_counts)) if len(emotion_counts) > 1 else 1
    stability = 1 - (entropy / max_entropy) if max_entropy > 0 else 1.0
    
    return float(stability)

def apply_weighted_fusion(modality_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply weighted fusion across modalities
    """
    # Define modality weights based on reliability
    weights = {
        'audio': 0.4,    # Voice is often most authentic
        'video': 0.35,   # Facial expressions important but can be masked
        'text': 0.25     # Text can be deliberate/filtered
    }
    
    # Adjust weights based on data quality and stability
    adjusted_weights = {}
    total_weight = 0
    
    for modality, result in modality_results.items():
        if modality in weights:
            # Adjust weight based on confidence and stability
            quality_factor = (result['confidence'] * result['stability']) ** 0.5
            adjusted_weight = weights[modality] * quality_factor
            adjusted_weights[modality] = adjusted_weight
            total_weight += adjusted_weight
    
    # Normalize weights
    if total_weight > 0:
        for modality in adjusted_weights:
            adjusted_weights[modality] /= total_weight
    
    logger.info(f"🎯 Adjusted fusion weights: {adjusted_weights}")
    
    # Collect all emotions with weights
    weighted_emotions = defaultdict(float)
    overall_confidence = 0
    
    for modality, result in modality_results.items():
        if modality in adjusted_weights:
            weight = adjusted_weights[modality]
            primary_emotion = result['primary_emotion']
            confidence = result['confidence']
            
            weighted_emotions[primary_emotion] += weight * confidence
            overall_confidence += weight * confidence
    
    # Determine unified emotion
    if weighted_emotions:
        primary_emotion = max(weighted_emotions.items(), key=lambda x: x[1])[0]
        confidence = weighted_emotions[primary_emotion]
    else:
        primary_emotion = 'neutral'
        confidence = 0.0
    
    # Calculate intensity (1-10 scale)
    intensity = min(10, max(1, int(confidence * 10)))
    
    return {
        'primary_emotion': primary_emotion,
        'confidence': float(confidence),
        'intensity': intensity,
        'modality_weights': adjusted_weights,
        'modality_results': modality_results,
        'fusion_method': 'weighted_multi_modal',
        'timestamp': datetime.utcnow().isoformat()
    }

def add_temporal_analysis(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add temporal pattern analysis to fusion result
    """
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
        
        # Analyze trend
        trend = analyze_emotion_trend(emotion_sequence)
        
        # Calculate volatility
        volatility = calculate_emotion_volatility(emotion_sequence)
        
        # Detect patterns
        pattern = detect_emotion_patterns(emotion_sequence)
        
        fusion_result['temporal_analysis'] = {
            'trend': trend,
            'volatility': volatility,
            'pattern': pattern,
            'sequence_length': len(emotion_sequence),
            'unique_emotions': len(set(emotion_sequence))
        }
        
        return fusion_result
        
    except Exception as e:
        logger.error(f"❌ Error in temporal analysis: {str(e)}")
        fusion_result['temporal_analysis'] = {'error': str(e)}
        return fusion_result

def analyze_emotion_trend(emotion_sequence: List[str]) -> str:
    """
    Analyze the overall trend in emotions
    """
    if len(emotion_sequence) < 2:
        return 'stable'
    
    # Map emotions to valence scores
    valence_map = {
        'happy': 4, 'joy': 4, 'excited': 3,
        'calm': 2, 'neutral': 1, 'surprised': 1,
        'confused': 0, 'sad': -1, 'angry': -2,
        'fear': -2, 'disgusted': -2, 'stressed': -3
    }
    
    # Convert sequence to valence scores
    valence_scores = [valence_map.get(emotion.lower(), 0) for emotion in emotion_sequence]
    
    # Calculate trend using linear regression
    n = len(valence_scores)
    x = list(range(n))
    
    # Simple linear regression slope
    x_mean = sum(x) / n
    y_mean = sum(valence_scores) / n
    
    numerator = sum((x[i] - x_mean) * (valence_scores[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 'stable'
    
    slope = numerator / denominator
    
    if slope > 0.1:
        return 'improving'
    elif slope < -0.1:
        return 'declining'
    else:
        return 'stable'

def calculate_emotion_volatility(emotion_sequence: List[str]) -> str:
    """
    Calculate emotion volatility/changeability
    """
    if len(emotion_sequence) < 2:
        return 'low'
    
    # Count emotion changes
    changes = sum(1 for i in range(1, len(emotion_sequence)) 
                  if emotion_sequence[i] != emotion_sequence[i-1])
    
    change_rate = changes / (len(emotion_sequence) - 1)
    
    if change_rate > 0.7:
        return 'high'
    elif change_rate > 0.3:
        return 'medium'
    else:
        return 'low'

def detect_emotion_patterns(emotion_sequence: List[str]) -> str:
    """
    Detect patterns in emotion sequence
    """
    if len(emotion_sequence) < 3:
        return 'insufficient_data'
    
    # Check for cycles
    if len(set(emotion_sequence)) == 1:
        return 'constant'
    
    # Check for alternating pattern
    if len(emotion_sequence) >= 4:
        alternating = all(emotion_sequence[i] == emotion_sequence[i+2] 
                         for i in range(len(emotion_sequence)-2))
        if alternating and emotion_sequence[0] != emotion_sequence[1]:
            return 'alternating'
    
    # Check for escalation/de-escalation
    valence_map = {
        'happy': 4, 'joy': 4, 'excited': 3, 'calm': 2, 'neutral': 1,
        'confused': 0, 'sad': -1, 'angry': -2, 'fear': -2, 'disgusted': -2
    }
    
    valences = [valence_map.get(emotion.lower(), 0) for emotion in emotion_sequence]
    
    if all(valences[i] <= valences[i+1] for i in range(len(valences)-1)):
        return 'escalating_positive'
    elif all(valences[i] >= valences[i+1] for i in range(len(valences)-1)):
        return 'escalating_negative'
    
    return 'variable'

def add_risk_assessment(fusion_result: Dict[str, Any], modality_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add comprehensive risk assessment
    """
    primary_emotion = fusion_result.get('primary_emotion', 'neutral')
    confidence = fusion_result.get('confidence', 0.0)
    intensity = fusion_result.get('intensity', 1)
    
    # Base risk from emotion type
    high_risk_emotions = ['angry', 'fear', 'disgusted', 'stressed', 'sad']
    medium_risk_emotions = ['confused', 'surprised']
    
    if primary_emotion.lower() in high_risk_emotions:
        base_risk = 'high'
    elif primary_emotion.lower() in medium_risk_emotions:
        base_risk = 'medium'
    else:
        base_risk = 'low'
    
    # Adjust risk based on intensity and confidence
    risk_score = 0
    if base_risk == 'high':
        risk_score = 3
    elif base_risk == 'medium':
        risk_score = 2
    else:
        risk_score = 1
    
    # Intensity multiplier
    if intensity >= 8:
        risk_score += 1
    elif intensity >= 6:
        risk_score += 0.5
    
    # Confidence multiplier
    if confidence >= 0.8:
        risk_score += 0.5
    elif confidence >= 0.6:
        risk_score += 0.25
    
    # Cross-modality consistency (if emotions agree, higher risk)
    modality_emotions = [r.get('primary_emotion', 'neutral') for r in modality_results.values()]
    if len(set(modality_emotions)) == 1 and primary_emotion.lower() in high_risk_emotions:
        risk_score += 1
    
    # Final risk level
    if risk_score >= 4:
        final_risk = 'critical'
    elif risk_score >= 3:
        final_risk = 'high'
    elif risk_score >= 2:
        final_risk = 'medium'
    else:
        final_risk = 'low'
    
    fusion_result['risk_assessment'] = {
        'level': final_risk,
        'score': float(risk_score),
        'factors': {
            'emotion_type': base_risk,
            'intensity': intensity,
            'confidence': confidence,
            'cross_modal_consistency': len(set(modality_emotions)) <= 1
        }
    }
    
    return fusion_result

def enhance_with_ai(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enhance fusion with AI analysis using Amazon Bedrock
    """
    try:
        if not bedrock:
            logger.warning("⚠️ Bedrock not available for AI enhancement")
            return fusion_result
        
        # Prepare data for AI
        ai_context = {
            'fusion_result': fusion_result,
            'emotion_count': len(emotion_data),
            'modalities': list(set(item.get('modality') for item in emotion_data)),
            'time_span_minutes': 5
        }
        
        prompt = f"""
        You are an expert emotion AI. Analyze this multi-modal emotion fusion result and provide enhancements.

        Current Fusion Result: {json.dumps(fusion_result, indent=2, default=str)}

        Context: {json.dumps(ai_context, default=str)}

        Please provide insights in JSON format with these fields only:
        {{
            "confidence_adjustment": "number between -0.3 and +0.3",
            "risk_adjustment": "increase, decrease, or none",
            "interpretation": "brief insight in 1-2 sentences",
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 400,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        try:
            ai_insights = json.loads(ai_response)
            
            # Apply AI enhancements
            if 'confidence_adjustment' in ai_insights:
                adjustment = float(ai_insights['confidence_adjustment'])
                fusion_result['confidence'] = max(0.0, min(1.0, 
                    fusion_result['confidence'] + adjustment))
            
            if 'interpretation' in ai_insights:
                fusion_result['ai_interpretation'] = ai_insights['interpretation']
            
            if 'recommendations' in ai_insights:
                fusion_result['ai_recommendations'] = ai_insights['recommendations']
            
            fusion_result['ai_enhanced'] = True
            logger.info("✨ Successfully enhanced with AI")
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse AI response")
        
    except Exception as e:
        logger.error(f"❌ AI enhancement error: {str(e)}")
    
    return fusion_result

def generate_smart_recommendations(fusion_result: Dict[str, Any], emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on fusion results
    """
    primary_emotion = fusion_result.get('primary_emotion', 'neutral')
    intensity = fusion_result.get('intensity', 1)
    risk_level = fusion_result.get('risk_assessment', {}).get('level', 'low')
    
    recommendations = {
        'immediate': [],
        'short_term': [],
        'long_term': [],
        'priority': 'low'
    }
    
    # Immediate recommendations based on emotion and risk
    if risk_level in ['high', 'critical']:
        recommendations['immediate'].extend([
            "Take slow, deep breaths for 2 minutes",
            "Step away from stressful stimuli if possible",
            "Consider reaching out to a trusted friend or counselor"
        ])
        recommendations['priority'] = 'high'
    
    # Emotion-specific recommendations
    emotion_recommendations = {
        'angry': {
            'immediate': ["Count to 10 slowly", "Take a brief walk"],
            'short_term': ["Practice anger management techniques", "Identify triggers"],
            'long_term': ["Consider stress management courses", "Regular exercise routine"]
        },
        'sad': {
            'immediate': ["Listen to uplifting music", "Practice gratitude"],
            'short_term': ["Connect with supportive people", "Engage in enjoyable activities"],
            'long_term': ["Consider counseling if persistent", "Build support network"]
        },
        'stressed': {
            'immediate': ["Progressive muscle relaxation", "Mindfulness breathing"],
            'short_term': ["Organize priorities", "Time management techniques"],
            'long_term': ["Stress management training", "Work-life balance"]
        },
        'happy': {
            'immediate': ["Share your joy with others", "Capture the positive moment"],
            'short_term': ["Plan activities that maintain positivity"],
            'long_term': ["Build habits that support well-being"]
        }
    }
    
    if primary_emotion.lower() in emotion_recommendations:
        emotion_recs = emotion_recommendations[primary_emotion.lower()]
        recommendations['immediate'].extend(emotion_recs.get('immediate', []))
        recommendations['short_term'].extend(emotion_recs.get('short_term', []))
        recommendations['long_term'].extend(emotion_recs.get('long_term', []))
    
    # Intensity-based adjustments
    if intensity >= 8:
        recommendations['immediate'].insert(0, "Urgent: Take immediate steps to manage intense emotions")
        recommendations['priority'] = 'critical' if risk_level == 'high' else 'high'
    
    # Remove duplicates and limit recommendations
    for category in ['immediate', 'short_term', 'long_term']:
        recommendations[category] = list(dict.fromkeys(recommendations[category]))[:5]
    
    return recommendations

def create_baseline_fusion_result(user_id: str, session_id: str) -> Dict[str, Any]:
    """
    Create a baseline fusion result when no data is available
    """
    return {
        'primary_emotion': 'neutral',
        'confidence': 0.5,
        'intensity': 1,
        'fusion_method': 'baseline',
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'session_id': session_id,
        'risk_assessment': {
            'level': 'low',
            'score': 1.0
        },
        'temporal_analysis': {
            'trend': 'stable',
            'volatility': 'low',
            'pattern': 'baseline'
        }
    }

def create_fallback_fusion(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create fallback fusion when advanced processing fails
    """
    if not emotion_data:
        return create_baseline_fusion_result('unknown', 'unknown')
    
    # Simple majority vote
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
    primary_emotion = emotion_counter.most_common(1)[0][0]
    
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

def store_fusion_results(fusion_result: Dict[str, Any], recommendations: Dict[str, Any], 
                        user_id: str, session_id: str) -> None:
    """
    Store fusion results in DynamoDB
    """
    try:
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        item = {
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id,
            'modality': 'fusion',
            'emotion_data': fusion_result,
            'recommendations': recommendations,
            'type': 'unified_emotion'
        }
        
        table.put_item(Item=item)
        logger.info("💾 Stored fusion results in DynamoDB")
        
    except Exception as e:
        logger.error(f"❌ Error storing fusion results: {str(e)}")

def send_realtime_notifications(fusion_result: Dict[str, Any], recommendations: Dict[str, Any], 
                               user_id: str, session_id: str) -> None:
    """
    Send real-time notifications for high-risk situations
    """
    try:
        risk_level = fusion_result.get('risk_assessment', {}).get('level', 'low')
        
        if risk_level in ['high', 'critical']:
            # Send EventBridge event for real-time processing
            eventbridge.put_events(
                Entries=[
                    {
                        'Source': 'mindbridge.emotion-fusion',
                        'DetailType': 'High Risk Emotion Detected',
                        'Detail': json.dumps({
                            'user_id': user_id,
                            'session_id': session_id,
                            'emotion': fusion_result.get('primary_emotion'),
                            'risk_level': risk_level,
                            'intensity': fusion_result.get('intensity'),
                            'recommendations': recommendations.get('immediate', []),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    }
                ]
            )
            
            logger.info(f"🚨 Sent high-risk notification for {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending notifications: {str(e)}") 