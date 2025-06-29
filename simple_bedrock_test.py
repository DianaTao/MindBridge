#!/usr/bin/env python3
"""
Simple test to verify Bedrock is enabled
"""

import boto3
import json

def test_bedrock_enabled():
    """Test if Bedrock is enabled in the account"""
    
    print("🔍 Testing if Bedrock is enabled...")
    
    try:
        # Try to list foundation models
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        response = bedrock.list_foundation_models()
        
        print("✅ Bedrock is enabled!")
        print(f"📊 Found {len(response.get('modelSummaries', []))} models")
        
        # Check for our specific model
        models = [m['modelId'] for m in response.get('modelSummaries', [])]
        target_model = 'anthropic.claude-3-haiku-20240307-v1:0'
        
        if target_model in models:
            print(f"✅ {target_model} is available")
            return True
        else:
            print(f"❌ {target_model} not found - request access in console")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock not enabled: {str(e)}")
        print("💡 Go to https://console.aws.amazon.com/bedrock/ and click 'Get started'")
        return False

if __name__ == "__main__":
    test_bedrock_enabled() 