# 🚀 AWS Lambda Deployment Workflow for MindBridge Emotion Fusion

## 📦 ZIP File Contents

### What to Include in ZIP:
```
mindbridge-emotion-fusion.zip
├── lambda_function.py          # Main handler (30KB)
```

### Why This Approach:
- **Lightweight**: Only 8KB compressed ZIP file
- **Fast Upload**: Quick deployment via AWS Console
- **Built-in Dependencies**: Uses AWS Lambda's built-in boto3, numpy
- **Easy Updates**: Simple code-only deployments

## 🔄 Complete Deployment Workflow

### Step 1: Prepare ZIP File ✅ (Already Done)
```bash
# Navigate to deployment directory
cd /Users/yifeitao/Desktop/MindBridge/lambda-deployment

# ZIP file is ready: mindbridge-emotion-fusion.zip (8KB)
ls -la mindbridge-emotion-fusion.zip
```

### Step 2: AWS Console Deployment

#### 2.1 Open AWS Lambda Console
1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Find your function: `mindbridge-emotion-fusion`
3. Click on the function name

#### 2.2 Upload ZIP File
1. **Code tab** → **Upload from** → **.zip file**
2. Click **Upload** → Select `mindbridge-emotion-fusion.zip`
3. Click **Save**

#### 2.3 Configure Function Settings
```
Runtime: Python 3.9 (or later)
Handler: lambda_function.lambda_handler
Memory: 512 MB (minimum for numpy operations)
Timeout: 60 seconds (for AI processing)
```

### Step 3: Environment Variables
Add these in **Configuration** → **Environment Variables**:
```
EMOTIONS_TABLE = mindbridge-emotions
BEDROCK_MODEL_ID = anthropic.claude-3-sonnet-20240229-v1:0
```

### Step 4: IAM Permissions
Ensure your Lambda execution role has these policies:

#### DynamoDB Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query",
                "dynamodb:PutItem",
                "dynamodb:GetItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/mindbridge-emotions"
        }
    ]
}
```

#### EventBridge Access
```json
{
    "Effect": "Allow",
    "Action": ["events:PutEvents"],
    "Resource": "*"
}
```

#### Bedrock Access (Optional - for AI enhancement)
```json
{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel"],
    "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
}
```

#### CloudWatch Logs (Standard)
```json
{
    "Effect": "Allow",
    "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:*:*:*"
}
```

### Step 5: Test Deployment

#### 5.1 Create Test Event
```json
{
    "user_id": "test-user",
    "session_id": "test-session-123",
    "detail": {
        "modality": "fusion_test",
        "user_id": "test-user",
        "session_id": "test-session-123",
        "timestamp": "2024-06-27T14:00:00Z"
    }
}
```

#### 5.2 Execute Test
1. **Test tab** → **Create new test event**
2. Paste the test JSON above
3. Click **Test**
4. Check execution results and logs

### Step 6: Verify Integration

#### 6.1 Check CloudWatch Logs
Look for these log patterns:
```
🚀 EMOTION FUSION STARTED - Request: [request-id]
👤 Processing fusion for user: test-user, session: test-session-123
ℹ️ No recent emotion data - creating baseline response
✅ FUSION COMPLETE: neutral
```

#### 6.2 Test with Real Data
1. Trigger video/audio/text analysis functions
2. Wait for fusion to be automatically triggered
3. Check DynamoDB for stored fusion results
4. Verify EventBridge events for high-risk alerts

## 🔧 Alternative Deployment Methods

### Method A: Code Editor (Current Approach)
```bash
# Simple ZIP with just Python code
zip -r mindbridge-emotion-fusion.zip lambda_function.py
# Size: ~8KB, Upload via console
```

### Method B: With Dependencies (If Needed)
```bash
# Install dependencies locally
pip install -r requirements.txt -t .

# Create ZIP with all dependencies
zip -r mindbridge-emotion-fusion-full.zip .
# Size: ~50MB+, Upload via S3 or CLI
```

### Method C: Lambda Layers (Advanced)
```bash
# Create separate layer for dependencies
mkdir python
pip install -r requirements.txt -t python/
zip -r emotion-fusion-layer.zip python/

# Deploy layer first, then function code separately
```

## 📊 Monitoring and Validation

### CloudWatch Metrics to Monitor:
- **Invocations**: Function call frequency
- **Duration**: Processing time (should be <30s typically)
- **Errors**: Failed executions
- **Throttles**: Concurrent execution limits

### Success Indicators:
- ✅ Function deploys without errors
- ✅ Test execution completes successfully
- ✅ Logs show emotion fusion processing
- ✅ DynamoDB receives fusion results
- ✅ EventBridge events for high-risk scenarios

## 🚨 Troubleshooting

### Common Issues:

#### 1. Import Errors
```
ERROR: No module named 'numpy'
```
**Solution**: Increase memory to 512MB+ (Lambda includes numpy in larger runtimes)

#### 2. Timeout Errors
```
Task timed out after 3.00 seconds
```
**Solution**: Increase timeout to 60 seconds in Configuration

#### 3. Permission Errors
```
User: arn:aws:sts::123:assumed-role/lambda-role is not authorized to perform: dynamodb:Query
```
**Solution**: Add DynamoDB permissions to execution role

#### 4. Memory Issues
```
Runtime.ExitError: RequestId: memory allocation failed
```
**Solution**: Increase memory allocation to 512MB or higher

## 🎯 Quick Checklist

- [ ] ZIP file created: `mindbridge-emotion-fusion.zip` (8KB)
- [ ] Uploaded to Lambda function via AWS Console
- [ ] Handler set to: `lambda_function.lambda_handler`
- [ ] Runtime: Python 3.9+
- [ ] Memory: 512MB+
- [ ] Timeout: 60 seconds
- [ ] Environment variables configured
- [ ] IAM permissions attached
- [ ] Test event executed successfully
- [ ] CloudWatch logs show successful processing
- [ ] Integration with other Lambda functions verified

## 📁 File Locations

Your deployment files are in:
```
/Users/yifeitao/Desktop/MindBridge/lambda-deployment/
├── mindbridge-emotion-fusion.zip    # Ready for upload (8KB)
├── lambda_function.py               # Source code
├── requirements.txt                 # Dependencies reference
└── README.md                        # Quick instructions
```

## 🚀 Ready to Deploy!

Your ZIP file is ready for immediate deployment:
- **File**: `mindbridge-emotion-fusion.zip` (8KB)
- **Location**: `/Users/yifeitao/Desktop/MindBridge/lambda-deployment/`
- **Next Step**: Upload to AWS Lambda Console

The function will replace your current basic "TODO implement" code with advanced multi-modal emotion fusion capabilities! 🎉
