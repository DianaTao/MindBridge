#!/usr/bin/env python3
"""
Script to check Bedrock service status and model access
"""

import boto3
import json

def check_bedrock_status():
    """Check Bedrock service status"""
    
    print("🔍 Checking AWS Bedrock Status...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # Check if Bedrock is enabled
        try:
            response = bedrock.list_foundation_models()
            print("✅ Bedrock service is enabled")
            print(f"📊 Found {len(response.get('modelSummaries', []))} foundation models")
            
            # Check for specific models
            models_to_check = [
                'anthropic.claude-3-sonnet-20240229-v1:0',
                'anthropic.claude-3-haiku-20240307-v1:0'
            ]
            
            available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
            
            print("\n🔍 Checking model availability:")
            for model_id in models_to_check:
                if model_id in available_models:
                    print(f"✅ {model_id} - Available")
                else:
                    print(f"❌ {model_id} - Not available")
                    
        except Exception as e:
            print(f"❌ Bedrock service error: {str(e)}")
            print("💡 You may need to enable Bedrock in the AWS Console")
            
    except Exception as e:
        print(f"❌ Error checking Bedrock status: {str(e)}")

def check_bedrock_runtime():
    """Check Bedrock runtime access"""
    
    print("\n🔍 Checking Bedrock Runtime Access...")
    
    try:
        # Initialize Bedrock runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with a simple model list (this should work if runtime is accessible)
        print("✅ Bedrock runtime client initialized successfully")
        
        # Try to invoke a model (this will fail if no access, but we can catch the error)
        try:
            response = bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    'prompt': 'Hello',
                    'max_tokens': 10
                })
            )
            print("✅ Bedrock runtime access confirmed")
            
        except Exception as e:
            error_msg = str(e)
            if 'AccessDeniedException' in error_msg:
                print("❌ Access denied - Check IAM permissions")
            elif 'Model not found' in error_msg:
                print("❌ Model not found - Check model access")
            else:
                print(f"❌ Runtime error: {error_msg}")
                
    except Exception as e:
        print(f"❌ Error checking Bedrock runtime: {str(e)}")

def check_iam_permissions():
    """Check IAM permissions for Bedrock"""
    
    print("\n🔍 Checking IAM Permissions...")
    
    try:
        # Get current user/role
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"👤 Current identity: {identity['Arn']}")
        
        # Check if we can list policies
        iam = boto3.client('iam')
        
        try:
            # Try to list policies (this will fail if no IAM permissions)
            response = iam.list_policies(Scope='Local', MaxItems=5)
            print("✅ IAM access confirmed")
            
            # Check for Bedrock policies
            bedrock_policies = [p for p in response['Policies'] if 'bedrock' in p['PolicyName'].lower()]
            
            if bedrock_policies:
                print(f"✅ Found {len(bedrock_policies)} Bedrock-related policies")
                for policy in bedrock_policies:
                    print(f"   📋 {policy['PolicyName']}")
            else:
                print("⚠️ No Bedrock policies found")
                
        except Exception as e:
            print(f"❌ IAM access error: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error checking IAM: {str(e)}")

if __name__ == "__main__":
    check_bedrock_status()
    check_bedrock_runtime()
    check_iam_permissions() 