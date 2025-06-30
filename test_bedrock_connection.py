#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock connection and permissions
"""

import boto3
import json
import os

def test_bedrock_connection():
    """Test Bedrock connection and model access"""
    
    print("🧪 Testing AWS Bedrock Connection...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ Bedrock client initialized successfully")
        
        # Test models
        models_to_test = [
            'anthropic.claude-3-haiku-20240307-v1:0',
            'anthropic.claude-3-sonnet-20240229-v1:0'
        ]
        
        for model_id in models_to_test:
            print(f"\n🔍 Testing model: {model_id}")
            
            try:
                # Simple test prompt
                test_prompt = "Hello! Please respond with 'Connection successful' if you can read this."
                
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        'prompt': test_prompt,
                        'max_tokens': 50,
                        'temperature': 0.1
                    })
                )
                
                response_body = json.loads(response['body'].read())
                completion = response_body['completion']
                
                print(f"✅ Model {model_id} - Response: {completion.strip()}")
                
            except Exception as e:
                print(f"❌ Model {model_id} - Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Bedrock client initialization failed: {str(e)}")
        return False
    
    return True

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing Environment Variables...")
    
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'Not set')
    print(f"BEDROCK_MODEL_ID: {model_id}")
    
    region = os.environ.get('AWS_REGION', 'Not set')
    print(f"AWS_REGION: {region}")

if __name__ == "__main__":
    test_environment_variables()
    test_bedrock_connection() 