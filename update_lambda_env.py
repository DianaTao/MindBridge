#!/usr/bin/env python3
"""
Script to update Lambda environment variables for Bedrock configuration
"""

import boto3
import json

def update_lambda_environment():
    """Update Lambda function environment variables"""
    
    print("🔧 Updating Lambda environment variables...")
    
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda')
        
        # Function names to update
        function_configs = [
            {
                'name': 'mindbridge-checkin-processor-dev',
                'env_vars': {
                    'CHECKINS_TABLE': 'mindbridge-checkins-dev',
                    'BEDROCK_MODEL_ID': 'anthropic.claude-3-haiku-20240307-v1:0',
                    'STAGE': 'dev'
                }
            },
            {
                'name': 'mindbridge-checkin-retriever-dev',
                'env_vars': {
                    'CHECKINS_TABLE': 'mindbridge-checkins-dev',
                    'BEDROCK_MODEL_ID': 'anthropic.claude-3-haiku-20240307-v1:0',
                    'STAGE': 'dev'
                }
            }
        ]
        
        for config in function_configs:
            function_name = config['name']
            env_vars = config['env_vars']
            
            print(f"\n🔍 Updating function: {function_name}")
            
            try:
                # Update function configuration
                response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Environment={
                        'Variables': env_vars
                    }
                )
                
                print(f"✅ Updated environment variables for {function_name}")
                print(f"📋 Environment variables: {json.dumps(env_vars, indent=2)}")
                
            except Exception as e:
                print(f"❌ Error updating {function_name}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def verify_lambda_environment():
    """Verify Lambda function environment variables"""
    
    print("\n🔍 Verifying Lambda environment variables...")
    
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda')
        
        function_names = [
            'mindbridge-checkin-processor-dev',
            'mindbridge-checkin-retriever-dev'
        ]
        
        for function_name in function_names:
            print(f"\n📋 Function: {function_name}")
            
            try:
                # Get function configuration
                response = lambda_client.get_function_configuration(
                    FunctionName=function_name
                )
                
                env_vars = response.get('Environment', {}).get('Variables', {})
                
                print(f"✅ Environment variables:")
                for key, value in env_vars.items():
                    print(f"   {key}: {value}")
                    
            except Exception as e:
                print(f"❌ Error getting config for {function_name}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_lambda_environment()
    verify_lambda_environment()
