# AWS Setup Guide for MindBridge AI

This guide will help you set up AWS services and deploy the MindBridge AI infrastructure.

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **AWS CLI**: Already installed via Homebrew
3. **Node.js and npm**: For CDK deployment
4. **Python 3.9+**: For Lambda functions

## Step 1: Configure AWS Credentials

### Option A: Using AWS CLI (Recommended)
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key  
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

### Option B: Using AWS IAM User
1. Go to AWS Console → IAM → Users
2. Create a new user or use existing one
3. Attach policies: `AdministratorAccess` (for development) or custom policies
4. Generate access keys
5. Use these keys in `aws configure`

### Option C: Using AWS SSO (Enterprise)
```bash
aws configure sso
```

## Step 2: Install CDK and Dependencies

```bash
# Install AWS CDK globally
npm install -g aws-cdk

# Install project dependencies
npm install
cd infrastructure && npm install && cd ..
cd frontend && npm install && cd ..
```

## Step 3: Bootstrap CDK (First-time setup)

```bash
cd infrastructure
cdk bootstrap
```

This creates the CDK toolkit stack in your AWS account.

## Step 4: Deploy Infrastructure

### Deploy to Development Environment
```bash
cd infrastructure
cdk deploy --context environment=development
```

### Deploy to Production Environment
```bash
cd infrastructure
cdk deploy --context environment=production
```

## Step 5: Update Frontend Configuration

After deployment, CDK will output the API endpoints. Update your frontend environment variables:

```bash
# Create .env.production file in frontend directory
echo "REACT_APP_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com" > frontend/.env.production
echo "REACT_APP_WEBSOCKET_URL=wss://your-websocket-url.execute-api.us-east-1.amazonaws.com/dev" >> frontend/.env.production
```

## Step 6: Test the Deployment

### Test API Endpoints
```bash
# Health check
curl https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/health

# Test video analysis
curl -X POST https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/video-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "frame_data": "base64-encoded-image",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

### Test WebSocket Connection
```javascript
const ws = new WebSocket('wss://your-websocket-url.execute-api.us-east-1.amazonaws.com/dev');
ws.onopen = () => console.log('Connected to MindBridge WebSocket');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
```

## AWS Services Used

### Core Infrastructure
- **AWS Lambda**: Serverless compute for emotion analysis
- **API Gateway**: HTTP and WebSocket APIs
- **DynamoDB**: NoSQL database for emotions data
- **Amazon S3**: Media storage
- **Amazon TimeStream**: Time-series analytics

### AI/ML Services
- **Amazon Rekognition**: Video emotion analysis
- **Amazon Transcribe**: Speech-to-text
- **Amazon Comprehend**: Text sentiment analysis
- **Amazon Bedrock**: Multi-modal emotion fusion

### Supporting Services
- **EventBridge**: Event-driven architecture
- **CloudWatch**: Logging and monitoring
- **IAM**: Security and permissions

## Cost Optimization

### Development Environment
- Use `PAY_PER_REQUEST` billing for DynamoDB
- Set shorter retention periods for TimeStream
- Use smaller Lambda memory allocations

### Production Environment
- Consider provisioned capacity for DynamoDB
- Implement proper CloudWatch alarms
- Use AWS Cost Explorer to monitor spending

## Security Best Practices

1. **IAM Roles**: Use least-privilege access
2. **VPC**: Consider placing Lambda functions in VPC
3. **Encryption**: Enable encryption at rest and in transit
4. **API Keys**: Implement API key authentication
5. **CORS**: Configure proper CORS policies

## Troubleshooting

### Common Issues

1. **CDK Bootstrap Error**
   ```bash
   cdk bootstrap aws://ACCOUNT-NUMBER/REGION
   ```

2. **Permission Errors**
   - Check IAM user/role permissions
   - Verify AWS credentials are correct

3. **Lambda Timeout**
   - Increase timeout in CDK stack
   - Optimize Lambda function code

4. **API Gateway CORS**
   - Update CORS configuration in CDK
   - Check frontend origin settings

### Useful Commands

```bash
# View stack outputs
aws cloudformation describe-stacks --stack-name MindBridgeStack

# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/mindbridge"

# Update stack
cd infrastructure && cdk deploy

# Destroy stack (be careful!)
cd infrastructure && cdk destroy
```

## Local Development with AWS Services

For local development, you can use:

1. **LocalStack**: For S3, DynamoDB, etc.
2. **DynamoDB Local**: For database testing
3. **SAM Local**: For Lambda testing

See `LOCAL_DEVELOPMENT.md` for detailed local setup instructions.

## Next Steps

1. **Monitor**: Set up CloudWatch dashboards
2. **Scale**: Implement auto-scaling policies
3. **Backup**: Set up automated backups
4. **CI/CD**: Implement deployment pipelines
5. **Testing**: Add comprehensive test suites

## Support

- AWS Documentation: https://docs.aws.amazon.com/
- CDK Documentation: https://docs.aws.amazon.com/cdk/
- MindBridge Issues: Create GitHub issues for project-specific problems 