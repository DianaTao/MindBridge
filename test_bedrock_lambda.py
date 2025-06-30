#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock access from Lambda functions
"""

import json
import boto3
import os

def test_bedrock_access():
    """Test if we can access AWS Bedrock"""
    try:
        print("🧪 Testing AWS Bedrock Access...")
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime')
        
        # Get model ID from environment or use default
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        print(f"📋 Using model: {model_id}")
        
        # Test prompt with correct Claude format
        test_text = "I'm feeling really stressed about work lately"
        prompt = f"""You are an expert in emotion analysis and sentiment detection. Analyze the following text and provide a detailed emotional analysis.

Text to analyze: "{test_text}"

Please provide your analysis in the following JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "sentiment_score": 0.0-1.0,
    "emotions": [
        {{
            "Type": "emotion_name",
            "Confidence": 0.0-1.0,
            "Intensity": "low|medium|high"
        }}
    ],
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "emotional_context": "brief description of the emotional context",
    "recommendations": "brief personalized recommendations based on the emotional state"
}}

Focus on detecting emotions like: joy, sadness, anger, fear, surprise, disgust, love, anxiety, excitement, frustration, contentment, confusion, etc.

Be empathetic and provide helpful insights. If the text is very short or unclear, make reasonable inferences based on context."""
        
        print("🤖 Calling AWS Bedrock...")
        
        # Call AWS Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 800,
                'temperature': 0.3,
                'top_p': 0.9
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        llm_output = response_body['content'][0]['text']
        
        print("✅ AWS Bedrock call successful!")
        print(f"📝 LLM Response: {llm_output[:200]}...")
        
        # Try to parse JSON from response
        try:
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_output[json_start:json_end]
                parsed_data = json.loads(json_str)
                print("✅ JSON parsing successful!")
                print(f"📊 Sentiment: {parsed_data.get('sentiment', 'N/A')}")
                print(f"😊 Emotions: {[e.get('Type', 'N/A') for e in parsed_data.get('emotions', [])]}")
                print(f"💡 Recommendations: {parsed_data.get('recommendations', 'N/A')}")
            else:
                print("⚠️ No JSON found in response")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📝 Raw response: {llm_output}")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS Bedrock test failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def test_lambda_environment():
    """Test Lambda environment variables"""
    print("\n🔧 Testing Lambda Environment...")
    
    # Check environment variables
    env_vars = [
        'BEDROCK_MODEL_ID',
        'AWS_REGION',
        'STAGE'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NOT_SET')
        print(f"📋 {var}: {value}")
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"👤 AWS Identity: {identity.get('Arn', 'Unknown')}")
        print(f"🏢 Account: {identity.get('Account', 'Unknown')}")
    except Exception as e:
        print(f"❌ AWS Identity check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting AWS Bedrock Lambda Test")
    print("=" * 50)
    
    # Test environment
    test_lambda_environment()
    
    print("\n" + "=" * 50)
    
    # Test Bedrock access
    success = test_bedrock_access()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! AWS Bedrock is accessible.")
    else:
        print("❌ Tests failed. Check AWS permissions and configuration.") 