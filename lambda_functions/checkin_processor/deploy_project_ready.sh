#!/bin/bash

echo "🚀 DEPLOYING PROJECT-READY HANDLER FOR SUBMISSION"

# Update Lambda function code
echo "📦 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name mindbridge-checkin-processor-dev \
    --zip-file fileb://checkin_processor_PROJECT_READY.zip \
    --region us-east-1

if [ $? -eq 0 ]; then
    echo "✅ Lambda function updated successfully!"
else
    echo "❌ Failed to update Lambda function"
    exit 1
fi

# Wait for update to complete
echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated \
    --function-name mindbridge-checkin-processor-dev \
    --region us-east-1

echo "🎉 DEPLOYMENT COMPLETE - PROJECT READY FOR SUBMISSION!"
echo "📝 Test the mental health check-in now - it should work!" 