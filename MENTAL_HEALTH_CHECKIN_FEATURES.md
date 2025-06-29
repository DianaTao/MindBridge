# 🧠 MindBridge Mental Health Check-in & Emotion Analytics

## Overview

MindBridge now includes comprehensive mental health check-in capabilities with AI-powered analysis and long-term emotion tracking. This system stores check-in data in AWS DynamoDB and generates personalized LLM reports for users.

## 🚀 New Features

### 1. Mental Health Check-in System
- **Real-time Emotion Analysis**: Uses camera to analyze facial expressions during check-ins
- **Self-Assessment**: Comprehensive questionnaire covering mood, energy, stress, sleep, social connection, and motivation
- **AI-Powered Reports**: LLM-generated personalized insights and recommendations
- **Data Storage**: Secure storage in AWS DynamoDB with user privacy protection

### 2. Emotion Analytics Dashboard
- **Historical Data**: View all past check-ins with detailed analytics
- **Trend Analysis**: Track emotional patterns over time
- **Personalized Insights**: AI-generated recommendations based on your data
- **Wellness Scoring**: Overall mental health score calculation

## 🏗️ Architecture

### Database Schema
```
mindbridge-checkins Table:
├── checkin_id (Hash Key)
├── timestamp (Range Key)
├── user_id
├── session_id
├── duration
├── emotion_analysis
│   ├── dominant_emotion
│   ├── emotion_scores
│   ├── average_wellbeing
│   ├── stress_level
│   └── mood_history
├── self_assessment
│   ├── overall_mood
│   ├── energy_level
│   ├── stress_level
│   ├── sleep_quality
│   ├── social_connection
│   ├── motivation
│   └── notes
├── llm_report
│   ├── emotional_summary
│   ├── key_insights
│   ├── recommendations
│   ├── trend_analysis
│   ├── overall_assessment
│   ├── mood_score
│   └── confidence_level
├── overall_score
└── ttl (1 year expiration)
```

### Lambda Functions

#### 1. checkin-processor
- **Purpose**: Processes mental health check-ins and generates LLM reports
- **Input**: Check-in data with emotion analysis and self-assessment
- **Output**: LLM-generated report with insights and recommendations
- **Features**:
  - Stores check-in data in DynamoDB
  - Calls AWS Bedrock for LLM analysis
  - Generates fallback reports if LLM unavailable
  - Calculates overall wellness score

#### 2. checkin-retriever
- **Purpose**: Retrieves check-in data for Emotion Analytics dashboard
- **Input**: Query parameters (user_id, days, limit)
- **Output**: Check-in history and analytics summary
- **Features**:
  - Retrieves historical check-in data
  - Generates analytics summary
  - Provides trend analysis
  - Creates personalized recommendations

## 🛠️ Setup Instructions

### 1. AWS Resources Setup
```bash
# Run the AWS resources setup script
./scripts/setup-aws-resources.sh
```

This creates:
- DynamoDB table: `mindbridge-checkins`
- IAM permissions for Lambda functions
- Required AWS resources

### 2. Deploy Lambda Functions
```bash
# Deploy the check-in Lambda functions
./scripts/deploy-checkin-functions.sh
```

This deploys:
- `checkin-processor` Lambda function
- `checkin-retriever` Lambda function

### 3. Start Local Development
```bash
# Start the local backend proxy
python local_backend_real.py

# In another terminal, start the frontend
cd frontend
npm start
```

## 📱 User Experience

### Mental Health Check-in Flow
1. **Start Check-in**: Click "Start Check-in" to begin
2. **Camera Analysis**: Position face in camera for emotion analysis
3. **Self-Assessment**: Complete the wellness questionnaire
4. **AI Report**: Receive personalized LLM-generated insights
5. **Data Storage**: Check-in data is securely stored

### Emotion Analytics Dashboard
1. **Historical View**: See all past check-ins
2. **Analytics Summary**: View overall statistics and trends
3. **LLM Reports**: Click on any check-in to see detailed AI analysis
4. **Recommendations**: Get personalized wellness suggestions

## 🔧 API Endpoints

### Check-in Processor
```
POST /checkin-processor
Content-Type: application/json

{
  "checkin_id": "checkin_1234567890",
  "user_id": "user_123",
  "session_id": "session_456",
  "duration": 120,
  "emotion_analysis": {
    "dominant_emotion": "happy",
    "emotion_scores": {...},
    "average_wellbeing": 75,
    "stress_level": "low"
  },
  "self_assessment": {
    "overall_mood": 8,
    "energy_level": 7,
    "stress_level": 3,
    "sleep_quality": 6,
    "social_connection": 8,
    "motivation": 7,
    "notes": "Feeling good today!"
  }
}
```

### Check-in Retriever
```
GET /checkin-retriever?user_id=user_123&days=30&limit=50

Response:
{
  "checkins": [...],
  "analytics_summary": {
    "total_checkins": 15,
    "average_score": 72.5,
    "mood_trend": "improving",
    "most_common_emotion": "happy",
    "recommendations": [...],
    "period_covered": "2024-01-01 to 2024-01-31"
  }
}
```

## 🎯 Key Features

### AI-Powered Analysis
- **Emotional Summary**: Brief overview of emotional state
- **Key Insights**: 3-4 bullet points highlighting important patterns
- **Recommendations**: Actionable wellness suggestions
- **Trend Analysis**: Long-term emotional pattern recognition
- **Overall Assessment**: Comprehensive mental health evaluation

### Privacy & Security
- **User Isolation**: Each user's data is completely separate
- **Data Encryption**: All data encrypted at rest and in transit
- **TTL Expiration**: Data automatically expires after 1 year
- **No Personal Info**: No names, emails, or identifying information stored

### Fallback System
- **LLM Unavailable**: Generates helpful fallback reports
- **Network Issues**: Graceful degradation with local processing
- **Error Handling**: Comprehensive error messages and recovery

## 📊 Analytics Features

### Wellness Scoring
- **Emotion Analysis**: 60% weight from facial expression analysis
- **Self-Assessment**: 40% weight from questionnaire responses
- **Overall Score**: 0-100 scale with color-coded indicators

### Trend Analysis
- **Improving**: Recent scores higher than earlier scores
- **Declining**: Recent scores lower than earlier scores
- **Stable**: Consistent scores over time
- **Insufficient Data**: Not enough check-ins for trend analysis

### Personalized Recommendations
- **Score-Based**: Different suggestions for different wellness levels
- **Trend-Based**: Recommendations based on emotional patterns
- **Frequency-Based**: Suggestions based on check-in consistency

## 🚀 Future Enhancements

### Planned Features
- **Mood Prediction**: AI-powered mood forecasting
- **Integration**: Connect with calendar and activity data
- **Notifications**: Gentle reminders for regular check-ins
- **Export**: Data export for personal records
- **Sharing**: Optional sharing with healthcare providers

### Advanced Analytics
- **Correlation Analysis**: Identify triggers and patterns
- **Seasonal Trends**: Year-over-year comparison
- **Goal Setting**: Personalized wellness targets
- **Progress Tracking**: Visual progress indicators

## 🔍 Troubleshooting

### Common Issues

#### Check-in Not Saving
- Verify AWS permissions are correctly set
- Check Lambda function logs in AWS Console
- Ensure DynamoDB table exists and is accessible

#### LLM Reports Not Generating
- Verify Bedrock permissions and model access
- Check fallback reports are being generated
- Review Lambda function environment variables

#### Emotion Analytics Not Loading
- Verify check-in retriever Lambda function is deployed
- Check API Gateway endpoint configuration
- Review browser console for network errors

### Debug Commands
```bash
# Check Lambda function status
aws lambda get-function --function-name checkin-processor --region us-east-1

# View recent logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/checkin --region us-east-1

# Test DynamoDB table
aws dynamodb scan --table-name mindbridge-checkins --limit 5 --region us-east-1
```

## 📞 Support

For technical support or feature requests:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs for detailed error information
3. Verify all AWS resources are properly configured
4. Test with the local development environment first

---

**Note**: This system is designed for personal wellness tracking and should not replace professional mental health care. If you're experiencing mental health concerns, please consult with a qualified healthcare provider. 