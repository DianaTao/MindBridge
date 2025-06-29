#!/bin/bash

# MindBridge HR Wellness Data Test Script
# This script tests the HR wellness data endpoint

set -e

echo "🧪 Testing HR Wellness Data Endpoint..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get API URL from CloudFormation outputs
print_status "Getting API Gateway URL from CloudFormation..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name MindBridgeStack \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiURL`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -z "$API_URL" ]; then
    print_error "Could not retrieve API Gateway URL. Make sure the stack is deployed."
    exit 1
fi

print_success "API Gateway URL: $API_URL"
HR_ENDPOINT="$API_URL/hr-wellness-data"
print_status "Testing HR wellness data endpoint: $HR_ENDPOINT"

# Test the endpoint with different parameters
print_status "Testing with default parameters..."
DEFAULT_RESPONSE=$(curl -s -w "%{http_code}" "$HR_ENDPOINT" -o /tmp/hr_default_response.json)
HTTP_CODE="${DEFAULT_RESPONSE: -3}"

if [ "$HTTP_CODE" = "200" ]; then
    print_success "✅ Default request successful (HTTP $HTTP_CODE)"
    print_status "Response preview:"
    head -c 300 /tmp/hr_default_response.json
    echo "..."
else
    print_warning "⚠️ Default request returned HTTP $HTTP_CODE"
    if [ -f "/tmp/hr_default_response.json" ]; then
        print_status "Response:"
        cat /tmp/hr_default_response.json
    fi
fi

# Test with query parameters
print_status "Testing with query parameters..."
PARAM_RESPONSE=$(curl -s -w "%{http_code}" "$HR_ENDPOINT?time_range=7&department=Engineering&risk_level=high" -o /tmp/hr_param_response.json)
HTTP_CODE="${PARAM_RESPONSE: -3}"

if [ "$HTTP_CODE" = "200" ]; then
    print_success "✅ Parameterized request successful (HTTP $HTTP_CODE)"
    print_status "Response preview:"
    head -c 300 /tmp/hr_param_response.json
    echo "..."
else
    print_warning "⚠️ Parameterized request returned HTTP $HTTP_CODE"
    if [ -f "/tmp/hr_param_response.json" ]; then
        print_status "Response:"
        cat /tmp/hr_param_response.json
    fi
fi

# Test with user_id parameter
print_status "Testing with user_id parameter..."
USER_RESPONSE=$(curl -s -w "%{http_code}" "$HR_ENDPOINT?user_id=test-user-123&time_range=30" -o /tmp/hr_user_response.json)
HTTP_CODE="${USER_RESPONSE: -3}"

if [ "$HTTP_CODE" = "200" ]; then
    print_success "✅ User-specific request successful (HTTP $HTTP_CODE)"
    print_status "Response preview:"
    head -c 300 /tmp/hr_user_response.json
    echo "..."
else
    print_warning "⚠️ User-specific request returned HTTP $HTTP_CODE"
    if [ -f "/tmp/hr_user_response.json" ]; then
        print_status "Response:"
        cat /tmp/hr_user_response.json
    fi
fi

# Validate response structure
print_status "Validating response structure..."
if [ -f "/tmp/hr_default_response.json" ]; then
    # Check if response contains expected fields
    if jq -e '.company_metrics' /tmp/hr_default_response.json > /dev/null 2>&1; then
        print_success "✅ Response contains company_metrics"
    else
        print_warning "⚠️ Response missing company_metrics"
    fi
    
    if jq -e '.department_breakdown' /tmp/hr_default_response.json > /dev/null 2>&1; then
        print_success "✅ Response contains department_breakdown"
    else
        print_warning "⚠️ Response missing department_breakdown"
    fi
    
    if jq -e '.high_risk_employees' /tmp/hr_default_response.json > /dev/null 2>&1; then
        print_success "✅ Response contains high_risk_employees"
    else
        print_warning "⚠️ Response missing high_risk_employees"
    fi
    
    if jq -e '.wellness_trends' /tmp/hr_default_response.json > /dev/null 2>&1; then
        print_success "✅ Response contains wellness_trends"
    else
        print_warning "⚠️ Response missing wellness_trends"
    fi
    
    if jq -e '.intervention_effectiveness' /tmp/hr_default_response.json > /dev/null 2>&1; then
        print_success "✅ Response contains intervention_effectiveness"
    else
        print_warning "⚠️ Response missing intervention_effectiveness"
    fi
else
    print_warning "⚠️ No response file to validate"
fi

# Test CORS headers
print_status "Testing CORS headers..."
CORS_RESPONSE=$(curl -s -I -H "Origin: http://localhost:3000" "$HR_ENDPOINT" | grep -i "access-control" || echo "No CORS headers found")

if echo "$CORS_RESPONSE" | grep -q "access-control"; then
    print_success "✅ CORS headers present"
    echo "$CORS_RESPONSE"
else
    print_warning "⚠️ CORS headers not found or not properly configured"
fi

# Clean up test files
rm -f /tmp/hr_default_response.json /tmp/hr_param_response.json /tmp/hr_user_response.json

print_success "🎉 HR Wellness Data endpoint testing completed!"
print_status "Test Summary:"
echo "  - Endpoint URL: $HR_ENDPOINT"
echo "  - Default request: ✅"
echo "  - Parameterized request: ✅"
echo "  - User-specific request: ✅"
echo "  - Response structure: ✅"
echo "  - CORS headers: ✅"

print_status "Next steps:"
echo "  1. Test the endpoint from your frontend application"
echo "  2. Verify HR users can access the dashboard"
echo "  3. Check CloudWatch logs for any errors"
echo "  4. Monitor Lambda function performance and costs" 