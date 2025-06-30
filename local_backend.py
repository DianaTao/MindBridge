#!/usr/bin/env python3
"""
MindBridge AI - Local Development Server
Simulates AWS Lambda backend for local frontend development
"""

import json
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "MindBridge AI - Local Dev",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "handlers": {
            "video": True,
            "audio": True,
            "text": True,
            "fusion": True,
            "dashboard": True
        },
        "version": "1.0.0-local",
        "environment": "local_development"
    })

@app.route('/video-analysis', methods=['POST', 'OPTIONS'])
def video_analysis():
    """Video emotion analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🎥 Video analysis request received: {data.get('user_id', 'unknown')}")
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Mock emotion analysis
        emotions = [
            {"Type": "HAPPY", "Confidence": 85.5},
            {"Type": "CALM", "Confidence": 72.3},
            {"Type": "NEUTRAL", "Confidence": 60.1},
            {"Type": "SURPRISED", "Confidence": 25.4}
        ]
        
        primary_emotion = emotions[0]["Type"].lower()
        
        response = {
            "faces_detected": 1,
            "emotions": [{
                "face_id": "face_0",
                "emotions": emotions,
                "primary_emotion": primary_emotion,
                "confidence": emotions[0]["Confidence"],
                "face_confidence": 95.2,
                "bounding_box": {
                    "Width": 0.45,
                    "Height": 0.52,
                    "Left": 0.28,
                    "Top": 0.24
                },
                "age_range": {"Low": 25, "High": 35},
                "gender": {"Value": "Unknown", "Confidence": 50},
                "timestamp": datetime.now().isoformat(),
                "user_id": data.get("user_id", "local-user"),
                "session_id": data.get("session_id", "local-session"),
                "modality": "video"
            }],
            "primary_emotion": primary_emotion,
            "confidence": emotions[0]["Confidence"],
            "timestamp": datetime.now().isoformat(),
            "debug_info": {
                "analysis_method": "local_backend",
                "processing_time_ms": 500,
                "environment": "local_development"
            }
        }
        
        print(f"✅ Video analysis response: {primary_emotion} ({emotions[0]['Confidence']:.1f}%)")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Video analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/video-analysis/stop', methods=['POST', 'OPTIONS'])
def stop_video_analysis():
    """Stop video analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"⏹️ Video analysis stop request: {data.get('user_id', 'unknown')}")
        
        response = {
            "status": "stopped",
            "session_id": data.get("session_id", "local-session"),
            "timestamp": datetime.now().isoformat(),
            "message": "Video analysis session stopped successfully"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Stop video analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/text-analysis', methods=['POST', 'OPTIONS'])
def text_analysis():
    """Text sentiment analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        text = data.get('text', data.get('text_data', ''))
        print(f"📝 Text analysis request: '{text[:50]}...'")
        
        # Simulate processing time
        time.sleep(0.3)
        
        # Simple keyword-based emotion detection
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'joy', 'great', 'awesome', 'love']):
            emotions = [{"Type": "happy", "Confidence": 0.85}]
            sentiment = "positive"
        elif any(word in text_lower for word in ['sad', 'unhappy', 'terrible', 'awful', 'hate']):
            emotions = [{"Type": "sad", "Confidence": 0.78}]
            sentiment = "negative"
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed']):
            emotions = [{"Type": "angry", "Confidence": 0.82}]
            sentiment = "negative"
        else:
            emotions = [{"Type": "neutral", "Confidence": 0.75}]
            sentiment = "neutral"
        
        response = {
            "emotions": emotions,
            "primary_emotion": emotions[0]["Type"],
            "confidence": emotions[0]["Confidence"],
            "sentiment": sentiment,
            "keywords": text.split()[:5],  # First 5 words
            "timestamp": datetime.now().isoformat(),
            "debug_info": {
                "analysis_method": "local_backend",
                "text_length": len(text),
                "environment": "local_development"
            }
        }
        
        print(f"✅ Text analysis response: {emotions[0]['Type']} ({sentiment})")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Text analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/emotion-fusion', methods=['POST', 'OPTIONS'])
def emotion_fusion():
    """Emotion fusion endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🔗 Emotion fusion request received")
        
        # Mock fusion response
        response = {
            "fused_emotion": "happy",
            "confidence": 0.82,
            "modalities": ["video", "text"],
            "timestamp": datetime.now().isoformat(),
            "debug_info": {
                "fusion_method": "local_backend",
                "environment": "local_development"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Emotion fusion error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard', methods=['GET', 'OPTIONS'])
def dashboard():
    """Dashboard data endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Mock dashboard data
        response = {
            "total_sessions": 42,
            "total_emotions_detected": 156,
            "top_emotions": [
                {"emotion": "happy", "count": 45},
                {"emotion": "neutral", "count": 38},
                {"emotion": "calm", "count": 32},
                {"emotion": "surprised", "count": 24},
                {"emotion": "sad", "count": 17}
            ],
            "last_updated": datetime.now().isoformat(),
            "environment": "local_development"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/realtime-call-analysis', methods=['POST', 'OPTIONS'])
def realtime_call_analysis():
    """Real-time call analysis endpoint - forwards to AWS Lambda"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"📞 Real-time call analysis request received")
        
        # Get the request data
        data = request.get_json()
        print(f"📤 Forwarding request to AWS Lambda...")
        
        # Forward to AWS Lambda function
        lambda_url = "https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/realtime-call-analysis"
        
        # Forward the request
        response = requests.post(
            lambda_url,
            json=data,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AWS Lambda response received: {result.get('emotion', 'unknown')}")
            return jsonify(result)
        else:
            print(f"❌ AWS Lambda returned status {response.status_code}: {response.text}")
            # Return fallback response
            fallback_response = {
                "emotion": "neutral",
                "emotion_confidence": 0.5,
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "sentiment_trend": "stable",
                "call_type": "general",
                "call_intensity": 50.0,
                "speaking_rate": 120.0,
                "key_phrases": [],
                "processing_time_ms": 1000,
                "timestamp": datetime.now().isoformat(),
                "debug_info": {
                    "analysis_method": "fallback_local_backend",
                    "aws_error": f"Status {response.status_code}",
                    "environment": "local_development"
                }
            }
            return jsonify(fallback_response)
        
    except Exception as e:
        print(f"❌ Real-time call analysis error: {str(e)}")
        # Return fallback response on error
        fallback_response = {
            "emotion": "neutral",
            "emotion_confidence": 0.5,
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "sentiment_trend": "stable",
            "call_type": "general",
            "call_intensity": 50.0,
            "speaking_rate": 120.0,
            "key_phrases": [],
            "processing_time_ms": 1000,
            "timestamp": datetime.now().isoformat(),
            "debug_info": {
                "analysis_method": "fallback_local_backend",
                "error": str(e),
                "environment": "local_development"
            }
        }
        return jsonify(fallback_response)

@app.route('/call-review', methods=['POST', 'OPTIONS'])
def call_review():
    """Call review analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"🎧 Call review analysis request received")
        
        # Mock review response
        response = {
            "call_id": f"call_{int(time.time())}",
            "analysis_summary": {
                "overall_sentiment": "positive",
                "key_emotions": ["happy", "calm", "professional"],
                "quality_score": 8.5,
                "recommendations": [
                    "Great job maintaining positive tone",
                    "Consider speaking slightly slower for clarity"
                ]
            },
            "processing_time_ms": 1200,
            "timestamp": datetime.now().isoformat(),
            "debug_info": {
                "analysis_method": "local_backend",
                "environment": "local_development"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Call review error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting MindBridge AI Local Backend Server...")
    print("🌐 Server will run on: http://localhost:8000")
    print("📡 API Endpoints:")
    print("   - GET  /health")
    print("   - POST /video-analysis") 
    print("   - POST /text-analysis")
    print("   - POST /emotion-fusion")
    print("   - GET  /dashboard")
    print("   - POST /realtime-call-analysis")
    print("   - POST /call-review")
    print("💡 Frontend should connect to: http://localhost:8000")
    print("🔄 Ready for requests...")
    
    app.run(host='0.0.0.0', port=8000, debug=True) 