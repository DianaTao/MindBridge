# HR Wellness Data Deployment Guide

This guide covers the deployment of the HR Wellness Dashboard feature for MindBridge, including the Lambda function and API Gateway endpoint.

## 🏗️ Architecture Overview

The HR Wellness Data feature consists of:

1. **Frontend Components**:
   - `HRWellnessDashboard.js` - Main dashboard component
   - `HRWellnessDashboard.css` - Styling for the dashboard
   - Integration with `EmotionAnalytics.js` for role-based access

2. **Backend Infrastructure**:
   - `hr_wellness_data` Lambda function for data aggregation
   - API Gateway endpoint `/hr-wellness-data`
   - DynamoDB integration for real-time data

3. **Deployment Scripts**:
   - `deploy-hr-wellness.sh` - Automated deployment script
   - `test-hr-wellness.sh` - Endpoint testing script

## 🚀 Deployment Process

### Prerequisites

1. **AWS CLI** installed and configured
2. **AWS CDK** installed globally: `npm install -g aws-cdk`
3. **Node.js** and **npm** for CDK dependencies
4. **Python 3.9+** for Lambda functions

### Step 1: Deploy the Infrastructure

```bash
# Deploy to development environment
./scripts/deploy-hr-wellness.sh development

# Deploy to production environment
./scripts/deploy-hr-wellness.sh production
```

The deployment script will:
- Install CDK dependencies
- Bootstrap CDK if needed
- Deploy the updated stack with HR wellness data Lambda
- Test the new endpoint
- Display the API Gateway URL

### Step 2: Verify Deployment

```bash
# Test the HR wellness data endpoint
./scripts/test-hr-wellness.sh
```

The test script will:
- Verify the endpoint is accessible
- Test with different query parameters
- Validate response structure
- Check CORS headers

## 📊 API Endpoint

### Endpoint Details

- **URL**: `{API_GATEWAY_URL}/hr-wellness-data`
- **Method**: GET
- **Authentication**: None (handled by frontend)
- **CORS**: Enabled for all origins

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | string | 'anonymous' | User identifier for filtering |
| `time_range` | integer | 30 | Number of days to analyze (7, 30, 90) |
| `department` | string | 'all' | Department filter |
| `risk_level` | string | 'all' | Risk level filter (high, medium, low) |

### Example Requests

```bash
# Default request
curl "https://your-api-gateway-url/hr-wellness-data"

# With parameters
curl "https://your-api-gateway-url/hr-wellness-data?time_range=7&department=Engineering&risk_level=high"

# User-specific request
curl "https://your-api-gateway-url/hr-wellness-data?user_id=hr@company.com&time_range=30"
```

### Response Structure

```json
{
  "company_metrics": {
    "total_employees": 1250,
    "active_participants": 892,
    "participation_rate": 71.4,
    "avg_wellness_score": 72.3,
    "burnout_risk_rate": 18.7,
    "high_risk_employees": 234,
    "interventions_needed": 45
  },
  "department_breakdown": [
    {
      "name": "Engineering",
      "avg_score": 68.2,
      "risk_rate": 24.3,
      "employees": 320,
      "high_risk": 78
    }
  ],
  "high_risk_employees": [
    {
      "id": "emp_001",
      "name": "Employee 0001",
      "email": "emp_001@company.com",
      "department": "General",
      "position": "Team Member",
      "risk_score": 87,
      "risk_level": "high",
      "last_checkin": "2024-01-15T10:30:00Z",
      "trend": "declining",
      "symptoms": ["stress", "fatigue", "irritability"],
      "recommendations": [
        "Schedule 1:1 meeting to discuss workload",
        "Consider temporary workload reduction"
      ],
      "interventions": [
        {
          "type": "meeting",
          "status": "scheduled",
          "date": "2024-01-18"
        }
      ]
    }
  ],
  "wellness_trends": {
    "weekly_data": [
      {
        "week": "Week 1",
        "avg_score": 73.2,
        "high_risk_count": 42
      }
    ],
    "monthly_comparison": {
      "current_month": {"avg_score": 72.3, "participation": 71.4},
      "previous_month": {"avg_score": 70.1, "participation": 68.2}
    }
  },
  "intervention_effectiveness": [
    {
      "intervention": "Flexible Work Arrangements",
      "success_rate": 78.5,
      "employees_helped": 156
    }
  ]
}
```

## 🔧 Lambda Function Details

### Function Configuration

- **Runtime**: Python 3.9
- **Timeout**: 60 seconds
- **Memory**: 1024 MB
- **Handler**: `handler.lambda_handler`

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CHECKINS_TABLE` | DynamoDB table for check-ins | `mindbridge-checkins-dev` |
| `USERS_TABLE` | DynamoDB table for users | `mindbridge-users-dev` |
| `STAGE` | Deployment stage | `dev` or `prod` |

### IAM Permissions

The Lambda function has the following permissions:
- **DynamoDB**: Read access to check-ins and users tables
- **CloudWatch Logs**: Write access for logging
- **Basic Lambda Execution**: Standard Lambda execution role

## 🎯 Frontend Integration

### HR User Detection

The system automatically detects HR users based on:
- Email domains containing 'hr.', 'people.', 'talent.'
- Specific HR email addresses

### Dashboard Access

HR users will see a toggle button in the Emotion Analytics page:
- **Personal View**: Standard emotion analytics
- **HR Dashboard**: Corporate wellness monitoring

### Component Usage

```jsx
import HRWellnessDashboard from './components/HRWellnessDashboard';

// In your component
<HRWellnessDashboard 
  userEmail={userEmail} 
  isHRUser={isHRUser} 
/>
```

## 📈 Monitoring and Troubleshooting

### CloudWatch Logs

Monitor the Lambda function in CloudWatch:
- **Log Group**: `/aws/lambda/mindbridge-hr-wellness-data-{stage}`
- **Log Stream**: Function execution logs

### Common Issues

1. **No Data Returned**
   - Check if check-ins exist in DynamoDB
   - Verify table names in environment variables
   - Check Lambda function logs

2. **CORS Errors**
   - Verify API Gateway CORS configuration
   - Check frontend origin settings

3. **Timeout Errors**
   - Increase Lambda timeout if processing large datasets
   - Optimize DynamoDB queries

4. **Permission Errors**
   - Verify IAM role permissions
   - Check DynamoDB table access

### Performance Optimization

1. **DynamoDB Queries**
   - Use GSI for efficient queries
   - Implement pagination for large datasets
   - Use batch operations where possible

2. **Lambda Optimization**
   - Increase memory for faster execution
   - Use connection pooling for DynamoDB
   - Implement caching for frequently accessed data

## 🔒 Security Considerations

1. **Data Privacy**
   - All data is anonymized in HR dashboard
   - Individual user data is not exposed
   - Access is restricted to HR users only

2. **API Security**
   - Consider implementing API key authentication
   - Add rate limiting for production use
   - Monitor API usage and costs

3. **Compliance**
   - Ensure GDPR compliance for EU users
   - Implement data retention policies
   - Regular security audits

## 📋 Maintenance

### Regular Tasks

1. **Monitor Costs**
   - Check Lambda function execution costs
   - Monitor DynamoDB read capacity
   - Review API Gateway usage

2. **Performance Monitoring**
   - Monitor Lambda function duration
   - Check error rates and logs
   - Optimize queries based on usage patterns

3. **Data Quality**
   - Verify data accuracy in HR dashboard
   - Check for missing or corrupted data
   - Validate aggregation logic

### Updates and Upgrades

1. **Lambda Function Updates**
   - Deploy new versions using CDK
   - Test thoroughly before production
   - Use blue-green deployment for zero downtime

2. **Frontend Updates**
   - Deploy frontend changes independently
   - Test HR dashboard functionality
   - Verify role-based access control

## 🎉 Success Metrics

Track the following metrics to measure success:

1. **Adoption**
   - Number of HR users accessing dashboard
   - Frequency of dashboard usage
   - User engagement metrics

2. **Impact**
   - Reduction in high-risk employees
   - Improvement in wellness scores
   - Effectiveness of interventions

3. **Technical**
   - API response times
   - Error rates
   - System availability

## 📞 Support

For issues or questions:

1. **Check CloudWatch Logs** for detailed error information
2. **Review this documentation** for common solutions
3. **Test the endpoint** using the provided test script
4. **Monitor the deployment** using AWS Console

---

**Last Updated**: January 2024
**Version**: 1.0.0 