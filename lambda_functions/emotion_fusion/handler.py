"""
Emotion Fusion Lambda Function
Uses Amazon Bedrock (Claude) to fuse multi-modal emotion data and generate personalized recommendations
"""

import json
import boto3
import logging
import os
import numpy as np
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
        temporal_data = unified_emotion.get('temporal_analysis', {})
        recommendations = generate_comprehensive_recommendations(unified_emotion, temporal_data)
        
        # Store unified emotion state
        store_unified_emotion(unified_emotion, recommendations, user_id, session_id)
        
        # Store time-series data
        store_timestream_data(unified_emotion, user_id, session_id)
        
        # Send real-time updates
        send_realtime_updates(unified_emotion, recommendations, user_id, session_id)
        
        logger.info(f"Successfully processed emotion fusion for {user_id}")
        
    except Exception as e:
        logger.error(f"Error in emotion fusion processing: {str(e)}")

def collect_recent_emotions(user_id: str, session_id: str, window_minutes: int = 5) -> List[Dict[str, Any]]:
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
    Use advanced fusion logic combining rule-based and AI approaches
    """
    try:
        if not emotion_data:
            return None
        
        # First apply rule-based fusion for immediate processing
        rule_based_result = apply_rule_based_fusion(emotion_data)
        
        # Then enhance with AI analysis if available
        ai_enhanced_result = enhance_with_ai_analysis(emotion_data, rule_based_result)
        
        return ai_enhanced_result or rule_based_result
        
    except Exception as e:
        logger.error(f"Error in emotion fusion: {str(e)}")
        return apply_fallback_fusion(emotion_data)

def apply_rule_based_fusion(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Advanced rule-based emotion fusion algorithm
    """
    logger.info("🔗 APPLYING RULE-BASED FUSION")
    
    # Separate emotions by modality
    modality_emotions = {'video': [], 'audio': [], 'text': []}
    
    for item in emotion_data:
        modality = item.get('modality', 'unknown')
        emotion_data_content = item.get('emotion_data', {})
        
        if modality in modality_emotions:
            modality_emotions[modality].append({
                'timestamp': item.get('timestamp'),
                'emotions': emotion_data_content.get('emotions', []),
                'primary_emotion': emotion_data_content.get('primary_emotion', 'neutral'),
                'confidence': emotion_data_content.get('confidence', 0.0),
                'metadata': emotion_data_content
            })
    
    # Calculate modality-specific insights
    modality_insights = {}
    for modality, emotions in modality_emotions.items():
        if emotions:
            modality_insights[modality] = analyze_modality_emotions(emotions, modality)
    
    # Perform temporal analysis across modalities
    temporal_analysis = analyze_temporal_patterns(modality_emotions)
    
    # Apply fusion weights based on modality reliability
    fusion_weights = {
        'audio': 0.4,  # Voice patterns are often most authentic
        'video': 0.35, # Facial expressions can be masked but important
        'text': 0.25   # Text provides cognitive context
    }
    
    # Calculate weighted emotion scores
    emotion_scores = {}
    total_weight = 0
    
    for modality, insights in modality_insights.items():
        weight = fusion_weights.get(modality, 0.33)
        reliability_factor = insights['reliability_score']
        adjusted_weight = weight * reliability_factor
        total_weight += adjusted_weight
        
        for emotion_type, score in insights['emotion_scores'].items():
            if emotion_type not in emotion_scores:
                emotion_scores[emotion_type] = 0
            emotion_scores[emotion_type] += score * adjusted_weight
    
    # Normalize scores
    if total_weight > 0:
        emotion_scores = {k: v / total_weight for k, v in emotion_scores.items()}
    
    # Determine unified emotion
    unified_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else 'neutral'
    unified_confidence = emotion_scores.get(unified_emotion, 0.0)
    
    # Calculate intensity based on cross-modal consistency
    intensity = calculate_emotion_intensity(modality_insights, unified_emotion)
    
    # Enhanced risk assessment
    risk_assessment = enhanced_risk_assessment(unified_emotion, intensity, modality_insights, temporal_analysis)
    
    # Generate contextual explanation
    context = generate_fusion_context(unified_emotion, modality_insights, intensity)
    
    result = {
        'unified_emotion': unified_emotion,
        'intensity': intensity,
        'confidence': unified_confidence,
        'contributing_factors': list(modality_insights.keys()),
        'trend': temporal_analysis['trend'],
        'context': context,
        'risk_level': risk_assessment['risk_level'],
        'risk_factors': risk_assessment['risk_factors'],
        'fusion_method': 'rule_based',
        'modality_breakdown': modality_insights,
        'emotion_scores': emotion_scores,
        'temporal_analysis': temporal_analysis,
        'volatility': temporal_analysis['volatility']
    }
    
    logger.info(f"🎯 Rule-based fusion result: {unified_emotion} (intensity: {intensity}, confidence: {unified_confidence:.2f})")
    return result

def analyze_modality_emotions(emotions: List[Dict[str, Any]], modality: str) -> Dict[str, Any]:
    """
    Analyze emotions from a specific modality
    """
    if not emotions:
        return {'emotion_scores': {}, 'reliability_score': 0.0, 'consistency': 0.0}
    
    # Aggregate emotion scores across time
    emotion_totals = {}
    emotion_counts = {}
    confidences = []
    
    for emotion_data in emotions:
        confidences.append(emotion_data['confidence'])
        
        # Process individual emotions
        for emotion in emotion_data.get('emotions', []):
            emotion_type = emotion['Type'].lower()
            confidence = emotion['Confidence'] / 100.0  # Normalize to 0-1
            
            if emotion_type not in emotion_totals:
                emotion_totals[emotion_type] = 0
                emotion_counts[emotion_type] = 0
            
            emotion_totals[emotion_type] += confidence
            emotion_counts[emotion_type] += 1
    
    # Calculate average scores
    emotion_scores = {}
    for emotion_type, total in emotion_totals.items():
        emotion_scores[emotion_type] = total / emotion_counts[emotion_type]
    
    # Calculate reliability based on consistency and confidence
    avg_confidence = np.mean(confidences) if confidences else 0.0
    consistency = calculate_emotion_consistency(emotions)
    reliability_score = (avg_confidence / 100.0) * consistency
    
    # Apply modality-specific adjustments
    if modality == 'audio':
        reliability_score *= 1.1  # Audio tends to be more authentic
    elif modality == 'video':
        reliability_score *= 0.95  # Video can be affected by lighting, angle
    elif modality == 'text':
        reliability_score *= 0.9   # Text may not reflect immediate emotion
    
    return {
        'emotion_scores': emotion_scores,
        'reliability_score': min(1.0, reliability_score),
        'consistency': consistency,
        'data_points': len(emotions),
        'avg_confidence': avg_confidence
    }

def calculate_emotion_consistency(emotions: List[Dict[str, Any]]) -> float:
    """
    Calculate consistency of emotions over time
    """
    if len(emotions) < 2:
        return 1.0
    
    primary_emotions = [e['primary_emotion'] for e in emotions]
    
    # Calculate how often the same emotion appears
    emotion_counts = {}
    for emotion in primary_emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Consistency = (most frequent emotion count) / total count
    max_count = max(emotion_counts.values())
    consistency = max_count / len(primary_emotions)
    
    return consistency

def calculate_emotion_intensity(modality_insights: Dict[str, Any], unified_emotion: str) -> int:
    """
    Calculate emotion intensity based on cross-modal agreement
    """
    base_intensity = 5  # Default medium intensity
    
    # Check if unified emotion appears strongly across modalities
    modality_agreement = 0
    total_modalities = len(modality_insights)
    
    for modality, insights in modality_insights.items():
        emotion_scores = insights.get('emotion_scores', {})
        if unified_emotion in emotion_scores:
            score = emotion_scores[unified_emotion]
            if score > 0.6:  # Strong presence
                modality_agreement += 1
                base_intensity += int(score * 3)  # Boost intensity
    
    # Adjust based on cross-modal consistency
    if modality_agreement == total_modalities and total_modalities > 1:
        base_intensity += 2  # All modalities agree
    elif modality_agreement >= total_modalities * 0.67:
        base_intensity += 1  # Most modalities agree
    
    # Consider reliability scores
    avg_reliability = np.mean([insights['reliability_score'] for insights in modality_insights.values()])
    if avg_reliability > 0.8:
        base_intensity += 1
    
    return min(10, max(1, base_intensity))

def assess_emotion_trend(modality_insights: Dict[str, Any]) -> str:
    """
    Assess if emotions are improving, declining, or stable
    """
    # This is a simplified version - in practice, you'd analyze temporal patterns
    positive_emotions = {'happy', 'excited', 'calm', 'confident'}
    negative_emotions = {'sad', 'angry', 'fear', 'disgusted', 'confused'}
    
    positive_score = 0
    negative_score = 0
    
    for insights in modality_insights.values():
        emotion_scores = insights.get('emotion_scores', {})
        for emotion, score in emotion_scores.items():
            if emotion in positive_emotions:
                positive_score += score
            elif emotion in negative_emotions:
                negative_score += score
    
    if positive_score > negative_score * 1.2:
        return 'improving'
    elif negative_score > positive_score * 1.2:
        return 'declining'
    else:
        return 'stable'

def assess_risk_level(unified_emotion: str, intensity: int, modality_insights: Dict[str, Any]) -> str:
    """
    Assess mental health risk level
    """
    high_risk_emotions = {'sad', 'angry', 'fear', 'disgusted'}
    medium_risk_emotions = {'confused', 'surprised'}
    
    if unified_emotion in high_risk_emotions:
        if intensity >= 8:
            return 'high'
        elif intensity >= 6:
            return 'medium'
        else:
            return 'low'
    elif unified_emotion in medium_risk_emotions:
        if intensity >= 7:
            return 'medium'
        else:
            return 'low'
    else:
        return 'low'

def generate_fusion_context(unified_emotion: str, modality_insights: Dict[str, Any], intensity: int) -> str:
    """
    Generate contextual explanation of the fusion result
    """
    modalities_present = list(modality_insights.keys())
    
    context = f"The unified emotion '{unified_emotion}' was determined with intensity {intensity}/10 "
    context += f"based on analysis of {len(modalities_present)} modalities: {', '.join(modalities_present)}. "
    
    # Add modality-specific insights
    strongest_modality = max(modality_insights.items(), 
                           key=lambda x: x[1]['reliability_score'])[0]
    context += f"The {strongest_modality} signal provided the most reliable indicators."
    
    return context

def enhance_with_ai_analysis(emotion_data: List[Dict[str, Any]], rule_based_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Enhance rule-based fusion with AI analysis when available
    """
    try:
        # Only use AI if we have sufficient data and cloud access
        stage = os.environ.get('STAGE')
        if stage == 'local' or len(emotion_data) < 2:
            return rule_based_result
        
        # Prepare data for AI analysis
        formatted_data = format_emotion_data_for_ai(emotion_data)
        
        prompt = f"""
        You are an expert emotional intelligence AI. I have performed initial rule-based fusion and need your enhancement.

        Rule-based Result: {json.dumps(rule_based_result, indent=2)}
        
        Raw Emotion Data: {json.dumps(formatted_data, indent=2)}

        Please analyze and provide enhanced insights focusing on:
        1. Cross-modal emotional coherence and conflicts
        2. Temporal patterns and emotional transitions
        3. Contextual factors that may influence interpretation
        4. Confidence adjustments based on data quality

        Respond with JSON containing ONLY these fields:
        {{
            "confidence_adjustment": "number between -0.3 and +0.3 to adjust confidence",
            "intensity_adjustment": "number between -2 and +2 to adjust intensity",
            "enhanced_context": "additional contextual insights (1-2 sentences)",
            "risk_adjustment": "none, increase, or decrease"
        }}
        """
        
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        claude_response = result['content'][0]['text']
        
        try:
            ai_enhancements = json.loads(claude_response)
            
            # Apply AI enhancements to rule-based result
            enhanced_result = rule_based_result.copy()
            
            # Adjust confidence
            conf_adj = ai_enhancements.get('confidence_adjustment', 0)
            enhanced_result['confidence'] = max(0.0, min(1.0, 
                enhanced_result['confidence'] + conf_adj))
            
            # Adjust intensity
            int_adj = ai_enhancements.get('intensity_adjustment', 0)
            enhanced_result['intensity'] = max(1, min(10, 
                enhanced_result['intensity'] + int_adj))
            
            # Enhance context
            enhanced_context = ai_enhancements.get('enhanced_context', '')
            if enhanced_context:
                enhanced_result['context'] += f" {enhanced_context}"
            
            # Adjust risk level
            risk_adj = ai_enhancements.get('risk_adjustment', 'none')
            if risk_adj == 'increase':
                risk_levels = ['low', 'medium', 'high']
                current_idx = risk_levels.index(enhanced_result['risk_level'])
                enhanced_result['risk_level'] = risk_levels[min(2, current_idx + 1)]
            elif risk_adj == 'decrease':
                risk_levels = ['low', 'medium', 'high']
                current_idx = risk_levels.index(enhanced_result['risk_level'])
                enhanced_result['risk_level'] = risk_levels[max(0, current_idx - 1)]
            
            enhanced_result['fusion_method'] = 'ai_enhanced'
            enhanced_result['ai_model'] = BEDROCK_MODEL_ID
            
            logger.info("✨ Enhanced fusion result with AI analysis")
            return enhanced_result
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI enhancement response, using rule-based result")
            return rule_based_result
            
    except Exception as e:
        logger.error(f"AI enhancement failed: {str(e)}, using rule-based result")
        return rule_based_result

def apply_fallback_fusion(emotion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simple fallback fusion when advanced methods fail
    """
    logger.info("🔄 Applying fallback fusion")
    
    if not emotion_data:
        return {
            'unified_emotion': 'neutral',
            'intensity': 5,
            'confidence': 0.5,
            'contributing_factors': [],
            'trend': 'stable',
            'context': 'No emotion data available for analysis.',
            'risk_level': 'low',
            'fusion_method': 'fallback'
        }
    
    # Simple averaging approach
    all_emotions = []
    for item in emotion_data:
        emotion_data_content = item.get('emotion_data', {})
        primary_emotion = emotion_data_content.get('primary_emotion', 'neutral')
        confidence = emotion_data_content.get('confidence', 0.0)
        all_emotions.append((primary_emotion, confidence))
    
    # Find most confident emotion
    if all_emotions:
        best_emotion = max(all_emotions, key=lambda x: x[1])
        unified_emotion = best_emotion[0]
        confidence = best_emotion[1] / 100.0 if best_emotion[1] > 1 else best_emotion[1]
    else:
        unified_emotion = 'neutral'
        confidence = 0.5
    
    return {
        'unified_emotion': unified_emotion,
        'intensity': 5,
        'confidence': confidence,
        'contributing_factors': ['fallback'],
        'trend': 'stable', 
        'context': f'Fallback analysis identified {unified_emotion} as the primary emotion.',
        'risk_level': 'low',
        'fusion_method': 'fallback'
    }

def analyze_temporal_patterns(modality_emotions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Analyze temporal patterns across all modalities
    """
    all_timestamps = []
    all_emotions_with_time = []
    
    # Collect all emotion data with timestamps
    for modality, emotions in modality_emotions.items():
        for emotion_data in emotions:
            timestamp_str = emotion_data.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    all_timestamps.append(timestamp)
                    all_emotions_with_time.append({
                        'timestamp': timestamp,
                        'modality': modality,
                        'primary_emotion': emotion_data['primary_emotion'],
                        'confidence': emotion_data['confidence']
                    })
                except:
                    continue
    
    if not all_emotions_with_time:
        return {'trend': 'stable', 'volatility': 0.0, 'emotion_transitions': []}
    
    # Sort by timestamp
    all_emotions_with_time.sort(key=lambda x: x['timestamp'])
    
    # Analyze emotion transitions
    transitions = []
    if len(all_emotions_with_time) > 1:
        for i in range(1, len(all_emotions_with_time)):
            prev_emotion = all_emotions_with_time[i-1]['primary_emotion']
            curr_emotion = all_emotions_with_time[i]['primary_emotion']
            if prev_emotion != curr_emotion:
                transitions.append({
                    'from': prev_emotion,
                    'to': curr_emotion,
                    'timestamp': all_emotions_with_time[i]['timestamp']
                })
    
    # Calculate volatility (emotion change frequency)
    volatility = len(transitions) / len(all_emotions_with_time) if all_emotions_with_time else 0.0
    
    # Determine trend based on recent emotions
    positive_emotions = {'happy', 'excited', 'calm', 'confident'}
    negative_emotions = {'sad', 'angry', 'fear', 'disgusted', 'confused'}
    
    recent_trend = 'stable'
    if len(all_emotions_with_time) >= 3:
        recent_emotions = all_emotions_with_time[-3:]
        positive_count = sum(1 for e in recent_emotions if e['primary_emotion'] in positive_emotions)
        negative_count = sum(1 for e in recent_emotions if e['primary_emotion'] in negative_emotions)
        
        if positive_count > negative_count:
            recent_trend = 'improving'
        elif negative_count > positive_count:
            recent_trend = 'declining'
    
    return {
        'trend': recent_trend,
        'volatility': volatility,
        'emotion_transitions': transitions[-5:],  # Keep last 5 transitions
        'total_data_points': len(all_emotions_with_time),
        'analysis_window_minutes': (max(all_timestamps) - min(all_timestamps)).total_seconds() / 60 if len(all_timestamps) > 1 else 0
    }

def enhanced_risk_assessment(unified_emotion: str, intensity: int, modality_insights: Dict[str, Any], temporal_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced risk assessment considering temporal patterns and multi-modal consistency
    """
    base_risk = assess_risk_level(unified_emotion, intensity, modality_insights)
    
    # Risk factors
    risk_factors = []
    risk_score = 0
    
    # High-risk emotions with high intensity
    high_risk_emotions = {'sad', 'angry', 'fear', 'disgusted'}
    if unified_emotion in high_risk_emotions and intensity >= 7:
        risk_score += 2
        risk_factors.append(f"High intensity {unified_emotion} emotion")
    
    # Rapid emotion volatility
    volatility = temporal_analysis.get('volatility', 0.0)
    if volatility > 0.6:
        risk_score += 1
        risk_factors.append("High emotional volatility")
    
    # Declining trend
    if temporal_analysis.get('trend') == 'declining':
        risk_score += 1
        risk_factors.append("Declining emotional trend")
    
    # Inconsistency across modalities (potential masking)
    modality_count = len(modality_insights)
    if modality_count > 1:
        reliability_scores = [insights['reliability_score'] for insights in modality_insights.values()]
        if max(reliability_scores) - min(reliability_scores) > 0.3:
            risk_score += 1
            risk_factors.append("Inconsistent cross-modal signals")
    
    # Determine final risk level
    if risk_score >= 3:
        final_risk = 'high'
    elif risk_score >= 2:
        final_risk = 'medium'
    elif risk_score >= 1:
        final_risk = 'low'
    else:
        final_risk = 'low'
    
    return {
        'risk_level': final_risk,
        'risk_score': risk_score,
        'risk_factors': risk_factors,
        'base_risk': base_risk
    }

def generate_comprehensive_recommendations(emotion_state: Dict[str, Any], temporal_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive recommendations based on emotion state and temporal patterns
    """
    unified_emotion = emotion_state.get('unified_emotion', 'neutral')
    intensity = emotion_state.get('intensity', 5)
    trend = temporal_analysis.get('trend', 'stable')
    volatility = temporal_analysis.get('volatility', 0.0)
    
    recommendations = {
        'immediate_actions': [],
        'breathing_exercise': '',
        'environment_changes': [],
        'activity_suggestions': [],
        'when_to_seek_help': '',
        'positive_affirmations': [],
        'priority_level': 'low'
    }
    
    # Base recommendations by emotion type
    if unified_emotion in ['sad', 'depressed']:
        recommendations['immediate_actions'] = [
            'Acknowledge your feelings without judgment',
            'Reach out to a trusted friend or family member',
            'Engage in gentle physical movement'
        ]
        recommendations['activity_suggestions'] = [
            'Listen to uplifting music',
            'Practice gratitude journaling',
            'Spend time in nature or sunlight'
        ]
        recommendations['positive_affirmations'] = [
            'This feeling will pass',
            'You are valued and loved',
            'Every small step forward matters'
        ]
    
    elif unified_emotion in ['angry', 'frustrated']:
        recommendations['immediate_actions'] = [
            'Take 10 slow, deep breaths',
            'Step away from the triggering situation',
            'Use progressive muscle relaxation'
        ]
        recommendations['activity_suggestions'] = [
            'Physical exercise or movement',
            'Write down your thoughts',
            'Practice mindfulness meditation'
        ]
        recommendations['positive_affirmations'] = [
            'You have the power to choose your response',
            'This anger will fade with time',
            'You can handle this situation calmly'
        ]
    
    elif unified_emotion in ['anxious', 'worried', 'fear']:
        recommendations['immediate_actions'] = [
            'Use the 5-4-3-2-1 grounding technique',
            'Focus on what you can control',
            'Practice belly breathing'
        ]
        recommendations['activity_suggestions'] = [
            'Meditation or mindfulness exercises',
            'Talk to someone you trust',
            'Break overwhelming tasks into smaller steps'
        ]
        recommendations['positive_affirmations'] = [
            'You are safe in this moment',
            'You have overcome challenges before',
            'One breath at a time, one step at a time'
        ]
    
    else:  # Positive or neutral emotions
        recommendations['immediate_actions'] = [
            'Take a moment to appreciate this feeling',
            'Share your positive energy with others',
            'Continue what you are doing'
        ]
        recommendations['activity_suggestions'] = [
            'Engage in activities you enjoy',
            'Connect with loved ones',
            'Practice maintaining this positive state'
        ]
        recommendations['positive_affirmations'] = [
            'You deserve to feel good',
            'This positive energy serves you well',
            'You are in a good place right now'
        ]
    
    # Adjust based on intensity
    if intensity >= 8:
        recommendations['priority_level'] = 'high'
        recommendations['immediate_actions'].insert(0, 'Seek immediate support if feeling overwhelmed')
    elif intensity >= 6:
        recommendations['priority_level'] = 'medium'
    
    # Adjust based on trend
    if trend == 'declining':
        recommendations['when_to_seek_help'] = 'Consider professional support if this trend continues for more than a few days'
        recommendations['priority_level'] = 'medium' if recommendations['priority_level'] == 'low' else 'high'
    
    # Adjust based on volatility
    if volatility > 0.5:
        recommendations['environment_changes'].extend([
            'Create a calmer, more stable environment',
            'Reduce stimulation and distractions',
            'Establish routine activities'
        ])
        recommendations['breathing_exercise'] = 'Box breathing: Inhale 4 counts, hold 4, exhale 4, hold 4. Repeat for 2-3 minutes.'
    else:
        recommendations['breathing_exercise'] = '4-7-8 breathing: Inhale for 4 counts, hold for 7, exhale for 8. Repeat 3-4 times.'
    
    # Default environment changes if none specified
    if not recommendations['environment_changes']:
        recommendations['environment_changes'] = [
            'Ensure comfortable lighting and temperature',
            'Minimize distractions',
            'Create a peaceful space'
        ]
    
    recommendations['generated_at'] = datetime.utcnow().isoformat()
    return recommendations

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