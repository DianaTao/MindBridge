# 🚀 Quick AWS Setup for MindBridge AI

This is the fastest way to get MindBridge AI running in AWS Console.

## Prerequisites

✅ **AWS Account**: You need an AWS account with billing enabled
✅ **AWS CLI**: Already installed on your machine
✅ **Basic Terminal Knowledge**: Ability to run commands

## Step 1: Configure AWS (One-time setup)

Open your terminal and run:

```bash
aws configure
```

You'll be asked for:
- **AWS Access Key ID**: Get this from AWS Console → IAM → Users → Your User → Security credentials
- **AWS Secret Access Key**: Get this from the same place as above
- **Default region**: Type `us-east-1` (or your preferred region)
- **Default output format**: Type `json`

## Step 2: Run the Automated Deployment

From your MindBridge project directory, run:

```bash
./scripts/deploy-aws-console.sh
```

This script will:
- ✅ Check all prerequisites
- ✅ Install all dependencies
- ✅ Build Lambda functions
- ✅ Deploy everything to AWS
- ✅ Test the deployment
- ✅ Give you the URLs

## Step 3: What Gets Created in AWS

After running the script, you'll have:

### 🔧 AWS Services Created:
- **4 Lambda Functions**: Video analysis, audio analysis, emotion fusion, dashboard
- **2 API Gateways**: HTTP API and WebSocket API
- **2 DynamoDB Tables**: For emotions and user data
- **1 TimeStream Database**: For time-series analytics
- **1 S3 Bucket**: For media storage
- **1 EventBridge Rule**: For event processing
- **IAM Roles**: With proper permissions

### 🌐 URLs You'll Get:
- **HTTP API URL**: For REST API calls
- **WebSocket URL**: For real-time updates
- **Frontend URL**: If you choose to deploy to S3

## Step 4: Verify in AWS Console

After deployment, check these in AWS Console:

### 1. Lambda Functions
1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. You should see 4 functions starting with `mindbridge-`
3. Click on any function to see the code and logs

### 2. API Gateway
1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway/)
2. You should see 2 APIs: HTTP and WebSocket
3. Click on HTTP API to see the endpoints

### 3. DynamoDB Tables
1. Go to [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. You should see 2 tables: `mindbridge-emotions-dev` and `mindbridge-users-dev`

### 4. S3 Bucket
1. Go to [S3 Console](https://console.aws.amazon.com/s3/)
2. You should see a bucket starting with `mindbridge-media-dev`

## Step 5: Test Your Deployment

### Test API Endpoints
```bash
# Replace YOUR_API_URL with the URL from the deployment output
curl https://YOUR_API_URL/health
```

### Test Frontend
1. Start the frontend locally:
   ```bash
   cd frontend
   npm start
   ```
2. Open http://localhost:3001 in your browser
3. The frontend will automatically connect to your AWS APIs

## Step 6: Monitor and Manage

### View Logs
1. Go to [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2. Click "Log groups"
3. Look for `/aws/lambda/mindbridge-*` groups
4. Click on any group to see logs

### Monitor Costs
1. Go to [AWS Cost Explorer](https://console.aws.amazon.com/cost-management/home#/costexplorer)
2. Set date range to "Last 7 days"
3. Monitor your spending

### Update Code
To update your Lambda functions:
```bash
cd infrastructure
cdk deploy
```

## Troubleshooting

### Common Issues:

1. **"AWS CLI not configured"**
   - Run `aws configure` again
   - Make sure your AWS credentials are correct

2. **"Permission denied"**
   - Your AWS user needs AdministratorAccess or equivalent permissions
   - Go to IAM Console → Users → Your User → Add permissions

3. **"CDK not found"**
   - The script will install CDK automatically
   - If it fails, run: `npm install -g aws-cdk`

4. **"Stack deployment failed"**
   - Check the error message in the terminal
   - Common causes: insufficient permissions, region issues, or resource limits

### Get Help:

1. **Check the logs**: Look at CloudWatch logs for error details
2. **Review permissions**: Ensure your AWS user has proper permissions
3. **Check region**: Make sure you're using the same region everywhere
4. **Contact support**: Use AWS Support if you have a paid plan

## Cost Estimation

### Development Environment (Estimated monthly):
- **Lambda**: $0-5 (depending on usage)
- **API Gateway**: $0-1 (depending on requests)
- **DynamoDB**: $0-2 (depending on storage)
- **S3**: $0-1 (depending on storage)
- **TimeStream**: $0-5 (depending on data points)
- **Total**: $0-15/month for light usage

### Production Environment:
- Costs will be higher depending on usage
- Consider setting up billing alerts
- Monitor costs regularly

## Next Steps

1. **Test the application**: Use the frontend to test emotion analysis
2. **Customize**: Modify the Lambda functions for your needs
3. **Scale**: Add more features and optimize performance
4. **Monitor**: Set up CloudWatch dashboards and alarms
5. **Secure**: Review and tighten security settings

## Quick Commands Reference

```bash
# Deploy everything
./scripts/deploy-aws-console.sh

# Update infrastructure
cd infrastructure && cdk deploy

# View logs
aws logs tail /aws/lambda/mindbridge-video-analysis-dev --follow

# Test API
curl https://YOUR_API_URL/health

# Start frontend locally
cd frontend && npm start

# Destroy everything (be careful!)
cd infrastructure && cdk destroy
```

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/
- **CDK Documentation**: https://docs.aws.amazon.com/cdk/
- **Project Issues**: Create GitHub issues for project-specific problems

---

🎉 **Congratulations!** Your MindBridge AI platform is now running in AWS! 