#!/bin/bash

# MindBridge CloudFront Deployment Script
# This script deploys the frontend to S3 and creates/updates CloudFront distribution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="MindBridgeCloudFront"
BUCKET_NAME="mindbridge-frontend-265974216988"
REGION="us-east-1"

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking Prerequisites"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if S3 bucket exists
    if ! aws s3 ls s3://$BUCKET_NAME &> /dev/null; then
        print_error "S3 bucket $BUCKET_NAME does not exist. Please create it first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    echo ""
}

# Build frontend
build_frontend() {
    print_step "Building Frontend"
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    # Build the application
    echo "Building React application..."
    npm run build
    
    cd ..
    
    print_success "Frontend built successfully"
    echo ""
}

# Deploy to S3
deploy_to_s3() {
    print_step "Deploying to S3"
    
    echo "Syncing build files to S3 bucket: $BUCKET_NAME"
    
    # Sync with cache control headers
    aws s3 sync frontend/build/ s3://$BUCKET_NAME \
        --delete \
        --cache-control "public, max-age=31536000" \
        --exclude "*.html" \
        --exclude "asset-manifest.json"
    
    # Upload HTML files with no-cache
    aws s3 sync frontend/build/ s3://$BUCKET_NAME \
        --cache-control "no-cache, no-store, must-revalidate" \
        --include "*.html" \
        --include "asset-manifest.json"
    
    print_success "Frontend deployed to S3"
    echo ""
}

# Deploy CloudFront distribution
deploy_cloudfront() {
    print_step "Deploying CloudFront Distribution"
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME &> /dev/null; then
        echo "Updating existing CloudFront stack..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://cloudfront-deployment.yaml \
            --parameters ParameterKey=S3BucketName,ParameterValue=$BUCKET_NAME \
            --capabilities CAPABILITY_IAM
        
        echo "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME
    else
        echo "Creating new CloudFront stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://cloudfront-deployment.yaml \
            --parameters ParameterKey=S3BucketName,ParameterValue=$BUCKET_NAME \
            --capabilities CAPABILITY_IAM
        
        echo "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME
    fi
    
    print_success "CloudFront distribution deployed"
    echo ""
}

# Get CloudFront URL
get_cloudfront_url() {
    print_step "Getting CloudFront URL"
    
    # Get the CloudFront domain name
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text)
    
    CLOUDFRONT_URL="https://$CLOUDFRONT_DOMAIN"
    
    echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
    echo "CloudFront URL: $CLOUDFRONT_URL"
    
    print_success "CloudFront URL retrieved"
    echo ""
}

# Invalidate CloudFront cache
invalidate_cache() {
    print_step "Invalidating CloudFront Cache"
    
    # Get distribution ID
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text)
    
    echo "Creating cache invalidation for distribution: $DISTRIBUTION_ID"
    
    # Create invalidation
    aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*"
    
    print_success "Cache invalidation created"
    echo ""
}

# Test deployment
test_deployment() {
    print_step "Testing Deployment"
    
    # Get CloudFront URL
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text)
    
    CLOUDFRONT_URL="https://$CLOUDFRONT_DOMAIN"
    
    echo "Testing CloudFront URL: $CLOUDFRONT_URL"
    
    # Wait a bit for CloudFront to propagate
    echo "Waiting for CloudFront to propagate (30 seconds)..."
    sleep 30
    
    # Test the URL
    if curl -s -o /dev/null -w "%{http_code}" "$CLOUDFRONT_URL" | grep -q "200"; then
        print_success "CloudFront deployment is working!"
    else
        print_warning "CloudFront might still be propagating. Please wait a few minutes and try again."
    fi
    
    echo ""
}

# Display summary
display_summary() {
    print_step "Deployment Summary"
    
    # Get CloudFront URL
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
        --output text)
    
    CLOUDFRONT_URL="https://$CLOUDFRONT_DOMAIN"
    
    echo -e "${GREEN}🎉 MindBridge CloudFront deployment completed successfully!${NC}"
    echo ""
    echo "📊 Deployment Details:"
    echo "  • S3 Bucket: $BUCKET_NAME"
    echo "  • CloudFront Domain: $CLOUDFRONT_DOMAIN"
    echo "  • CloudFront URL: $CLOUDFRONT_URL"
    echo "  • Region: $REGION"
    echo ""
    echo "🔗 Access Your Application:"
    echo "  • Production URL: $CLOUDFRONT_URL"
    echo "  • S3 Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
    echo ""
    echo "📚 Useful Commands:"
    echo "  • View CloudFront distribution: aws cloudfront get-distribution --id <distribution-id>"
    echo "  • Create cache invalidation: aws cloudfront create-invalidation --distribution-id <distribution-id> --paths '/*'"
    echo "  • Monitor CloudFront metrics: https://console.aws.amazon.com/cloudfront/home"
    echo ""
    echo "⚠️  Important Notes:"
    echo "  • CloudFront may take 5-10 minutes to fully propagate globally"
    echo "  • Cache invalidation may take 5-10 minutes to complete"
    echo "  • Monitor CloudWatch metrics for performance and costs"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🚀 MindBridge CloudFront Deployment${NC}"
    echo "=================================="
    echo ""
    
    check_prerequisites
    build_frontend
    deploy_to_s3
    deploy_cloudfront
    get_cloudfront_url
    invalidate_cache
    test_deployment
    display_summary
}

# Run main function
main "$@" 