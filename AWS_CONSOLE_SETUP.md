# MindBridge AI - AWS Console Setup Guide

This guide will walk you through setting up MindBridge AI in AWS Console step by step.

## Prerequisites

1. **AWS Account**: Active AWS account with billing enabled
2. **AWS CLI**: Already installed and configured
3. **Node.js**: For CDK deployment
4. **Python 3.9+**: For Lambda functions

## Step 1: Configure AWS CLI

First, configure your AWS credentials:

```bash
aws configure
```

Enter your:
- **AWS Access Key ID**
- **AWS Secret Access Key**
- **Default region** (e.g., `us-east-1`)
- **Default output format** (`json`)

## Step 2: Install Dependencies

```bash
# Install AWS CDK globally
npm install -g aws-cdk

# Install project dependencies
npm install
cd infrastructure && npm install && cd ..
cd frontend && npm install && cd ..

# Install Python dependencies in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Bootstrap CDK

```bash
cd infrastructure
cdk bootstrap
```

This creates the CDK toolkit stack in your AWS account.

## Step 4: Deploy Infrastructure

```bash
# Deploy to development environment
cdk deploy --context environment=development --require-approval never
```

## Step 5: Verify AWS Services in Console

After deployment, verify these services in AWS Console:

### 1. Lambda Functions
**Console**: AWS Lambda → Functions
- `mindbridge-video-analysis-dev`
- `mindbridge-audio-analysis-dev`
- `mindbridge-emotion-fusion-dev`
- `mindbridge-dashboard-dev`

### 2. API Gateway
**Console**: API Gateway → APIs
- HTTP API: `mindbridge-http-dev`
- WebSocket API: `mindbridge-websocket-dev`

### 3. DynamoDB Tables
**Console**: DynamoDB → Tables
- `mindbridge-emotions-dev`
- `mindbridge-users-dev`

### 4. TimeStream Database
**Console**: TimeStream → Databases
- `MindBridge-dev`

### 5. S3 Bucket
**Console**: S3 → Buckets
- `mindbridge-media-dev-{account-id}`

### 6. EventBridge Rules
**Console**: EventBridge → Rules
- `mindbridge-emotion-fusion-dev`

## Step 6: Get API Endpoints

After deployment, CDK will output the API endpoints. Note these URLs:

```bash
# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name MindBridgeStack \
  --query 'Stacks[0].Outputs'
```

## Step 7: Update Frontend Configuration

Create environment files for the frontend:

```bash
# Create production environment file
cat > frontend/.env.production << EOF
REACT_APP_API_URL=https://your-http-api-url.execute-api.us-east-1.amazonaws.com
REACT_APP_WEBSOCKET_URL=wss://your-websocket-url.execute-api.us-east-1.amazonaws.com/dev
EOF
```

## Step 8: Test AWS Deployment

### Test HTTP API
```bash
# Health check
curl https://your-http-api-url.execute-api.us-east-1.amazonaws.com/health

# Video analysis
curl -X POST https://your-http-api-url.execute-api.us-east-1.amazonaws.com/video-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "frame_data": "base64-encoded-image",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

### Test WebSocket
```javascript
const ws = new WebSocket('wss://your-websocket-url.execute-api.us-east-1.amazonaws.com/dev');
ws.onopen = () => console.log('Connected to MindBridge WebSocket');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
```

## Step 9: Deploy Frontend (Optional)

### Option A: Deploy to S3 + CloudFront
```bash
# Build frontend
cd frontend
npm run build

# Create S3 bucket for hosting
aws s3 mb s3://mindbridge-frontend-{your-account-id}

# Upload build files
aws s3 sync build/ s3://mindbridge-frontend-{your-account-id}

# Configure bucket for static website hosting
aws s3 website s3://mindbridge-frontend-{your-account-id} \
  --index-document index.html \
  --error-document index.html
```

### Option B: Deploy to Vercel/Netlify
1. Push code to GitHub
2. Connect repository to Vercel/Netlify
3. Set environment variables
4. Deploy

## AWS Console Navigation Guide

### Lambda Functions
1. Go to **AWS Lambda** console
2. Click **Functions**
3. You should see 4 functions with `mindbridge-` prefix
4. Click on any function to view:
   - Code
   - Configuration
   - Monitoring
   - Logs

### API Gateway
1. Go to **API Gateway** console
2. Click **APIs**
3. You should see:
   - HTTP API: `mindbridge-http-dev`
   - WebSocket API: `mindbridge-websocket-dev`
4. Click on HTTP API to see:
   - Routes
   - Integrations
   - Stages

### DynamoDB
1. Go to **DynamoDB** console
2. Click **Tables**
3. You should see:
   - `mindbridge-emotions-dev`
   - `mindbridge-users-dev`
4. Click on a table to view:
   - Items
   - Indexes
   - Monitoring

### CloudWatch Logs
1. Go to **CloudWatch** console
2. Click **Log groups**
3. Look for `/aws/lambda/mindbridge-*` log groups
4. Click on any log group to view logs

### IAM Roles
1. Go to **IAM** console
2. Click **Roles**
3. Look for `MindBridgeStack-*` roles
4. Click on a role to view:
   - Permissions
   - Trust relationships

## Monitoring and Troubleshooting

### View Lambda Logs
```bash
# Get log group names
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/mindbridge"

# View recent logs
aws logs tail /aws/lambda/mindbridge-video-analysis-dev --follow
```

### Test Lambda Functions
1. Go to **Lambda** console
2. Click on a function
3. Click **Test** tab
4. Create test event
5. Run test

### Monitor API Gateway
1. Go to **API Gateway** console
2. Click on your API
3. Click **Monitoring** tab
4. View metrics and logs

## Cost Optimization

### Development Environment
- Lambda functions use minimal memory (512MB-1GB)
- DynamoDB uses PAY_PER_REQUEST billing
- TimeStream has short retention periods
- S3 lifecycle rules delete old files

### Monitor Costs
1. Go to **AWS Cost Explorer**
2. Set date range
3. Filter by service
4. Monitor daily spending

## Security Best Practices

### IAM
1. Review IAM roles in console
2. Ensure least-privilege access
3. Rotate access keys regularly

### API Gateway
1. Enable API key authentication
2. Configure CORS properly
3. Use HTTPS endpoints

### Lambda
1. Review function permissions
2. Enable VPC if needed
3. Use environment variables for secrets

## Common Issues and Solutions

### 1. CDK Bootstrap Error
```bash
# If bootstrap fails, run manually
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### 2. Permission Errors
- Check IAM user permissions
- Verify AWS credentials
- Ensure user has AdministratorAccess or equivalent

### 3. Lambda Timeout
- Increase timeout in CDK stack
- Optimize function code
- Check external service calls

### 4. API Gateway CORS
- Update CORS configuration in CDK
- Check frontend origin settings
- Test with browser developer tools

## Next Steps

1. **Monitor**: Set up CloudWatch dashboards
2. **Scale**: Implement auto-scaling
3. **Backup**: Set up automated backups
4. **CI/CD**: Implement deployment pipelines
5. **Testing**: Add comprehensive tests

## Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **CDK Documentation**: https://docs.aws.amazon.com/cdk/
- **AWS Support**: Available with paid plans
- **Community**: AWS Forums and Stack Overflow 