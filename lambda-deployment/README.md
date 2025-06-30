# MindBridge Emotion Fusion Lambda Deployment Package

## Contents
- `lambda_function.py` - Main Lambda handler (renamed from aws_fusion_handler.py)
- `requirements.txt` - Python dependencies

## Deployment Instructions

### Method 1: ZIP Upload (Recommended)
1. Create ZIP file: `zip -r mindbridge-emotion-fusion.zip lambda_function.py`
2. Upload to AWS Lambda Console
3. Set handler to: `lambda_function.lambda_handler`
4. Configure environment variables and IAM permissions

### Method 2: With Dependencies (if needed)
1. Install dependencies: `pip install -r requirements.txt -t .`
2. Create ZIP: `zip -r mindbridge-emotion-fusion.zip .`
3. Upload to Lambda (may exceed inline editor limit)

## Configuration
- Runtime: Python 3.9+
- Memory: 512 MB minimum
- Timeout: 60 seconds
- Handler: lambda_function.lambda_handler

## Environment Variables
- EMOTIONS_TABLE=mindbridge-emotions
- BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
