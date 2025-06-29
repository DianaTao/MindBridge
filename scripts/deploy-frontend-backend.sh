#!/bin/bash

# MindBridge Frontend and Backend Deployment Script
# Deploys React frontend to S3 + CloudFront and backend proxy

set -e

# Configuration
REGION="us-east-1"
STAGE="dev"
FRONTEND_BUCKET="mindbridge-frontend-${STAGE}-$(aws sts get-caller-identity --query Account --output text)"
BACKEND_BUCKET="mindbridge-backend-${STAGE}-$(aws sts get-caller-identity --query Account --output text)"
CLOUDFRONT_DISTRIBUTION_NAME="mindbridge-frontend-${STAGE}"

echo "🚀 MindBridge Frontend & Backend Deployment"
echo "==========================================="
echo "Region: $REGION"
echo "Stage: $STAGE"
echo "Frontend Bucket: $FRONTEND_BUCKET"
echo "Backend Bucket: $BACKEND_BUCKET"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install it first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# ==============================================
# CREATE S3 BUCKETS
# ==============================================

echo ""
echo "📦 Creating S3 buckets..."

# Create frontend bucket
if ! aws s3 ls "s3://$FRONTEND_BUCKET" &> /dev/null; then
    echo "🆕 Creating frontend bucket: $FRONTEND_BUCKET"
    aws s3 mb "s3://$FRONTEND_BUCKET" --region $REGION
    
    # Configure bucket for static website hosting
    aws s3 website "s3://$FRONTEND_BUCKET" \
        --index-document index.html \
        --error-document index.html
else
    echo "✅ Frontend bucket already exists: $FRONTEND_BUCKET"
fi

# Create backend bucket
if ! aws s3 ls "s3://$BACKEND_BUCKET" &> /dev/null; then
    echo "🆕 Creating backend bucket: $BACKEND_BUCKET"
    aws s3 mb "s3://$BACKEND_BUCKET" --region $REGION
else
    echo "✅ Backend bucket already exists: $BACKEND_BUCKET"
fi

# ==============================================
# BUILD FRONTEND
# ==============================================

echo ""
echo "🔨 Building React frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🏗️  Building project..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed. Please check the build output."
    exit 1
fi

echo "✅ Frontend build completed"

# ==============================================
# DEPLOY FRONTEND TO S3
# ==============================================

echo ""
echo "📤 Deploying frontend to S3..."

# Sync build files to S3
aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
    --delete \
    --cache-control "max-age=31536000,public" \
    --exclude "*.html" \
    --exclude "*.json"

# Upload HTML files with no-cache headers
aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
    --delete \
    --cache-control "no-cache,no-store,must-revalidate" \
    --include "*.html" \
    --include "*.json"

echo "✅ Frontend deployed to S3"

# ==============================================
# CREATE CLOUDFRONT DISTRIBUTION
# ==============================================

echo ""
echo "🌐 Setting up CloudFront distribution..."

# Check if CloudFront distribution already exists
EXISTING_DISTRIBUTION=$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, '$FRONTEND_BUCKET')].Id" --output text)

if [ -z "$EXISTING_DISTRIBUTION" ] || [ "$EXISTING_DISTRIBUTION" == "None" ]; then
    echo "🆕 Creating CloudFront distribution..."
    
    # Create CloudFront distribution
    DISTRIBUTION_CONFIG=$(cat <<EOF
{
    "CallerReference": "$(date +%s)",
    "Comment": "MindBridge Frontend Distribution",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$FRONTEND_BUCKET",
                "DomainName": "$FRONTEND_BUCKET.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$FRONTEND_BUCKET",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 0
            }
        ]
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF
)

    # Create the distribution
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config "$DISTRIBUTION_CONFIG" \
        --query 'Distribution.Id' \
        --output text)
    
    echo "✅ CloudFront distribution created: $DISTRIBUTION_ID"
else
    echo "✅ CloudFront distribution already exists: $EXISTING_DISTRIBUTION"
    DISTRIBUTION_ID=$EXISTING_DISTRIBUTION
fi

# Wait for distribution to be deployed
echo "⏳ Waiting for CloudFront distribution to be deployed..."
aws cloudfront wait distribution-deployed --id $DISTRIBUTION_ID

# Get the CloudFront domain name
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)
echo "✅ CloudFront domain: $CLOUDFRONT_DOMAIN"

# ==============================================
# DEPLOY BACKEND PROXY
# ==============================================

echo ""
echo "🔧 Deploying backend proxy..."

# Navigate back to root directory
cd ..

# Create a simple backend proxy for API Gateway
cat > backend_proxy.py << 'EOF'
#!/usr/bin/env python3
"""
MindBridge Backend Proxy
Serves as a proxy between the frontend and AWS API Gateway
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Gateway URL (will be updated after deployment)
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'https://your-api-gateway-url.amazonaws.com/prod')

@app.route('/api/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(subpath):
    """Proxy requests to API Gateway"""
    try:
        # Construct the full URL
        url = f"{API_GATEWAY_URL}/{subpath}"
        
        # Forward the request
        headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'content-length']}
        
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json())
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json())
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'mindbridge-backend-proxy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Create requirements.txt for backend
cat > backend_requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
gunicorn==21.2.0
EOF

# Create Procfile for backend
cat > Procfile << 'EOF'
web: gunicorn backend_proxy:app --bind 0.0.0.0:$PORT
EOF

# Create a simple deployment package
mkdir -p backend_deploy
cp backend_proxy.py backend_deploy/
cp backend_requirements.txt backend_deploy/
cp Procfile backend_deploy/

# Create a simple index.html for backend health check
cat > backend_deploy/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>MindBridge Backend</title>
</head>
<body>
    <h1>MindBridge Backend Proxy</h1>
    <p>Status: <span id="status">Checking...</span></p>
    <script>
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.status;
            })
            .catch(error => {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            });
    </script>
</body>
</html>
EOF

# Upload backend files to S3
echo "📤 Uploading backend files to S3..."
aws s3 sync backend_deploy/ "s3://$BACKEND_BUCKET" --delete

# Configure backend bucket for static website hosting
aws s3 website "s3://$BACKEND_BUCKET" \
    --index-document index.html \
    --error-document index.html

echo "✅ Backend proxy deployed to S3"

# ==============================================
# UPDATE FRONTEND CONFIGURATION
# ==============================================

echo ""
echo "⚙️  Updating frontend configuration..."

# Get the backend website URL
BACKEND_URL="http://$BACKEND_BUCKET.s3-website-$REGION.amazonaws.com"

# Update the frontend API configuration
cd frontend

# Create a production config file
cat > src/config.prod.js << EOF
// Production configuration
export const config = {
    API_BASE_URL: '$BACKEND_URL/api',
    WEBSOCKET_URL: 'wss://your-websocket-url.amazonaws.com/prod',
    CLOUDFRONT_URL: 'https://$CLOUDFRONT_DOMAIN'
};
EOF

# Update package.json to include the config
if ! grep -q "config.prod.js" package.json; then
    # Add a build script that copies the config
    sed -i '' 's/"build": "react-scripts build"/"build": "cp src\/config.prod.js src\/config.js \&\& react-scripts build"/' package.json
fi

# Rebuild with production config
echo "🏗️  Rebuilding frontend with production configuration..."
npm run build

# Re-deploy to S3
echo "📤 Re-deploying frontend with updated configuration..."
aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
    --delete \
    --cache-control "max-age=31536000,public" \
    --exclude "*.html" \
    --exclude "*.json"

aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
    --delete \
    --cache-control "no-cache,no-store,must-revalidate" \
    --include "*.html" \
    --include "*.json"

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*"

# ==============================================
# CLEANUP
# ==============================================

echo ""
echo "🧹 Cleaning up temporary files..."
cd ..
rm -rf backend_deploy
rm -f backend_proxy.py
rm -f backend_requirements.txt
rm -f Procfile

# ==============================================
# SUMMARY
# ==============================================

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Summary:"
echo "   Frontend URL: https://$CLOUDFRONT_DOMAIN"
echo "   Backend URL: http://$BACKEND_URL"
echo "   Frontend S3 Bucket: $FRONTEND_BUCKET"
echo "   Backend S3 Bucket: $BACKEND_BUCKET"
echo "   CloudFront Distribution ID: $DISTRIBUTION_ID"
echo ""
echo "🔧 Next steps:"
echo "   1. Update your API Gateway URL in the backend configuration"
echo "   2. Test the frontend at: https://$CLOUDFRONT_DOMAIN"
echo "   3. Monitor CloudWatch logs for any issues"
echo ""
echo "💡 Note: CloudFront may take 5-10 minutes to fully propagate changes" 