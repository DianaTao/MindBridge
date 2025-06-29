#!/usr/bin/env python3
"""
Test script to invoke Lambda through API Gateway
"""

import requests
import json

def test_api_gateway():
    """Test Lambda function through API Gateway"""
    
    print("🔍 Testing through API Gateway...")
    
    try:
        # Get API Gateway URL from CDK outputs or construct it
        # You can find this in the AWS Console or CDK outputs
        api_url = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod/checkin-processor"
        
        # Test data
        test_data = {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "duration": 30,
            "checkin_id": "test-checkin-789",
            "emotion_analysis": {
                "dominant_emotion": "happy",
                "emotion_scores": {
                    "happy": 0.8,
                    "sad": 0.1,
                    "angry": 0.05,
                    "surprised": 0.05
                },
                "average_wellbeing": 75,
                "stress_level": "low"
            },
            "self_assessment": {
                "overall_mood": 8,
                "energy_level": 7,
                "stress_level": 3,
                "sleep_quality": 6,
                "social_connection": 8,
                "motivation": 7,
                "notes": "Feeling good today!"
            }
        }
        
        # Make HTTP request
        print("📤 Making API Gateway request...")
        response = requests.post(
            api_url,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ API Gateway request successful")
            
            if 'llm_report' in response_data:
                llm_report = response_data['llm_report']
                print(f"🧠 LLM Report Generated: {llm_report.get('llm_generated', False)}")
                
                if llm_report.get('llm_generated'):
                    print("✅ Bedrock LLM integration is working!")
                    print(f"📝 Emotional Summary: {llm_report.get('emotional_summary', 'N/A')[:100]}...")
                    print(f"💡 Recommendations: {len(llm_report.get('recommendations', []))} items")
                else:
                    print("⚠️ Using fallback report - Bedrock may not be working")
            else:
                print("❌ No LLM report in response")
                print(f"📋 Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ API Gateway request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Make sure to update the API Gateway URL in the script")

if __name__ == "__main__":
    test_api_gateway() 