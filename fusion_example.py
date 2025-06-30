"""
Example demonstrating the emotion fusion logic
Run this to see how multi-modal emotions are combined
"""

import json
from collections import defaultdict, Counter
import numpy as np

def demonstrate_fusion_logic():
    """
    🎯 DEMONSTRATION: Multi-Modal Emotion Fusion
    
    Shows how video, audio, and text emotions are combined into unified insights
    """
    
    print("🧠 EMOTION FUSION DEMONSTRATION")
    print("=" * 50)
    
    # Sample multi-modal emotion data
    sample_data = {
        "video": {
            "emotions": [
                {"name": "sad", "confidence": 0.85},
                {"name": "sad", "confidence": 0.82},
                {"name": "neutral", "confidence": 0.15}
            ],
            "primary_emotion": "sad",
            "confidence": 0.85,
            "stability": 0.9,  # High consistency
            "data_points": 3
        },
        "audio": {
            "emotions": [
                {"name": "stressed", "confidence": 0.75},
                {"name": "angry", "confidence": 0.65}
            ],
            "primary_emotion": "stressed", 
            "confidence": 0.75,
            "stability": 0.6,  # Medium consistency
            "data_points": 2
        },
        "text": {
            "emotions": [
                {"name": "neutral", "confidence": 0.6}
            ],
            "primary_emotion": "neutral",
            "confidence": 0.6,
            "stability": 0.8,  # High consistency (only one emotion)
            "data_points": 1
        }
    }
    
    print("📊 INPUT DATA:")
    for modality, data in sample_data.items():
        print(f"  {modality.upper()}:")
        print(f"    Primary: {data['primary_emotion']} (conf: {data['confidence']:.2f})")
        print(f"    Stability: {data['stability']:.2f}")
        print(f"    Data points: {data['data_points']}")
    
    print("\n⚖️ WEIGHTED FUSION CALCULATION:")
    
    # Step 1: Base weights
    base_weights = {
        'audio': 0.4,    # Voice most authentic
        'video': 0.35,   # Facial expressions important
        'text': 0.25     # Text can be filtered
    }
    print(f"  Base weights: {base_weights}")
    
    # Step 2: Quality adjustments
    adjusted_weights = {}
    total_weight = 0
    
    for modality, data in sample_data.items():
        if modality in base_weights:
            confidence = data['confidence']
            stability = data['stability']
            data_points = data['data_points']
            
            # Quality factor
            quality_factor = min(1.0, (confidence * stability * min(data_points/3, 1)) ** 0.5)
            adjusted_weight = base_weights[modality] * quality_factor
            adjusted_weights[modality] = adjusted_weight
            total_weight += adjusted_weight
            
            print(f"  {modality}: {base_weights[modality]:.2f} × {quality_factor:.3f} = {adjusted_weight:.3f}")
    
    # Step 3: Normalize weights
    if total_weight > 0:
        for modality in adjusted_weights:
            adjusted_weights[modality] /= total_weight
    
    print(f"  Final weights: {dict((k, round(v, 3)) for k, v in adjusted_weights.items())}")
    
    # Step 4: Calculate weighted emotion scores
    emotion_scores = defaultdict(float)
    
    print("\n🔬 EMOTION SCORING:")
    for modality, data in sample_data.items():
        if modality in adjusted_weights:
            weight = adjusted_weights[modality]
            emotion = data['primary_emotion']
            confidence = data['confidence']
            
            score = weight * confidence
            emotion_scores[emotion] += score
            
            print(f"  {modality}: {emotion} × {weight:.3f} × {confidence:.2f} = {score:.3f}")
    
    print(f"\n📈 COMBINED SCORES:")
    for emotion, score in sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {emotion}: {score:.3f}")
    
    # Step 5: Determine final result
    primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
    confidence = emotion_scores[primary_emotion]
    intensity = min(10, max(1, int(confidence * 10) + 1))
    
    print(f"\n✨ FUSION RESULT:")
    print(f"  Primary Emotion: {primary_emotion}")
    print(f"  Confidence: {confidence:.3f}")
    print(f"  Intensity: {intensity}/10")
    
    # Step 6: Risk assessment
    high_risk_emotions = ['angry', 'fear', 'disgusted', 'stressed', 'sad']
    
    if primary_emotion.lower() in high_risk_emotions:
        risk_score = 3.0
    else:
        risk_score = 1.0
    
    if intensity >= 8:
        risk_score += 1.5
    elif intensity >= 6:
        risk_score += 0.5
    
    if confidence >= 0.8:
        risk_score += 0.5
    elif confidence >= 0.6:
        risk_score += 0.25
    
    if risk_score >= 4:
        risk_level = 'high'
    elif risk_score >= 2.5:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    print(f"\n�� RISK ASSESSMENT:")
    print(f"  Risk Level: {risk_level}")
    print(f"  Risk Score: {risk_score:.1f}")
    
    # Step 7: Generate recommendations
    recommendations = generate_sample_recommendations(primary_emotion, intensity, risk_level)
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  Priority: {recommendations['priority']}")
    print(f"  Immediate actions:")
    for action in recommendations['immediate']:
        print(f"    • {action}")
    
    print(f"\n🎯 FINAL UNIFIED STATE:")
    unified_result = {
        'primary_emotion': primary_emotion,
        'confidence': round(confidence, 3),
        'intensity': intensity,
        'risk_level': risk_level,
        'fusion_weights': dict((k, round(v, 3)) for k, v in adjusted_weights.items()),
        'recommendations_priority': recommendations['priority']
    }
    
    print(json.dumps(unified_result, indent=2))

def generate_sample_recommendations(emotion, intensity, risk_level):
    """Generate sample recommendations"""
    
    recommendations = {
        'immediate': [],
        'priority': 'low'
    }
    
    if risk_level in ['high', 'critical']:
        recommendations['immediate'] = [
            "Take 5 deep, slow breaths",
            "Step away from current stressors",
            "Practice grounding techniques"
        ]
        recommendations['priority'] = 'high'
    
    emotion_strategies = {
        'sad': [
            "Listen to uplifting music",
            "Reach out to a supportive friend",
            "Practice gratitude"
        ],
        'stressed': [
            "Progressive muscle relaxation", 
            "Take a brief walk",
            "Organize priorities"
        ],
        'angry': [
            "Count to 10 slowly",
            "Clench and release fists",
            "Use assertive communication"
        ]
    }
    
    if emotion.lower() in emotion_strategies:
        recommendations['immediate'].extend(emotion_strategies[emotion.lower()][:2])
    
    if intensity >= 8:
        recommendations['priority'] = 'critical'
        recommendations['immediate'].insert(0, "URGENT: Manage intense emotions immediately")
    
    return recommendations

if __name__ == "__main__":
    demonstrate_fusion_logic()
