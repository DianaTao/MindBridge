#!/usr/bin/env python3
"""
Script to update Bedrock permissions for Lambda functions
"""

import boto3
import json

def update_bedrock_permissions():
    """Update Bedrock permissions for Lambda functions"""
    
    print("🔧 Updating Bedrock permissions...")
    
    try:
        # Get Lambda function details
        lambda_client = boto3.client('lambda')
        iam_client = boto3.client('iam')
        
        # Function names to update
        function_names = [
            'mindbridge-checkin-processor-dev',
            'mindbridge-checkin-retriever-dev'
        ]
        
        for function_name in function_names:
            print(f"\n🔍 Processing function: {function_name}")
            
            try:
                # Get function configuration
                response = lambda_client.get_function(FunctionName=function_name)
                role_arn = response['Configuration']['Role']
                role_name = role_arn.split('/')[-1]
                
                print(f"✅ Found role: {role_name}")
                
                # Create Bedrock policy
                bedrock_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream"
                            ],
                            "Resource": [
                                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
                            ]
                        }
                    ]
                }
                
                # Attach policy to role
                policy_name = f"BedrockPermissions-{function_name}"
                
                try:
                    # Create policy
                    iam_client.create_policy(
                        PolicyName=policy_name,
                        PolicyDocument=json.dumps(bedrock_policy),
                        Description=f"Bedrock permissions for {function_name}"
                    )
                    print(f"✅ Created policy: {policy_name}")
                except iam_client.exceptions.EntityAlreadyExistsException:
                    print(f"ℹ️ Policy {policy_name} already exists")
                
                # Attach policy to role
                try:
                    iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
                    )
                    print(f"✅ Attached policy to role: {role_name}")
                except Exception as e:
                    print(f"ℹ️ Policy may already be attached: {str(e)}")
                
            except Exception as e:
                print(f"❌ Error processing {function_name}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_bedrock_permissions()
