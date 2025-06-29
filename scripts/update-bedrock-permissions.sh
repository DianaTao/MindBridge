#!/bin/bash

# Update Lambda execution role with Bedrock permissions
# This script adds the necessary permissions for AWS Bedrock access

set -e

REGION="us-east-1"
STAGE="dev"
ROLE_NAME="mindbridge-lambda-execution-role-${STAGE}"

echo "🔐 Updating Lambda execution role with Bedrock permissions"
echo "=========================================================="
echo "Region: ${REGION}"
echo "Stage: ${STAGE}"
echo "Role: ${ROLE_NAME}"
echo ""

# Create Bedrock policy
echo "📝 Creating Bedrock access policy..."
BEDROCK_POLICY_ARN=$(aws iam create-policy \
    --policy-name "MindBridgeBedrockAccess-${STAGE}" \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-opus-20240229-v1:0"
                ]
            }
        ]
    }' \
    --region "$REGION" \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || echo "")

if [ -z "$BEDROCK_POLICY_ARN" ]; then
    echo "📝 Getting existing Bedrock policy..."
    BEDROCK_POLICY_ARN=$(aws iam list-policies \
        --query "Policies[?PolicyName=='MindBridgeBedrockAccess-${STAGE}'].Arn" \
        --output text)
fi

if [ -z "$BEDROCK_POLICY_ARN" ]; then
    echo "❌ Failed to create or find Bedrock policy"
    exit 1
fi

echo "✅ Bedrock policy ARN: $BEDROCK_POLICY_ARN"

# Attach policy to role
echo "🔗 Attaching Bedrock policy to Lambda execution role..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$BEDROCK_POLICY_ARN" \
    --region "$REGION" 2>/dev/null || echo "⚠️  Policy already attached"

echo ""
echo "✅ Bedrock permissions updated successfully!"
echo ""
echo "📋 Updated permissions:"
echo "   - bedrock:InvokeModel"
echo "   - bedrock:InvokeModelWithResponseStream"
echo "   - Access to Claude 3 models (Haiku, Sonnet, Opus)"
echo ""
echo "🔧 Next steps:"
echo "   1. Deploy the updated Lambda function"
echo "   2. Test the LLM integration"
echo "   3. Monitor CloudWatch logs for any issues" 