#!/usr/bin/env python3
"""
Debug script to see full Lambda response
"""

import boto3
import json

def debug_lambda_response():
    """Debug Lambda function response"""
    
    print("🔍 Debugging Lambda function response...")
    
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda')
        
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
        
        # Invoke Lambda function
        print("📤 Invoking Lambda function...")
        response = lambda_client.invoke(
            FunctionName='mindbridge-checkin-processor-dev',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_data)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        print(f"📥 Response Status: {response['StatusCode']}")
        
        print("\n📋 Full Response:")
        print(json.dumps(response_payload, indent=2))
        
        # Check specific fields
        if 'llm_report' in response_payload:
            llm_report = response_payload['llm_report']
            print(f"\n🧠 LLM Report Found:")
            print(f"   - llm_generated: {llm_report.get('llm_generated', 'Not set')}")
            print(f"   - emotional_summary: {llm_report.get('emotional_summary', 'Not set')[:100]}...")
            print(f"   - recommendations: {len(llm_report.get('recommendations', []))} items")
        else:
            print("\n❌ No 'llm_report' field in response")
            
        # Check for error fields
        if 'errorMessage' in response_payload:
            print(f"\n❌ Error: {response_payload['errorMessage']}")
            
        if 'errorType' in response_payload:
            print(f"❌ Error Type: {response_payload['errorType']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_lambda_response() 