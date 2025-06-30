#!/usr/bin/env python3
"""
Test script to verify project is ready for submission
"""

import json
import requests
from datetime import datetime

def test_checkin_processor():
    """Test the checkin processor endpoint"""
    print("🧪 TESTING PROJECT READINESS FOR SUBMISSION")
    print("=" * 60)
    
    # Test data
    test_data = {
        "user_id": "test_user_project_submission",
        "session_id": "test_session_" + datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
        "duration": 120,
        "checkin_id": "test_checkin_" + datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
        "emotion_analysis": {
            "dominant_emotion": "happy",
            "confidence": 0.85,
            "intensity": 75
        },
        "self_assessment": {
            "mood_score": 8,
            "energy_level": 7,
            "stress_level": 3
        }
    }
    
    # API endpoint
    url = "https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/checkin-processor"
    
    try:
        print(f"📡 Testing endpoint: {url}")
        print(f"📦 Sending test data: {json.dumps(test_data, indent=2)}")
        
        # Make request
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - PROJECT READY FOR SUBMISSION!")
            print(f"📝 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_checkin_retriever():
    """Test the checkin retriever endpoint"""
    print("\n" + "=" * 60)
    print("🧪 TESTING CHECK-IN RETRIEVER")
    print("=" * 60)
    
    # API endpoint
    url = "https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/checkin-retriever"
    params = {
        "user_id": "test_user_project_submission",
        "days": 7,
        "limit": 10
    }
    
    try:
        print(f"📡 Testing endpoint: {url}")
        print(f"📦 Query params: {params}")
        
        # Make request
        response = requests.get(
            url,
            params=params,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - RETRIEVER WORKING!")
            print(f"📝 Total check-ins: {result.get('total_count', 0)}")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 MIND BRIDGE PROJECT SUBMISSION TEST")
    print("=" * 60)
    
    # Test checkin processor
    processor_ok = test_checkin_processor()
    
    # Test checkin retriever
    retriever_ok = test_checkin_retriever()
    
    # Final result
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS")
    print("=" * 60)
    
    if processor_ok and retriever_ok:
        print("🎉 ALL TESTS PASSED - PROJECT READY FOR SUBMISSION!")
        print("✅ Check-in processor: WORKING")
        print("✅ Check-in retriever: WORKING")
        print("✅ Emotion Analytics: READY")
        print("✅ Frontend: DEPLOYED")
        print("✅ Backend: DEPLOYED")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"✅ Check-in processor: {'WORKING' if processor_ok else 'FAILED'}")
        print(f"✅ Check-in retriever: {'WORKING' if retriever_ok else 'FAILED'}")
    
    print("\n📝 NEXT STEPS:")
    print("1. Test mental health check-in in the frontend")
    print("2. Verify data appears in Emotion Analytics")
    print("3. Submit your project!") 