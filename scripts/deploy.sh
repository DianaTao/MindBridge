#!/bin/bash

# MindBridge Deployment Script
# This script handles the complete deployment of the MindBridge application

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS CLI configuration
check_aws_config() {
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi

    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi

    print_success "AWS CLI is configured"
}

# Function to check Node.js
check_node() {
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install it first."
        exit 1
    fi

    if ! command_exists npm; then
        print_error "npm is not installed. Please install it first."
        exit 1
    fi

    print_success "Node.js and npm are available"
}

# Function to check Python
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi

    print_success "Python 3 is available"
}

# Function to build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm ci
    
    # Run linting
    print_status "Running frontend linting..."
    npm run lint
    
    # Run tests
    print_status "Running frontend tests..."
    npm test -- --watchAll=false --passWithNoTests
    
    # Build
    print_status "Building frontend for production..."
    GENERATE_SOURCEMAP=false npm run build
    
    cd ..
    print_success "Frontend build completed"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying infrastructure..."
    
    cd infrastructure
    
    # Install dependencies
    print_status "Installing CDK dependencies..."
    npm install
    
    # Bootstrap CDK (if needed)
    print_status "Bootstrapping CDK..."
    cdk bootstrap || print_warning "CDK bootstrap failed, continuing..."
    
    # Deploy
    print_status "Deploying CDK stack..."
    cdk deploy --require-approval never --context environment=$ENVIRONMENT
    
    cd ..
    print_success "Infrastructure deployment completed"
}

# Function to deploy frontend to S3
deploy_frontend() {
    print_status "Deploying frontend to S3..."
    
    # Get bucket name from CloudFormation outputs
    FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
        --output text)
    
    if [ -z "$FRONTEND_BUCKET" ]; then
        print_error "Could not get frontend bucket name from CloudFormation"
        exit 1
    fi
    
    print_status "Deploying to bucket: $FRONTEND_BUCKET"
    
    # Sync build files
    aws s3 sync frontend/build/ s3://$FRONTEND_BUCKET \
        --delete \
        --cache-control "max-age=31536000,public"
    
    # Upload index.html with no-cache
    aws s3 cp frontend/build/index.html s3://$FRONTEND_BUCKET/index.html \
        --cache-control "no-cache,no-store,must-revalidate"
    
    # Invalidate CloudFront cache
    print_status "Invalidating CloudFront cache..."
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text)
    
    if [ ! -z "$DISTRIBUTION_ID" ]; then
        aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*"
    fi
    
    print_success "Frontend deployment completed"
}

# Function to deploy Lambda functions
deploy_lambda_functions() {
    print_status "Deploying Lambda functions..."
    
    # Create deployment script
    cat > deploy_lambda.sh << 'EOF'
#!/bin/bash
FUNCTION_DIR=$1
FUNCTION_NAME=$2

echo "Deploying $FUNCTION_NAME from $FUNCTION_DIR"

# Create deployment package
cd $FUNCTION_DIR
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t .
fi

# Create ZIP file
zip -r ../${FUNCTION_NAME}.zip . -x "*.pyc" "__pycache__/*" "*.git*"

# Update Lambda function
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://../${FUNCTION_NAME}.zip

echo "Deployed $FUNCTION_NAME successfully"
EOF
    
    chmod +x deploy_lambda.sh
    
    # Deploy each Lambda function
    local functions=(
        "lambda_functions/checkin_processor:mindbridge-checkin-processor-$ENVIRONMENT"
        "lambda_functions/checkin_retriever:mindbridge-checkin-retriever-$ENVIRONMENT"
        "lambda_functions/dashboard:mindbridge-dashboard-$ENVIRONMENT"
        "lambda_functions/emotion_fusion:mindbridge-emotion-fusion-$ENVIRONMENT"
        "lambda_functions/health_check:mindbridge-health-check-$ENVIRONMENT"
        "lambda_functions/realtime_call_analysis:mindbridge-realtime-call-analysis-$ENVIRONMENT"
        "lambda_functions/text_analysis:mindbridge-text-analysis-$ENVIRONMENT"
        "lambda_functions/user_auth:mindbridge-user-auth-$ENVIRONMENT"
        "lambda_functions/video_analysis:mindbridge-video-analysis-$ENVIRONMENT"
    )
    
    for func in "${functions[@]}"; do
        IFS=':' read -r dir name <<< "$func"
        print_status "Deploying $name..."
        ./deploy_lambda.sh "$dir" "$name"
    done
    
    # Clean up
    rm deploy_lambda.sh
    rm -f *.zip
    
    print_success "Lambda functions deployment completed"
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    print_status "Running post-deployment tests..."
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f "$API_URL/health" >/dev/null 2>&1; then
        print_success "Health endpoint is working"
    else
        print_error "Health endpoint is not working"
        exit 1
    fi
    
    # Get frontend URL
    FRONTEND_URL=$(aws cloudformation describe-stacks \
        --stack-name MindBridgeStack \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
        --output text)
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -f "$FRONTEND_URL" >/dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
        exit 1
    fi
    
    print_success "Post-deployment tests completed"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Deployment environment (dev/prod) [default: dev]"
    echo "  -f, --frontend-only      Deploy only frontend"
    echo "  -i, --infrastructure-only Deploy only infrastructure"
    echo "  -l, --lambda-only        Deploy only Lambda functions"
    echo "  -t, --test-only          Run tests only"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Deploy everything to dev"
    echo "  $0 -e prod               # Deploy everything to production"
    echo "  $0 -f                    # Deploy only frontend"
    echo "  $0 -i                    # Deploy only infrastructure"
}

# Main script
main() {
    # Default values
    ENVIRONMENT="dev"
    DEPLOY_FRONTEND=true
    DEPLOY_INFRASTRUCTURE=true
    DEPLOY_LAMBDA=true
    RUN_TESTS=true
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -f|--frontend-only)
                DEPLOY_INFRASTRUCTURE=false
                DEPLOY_LAMBDA=false
                RUN_TESTS=false
                shift
                ;;
            -i|--infrastructure-only)
                DEPLOY_FRONTEND=false
                DEPLOY_LAMBDA=false
                RUN_TESTS=false
                shift
                ;;
            -l|--lambda-only)
                DEPLOY_FRONTEND=false
                DEPLOY_INFRASTRUCTURE=false
                RUN_TESTS=false
                shift
                ;;
            -t|--test-only)
                DEPLOY_FRONTEND=false
                DEPLOY_INFRASTRUCTURE=false
                DEPLOY_LAMBDA=false
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    print_status "Starting MindBridge deployment..."
    print_status "Environment: $ENVIRONMENT"
    
    # Check prerequisites
    check_aws_config
    check_node
    check_python
    
    # Build frontend if needed
    if [ "$DEPLOY_FRONTEND" = true ]; then
        build_frontend
    fi
    
    # Deploy infrastructure if needed
    if [ "$DEPLOY_INFRASTRUCTURE" = true ]; then
        deploy_infrastructure
    fi
    
    # Deploy frontend if needed
    if [ "$DEPLOY_FRONTEND" = true ]; then
        deploy_frontend
    fi
    
    # Deploy Lambda functions if needed
    if [ "$DEPLOY_LAMBDA" = true ]; then
        deploy_lambda_functions
    fi
    
    # Run post-deployment tests if needed
    if [ "$RUN_TESTS" = true ]; then
        run_post_deployment_tests
    fi
    
    print_success "Deployment completed successfully!"
    
    # Display URLs
    if [ "$DEPLOY_INFRASTRUCTURE" = true ] || [ "$DEPLOY_FRONTEND" = true ]; then
        echo ""
        print_status "Deployment URLs:"
        FRONTEND_URL=$(aws cloudformation describe-stacks \
            --stack-name MindBridgeStack \
            --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
            --output text)
        API_URL=$(aws cloudformation describe-stacks \
            --stack-name MindBridgeStack \
            --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
            --output text)
        echo "Frontend: $FRONTEND_URL"
        echo "API: $API_URL"
    fi
}

# Run main function
main "$@" 