#!/bin/bash

# MindBridge Local Test Script
# This script tests the local development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 MindBridge Local Test${NC}"
echo -e "${BLUE}========================${NC}"
echo ""

# Function to test API endpoint
test_api() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    
    echo -e "${BLUE}Testing $method $endpoint...${NC}"
    
    if [ "$method" = "POST" ] && [ ! -z "$data" ]; then
        response=$(curl -s -X POST "http://localhost:3001$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo "{}")
    else
        response=$(curl -s "http://localhost:3001$endpoint" 2>/dev/null || echo "{}")
    fi
    
    if [ "$response" != "{}" ]; then
        echo -e "${GREEN}✅ Success${NC}"
        echo "Response: $response" | head -c 200
        echo "..."
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
    echo ""
}

# Function to test frontend
test_frontend() {
    echo -e "${BLUE}Testing frontend...${NC}"
    
    if curl -s "http://localhost:3000" >/dev/null; then
        echo -e "${GREEN}✅ Frontend is running${NC}"
    else
        echo -e "${RED}❌ Frontend is not running${NC}"
        echo "Start frontend with: cd frontend && npm start"
    fi
    echo ""
}

# Main test logic
main() {
    echo "Testing local MindBridge development environment..."
    echo ""
    
    # Test API endpoints
    echo -e "${YELLOW}Testing API Endpoints:${NC}"
    test_api "/health"
    test_api "/test"
    
    # Test video analysis endpoint
    test_api "/video-analysis" "POST" '{
        "frame_data": "test-base64-data",
        "user_id": "test-user",
        "session_id": "test-session"
    }'
    
    # Test audio analysis endpoint
    test_api "/audio-analysis" "POST" '{
        "audio_data": "test-base64-data",
        "user_id": "test-user",
        "session_id": "test-session"
    }'
    
    # Test emotion fusion endpoint
    test_api "/emotion-fusion" "POST" '{
        "user_id": "test-user",
        "session_id": "test-session"
    }'
    
    # Test dashboard endpoint
    test_api "/dashboard/analytics" "POST" '{
        "user_id": "test-user",
        "session_id": "test-session"
    }'
    
    # Test frontend
    echo -e "${YELLOW}Testing Frontend:${NC}"
    test_frontend
    
    echo -e "${GREEN}🎉 Local test complete!${NC}"
    echo ""
    echo "If all tests passed, your local environment is working correctly."
    echo "You can now:"
    echo "1. Open http://localhost:3001 in your browser"
    echo "2. Test the emotion analysis features"
    echo "3. Proceed with AWS deployment using scripts/setup-aws.sh"
}

# Run main function
main "$@" 