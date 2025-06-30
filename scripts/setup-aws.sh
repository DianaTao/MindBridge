#!/bin/bash

# MindBridge AWS Setup Script
# This script helps set up AWS credentials and deploy the infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 MindBridge AWS Setup${NC}"
echo -e "${BLUE}=======================${NC}"
echo ""

# Function to check if AWS CLI is configured
check_aws_config() {
    if aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${GREEN}✅ AWS CLI is configured${NC}"
        aws sts get-caller-identity --query 'Arn' --output text
        return 0
    else
        echo -e "${RED}❌ AWS CLI is not configured${NC}"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    
    # Install CDK globally
    if ! command -v cdk >/dev/null 2>&1; then
        echo "Installing AWS CDK..."
        npm install -g aws-cdk
    fi
    
    # Install project dependencies
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
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to bootstrap CDK
bootstrap_cdk() {
    echo -e "${BLUE}🚀 Bootstrapping CDK...${NC}"
    cd infrastructure
    cdk bootstrap
    cd ..
    echo -e "${GREEN}✅ CDK bootstrapped${NC}"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    local environment=${1:-development}
    echo -e "${BLUE}🏗️  Deploying infrastructure (${environment})...${NC}"
    cd infrastructure
    cdk deploy --context environment=$environment --require-approval never
    cd ..
    echo -e "${GREEN}✅ Infrastructure deployed${NC}"
}

# Function to get stack outputs
get_outputs() {
    echo -e "${BLUE}📊 Getting stack outputs...${NC}"
    
    # Get WebSocket URL
    WEBSOCKET_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    # Get HTTP API URL
    HTTP_API_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`HttpApiURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$WEBSOCKET_URL" ] && [ ! -z "$HTTP_API_URL" ]; then
        echo -e "${GREEN}✅ Stack outputs retrieved${NC}"
        echo "WebSocket URL: $WEBSOCKET_URL"
        echo "HTTP API URL: $HTTP_API_URL"
        
        # Update frontend configuration
        echo "REACT_APP_WEBSOCKET_URL=$WEBSOCKET_URL" > frontend/.env.production
        echo "REACT_APP_API_URL=$HTTP_API_URL" >> frontend/.env.production
        echo -e "${GREEN}✅ Frontend configuration updated${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not retrieve stack outputs${NC}"
    fi
}

# Function to test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    # Get HTTP API URL
    HTTP_API_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`HttpApiURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$HTTP_API_URL" ]; then
        echo "Testing health endpoint..."
        if curl -s "$HTTP_API_URL/health" >/dev/null; then
            echo -e "${GREEN}✅ Health endpoint is working${NC}"
        else
            echo -e "${RED}❌ Health endpoint failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not test deployment - no API URL found${NC}"
    fi
}

# Main script logic
main() {
    echo "This script will help you set up AWS and deploy MindBridge AI."
    echo ""
    
    # Check if AWS CLI is configured
    if ! check_aws_config; then
        echo ""
        echo -e "${YELLOW}Please configure AWS CLI first:${NC}"
        echo "1. Run: aws configure"
        echo "2. Enter your AWS Access Key ID"
        echo "3. Enter your AWS Secret Access Key"
        echo "4. Enter your preferred region (e.g., us-east-1)"
        echo "5. Enter output format (json)"
        echo ""
        echo "Or see AWS_SETUP.md for detailed instructions."
        exit 1
    fi
    
    echo ""
    read -p "Do you want to install dependencies? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    
    echo ""
    read -p "Do you want to bootstrap CDK? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        bootstrap_cdk
    fi
    
    echo ""
    read -p "Do you want to deploy infrastructure? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter environment (development/production) [development]: " environment
        environment=${environment:-development}
        deploy_infrastructure $environment
    fi
    
    echo ""
    read -p "Do you want to get stack outputs and update frontend config? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        get_outputs
    fi
    
    echo ""
    read -p "Do you want to test the deployment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_deployment
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start the frontend: cd frontend && npm start"
    echo "2. Test the application in your browser"
    echo "3. Check AWS_SETUP.md for more details"
    echo "4. Monitor your AWS costs in the AWS Console"
}

# Run main function
main "$@" 