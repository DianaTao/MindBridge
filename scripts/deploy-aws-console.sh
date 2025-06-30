#!/bin/bash

# MindBridge AWS Console Deployment Script
# This script deploys the entire MindBridge AI platform to AWS

set -e

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

echo -e "${BLUE}🧠 MindBridge AWS Console Deployment${NC}"
echo -e "${BLUE}=====================================${NC}"
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

# Function to check AWS configuration
check_aws_config() {
    echo -e "${BLUE}Checking AWS configuration...${NC}"
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${RED}❌ AWS CLI is not configured${NC}"
        echo "Please run: aws configure"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI is configured${NC}"
    aws sts get-caller-identity --query 'Arn' --output text
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking Prerequisites"
    
    local missing_deps=()
    
    if ! command_exists node; then
        missing_deps+=("node.js")
    fi
    
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if ! command_exists pip; then
        missing_deps+=("pip")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies: ${missing_deps[*]}${NC}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
    echo ""
}

# Function to install dependencies
install_dependencies() {
    print_step "Installing Dependencies"
    
    # Install CDK globally
    if ! command_exists cdk; then
        echo "Installing AWS CDK..."
        npm install -g aws-cdk
    fi
    
    # Install root dependencies
    echo "Installing root dependencies..."
    npm install
    
    # Install infrastructure dependencies
    echo "Installing infrastructure dependencies..."
    cd infrastructure
    npm install
    cd ..
    
    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    # Use simplified requirements to avoid compilation issues
    if [ -f "requirements-simple.txt" ]; then
        pip install -r requirements-simple.txt
    else
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
}

# Function to build Lambda functions
build_lambda_functions() {
    print_step "Building Lambda Functions"
    
    for lambda_dir in lambda_functions/*/; do
        if [ -d "$lambda_dir" ]; then
            lambda_name=$(basename "$lambda_dir")
            echo "Building $lambda_name..."
            
            # Install lambda-specific dependencies if requirements.txt exists
            if [ -f "$lambda_dir/requirements.txt" ]; then
                pip install -r "$lambda_dir/requirements.txt" -t "$lambda_dir"
            fi
            
            # Compile Python files
            python3 -m compileall "$lambda_dir"
        fi
    done
    
    echo -e "${GREEN}✅ Lambda functions built${NC}"
    echo ""
}

# Function to bootstrap CDK
bootstrap_cdk() {
    print_step "Bootstrapping CDK"
    
    cd infrastructure
    
    # Check if already bootstrapped
    if aws cloudformation describe-stacks --stack-name CDKToolkit >/dev/null 2>&1; then
        echo "CDK is already bootstrapped"
    else
        echo "Bootstrapping CDK..."
        cdk bootstrap
    fi
    
    cd ..
    echo -e "${GREEN}✅ CDK bootstrapped${NC}"
    echo ""
}

# Function to deploy infrastructure
deploy_infrastructure() {
    print_step "Deploying Infrastructure"
    
    cd infrastructure
    
    echo "Deploying CDK stack..."
    cdk deploy --context environment=$ENVIRONMENT --require-approval never
    
    cd ..
    echo -e "${GREEN}✅ Infrastructure deployed${NC}"
    echo ""
}

# Function to get stack outputs
get_stack_outputs() {
    print_step "Getting Stack Outputs"
    
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
    
    echo ""
}

# Function to test deployment
test_deployment() {
    print_step "Testing Deployment"
    
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
        
        echo "Testing video analysis endpoint..."
        if curl -s -X POST "$HTTP_API_URL/video-analysis" \
            -H "Content-Type: application/json" \
            -d '{"frame_data": "test", "user_id": "test", "session_id": "test"}' >/dev/null; then
            echo -e "${GREEN}✅ Video analysis endpoint is working${NC}"
        else
            echo -e "${RED}❌ Video analysis endpoint failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not test deployment - no API URL found${NC}"
    fi
    
    echo ""
}

# Function to build and deploy frontend
deploy_frontend() {
    print_step "Building Frontend"
    
    cd frontend
    npm run build
    cd ..
    
    echo -e "${GREEN}✅ Frontend built${NC}"
    echo ""
    
    # Ask if user wants to deploy frontend
    read -p "Do you want to deploy frontend to S3? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_frontend_to_s3
    fi
}

# Function to deploy frontend to S3
deploy_frontend_to_s3() {
    print_step "Deploying Frontend to S3"
    
    # Get account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
    BUCKET_NAME="mindbridge-frontend-$ACCOUNT_ID"
    
    echo "Creating S3 bucket: $BUCKET_NAME"
    
    # Create S3 bucket
    aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION 2>/dev/null || echo "Bucket already exists"
    
    # Upload build files
    echo "Uploading build files..."
    aws s3 sync frontend/build/ s3://$BUCKET_NAME --delete
    
    # Configure bucket for static website hosting
    echo "Configuring static website hosting..."
    aws s3 website s3://$BUCKET_NAME \
        --index-document index.html \
        --error-document index.html
    
    # Get website URL
    WEBSITE_URL=$(aws s3api get-bucket-website --bucket $BUCKET_NAME --query 'WebsiteEndpoint' --output text 2>/dev/null || echo "")
    
    if [ ! -z "$WEBSITE_URL" ]; then
        echo -e "${GREEN}✅ Frontend deployed to S3${NC}"
        echo "Website URL: http://$WEBSITE_URL"
    else
        echo -e "${YELLOW}⚠️  Could not get website URL${NC}"
    fi
    
    echo ""
}

# Function to display summary
display_summary() {
    print_step "Deployment Summary"
    
    echo -e "${GREEN}🎉 MindBridge AI deployment completed successfully!${NC}"
    echo ""
    
    # Get stack outputs
    WEBSOCKET_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    HTTP_API_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`HttpApiURL`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    echo "📊 Infrastructure Details:"
    echo "  • WebSocket URL: $WEBSOCKET_URL"
    echo "  • HTTP API URL: $HTTP_API_URL"
    echo "  • Environment: $ENVIRONMENT"
    echo "  • Region: $AWS_REGION"
    echo ""
    
    echo "🔗 AWS Console Links:"
    echo "  • Lambda Functions: https://console.aws.amazon.com/lambda/home?region=$AWS_REGION#/functions"
    echo "  • API Gateway: https://console.aws.amazon.com/apigateway/home?region=$AWS_REGION#/apis"
    echo "  • DynamoDB: https://console.aws.amazon.com/dynamodb/home?region=$AWS_REGION#tables"
    echo "  • CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups"
    echo "  • S3: https://console.aws.amazon.com/s3/home?region=$AWS_REGION"
    echo ""
    
    echo "🚀 Next Steps:"
    echo "  1. Test the API endpoints"
    echo "  2. Start the frontend locally: cd frontend && npm start"
    echo "  3. Monitor AWS costs in Cost Explorer"
    echo "  4. Set up CloudWatch dashboards"
    echo ""
    
    echo "📚 Useful Commands:"
    echo "  • View logs: aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/mindbridge'"
    echo "  • Update stack: cd infrastructure && cdk deploy"
    echo "  • Destroy stack: cd infrastructure && cdk destroy"
    echo ""
}

# Main execution
main() {
    check_aws_config
    check_prerequisites
    install_dependencies
    build_lambda_functions
    bootstrap_cdk
    deploy_infrastructure
    get_stack_outputs
    test_deployment
    deploy_frontend
    display_summary
}

# Run main function
main "$@" 