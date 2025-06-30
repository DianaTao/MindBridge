import json
import re
import boto3
import os
from datetime import datetime, timezone
from typing import Dict, Any

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('USERS_TABLE_NAME', 'mindbridge-users-dev')
table = dynamodb.Table(table_name)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user_record(email: str) -> Dict[str, Any]:
    """Create a new user record in DynamoDB"""
    user_record = {
        'email': email,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'last_login': datetime.now(timezone.utc).isoformat(),
        'status': 'active',
        'checkin_count': 0,
        'total_duration': 0
    }
    
    try:
        table.put_item(Item=user_record)
        print(f"✅ Created user record for: {email}")
        return user_record
    except Exception as e:
        print(f"❌ Failed to create user record: {e}")
        raise

def get_user_record(email: str) -> Dict[str, Any]:
    """Get existing user record from DynamoDB"""
    try:
        response = table.get_item(Key={'email': email})
        user_record = response.get('Item')
        
        if user_record:
            # Update last login
            table.update_item(
                Key={'email': email},
                UpdateExpression='SET last_login = :last_login',
                ExpressionAttributeValues={
                    ':last_login': datetime.now(timezone.utc).isoformat()
                }
            )
            print(f"✅ Retrieved user record for: {email}")
            return user_record
        else:
            print(f"📝 No existing user record for: {email}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to get user record: {e}")
        return None

def lambda_handler(event, context):
    """Main Lambda handler for user authentication"""
    print(f"🔐 User authentication request: {json.dumps(event)}")
    
    try:
        # Parse request
        if event.get('httpMethod') == 'OPTIONS':
            # Handle CORS preflight
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        # Get email from request body
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').lower().strip()
        
        if not email:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Email is required',
                    'message': 'Please provide a valid email address'
                })
            }
        
        # Validate email format
        if not validate_email(email):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Invalid email format',
                    'message': 'Please provide a valid email address'
                })
            }
        
        # Check if user exists
        user_record = get_user_record(email)
        
        if user_record:
            # Existing user - return user info
            response_data = {
                'success': True,
                'user': {
                    'email': user_record['email'],
                    'created_at': user_record['created_at'],
                    'last_login': user_record['last_login'],
                    'checkin_count': user_record.get('checkin_count', 0),
                    'status': user_record.get('status', 'active')
                },
                'message': 'Welcome back!'
            }
        else:
            # New user - create record
            user_record = create_user_record(email)
            response_data = {
                'success': True,
                'user': {
                    'email': user_record['email'],
                    'created_at': user_record['created_at'],
                    'last_login': user_record['last_login'],
                    'checkin_count': 0,
                    'status': 'active'
                },
                'message': 'Welcome to MindBridge!'
            }
        
        print(f"✅ Authentication successful for: {email}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Authentication failed. Please try again.'
            })
        } 