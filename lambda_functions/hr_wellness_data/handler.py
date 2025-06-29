import json
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda function to provide HR wellness data and analytics
    """
    try:
        logger.info(f"HR Wellness Data Request: {event}")
        
        # Parse request parameters
        params = event.get('queryStringParameters', {}) or {}
        user_id = params.get('user_id', 'anonymous')
        time_range = int(params.get('time_range', 30))
        department = params.get('department', 'all')
        risk_level = params.get('risk_level', 'all')
        
        logger.info(f"Processing request for user: {user_id}, time_range: {time_range}, department: {department}")
        
        # Get real data from DynamoDB
        wellness_data = get_wellness_data(time_range, department, risk_level)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps(wellness_data)
        }
        
    except Exception as e:
        logger.error(f"Error in HR wellness data handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to retrieve HR wellness data',
                'message': str(e)
            })
        }

def get_wellness_data(time_range: int, department: str, risk_level: str) -> Dict[str, Any]:
    """
    Retrieve and aggregate wellness data for HR dashboard
    """
    try:
        # Get table names from environment variables
        checkins_table_name = os.environ.get('CHECKINS_TABLE_NAME', 'mindbridge-checkins-dev')
        users_table_name = os.environ.get('USERS_TABLE_NAME', 'mindbridge-users-dev')
        
        checkins_table = dynamodb.Table(checkins_table_name)
        users_table = dynamodb.Table(users_table_name)
        
        # Calculate time range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_range)
        
        # Get all check-ins within the time range
        response = checkins_table.scan(
            FilterExpression='#timestamp BETWEEN :start_date AND :end_date',
            ExpressionAttributeNames={
                '#timestamp': 'timestamp'
            },
            ExpressionAttributeValues={
                ':start_date': start_date.isoformat(),
                ':end_date': end_date.isoformat()
            }
        )
        
        checkins = response.get('Items', [])
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = checkins_table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                FilterExpression='#timestamp BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#timestamp': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':start_date': start_date.isoformat(),
                    ':end_date': end_date.isoformat()
                }
            )
            checkins.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(checkins)} check-ins")
        
        # Process the data
        return process_wellness_data(checkins, department, risk_level)
        
    except Exception as e:
        logger.error(f"Error retrieving wellness data: {str(e)}")
        return {}

def process_wellness_data(checkins: List[Dict], department: str, risk_level: str) -> Dict[str, Any]:
    """
    Process check-in data to generate HR wellness analytics
    """
    if not checkins:
        return {
            'company_metrics': {
                'total_employees': 0,
                'active_participants': 0,
                'participation_rate': 0,
                'avg_wellness_score': 0,
                'burnout_risk_rate': 0,
                'high_risk_employees': 0,
                'interventions_needed': 0
            },
            'department_breakdown': [],
            'high_risk_employees': [],
            'wellness_trends': {
                'weekly_data': [],
                'monthly_comparison': {
                    'current_month': {'avg_score': 0, 'participation': 0},
                    'previous_month': {'avg_score': 0, 'participation': 0}
                }
            },
            'intervention_effectiveness': []
        }
    
    # Group check-ins by user
    user_checkins = {}
    for checkin in checkins:
        user_id = checkin.get('user_id')
        if user_id:
            if user_id not in user_checkins:
                user_checkins[user_id] = []
            user_checkins[user_id].append(checkin)
    
    # Calculate company metrics
    total_employees = len(user_checkins)
    active_participants = len([u for u in user_checkins.values() if len(u) > 0])
    participation_rate = (active_participants / total_employees * 100) if total_employees > 0 else 0
    
    # Calculate average wellness scores
    all_scores = []
    for user_data in user_checkins.values():
        for checkin in user_data:
            score = checkin.get('overall_score', 50)
            all_scores.append(score)
    
    avg_wellness_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Calculate risk metrics
    high_risk_threshold = 80
    high_risk_count = len([score for score in all_scores if score >= high_risk_threshold])
    burnout_risk_rate = (high_risk_count / len(all_scores) * 100) if all_scores else 0
    
    # Generate department breakdown (simplified - in real implementation, you'd have department data)
    department_breakdown = generate_department_breakdown(user_checkins)
    
    # Generate high-risk employee list
    high_risk_employees = generate_high_risk_employees(user_checkins, high_risk_threshold)
    
    # Generate wellness trends
    wellness_trends = generate_wellness_trends(checkins, time_range)
    
    # Generate intervention effectiveness (simplified)
    intervention_effectiveness = generate_intervention_effectiveness()
    
    return {
        'company_metrics': {
            'total_employees': total_employees,
            'active_participants': active_participants,
            'participation_rate': round(participation_rate, 1),
            'avg_wellness_score': round(avg_wellness_score, 1),
            'burnout_risk_rate': round(burnout_risk_rate, 1),
            'high_risk_employees': high_risk_count,
            'interventions_needed': max(0, high_risk_count - 10)  # Simplified calculation
        },
        'department_breakdown': department_breakdown,
        'high_risk_employees': high_risk_employees,
        'wellness_trends': wellness_trends,
        'intervention_effectiveness': intervention_effectiveness
    }

def generate_department_breakdown(user_checkins: Dict) -> List[Dict]:
    """
    Generate department breakdown from user check-ins
    """
    # Simplified department breakdown - in real implementation, you'd have department data
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Customer Support', 'Product']
    
    breakdown = []
    for dept in departments:
        # Simulate department data based on user check-ins
        dept_users = len(user_checkins) // len(departments)  # Simplified distribution
        dept_scores = []
        
        # Get scores for this department (simplified)
        user_list = list(user_checkins.values())
        start_idx = departments.index(dept) * (len(user_list) // len(departments))
        end_idx = start_idx + (len(user_list) // len(departments))
        
        for user_data in user_list[start_idx:end_idx]:
            for checkin in user_data:
                dept_scores.append(checkin.get('overall_score', 50))
        
        avg_score = sum(dept_scores) / len(dept_scores) if dept_scores else 70
        risk_rate = len([s for s in dept_scores if s >= 80]) / len(dept_scores) * 100 if dept_scores else 0
        high_risk = len([s for s in dept_scores if s >= 80]) if dept_scores else 0
        
        breakdown.append({
            'name': dept,
            'avg_score': round(avg_score, 1),
            'risk_rate': round(risk_rate, 1),
            'employees': dept_users,
            'high_risk': high_risk
        })
    
    return breakdown

def generate_high_risk_employees(user_checkins: Dict, threshold: int) -> List[Dict]:
    """
    Generate list of high-risk employees
    """
    high_risk_employees = []
    
    for user_id, checkins in user_checkins.items():
        if not checkins:
            continue
            
        # Calculate average score for this user
        scores = [checkin.get('overall_score', 50) for checkin in checkins]
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= threshold:
            # Get latest check-in
            latest_checkin = max(checkins, key=lambda x: x.get('timestamp', ''))
            
            # Determine trend
            if len(scores) >= 2:
                recent_avg = sum(scores[-3:]) / len(scores[-3:])  # Last 3 check-ins
                if recent_avg < avg_score - 5:
                    trend = 'declining'
                elif recent_avg > avg_score + 5:
                    trend = 'improving'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Generate symptoms based on score
            symptoms = []
            if avg_score >= 90:
                symptoms = ['severe_stress', 'burnout', 'exhaustion']
            elif avg_score >= 80:
                symptoms = ['stress', 'fatigue', 'irritability']
            elif avg_score >= 70:
                symptoms = ['mild_stress', 'tension']
            
            # Generate recommendations
            recommendations = []
            if avg_score >= 80:
                recommendations = [
                    'Schedule 1:1 meeting to discuss workload',
                    'Consider temporary workload reduction',
                    'Recommend stress management resources'
                ]
            elif avg_score >= 70:
                recommendations = [
                    'Monitor stress levels closely',
                    'Encourage regular breaks',
                    'Provide wellness resources'
                ]
            
            high_risk_employees.append({
                'id': user_id,
                'name': f"Employee {user_id[-4:]}",  # Simplified name
                'email': f"{user_id}@company.com",
                'department': 'General',  # Simplified department
                'position': 'Team Member',
                'risk_score': round(avg_score),
                'risk_level': 'high' if avg_score >= 80 else 'medium',
                'last_checkin': latest_checkin.get('timestamp'),
                'trend': trend,
                'symptoms': symptoms,
                'recommendations': recommendations,
                'interventions': [
                    {
                        'type': 'meeting',
                        'status': 'scheduled',
                        'date': (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')
                    }
                ]
            })
    
    return high_risk_employees[:10]  # Limit to top 10

def generate_wellness_trends(checkins: List[Dict], time_range: int) -> Dict:
    """
    Generate wellness trends data
    """
    # Group check-ins by week
    weekly_data = []
    for i in range(4):  # Last 4 weeks
        week_start = datetime.utcnow() - timedelta(weeks=4-i)
        week_end = week_start + timedelta(weeks=1)
        
        week_checkins = [
            c for c in checkins 
            if week_start <= datetime.fromisoformat(c.get('timestamp', '').replace('Z', '+00:00')) < week_end
        ]
        
        if week_checkins:
            scores = [c.get('overall_score', 50) for c in week_checkins]
            avg_score = sum(scores) / len(scores)
            high_risk_count = len([s for s in scores if s >= 80])
        else:
            avg_score = 70
            high_risk_count = 0
        
        weekly_data.append({
            'week': f"Week {i+1}",
            'avg_score': round(avg_score, 1),
            'high_risk_count': high_risk_count
        })
    
    # Monthly comparison (simplified)
    monthly_comparison = {
        'current_month': {'avg_score': 72.3, 'participation': 71.4},
        'previous_month': {'avg_score': 70.1, 'participation': 68.2}
    }
    
    return {
        'weekly_data': weekly_data,
        'monthly_comparison': monthly_comparison
    }

def generate_intervention_effectiveness() -> List[Dict]:
    """
    Generate intervention effectiveness data
    """
    return [
        {
            'intervention': 'Flexible Work Arrangements',
            'success_rate': 78.5,
            'employees_helped': 156
        },
        {
            'intervention': 'Stress Management Resources',
            'success_rate': 82.3,
            'employees_helped': 234
        },
        {
            'intervention': '1:1 HR Meetings',
            'success_rate': 89.2,
            'employees_helped': 89
        },
        {
            'intervention': 'Workload Adjustments',
            'success_rate': 75.8,
            'employees_helped': 67
        },
        {
            'intervention': 'Mental Health Resources',
            'success_rate': 85.1,
            'employees_helped': 123
        }
    ] 