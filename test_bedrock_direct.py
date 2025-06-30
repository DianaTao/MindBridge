#!/usr/bin/env python3
"""
Direct test of Bedrock from Lambda environment
"""

import boto3
import json
import os

def test_bedrock_direct():
    """Test Bedrock directly with the same setup as Lambda"""
    
    print("🔍 Testing Bedrock directly...")
    
    try:
        # Initialize Bedrock client (same as Lambda)
        bedrock = boto3.client('bedrock-runtime')
        print("✅ Bedrock client initialized")
        
        # Get model ID from environment (same as Lambda)
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        print(f"📋 Using model: {model_id}")
        
        # Simple test prompt
        test_prompt = "Hello! Please respond with 'Connection successful' if you can read this."
        
        print("📤 Invoking Bedrock model...")
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'prompt': test_prompt,
                'max_tokens_to_sample': 50,
                'temperature': 0.1
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        completion = response_body['completion']
        
        print(f"✅ Bedrock response: {completion.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_bedrock_direct()
