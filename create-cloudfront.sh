#!/bin/bash

# MindBridge CloudFront CLI Deployment Script
# This script creates a CloudFront distribution directly using AWS CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
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
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create CloudFront distribution
create_cloudfront_distribution() {
    print_step "Creating CloudFront Distribution"
    
    # Generate a unique caller reference
    CALLER_REFERENCE="mindbridge-$(date +%s)"
    
    # Create distribution configuration JSON
    cat > cloudfront-config.json << EOF
{
    "CallerReference": "${CALLER_REFERENCE}",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3Origin",
                "DomainName": "${BUCKET_NAME}.s3-website-us-east-1.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3Origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "TrustedKeyGroups": {
            "Enabled": false,
            "Quantity": 0
        },
        "AllowedMethods": {
            "Quantity": 7,
            "Items": [
                "GET",
                "HEAD",
                "OPTIONS",
                "PUT",
                "POST",
                "PATCH",
                "DELETE"
            ],
            "CachedMethods": {
                "Quantity": 2,
                "Items": [
                    "GET",
                    "HEAD"
                ]
            }
        },
        "SmoothStreaming": false,
        "Compress": true,
        "LambdaFunctionAssociations": {
            "Quantity": 0
        },
        "FunctionAssociations": {
            "Quantity": 0
        },
        "FieldLevelEncryptionId": "",
        "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
        "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf",
        "ResponseHeadersPolicyId": ""
    },
    "CacheBehaviors": {
        "Quantity": 0
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 0
            },
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 0
            }
        ]
    },
    "Comment": "MindBridge frontend CloudFront distribution",
    "Logging": {
        "Enabled": false,
        "IncludeCookies": false,
        "Bucket": "",
        "Prefix": ""
    },
    "PriceClass": "PriceClass_All",
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "Staging": false
}
EOF
    
    print_success "Distribution configuration created"
    
    # Create the distribution
    print_step "Creating CloudFront distribution (this may take 5-10 minutes)..."
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution --distribution-config file://cloudfront-config.json --query 'Distribution.Id' --output text)
    
    if [ $? -eq 0 ]; then
        print_success "CloudFront distribution created successfully!"
        print_success "Distribution ID: $DISTRIBUTION_ID"
        
        # Get the domain name
        DOMAIN_NAME=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)
        print_success "CloudFront Domain: $DOMAIN_NAME"
        
        # Save the distribution ID for future use
        echo $DISTRIBUTION_ID > .cloudfront-distribution-id
        echo $DOMAIN_NAME > .cloudfront-domain
        
        print_success "Your MindBridge frontend is now available at:"
        print_success "https://$DOMAIN_NAME"
        
    else
        print_error "Failed to create CloudFront distribution"
        exit 1
    fi
}

# Wait for distribution to be deployed
wait_for_deployment() {
    print_step "Waiting for CloudFront distribution to be deployed..."
    
    if [ -f .cloudfront-distribution-id ]; then
        DISTRIBUTION_ID=$(cat .cloudfront-distribution-id)
        
        print_warning "CloudFront distributions typically take 5-15 minutes to deploy globally."
        print_warning "You can check the status with: aws cloudfront get-distribution --id $DISTRIBUTION_ID"
        
        # Wait for the distribution to be deployed
        aws cloudfront wait distribution-deployed --id $DISTRIBUTION_ID
        
        if [ $? -eq 0 ]; then
            print_success "CloudFront distribution is now deployed and ready!"
        else
            print_warning "Distribution deployment is still in progress. Please wait a few more minutes."
        fi
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🚀 MindBridge CloudFront CLI Deployment${NC}"
    echo ""
    
    check_prerequisites
    create_cloudfront_distribution
    wait_for_deployment
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    print_step "Next Steps:"
    echo "1. Wait 5-15 minutes for global deployment"
    echo "2. Test your CloudFront URL"
    echo "3. Update your frontend API URL if needed"
    echo ""
}

# Run the script
main "$@" 