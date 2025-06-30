#!/bin/bash

echo "🚀 Setting up AWS Resources for MindBridge Real-Time Call Analysis"
echo "================================================================"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Create S3 bucket for audio chunks
echo "📦 Creating S3 bucket for audio chunks..."
aws s3 mb s3://mindbridge-audio-chunks --region us-east-1 2>/dev/null || echo "Bucket already exists"

# Create DynamoDB tables
echo "🗄️ Creating DynamoDB tables..."

# Emotions table
aws dynamodb create-table \
    --table-name mindbridge-emotions \
    --attribute-definitions AttributeName=session_id,AttributeType=S \
    --key-schema AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1 2>/dev/null || echo "Emotions table already exists"

# Call analysis table
aws dynamodb create-table \
    --table-name mindbridge-call-analysis \
    --attribute-definitions AttributeName=chunk_id,AttributeType=S \
    --key-schema AttributeName=chunk_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1 2>/dev/null || echo "Call analysis table already exists"

echo "✅ AWS Resources created successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/"
echo "2. Find your Lambda execution role"
echo "3. Attach the MindBridgeLambdaPermissions policy (see below)"
echo ""
echo "🔐 Required IAM Policy:"
echo "Create a policy with this JSON:"
echo "=================================="
cat << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
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
                "comprehend:DetectEntities"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::mindbridge-audio-chunks/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/mindbridge-emotions",
                "arn:aws:dynamodb:*:*:table/mindbridge-call-analysis"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
EOF
echo "=================================="
echo ""
echo "🎯 After setting up permissions, your real-time call analysis will work with real AWS services!" 