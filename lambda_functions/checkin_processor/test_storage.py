#!/usr/bin/env python3
"""
Test script to verify data storage in DynamoDB
"""

import json
import boto3
import os
from datetime import datetime

def test_dynamodb_storage():
    """Test storing and retrieving data from DynamoDB"""
    print("🧪 TESTING DYNAMODB STORAGE")
    print("=" * 60)
    
    # Test data
    test_user_id = "test_user_storage_" + datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    test_timestamp = datetime.utcnow().isoformat()
    test_checkin_id = "test_checkin_" + datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    test_record = {
        'user_id': test_user_id,
        'timestamp': test_timestamp,
        'checkin_id': test_checkin_id,
        'session_id': 'test_session',
        'duration': 120,
        'emotion_analysis': {
            'dominant_emotion': 'happy',
            'confidence': 0.85,
            'intensity': 75
        },
        'self_assessment': {
            'mood_score': 8,
            'energy_level': 7,
            'stress_level': 3
        },
        'overall_score': 75.0,
        'llm_report': {
            'emotional_summary': 'Test report for storage verification',
            'key_insights': ['Test insight 1', 'Test insight 2'],
            'recommendations': ['Test recommendation 1', 'Test recommendation 2'],
            'mood_score': 8,
            'confidence_level': 'high'
        },
        'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)
    }
    
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Try different table names
        table_names = [
            'mindbridge-checkins-dev',
            'mindbridge-checkins',
            'mindbridge-checkins-prod'
        ]
        
        table = None
        table_name = None
        
        for name in table_names:
            try:
                print(f"🔍 Trying table: {name}")
                table = dynamodb.Table(name)
                # Try to describe the table to see if it exists
                table.load()
                table_name = name
                print(f"✅ Found table: {name}")
                break
            except Exception as e:
                print(f"❌ Table {name} not found: {str(e)}")
                continue
        
        if not table:
            print("❌ No valid table found!")
            return False
        
        # Store test record
        print(f"💾 Storing test record in {table_name}...")
        table.put_item(Item=test_record)
        print("✅ Test record stored successfully!")
        
        # Retrieve test record
        print("📥 Retrieving test record...")
        response = table.get_item(
            Key={
                'user_id': test_user_id,
                'timestamp': test_timestamp
            }
        )
        
        if 'Item' in response:
            retrieved_record = response['Item']
            print("✅ Test record retrieved successfully!")
            print(f"📝 Retrieved data: {json.dumps(retrieved_record, indent=2, default=str)}")
            
            # Clean up - delete test record
            print("🧹 Cleaning up test record...")
            table.delete_item(
                Key={
                    'user_id': test_user_id,
                    'timestamp': test_timestamp
                }
            )
            print("✅ Test record cleaned up!")
            
            return True
        else:
            print("❌ Failed to retrieve test record!")
            return False
            
    except Exception as e:
        print(f"❌ Error in storage test: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_existing_data():
    """Test if there's any existing data in the table"""
    print("\n" + "=" * 60)
    print("🔍 CHECKING FOR EXISTING DATA")
    print("=" * 60)
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('mindbridge-checkins-dev')
        
        # Scan for any data
        response = table.scan(Limit=10)
        items = response.get('Items', [])
        
        print(f"📊 Found {len(items)} existing records")
        
        if items:
            print("📝 Sample records:")
            for i, item in enumerate(items[:3]):
                print(f"  Record {i+1}:")
                print(f"    user_id: {item.get('user_id', 'N/A')}")
                print(f"    timestamp: {item.get('timestamp', 'N/A')}")
                print(f"    checkin_id: {item.get('checkin_id', 'N/A')}")
                print(f"    duration: {item.get('duration', 'N/A')}")
                print()
        else:
            print("📭 No existing data found")
            
        return len(items)
        
    except Exception as e:
        print(f"❌ Error checking existing data: {str(e)}")
        return 0

if __name__ == "__main__":
    print("🚀 DYNAMODB STORAGE VERIFICATION")
    print("=" * 60)
    
    # Test storage functionality
    storage_ok = test_dynamodb_storage()
    
    # Check existing data
    existing_count = test_existing_data()
    
    # Final result
    print("\n" + "=" * 60)
    print("📋 STORAGE TEST RESULTS")
    print("=" * 60)
    
    if storage_ok:
        print("✅ DYNAMODB STORAGE: WORKING")
        print("✅ Data can be stored and retrieved")
        print(f"📊 Existing records: {existing_count}")
        
        if existing_count == 0:
            print("⚠️  No existing data found - this explains why Emotion Analytics is empty")
            print("💡 Try completing a mental health check-in to populate the database")
        else:
            print("✅ Data exists in database")
    else:
        print("❌ DYNAMODB STORAGE: FAILED")
        print("❌ Cannot store or retrieve data")
    
    print("\n📝 NEXT STEPS:")
    print("1. Complete a mental health check-in in the frontend")
    print("2. Check if data appears in Emotion Analytics")
    print("3. Verify the Lambda function is storing data correctly") 