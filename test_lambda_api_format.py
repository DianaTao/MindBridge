#!/usr/bin/env python3
"""
Test script to invoke Lambda with API Gateway event format
"""

import boto3
import json

def test_lambda_api_format():
    """Test Lambda function with API Gateway event format"""
    
    print("🔍 Testing Lambda with API Gateway format...")
    
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
        
        # Create API Gateway event format
        api_event = {
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(test_data),
            "isBase64Encoded": False
        }
        
        # Invoke Lambda function with API Gateway event
        print("📤 Invoking Lambda function with API Gateway format...")
        response = lambda_client.invoke(
            FunctionName='mindbridge-checkin-processor-dev',
            InvocationType='RequestResponse',
            Payload=json.dumps(api_event)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        print(f"📥 Response Status: {response['StatusCode']}")
        
        if response['StatusCode'] == 200:
            print("✅ Lambda function executed successfully")
            
            # Parse the body from API Gateway response
            if 'body' in response_payload:
                body_data = json.loads(response_payload['body'])
                
                if 'llm_report' in body_data:
                    llm_report = body_data['llm_report']
                    print(f"🧠 LLM Report Generated: {llm_report.get('llm_generated', False)}")
                    
                    if llm_report.get('llm_generated'):
                        print("✅ Bedrock LLM integration is working!")
                        print(f"📝 Emotional Summary: {llm_report.get('emotional_summary', 'N/A')[:100]}...")
                        print(f"💡 Recommendations: {len(llm_report.get('recommendations', []))} items")
                        print(f"🎯 Mood Score: {llm_report.get('mood_score', 'N/A')}/10")
                        print(f"📊 Confidence: {llm_report.get('confidence_level', 'N/A')}")
                    else:
                        print("⚠️ Using fallback report - Bedrock may not be working")
                        print(f"📋 Fallback Report: {json.dumps(llm_report, indent=2)}")
                else:
                    print("❌ No LLM report in response")
                    print(f"📋 Response body: {json.dumps(body_data, indent=2)}")
            else:
                print("❌ No body in response")
                print(f"📋 Full response: {json.dumps(response_payload, indent=2)}")
        else:
            print(f"❌ Lambda function failed with status: {response['StatusCode']}")
            print(f"Error: {response_payload}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_lambda_api_format()
