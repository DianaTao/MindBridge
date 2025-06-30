#!/usr/bin/env python3
"""
Test script to invoke Lambda function and test Bedrock integration
"""

import boto3
import json

def test_lambda_bedrock():
    """Test Lambda function with Bedrock integration"""
    
    print("🧪 Testing Lambda function with Bedrock...")
    
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
        
        if response['StatusCode'] == 200:
            print("✅ Lambda function executed successfully")
            
            # Check if LLM report was generated
            if 'llm_report' in response_payload:
                llm_report = response_payload['llm_report']
                print(f"🧠 LLM Report Generated: {llm_report.get('llm_generated', False)}")
                
                if llm_report.get('llm_generated'):
                    print("✅ Bedrock LLM integration is working!")
                    print(f"📝 Emotional Summary: {llm_report.get('emotional_summary', 'N/A')[:100]}...")
                    print(f"💡 Recommendations: {len(llm_report.get('recommendations', []))} items")
                else:
                    print("⚠️ Using fallback report - Bedrock may not be working")
            else:
                print("❌ No LLM report in response")
                
        else:
            print(f"❌ Lambda function failed with status: {response['StatusCode']}")
            print(f"Error: {response_payload}")
            
    except Exception as e:
        print(f"❌ Error testing Lambda: {str(e)}")

if __name__ == "__main__":
    test_lambda_bedrock() 