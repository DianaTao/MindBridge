#!/bin/bash

# Deploy checkin_processor Lambda function
echo "Deploying checkin_processor Lambda function..."

# Navigate to the checkin_processor directory
cd lambda_functions/checkin_processor

# Create a temporary directory for packaging
rm -rf package
mkdir package

# Copy the handler and requirements
cp handler.py package/
cp requirements.txt package/

# Install dependencies in the package directory
cd package
pip install -r requirements.txt -t .

# Create the deployment package
zip -r ../checkin_processor.zip .

# Go back to checkin_processor directory
cd ..

# Deploy to AWS Lambda
echo "Deploying to AWS Lambda..."
aws lambda update-function-code \
    --function-name mindbridge-checkin-processor \
    --zip-file fileb://checkin_processor.zip \
    --region us-east-1

# Clean up
rm -rf package
rm checkin_processor.zip

echo "checkin_processor Lambda function deployed successfully!"
echo "You can now test the mental health check-in feature." 