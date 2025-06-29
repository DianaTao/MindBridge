#!/bin/bash

# MindBridge AWS Resources Setup Script
# This script creates all necessary AWS resources for the MindBridge application

set -e

echo "🚀 Setting up MindBridge AWS Resources..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "📋 Account ID: $ACCOUNT_ID"
echo "🌍 Region: $REGION"

# Create S3 bucket for audio chunks
echo "📦 Creating S3 bucket for audio chunks..."
aws s3 mb s3://mindbridge-audio-chunks --region $REGION || echo "Bucket already exists"

# Create DynamoDB tables
echo "🗄️ Creating DynamoDB tables..."

# Emotions table
aws dynamodb create-table \
    --table-name mindbridge-emotions \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || echo "Emotions table already exists"

# Call analysis table
aws dynamodb create-table \
    --table-name mindbridge-call-analysis \
    --attribute-definitions \
        AttributeName=call_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=call_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || echo "Call analysis table already exists"

# Mental health check-ins table
aws dynamodb create-table \
    --table-name mindbridge-checkins \
    --attribute-definitions \
        AttributeName=checkin_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=checkin_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || echo "Check-ins table already exists"

# Create comprehensive IAM policy for Lambda functions
echo "🔐 Creating comprehensive IAM policy..."

cat > mindbridge-lambda-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:HeadBucket"
            ],
            "Resource": [
                "arn:aws:s3:::mindbridge-audio-chunks",
                "arn:aws:s3:::mindbridge-audio-chunks/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/mindbridge-emotions",
                "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/mindbridge-call-analysis"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:ListTranscriptionJobs"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "comprehend:DetectSentiment",
                "comprehend:DetectKeyPhrases",
                "comprehend:DetectEntities",
                "comprehend:BatchDetectSentiment",
                "comprehend:BatchDetectKeyPhrases",
                "comprehend:BatchDetectEntities"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${REGION}:${ACCOUNT_ID}:*"
        }
    ]
}
EOF

# Create the policy
aws iam create-policy \
    --policy-name MindBridgeLambdaPermissions \
    --policy-document file://mindbridge-lambda-policy.json \
    --description "Comprehensive permissions for MindBridge Lambda functions" || echo "Policy already exists"

# Get the policy ARN
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/MindBridgeLambdaPermissions"

# Find Lambda execution role and attach policy
echo "🔗 Attaching policy to Lambda execution role..."

# Get the Lambda function's execution role
LAMBDA_ROLE=$(aws lambda get-function --function-name mindbridge-realtime-call-analysis-dev --query 'Configuration.Role' --output text)
ROLE_NAME=$(echo $LAMBDA_ROLE | cut -d'/' -f2)

echo "📋 Lambda execution role: $ROLE_NAME"

# Attach the policy to the role
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn $POLICY_ARN || echo "Policy already attached"

echo "✅ AWS resources setup completed!"
echo ""
echo "📋 Summary:"
echo "   - S3 Bucket: mindbridge-audio-chunks"
echo "   - DynamoDB Tables: mindbridge-emotions, mindbridge-call-analysis, mindbridge-checkins"
echo "   - IAM Policy: MindBridgeLambdaPermissions"
echo "   - Lambda Role: $ROLE_NAME"
echo ""
echo "🔧 Next steps:"
echo "   1. Test the real-time call analysis feature"
echo "   2. Check CloudWatch logs for any remaining issues"
echo "   3. Monitor the application performance" 