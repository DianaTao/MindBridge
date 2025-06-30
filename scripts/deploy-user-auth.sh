#!/bin/bash

# MindBridge User Authentication Lambda Deployment Script
# This script deploys the user authentication Lambda function

set -e

# Configuration
REGION="us-east-1"
STAGE="dev"
FUNCTION_NAME="mindbridge-user-auth-${STAGE}"
LAMBDA_DIR="lambda_functions/user_auth"
ZIP_FILE="${LAMBDA_DIR}/user_auth.zip"

echo "🔐 MindBridge User Authentication Lambda Deployment"
echo "=================================================="
echo "Region: ${REGION}"
echo "Stage: ${STAGE}"
echo "Function: ${FUNCTION_NAME}"
echo ""

# Check if Lambda directory exists
if [ ! -d "$LAMBDA_DIR" ]; then
    echo "❌ Lambda directory not found: $LAMBDA_DIR"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
cd "$LAMBDA_DIR"

# Remove existing zip file
if [ -f "user_auth.zip" ]; then
    rm user_auth.zip
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -t . --quiet

# Create zip file
echo "🗜️  Creating zip file..."
zip -r user_auth.zip . -x "*.pyc" "__pycache__/*" "*.git*" "*.DS_Store" > /dev/null

echo "✅ Deployment package created: $ZIP_FILE"

# Check if function exists
echo "🔍 Checking if Lambda function exists..."
if aws lambda get-function --function-name "$FUNCTION_NAME" --region "$REGION" > /dev/null 2>&1; then
    echo "📤 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --zip-file "fileb://user_auth.zip" \
        --region "$REGION"
    
    echo "⚙️  Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --environment "Variables={USERS_TABLE_NAME=mindbridge-users-${STAGE}}" \
        --region "$REGION"
else
    echo "📤 Creating new Lambda function..."
    
    # Get execution role ARN
    ROLE_ARN=$(aws iam get-role --role-name "mindbridge-lambda-execution-role-${STAGE}" --query 'Role.Arn' --output text 2>/dev/null || echo "")
    
    if [ -z "$ROLE_ARN" ]; then
        echo "❌ Lambda execution role not found. Please create the role first."
        exit 1
    fi
    
    aws lambda create-function \
        --function-name "$FUNCTION_NAME" \
        --runtime python3.9 \
        --role "$ROLE_ARN" \
        --handler handler.lambda_handler \
        --zip-file "fileb://user_auth.zip" \
        --timeout 30 \
        --memory-size 256 \
        --environment "Variables={USERS_TABLE_NAME=mindbridge-users-${STAGE}}" \
        --region "$REGION"
fi

# Add API Gateway permissions if needed
echo "🔗 Setting up API Gateway permissions..."
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "api-gateway-invoke" \
    --action "lambda:InvokeFunction" \
    --principal "apigateway.amazonaws.com" \
    --region "$REGION" 2>/dev/null || echo "⚠️  Permission already exists"

echo ""
echo "✅ User Authentication Lambda deployed successfully!"
echo ""
echo "📋 Function Details:"
echo "   Function Name: $FUNCTION_NAME"
echo "   Runtime: Python 3.9"
echo "   Timeout: 30 seconds"
echo "   Memory: 256 MB"
echo "   Environment: USERS_TABLE_NAME=mindbridge-users-${STAGE}"
echo ""
echo "🔧 Next steps:"
echo "   1. Create the users DynamoDB table if it doesn't exist"
echo "   2. Add the Lambda function to your API Gateway"
echo "   3. Test the authentication endpoint"
echo ""
echo "💡 To create the users table, run:"
echo "   aws dynamodb create-table \\"
echo "     --table-name mindbridge-users-${STAGE} \\"
echo "     --attribute-definitions AttributeName=email,AttributeType=S \\"
echo "     --key-schema AttributeName=email,KeyType=HASH \\"
echo "     --billing-mode PAY_PER_REQUEST \\"
echo "     --region $REGION" 