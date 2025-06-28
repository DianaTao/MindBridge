#!/usr/bin/env python3
"""
Test script to simulate frontend camera capture and API calls
"""

import requests
import base64
import json
import time

def create_test_image():
    """Create a simple test image (1x1 pixel)"""
    # This is a 1x1 pixel PNG image
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_video_analysis():
    """Test the video analysis endpoint"""
    print("🧪 TESTING VIDEO ANALYSIS")
    print("=" * 50)
    
    # Create test data
    frame_data = create_test_image()
    user_id = "test-user-123"
    session_id = f"session-{int(time.time())}"
    
    print(f"📤 Sending request to: http://localhost:3000/video-analysis")
    print(f"👤 User ID: {user_id}")
    print(f"🆔 Session ID: {session_id}")
    print(f"📸 Frame data length: {len(frame_data)} characters")
    print(f"📸 Frame data preview: {frame_data[:50]}...")
    
    # Prepare request
    payload = {
        "frame_data": frame_data,
        "user_id": user_id,
        "session_id": session_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make request
        print("\n🔄 Making API request...")
        response = requests.post(
            "http://localhost:3000/video-analysis",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"✅ Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response data: {json.dumps(data, indent=2)}")
            
            # Check if it's a Lambda response format
            if 'body' in data:
                print("\n🔄 Parsing Lambda response body...")
                body_data = json.loads(data['body'])
                print(f"📊 Parsed body: {json.dumps(body_data, indent=2)}")
                
                # Extract key information
                faces_detected = body_data.get('faces_detected', 0)
                primary_emotion = body_data.get('primary_emotion', 'unknown')
                confidence = body_data.get('confidence', 0)
                
                print(f"\n🎯 RESULTS:")
                print(f"   👥 Faces detected: {faces_detected}")
                print(f"   😊 Primary emotion: {primary_emotion}")
                print(f"   📊 Confidence: {confidence:.2f}%")
                
                if 'debug_info' in body_data:
                    debug = body_data['debug_info']
                    print(f"   🔍 Debug info:")
                    print(f"      - Analysis method: {debug.get('analysis_method', 'unknown')}")
                    print(f"      - Environment: {debug.get('environment', 'unknown')}")
                    print(f"      - Image size: {debug.get('image_size_bytes', 0)} bytes")
                
                return faces_detected > 0
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_frontend_proxy():
    """Test if the frontend proxy is working"""
    print("\n🧪 TESTING FRONTEND PROXY")
    print("=" * 50)
    
    try:
        # Test the proxy endpoint
        response = requests.get("http://localhost:3001/health", timeout=5)
        print(f"✅ Frontend proxy health check: {response.status_code}")
        
        # Test video analysis through proxy
        frame_data = create_test_image()
        payload = {
            "frame_data": frame_data,
            "user_id": "proxy-test",
            "session_id": "proxy-session"
        }
        
        response = requests.post(
            "http://localhost:3001/video-analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"✅ Frontend proxy video analysis: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Proxy response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Proxy request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MIND BRIDGE FACE RECOGNITION DEBUG TEST")
    print("=" * 60)
    
    # Test direct backend
    success1 = test_video_analysis()
    
    # Test frontend proxy
    success2 = test_frontend_proxy()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Direct backend test: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Frontend proxy test: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Face recognition should be working.")
        print("💡 If you're still seeing '0 faces' in the frontend, check the browser console for errors.")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.") 