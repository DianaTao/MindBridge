#!/usr/bin/env python3
"""
Script to create sample data for any user ID dynamically
"""

import requests
import json
from datetime import datetime, timedelta
import random

def create_sample_data_for_user(user_id):
    """
    Create sample check-in data for any user ID
    """
    print(f"📤 Creating sample data for user: {user_id}")
    
    # Create multiple sample check-ins over the past 30 days
    sample_checkins = []
    
    # Generate 5-8 sample check-ins over the past 30 days
    num_checkins = random.randint(5, 8)
    
    for i in range(num_checkins):
        # Generate a random date within the past 30 days
        days_ago = random.randint(0, 30)
        checkin_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Generate random emotion data
        emotions = ['happy', 'excited', 'calm', 'focused', 'energetic', 'peaceful', 'motivated', 'relaxed']
        emotion = random.choice(emotions)
        confidence = round(random.uniform(0.7, 0.95), 2)
        intensity = random.randint(60, 90)
        
        # Generate random self-assessment
        mood_score = random.randint(6, 10)
        energy_level = random.randint(5, 9)
        stress_level = random.randint(1, 5)
        
        # Generate random duration
        duration = random.randint(30, 180)
        
        checkin_data = {
            'user_id': user_id,
            'session_id': f'sample_session_{i+1}',
            'duration': duration,
            'checkin_id': f'sample_checkin_{checkin_date.strftime("%Y%m%d_%H%M%S")}',
            'emotion_analysis': {
                'dominant_emotion': emotion,
                'confidence': confidence,
                'intensity': intensity
            },
            'self_assessment': {
                'mood_score': mood_score,
                'energy_level': energy_level,
                'stress_level': stress_level
            }
        }
        
        sample_checkins.append(checkin_data)
    
    # Submit all sample check-ins
    success_count = 0
    for i, checkin_data in enumerate(sample_checkins):
        try:
            response = requests.post(
                'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/checkin-processor',
                json=checkin_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Created check-in {i+1}/{len(sample_checkins)}")
            else:
                print(f"❌ Failed to create check-in {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating check-in {i+1}: {str(e)}")
    
    print(f"🎉 Successfully created {success_count}/{len(sample_checkins)} sample check-ins for user {user_id}")
    return success_count

def check_and_create_data_for_user(user_id):
    """
    Check if user has data, if not create sample data
    """
    print(f"🔍 Checking data for user: {user_id}")
    
    # First, check if user has any data
    try:
        response = requests.get(
            'https://wome1vjyzb.execute-api.us-east-1.amazonaws.com/prod/checkin-retriever',
            params={'user_id': user_id, 'days': 30, 'limit': 10},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            checkins = result.get('checkins', [])
            total_count = result.get('total_count', 0)
            
            print(f"📊 User {user_id} has {total_count} check-ins")
            
            if total_count == 0:
                print(f"📝 No data found for user {user_id}, creating sample data...")
                return create_sample_data_for_user(user_id)
            else:
                print(f"✅ User {user_id} already has data, no need to create sample data")
                return 0
        else:
            print(f"❌ Failed to check user data: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Error checking user data: {str(e)}")
        return 0

if __name__ == "__main__":
    print("🚀 DYNAMIC SAMPLE DATA CREATOR")
    print("=" * 60)
    
    # You can call this function with any user ID
    # For example, to create data for the current user from frontend:
    user_id = input("Enter user ID to create sample data for (or press Enter to use 'user_anauwiro9'): ").strip()
    
    if not user_id:
        user_id = "user_anauwiro9"
    
    print(f"🎯 Creating sample data for: {user_id}")
    success_count = check_and_create_data_for_user(user_id)
    
    if success_count > 0:
        print(f"\n🎉 SUCCESS! Created {success_count} sample check-ins")
        print("📊 Emotion Analytics should now show data!")
    else:
        print("\n❌ No sample data was created") 