#!/usr/bin/env python3
"""
Script to check Lambda logs for Bedrock errors
"""

import boto3
import json
from datetime import datetime, timedelta

def check_lambda_logs():
    """Check Lambda logs for recent errors"""
    
    print("🔍 Checking Lambda logs for Bedrock errors...")
    
    try:
        # Initialize CloudWatch Logs client
        logs_client = boto3.client('logs')
        
        # Get log group name
        log_group_name = "/aws/lambda/mindbridge-checkin-processor-dev"
        
        # Get latest log stream
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            maxItems=1
        )
        
        if not streams_response['logStreams']:
            print("❌ No log streams found")
            return
            
        latest_stream = streams_response['logStreams'][0]['logStreamName']
        print(f"📋 Latest log stream: {latest_stream}")
        
        # Get recent log events (last 5 minutes)
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)
        
        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=latest_stream,
            startTime=start_time,
            endTime=end_time,
            startFromHead=False
        )
        
        print(f"\n📝 Recent log events:")
        for event in events_response['events']:
            message = event['message']
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
            
            # Look for Bedrock-related messages
            if any(keyword in message.lower() for keyword in ['bedrock', 'llm', 'model', 'error', 'exception']):
                print(f"🔍 [{timestamp}] {message}")
            elif '❌' in message or '✅' in message:
                print(f"📋 [{timestamp}] {message}")
                
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")

def check_lambda_errors():
    """Check for specific error patterns"""
    
    print("\n🔍 Checking for specific error patterns...")
    
    try:
        # Initialize CloudWatch Logs client
        logs_client = boto3.client('logs')
        
        # Search for error logs
        log_group_name = "/aws/lambda/mindbridge-checkin-processor-dev"
        
        # Search for recent error logs
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(minutes=10)).timestamp() * 1000)
        
        filter_response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_time,
            endTime=end_time,
            filterPattern='ERROR OR Exception OR "❌" OR "bedrock" OR "LLM"'
        )
        
        print(f"📊 Found {len(filter_response['events'])} relevant log events:")
        
        for event in filter_response['events']:
            message = event['message']
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
            print(f"🔍 [{timestamp}] {message}")
            
    except Exception as e:
        print(f"❌ Error filtering logs: {str(e)}")

if __name__ == "__main__":
    check_lambda_logs()
    check_lambda_errors() 