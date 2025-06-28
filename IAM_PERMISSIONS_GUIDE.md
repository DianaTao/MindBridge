# 🔐 Setting IAM Permissions for MindBridge Emotion Fusion Lambda

## 📍 Where to Set IAM Permissions

### Method 1: Via Lambda Console (Recommended)

#### Step 1: Open Your Lambda Function
1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click on your function: `mindbridge-emotion-fusion`

#### Step 2: Navigate to Permissions
1. Click the **Configuration** tab
2. Click **Permissions** in the left sidebar
3. You'll see "Execution role" section

#### Step 3: Edit the Execution Role
1. Click on the **Role name** link (e.g., `mindbridge-emotion-fusion-role-xyz`)
2. This opens the **IAM Console** for that role

#### Step 4: Add Permissions
1. In IAM Console, click **Attach policies** button
2. **OR** click **Add permissions** → **Attach policies**

### Method 2: Via IAM Console Directly

#### Step 1: Open IAM Console
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Roles** in the left sidebar

#### Step 2: Find Lambda Role
1. Search for your Lambda function's role
2. Usually named: `mindbridge-emotion-fusion-role-[random-id]`
3. Click on the role name

#### Step 3: Add Permissions
1. Click **Attach policies** or **Add permissions**

## 🎯 Required Permissions to Add

### Option A: Use AWS Managed Policies (Easiest)

#### 1. DynamoDB Access
**Policy Name**: `AmazonDynamoDBFullAccess`
- **OR** create custom policy (see Option B)

#### 2. EventBridge Access  
**Policy Name**: `CloudWatchEventsFullAccess`
- **OR** create custom policy (see Option B)

#### 3. Bedrock Access
**Policy Name**: `AmazonBedrockFullAccess` 
- **OR** create custom policy (see Option B)

### Option B: Create Custom Policies (More Secure)

#### 1. DynamoDB Custom Policy
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
            "Resource": [
                "arn:aws:dynamodb:*:*:table/mindbridge-emotions",
                "arn:aws:dynamodb:*:*:table/mindbridge-emotions/index/*"
            ]
        }
    ]
}
```

#### 2. EventBridge Custom Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "events:PutEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 3. Bedrock Custom Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
        }
    ]
}
```

## 📋 Step-by-Step Visual Guide

### Via Lambda Console:

```
Lambda Console
    └── Your Function (mindbridge-emotion-fusion)
        └── Configuration Tab
            └── Permissions (left sidebar)
                └── Execution role section
                    └── Click role name link
                        └── Opens IAM Console
                            └── Attach policies button
```

### Screenshots Locations:
1. **Lambda Console** → **Configuration** → **Permissions**
2. **Execution role** section shows current role
3. Click the **blue hyperlink** role name
4. **IAM Console** opens → **Attach policies** button

## 🔧 Creating Custom Policies

If you choose custom policies:

#### Step 1: In IAM Console
1. Go to **Policies** → **Create policy**
2. Choose **JSON** tab
3. Paste the JSON policy from above
4. Give it a name like: `MindBridge-DynamoDB-Policy`

#### Step 2: Attach to Role
1. Go back to your Lambda execution role
2. **Attach policies** → Search for your custom policy
3. Select and attach

## ⚠️ Minimum Required Permissions

Your Lambda MUST have these to work:

### Already Included (Default):
- ✅ **CloudWatch Logs**: For logging (usually auto-attached)
- ✅ **Lambda Basic Execution**: Core Lambda permissions

### YOU NEED TO ADD:
- 🔄 **DynamoDB**: To read/write emotion data
- 🔄 **EventBridge**: To send high-risk alerts  
- 🔄 **Bedrock**: For AI enhancement (optional but recommended)

## 🚨 Common Issues

### Issue 1: Can't Find Lambda Role
**Problem**: Role not visible in IAM
**Solution**: Look for role name pattern: `[function-name]-role-[random-id]`

### Issue 2: Permission Denied Errors
**Problem**: Lambda logs show access denied
**Solution**: Check CloudWatch logs for specific service (DynamoDB/EventBridge)

### Issue 3: Bedrock Not Available
**Problem**: AI enhancement fails
**Solution**: Ensure Bedrock is available in your AWS region

## 🎯 Quick Checklist

- [ ] Lambda function deployed successfully
- [ ] Opened Lambda Console → Configuration → Permissions
- [ ] Clicked on execution role name (blue link)
- [ ] In IAM Console for the role
- [ ] Added DynamoDB permissions (Query, PutItem, GetItem)
- [ ] Added EventBridge permissions (PutEvents)
- [ ] Added Bedrock permissions (InvokeModel) - optional
- [ ] Tested Lambda function
- [ ] No permission errors in CloudWatch logs

## 🔗 Direct Links

- [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
- [AWS IAM Console](https://console.aws.amazon.com/iam/)
- [CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups)

## 📞 Need Help?

If you see errors like:
```
User: arn:aws:sts::123456789:assumed-role/lambda-role is not authorized to perform: dynamodb:Query on resource: arn:aws:dynamodb:us-east-1:123456789:table/mindbridge-emotions
```

This means you need to add the DynamoDB permissions following the steps above.
