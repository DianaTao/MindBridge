#!/bin/bash

# MindBridge Check-in Lambda Functions Deployment Script
# Deploys check-in processor and retriever Lambda functions

set -e

# Configuration
REGION="us-east-1"
ROLE_NAME="MindBridgeStack-LambdaExecutionRoleD5C26073-u6AqhS7wFIsS"
FUNCTIONS=(
    "checkin_processor"
    "checkin_retriever"
)

echo "🚀 MindBridge Check-in Functions Deployment"
echo "=========================================="
echo "Region: $REGION"
echo "Role: $ROLE_NAME"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if role exists
if ! aws iam get-role --role-name $ROLE_NAME --region $REGION &> /dev/null; then
    echo "❌ IAM role $ROLE_NAME does not exist. Please run setup-aws-resources.sh first."
    exit 1
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --region $REGION --query 'Role.Arn' --output text)
echo "✅ Using IAM role: $ROLE_ARN"

# Function to deploy a Lambda function
deploy_function() {
    local function_name=$1
    local function_dir="lambda_functions/${function_name}"
    
    echo ""
    echo "📦 Deploying $function_name..."
    
    # Check if function directory exists
    if [ ! -d "$function_dir" ]; then
        echo "❌ Function directory $function_dir does not exist"
        return 1
    fi
    
    # Create deployment package
    echo "📁 Creating deployment package..."
    cd "$function_dir"
    
    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt -t . --quiet
    fi
    
    # Create ZIP file
    echo "🗜️  Creating ZIP package..."
    zip -r "${function_name}.zip" . -x "*.pyc" "__pycache__/*" "*.git*" "*.DS_Store" > /dev/null
    
    # Check if function exists
    if aws lambda get-function --function-name $function_name --region $REGION &> /dev/null; then
        echo "🔄 Updating existing function..."
        aws lambda update-function-code \
            --function-name $function_name \
            --zip-file "fileb://${function_name}.zip" \
            --region $REGION > /dev/null
    else
        echo "🆕 Creating new function..."
        aws lambda create-function \
            --function-name $function_name \
            --runtime python3.9 \
            --role $ROLE_ARN \
            --handler handler.lambda_handler \
            --zip-file "fileb://${function_name}.zip" \
            --timeout 30 \
            --memory-size 512 \
            --region $REGION > /dev/null
    fi
    
    # Set environment variables
    echo "⚙️  Setting environment variables..."
    aws lambda update-function-configuration \
        --function-name $function_name \
        --environment "Variables={CHECKINS_TABLE=mindbridge-checkins,BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0}" \
        --region $REGION > /dev/null
    
    # Clean up
    rm -f "${function_name}.zip"
    cd - > /dev/null
    
    echo "✅ $function_name deployed successfully!"
}

# Deploy each function
for function in "${FUNCTIONS[@]}"; do
    deploy_function $function
done

echo ""
echo "🎉 All check-in functions deployed successfully!"
echo ""
echo "📋 Summary:"
echo "   - checkin_processor: Processes mental health check-ins and generates LLM reports"
echo "   - checkin_retriever: Retrieves check-in data for Emotion Analytics dashboard"
echo ""
echo "🔗 API Gateway endpoints will be created automatically when functions are invoked"
echo "💡 Test the functions using the Emotion Analytics tab in the frontend" 