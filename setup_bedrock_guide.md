# AWS Bedrock Setup Guide for MindBridge

## Step 1: Enable Bedrock in AWS Console

1. **Go to AWS Bedrock Console**
   - Navigate to: https://console.aws.amazon.com/bedrock/
   - Sign in with your AWS account

2. **Enable Bedrock Service**
   - Click "Get started" or "Enable Bedrock"
   - Accept the terms of service
   - Wait for activation (usually takes a few minutes)

3. **Request Model Access**
   - Go to "Model access" in the left sidebar
   - Request access to:
     - `anthropic.claude-3-sonnet-20240229-v1:0`
     - `anthropic.claude-3-haiku-20240307-v1:0`
   - Click "Submit" for each model
   - Wait for approval (usually instant for these models)

## Step 2: Update IAM Permissions

The Lambda function needs proper IAM permissions to access Bedrock. Run this script:

```bash
python update_bedrock_permissions.py
```

## Step 3: Verify Bedrock Access

Test if Bedrock is working:

```bash
python test_bedrock_connection.py
```

## Step 4: Update Lambda Environment Variables

Make sure the Lambda function has the correct environment variables:

```bash
aws lambda update-function-configuration \
  --function-name mindbridge-checkin-processor-dev \
  --environment "Variables={CHECKINS_TABLE=mindbridge-checkins-dev,BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0,STAGE=dev}"
```

## Step 5: Test Lambda Function

Test the complete integration:

```bash
python test_lambda_bedrock.py
```

## Troubleshooting

### If you get "AccessDeniedException":
1. Make sure Bedrock is enabled in your AWS account
2. Verify model access is granted
3. Check IAM permissions are attached to Lambda role

### If you get "Model not found":
1. Verify the model ID is correct
2. Make sure you have access to the specific model
3. Check the AWS region (Bedrock models are region-specific)

### If Lambda times out:
1. Increase Lambda timeout to 60 seconds
2. Check if Bedrock service is responding

## Expected Results

When working correctly, you should see:
- ✅ Bedrock client initialized successfully
- ✅ Model access granted
- ✅ Lambda function returns LLM-generated reports
- ✅ "🤖 AI Generated" badge in the UI 