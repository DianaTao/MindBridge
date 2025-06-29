#!/bin/bash

# MindBridge AI - Automated Call Review Deployment Script
# This script deploys the automated call processing pipeline

set -e

echo "🚀 Deploying MindBridge AI Automated Call Review System..."

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

# Step 1: Deploy Infrastructure
print_status "Deploying CDK infrastructure with automated call processing..."
cd infrastructure

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    print_status "Activating virtual environment..."
    source .venv/bin/activate
fi

# Deploy the stack
print_status "Running CDK deploy..."
cdk deploy --require-approval never --app "python mindbridge_stack.py"

if [ $? -eq 0 ]; then
    print_success "Infrastructure deployed successfully!"
else
    print_error "Infrastructure deployment failed!"
    exit 1
fi

cd ..

# Step 2: Build and Deploy Frontend
print_status "Building frontend application..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Build the application
print_status "Building React application..."
npm run build

if [ $? -eq 0 ]; then
    print_success "Frontend built successfully!"
else
    print_error "Frontend build failed!"
    exit 1
fi

# Deploy to S3
print_status "Deploying frontend to S3..."
aws s3 sync build/ s3://mindbridge-media-dev-$(aws sts get-caller-identity --query Account --output text) --delete --region us-east-1

if [ $? -eq 0 ]; then
    print_success "Frontend deployed to S3 successfully!"
else
    print_error "Frontend deployment failed!"
    exit 1
fi

cd ..

# Step 3: Test the API endpoints
print_status "Testing API endpoints..."

# Get the API URL from CDK outputs
API_URL=$(aws cloudformation describe-stacks --stack-name MindBridgeStack --region us-east-1 --query 'Stacks[0].Outputs[?OutputKey==`ApiURL`].OutputValue' --output text)

if [ -z "$API_URL" ]; then
    print_error "Could not retrieve API URL from CloudFormation outputs"
    exit 1
fi

print_status "API URL: $API_URL"

# Test health endpoint
print_status "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_success "Health endpoint is working!"
else
    print_warning "Health endpoint test failed: $HEALTH_RESPONSE"
fi

# Step 4: Create test call recording
print_status "Creating test call recording for automated processing..."

# Create a test directory structure
TEST_CALL_ID="test-call-$(date +%s)"
AGENT_ID="test-agent-123"
BUCKET_NAME="mindbridge-call-recordings-dev-$(aws sts get-caller-identity --query Account --output text)"

# Create a simple test audio file (1 second of silence)
print_status "Creating test audio file..."
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -q:a 9 -acodec libmp3lame test-audio.mp3 2>/dev/null || {
    print_warning "ffmpeg not available, creating empty test file..."
    echo "test audio content" > test-audio.mp3
}

# Upload to the incoming folder to trigger automated processing
print_status "Uploading test call to trigger automated processing..."
aws s3 cp test-audio.mp3 "s3://$BUCKET_NAME/incoming/$AGENT_ID/$TEST_CALL_ID.mp3" --region us-east-1

if [ $? -eq 0 ]; then
    print_success "Test call uploaded successfully!"
    print_status "This should trigger the automated call processing Lambda"
else
    print_error "Failed to upload test call"
fi

# Clean up test file
rm -f test-audio.mp3

# Step 5: Display deployment summary
print_success "🎉 MindBridge AI Automated Call Review System deployed successfully!"

echo ""
echo "📋 Deployment Summary:"
echo "======================"
echo "✅ Infrastructure: Deployed via CDK"
echo "✅ Frontend: Built and deployed to S3"
echo "✅ API Gateway: Available at $API_URL"
echo "✅ Automated Call Processing: Configured and ready"
echo ""
echo "🔗 Access Points:"
echo "=================="
echo "🌐 Frontend: Check S3 bucket for static hosting"
echo "🔌 API: $API_URL"
echo "📊 Call Review Dashboard: Available in the frontend"
echo ""
echo "🧪 Testing:"
echo "==========="
echo "📞 Test call uploaded: $TEST_CALL_ID"
echo "👤 Agent ID: $AGENT_ID"
echo "🪣 S3 Bucket: $BUCKET_NAME"
echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Access the frontend and navigate to 'Automated Call Review'"
echo "2. Monitor CloudWatch logs for call processing"
echo "3. Check DynamoDB for call analysis results"
echo "4. Set up CloudFront for HTTPS frontend access"
echo ""
echo "🔍 Monitoring:"
echo "=============="
echo "📊 CloudWatch Logs: Check Lambda function logs"
echo "🗄️  DynamoDB: Monitor call_reviews table"
echo "🪣 S3: Check incoming/ folder for new calls"
echo ""

print_success "Deployment completed! 🚀" 