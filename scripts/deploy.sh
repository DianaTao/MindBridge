#!/bin/bash

# MindBridge AI Deployment Script
# This script deploys the entire MindBridge AI platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_PROFILE=${AWS_PROFILE:-default}

echo -e "${BLUE}🧠 MindBridge AI Deployment${NC}"
echo -e "${BLUE}=============================${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "AWS Region: ${YELLOW}$AWS_REGION${NC}"
echo -e "AWS Profile: ${YELLOW}$AWS_PROFILE${NC}"
echo ""

# Function to print step headers
print_step() {
    echo -e "${GREEN}📦 $1${NC}"
    echo "----------------------------------------"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_step "Checking Prerequisites"

if ! command_exists aws; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install Node.js and npm.${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ python3 not found. Please install Python 3.9+.${NC}"
    exit 1
fi

if ! command_exists pip3; then
    echo -e "${RED}❌ pip3 not found. Please install pip3.${NC}"
    exit 1
fi

if ! command_exists cdk; then
    echo -e "${RED}❌ AWS CDK not found. Installing...${NC}"
    npm install -g aws-cdk
fi

echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
echo ""

# Install dependencies
print_step "Installing Dependencies"

echo "Installing root dependencies..."
npm install

echo "Installing infrastructure dependencies..."
cd infrastructure
npm install
cd ..

echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Build Lambda functions
print_step "Building Lambda Functions"

for lambda_dir in lambda_functions/*/; do
    if [ -d "$lambda_dir" ]; then
        lambda_name=$(basename "$lambda_dir")
        echo "Building $lambda_name..."
        
        # Install lambda-specific dependencies if requirements.txt exists
        if [ -f "$lambda_dir/requirements.txt" ]; then
            pip3 install -r "$lambda_dir/requirements.txt" -t "$lambda_dir"
        fi
        
        # Compile Python files
        python3 -m compileall "$lambda_dir"
    fi
done

echo -e "${GREEN}✅ Lambda functions built${NC}"
echo ""

# Build frontend
print_step "Building Frontend"

cd frontend
npm run build
cd ..

echo -e "${GREEN}✅ Frontend built${NC}"
echo ""

# Deploy infrastructure
print_step "Deploying Infrastructure"

cd infrastructure

# Bootstrap CDK if needed
echo "Checking CDK bootstrap..."
cdk bootstrap --profile $AWS_PROFILE

# Deploy with environment context
echo "Deploying CDK stack..."
cdk deploy --profile $AWS_PROFILE --context environment=$ENVIRONMENT --require-approval never

# Get outputs
echo "Getting stack outputs..."
WEBSOCKET_URL=$(aws cloudformation describe-stacks \
    --stack-name MindBridgeStack \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
    --output text)

HTTP_API_URL=$(aws cloudformation describe-stacks \
    --stack-name MindBridgeStack \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`HttpApiURL`].OutputValue' \
    --output text)

cd ..

echo -e "${GREEN}✅ Infrastructure deployed${NC}"
echo ""

# Update frontend configuration
print_step "Updating Frontend Configuration"

if [ ! -z "$WEBSOCKET_URL" ]; then
    echo "REACT_APP_WEBSOCKET_URL=$WEBSOCKET_URL" > frontend/.env.production
    echo "REACT_APP_HTTP_API_URL=$HTTP_API_URL" >> frontend/.env.production
    echo -e "${GREEN}✅ Frontend configuration updated${NC}"
else
    echo -e "${YELLOW}⚠️  Could not retrieve WebSocket URL. Please update frontend/.env.production manually${NC}"
fi

echo ""

# Deploy frontend (optional - would typically deploy to S3/CloudFront)
if [ "$ENVIRONMENT" = "production" ]; then
    print_step "Deploying Frontend to Production"
    echo -e "${YELLOW}⚠️  Frontend deployment to S3/CloudFront not implemented in this script${NC}"
    echo "You can manually deploy the frontend/build directory to your hosting service"
fi

# Summary
print_step "Deployment Summary"

echo -e "${GREEN}🎉 MindBridge AI deployment completed successfully!${NC}"
echo ""
echo "📊 Infrastructure Details:"
echo "  • WebSocket URL: $WEBSOCKET_URL"
echo "  • HTTP API URL: $HTTP_API_URL"
echo "  • Environment: $ENVIRONMENT"
echo "  • Region: $AWS_REGION"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test the WebSocket connection"
echo "  2. Verify Lambda functions are working"
echo "  3. Configure frontend environment variables"
echo "  4. Start the frontend development server: cd frontend && npm start"
echo ""
echo "📚 Useful Commands:"
echo "  • View logs: aws logs describe-log-groups --profile $AWS_PROFILE"
echo "  • Update stack: cd infrastructure && cdk deploy --profile $AWS_PROFILE"
echo "  • Destroy stack: cd infrastructure && cdk destroy --profile $AWS_PROFILE"
echo ""

if [ "$ENVIRONMENT" = "development" ]; then
    echo -e "${BLUE}💡 Development Mode:${NC}"
    echo "  • Frontend will run on http://localhost:3000"
    echo "  • WebSocket connection: $WEBSOCKET_URL"
    echo "  • Start development: cd frontend && npm start"
fi

echo -e "${GREEN}✨ Happy coding with MindBridge AI! ✨${NC}" 