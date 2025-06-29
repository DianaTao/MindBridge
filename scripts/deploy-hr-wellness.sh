#!/bin/bash

# MindBridge HR Wellness Data Deployment Script
# This script deploys the HR wellness data Lambda function and API Gateway endpoint

set -e

echo "🚀 Starting HR Wellness Data Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "infrastructure/mindbridge_stack.py" ]; then
    print_error "Please run this script from the MindBridge project root directory"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    print_error "AWS CDK is not installed. Please install it first: npm install -g aws-cdk"
    exit 1
fi

# Get environment from command line argument or default to development
ENVIRONMENT=${1:-development}
if [ "$ENVIRONMENT" = "production" ]; then
    STAGE="prod"
else
    STAGE="dev"
fi

print_status "Deploying to environment: $ENVIRONMENT (stage: $STAGE)"

# Navigate to infrastructure directory
cd infrastructure

# Install CDK dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing CDK dependencies..."
    npm install
fi

# Bootstrap CDK if needed
print_status "Checking CDK bootstrap status..."
if ! cdk list &> /dev/null; then
    print_status "Bootstrapping CDK..."
    cdk bootstrap
fi

# Deploy the stack
print_status "Deploying MindBridge stack with HR wellness data..."
cdk deploy --context environment=$ENVIRONMENT --require-approval never

# Get the API URL from CDK outputs
print_status "Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name MindBridgeStack \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiURL`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -n "$API_URL" ]; then
    print_success "API Gateway URL: $API_URL"
    print_success "HR Wellness Data endpoint: $API_URL/hr-wellness-data"
else
    print_warning "Could not retrieve API Gateway URL from CloudFormation outputs"
fi

# Test the new endpoint
print_status "Testing HR wellness data endpoint..."
if [ -n "$API_URL" ]; then
    TEST_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/hr-wellness-data" -o /tmp/hr_test_response.json || echo "000")
    HTTP_CODE="${TEST_RESPONSE: -3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "HR wellness data endpoint is working correctly!"
        print_status "Response preview:"
        head -c 200 /tmp/hr_test_response.json
        echo "..."
    else
        print_warning "HR wellness data endpoint returned HTTP $HTTP_CODE"
        if [ -f "/tmp/hr_test_response.json" ]; then
            print_status "Response:"
            cat /tmp/hr_test_response.json
        fi
    fi
else
    print_warning "Skipping endpoint test - no API URL available"
fi

# Clean up test file
rm -f /tmp/hr_test_response.json

print_success "🎉 HR Wellness Data deployment completed successfully!"
print_status "Next steps:"
echo "  1. Test the HR dashboard in your frontend application"
echo "  2. Verify that HR users can access the dashboard"
echo "  3. Check CloudWatch logs for any issues"
echo "  4. Monitor the Lambda function performance"

# Return to original directory
cd ..

print_success "Deployment script completed!" 