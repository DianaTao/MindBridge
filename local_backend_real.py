#!/usr/bin/env python3
"""
MindBridge AI - Local Development Server with Real AWS Analysis
Proxies requests to real AWS Lambda functions for actual emotion analysis
"""

import json
import time
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Real AWS API Gateway URL
AWS_API_BASE = "https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - proxy to real AWS"""
    try:
        response = requests.get(f"{AWS_API_BASE}/health", timeout=10)
        aws_data = response.json()
        
        # Add local development info
        aws_data["local_proxy"] = True
        aws_data["proxy_timestamp"] = datetime.now().isoformat()
        aws_data["environment"] = "local_development_with_real_aws"
        
        print(f"✅ Health check: AWS status = {aws_data.get('status', 'unknown')}")
        return jsonify(aws_data)
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return jsonify({
            "service": "MindBridge AI - Local Dev (AWS Unavailable)",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "environment": "local_development_fallback"
        }), 500

@app.route('/video-analysis', methods=['POST', 'OPTIONS'])
def video_analysis():
    """Video emotion analysis endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        print(f"🎥 Proxying video analysis request to AWS: {user_id}")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/video-analysis",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
            
            # Add local proxy info
            if 'debug_info' not in result:
                result['debug_info'] = {}
            result['debug_info']['local_proxy'] = True
            result['debug_info']['proxy_timestamp'] = datetime.now().isoformat()
            
            primary_emotion = result.get('primary_emotion', 'unknown')
            confidence = result.get('confidence', 0)
            print(f"✅ AWS video analysis response: {primary_emotion} ({confidence:.1f}%)")
            
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except requests.exceptions.Timeout:
        print("❌ AWS API timeout")
        return jsonify({"error": "AWS API timeout"}), 504
    except requests.exceptions.ConnectionError:
        print("❌ AWS API connection error")
        return jsonify({"error": "AWS API connection error"}), 503
    except Exception as e:
        print(f"❌ Video analysis proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/video-analysis/stop', methods=['POST', 'OPTIONS'])
def stop_video_analysis():
    """Stop video analysis endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        print(f"⏹️ Proxying video analysis stop to AWS: {user_id}")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/video-analysis/stop",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Stop video analysis proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/text-analysis', methods=['POST', 'OPTIONS'])
def text_analysis():
    """Text sentiment analysis endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        text = data.get('text', data.get('text_data', ''))
        print(f"📝 Proxying text analysis to AWS: '{text[:50]}...'")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/text-analysis",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
            
            # Add local proxy info
            if 'debug_info' not in result:
                result['debug_info'] = {}
            result['debug_info']['local_proxy'] = True
            
            primary_emotion = result.get('primary_emotion', 'unknown')
            sentiment = result.get('sentiment', 'unknown')
            print(f"✅ AWS text analysis response: {primary_emotion} ({sentiment})")
            
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Text analysis proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/emotion-fusion', methods=['POST', 'OPTIONS'])
def emotion_fusion():
    """Emotion fusion endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🔗 Proxying emotion fusion to AWS")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/emotion-fusion",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Emotion fusion proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard', methods=['GET', 'OPTIONS'])
def dashboard():
    """Dashboard data endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Forward request to real AWS API
        response = requests.get(
            f"{AWS_API_BASE}/dashboard",
            timeout=10
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Dashboard proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/realtime-call-analysis', methods=['POST', 'OPTIONS'])
def realtime_call_analysis():
    """Real-time call analysis endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"📞 Proxying real-time call analysis to AWS")
        
        # Handle both JSON and FormData
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Forward FormData as-is
            files = {}
            data = {}
            for key, value in request.form.items():
                data[key] = value
            for key, file in request.files.items():
                files[key] = file
                
            response = requests.post(
                f"{AWS_API_BASE}/realtime-call-analysis",
                data=data,
                files=files,
                timeout=20
            )
        else:
            # Forward JSON data
            data = request.get_json()
            response = requests.post(
                f"{AWS_API_BASE}/realtime-call-analysis",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Real-time call analysis proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/call-review', methods=['POST', 'OPTIONS'])
def call_review():
    """Call review analysis endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🎧 Proxying call review to AWS")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/call-review",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Call review proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/checkin-processor', methods=['POST', 'OPTIONS'])
def checkin_processor():
    """Mental health check-in processor endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"🧠 Proxying check-in processor to AWS")
        
        # Forward request to real AWS API
        response = requests.post(
            f"{AWS_API_BASE}/checkin-processor",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Check-in processor proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/checkin-retriever', methods=['GET', 'OPTIONS'])
def checkin_retriever():
    """Mental health check-in retriever endpoint - proxy to real AWS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get query parameters
        params = request.args.to_dict()
        print(f"📊 Proxying check-in retriever to AWS with params: {params}")
        
        # Forward request to real AWS API
        response = requests.get(
            f"{AWS_API_BASE}/checkin-retriever",
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            aws_data = response.json()
            
            # Handle Lambda response format
            if 'body' in aws_data:
                result = json.loads(aws_data['body'])
            else:
                result = aws_data
                
            return jsonify(result)
        else:
            print(f"❌ AWS API error: {response.status_code}")
            return jsonify({"error": f"AWS API error: {response.status_code}"}), response.status_code
            
    except Exception as e:
        print(f"❌ Check-in retriever proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting MindBridge AI Local Proxy Server...")
    print("🌐 Local Server: http://localhost:8000")
    print("☁️  AWS Backend: https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod")
    print("📡 Proxy Endpoints:")
    print("   - GET  /health                    → AWS /health")
    print("   - POST /video-analysis            → AWS /video-analysis") 
    print("   - POST /text-analysis             → AWS /text-analysis")
    print("   - POST /emotion-fusion            → AWS /emotion-fusion")
    print("   - GET  /dashboard                 → AWS /dashboard")
    print("   - POST /realtime-call-analysis    → AWS /realtime-call-analysis")
    print("   - POST /call-review               → AWS /call-review")
    print("   - POST /checkin-processor         → AWS /checkin-processor")
    print("   - GET  /checkin-retriever         → AWS /checkin-retriever")
    print("💡 Frontend connects to localhost:8000, gets REAL AWS analysis!")
    print("🔄 Ready for requests...")
    
    app.run(host='0.0.0.0', port=8000, debug=True) 