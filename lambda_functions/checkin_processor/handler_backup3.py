"""
Mental Health Check-in Processor Lambda Function
Stores check-in data and generates LLM-powered reports
"""

import json
import boto3
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
try:
    dynamodb = boto3.resource('dynamodb')
    logger.info("✅ DynamoDB client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize DynamoDB client: {str(e)}")
    dynamodb = None

try:
    bedrock = boto3.client('bedrock-runtime')
    logger.info("✅ Bedrock client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Bedrock client: {str(e)}")
    bedrock = None

# Environment variables
CHECKINS_TABLE = os.environ.get('CHECKINS_TABLE', 'mindbridge-checkins')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for mental health check-in processing
    
    Trigger: API Gateway (check-in submissions)
    Purpose: Store check-in data and generate LLM reports
    """
    try:
        logger.info("=" * 60)
        logger.info("🧠 MENTAL HEALTH CHECK-IN PROCESSOR STARTED")
        logger.info("=" * 60)
        logger.info(f"Request ID: {event.get('requestContext', {}).get('requestId')}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return create_cors_response()
        
        # Parse request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        try:
            request_data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {str(e)}")
            return create_error_response(400, "Invalid JSON format")
        
        # Process the check-in
        result = process_checkin(request_data)
        
        logger.info(f"✅ SUCCESS: Check-in processed successfully")
        logger.info("=" * 60)
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"❌ ERROR in check-in processing: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Check-in processing failed: {str(e)}")

def process_checkin(checkin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process mental health check-in data
    """
    try:
        logger.info("🔍 Processing check-in data...")
        
        # Extract check-in information
        checkin_id = checkin_data.get('checkin_id', f"checkin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        user_id = checkin_data.get('user_id', 'anonymous')
        session_id = checkin_data.get('session_id', 'default')
        duration = checkin_data.get('duration', 0)
        emotion_analysis = checkin_data.get('emotion_analysis', {})
        self_assessment = checkin_data.get('self_assessment', {})
        
        # Generate timestamp for consistency
        timestamp = datetime.utcnow().isoformat()
        
        # Store check-in data in DynamoDB
        store_checkin_data(checkin_id, user_id, session_id, duration, emotion_analysis, self_assessment, timestamp)
        
        # Generate LLM report
        llm_report = generate_llm_report(checkin_data)
        
        # Store the report
        store_llm_report(checkin_id, llm_report, user_id, timestamp)
        
        return {
            'checkin_id': checkin_id,
            'status': 'completed',
            'llm_report': llm_report,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing check-in: {str(e)}")
        raise

def store_checkin_data(checkin_id: str, user_id: str, session_id: str, duration: int, 
                      emotion_analysis: Dict[str, Any], self_assessment: Dict[str, Any], timestamp: str) -> None:
    """
    Store check-in data in DynamoDB
    """
    try:
        logger.info(f"🔍 Attempting to store check-in data...")
        logger.info(f"📋 Table name: {CHECKINS_TABLE}")
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"🆔 Check-in ID: {checkin_id}")
        
        if dynamodb is None:
            logger.error("❌ DynamoDB client not available")
            raise Exception("DynamoDB client not initialized")
        
        logger.info("✅ DynamoDB client is available")
        table = dynamodb.Table(CHECKINS_TABLE)
        logger.info(f"✅ DynamoDB table reference obtained: {table.name}")
        
        record = {
            'user_id': user_id,  # Partition key
            'timestamp': timestamp,  # Sort key
            'checkin_id': checkin_id,  # Regular attribute
            'session_id': session_id,
            'duration': duration,
            'emotion_analysis': emotion_analysis,
            'self_assessment': self_assessment,
            'overall_score': calculate_overall_score(emotion_analysis, self_assessment),
            'ttl': int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)  # 1 year TTL
        }
        
        logger.info(f"📝 Record to store: {json.dumps(record, default=str)}")
        logger.info("💾 Attempting to put item in DynamoDB...")
        
        table.put_item(Item=record)
        logger.info(f"✅ Check-in data stored successfully: {checkin_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to store check-in data: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def generate_llm_report(checkin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate LLM-powered mental health report
    """
    try:
        logger.info("🤖 Generating LLM report...")
        
        # Prepare data for LLM analysis
        emotion_analysis = checkin_data.get('emotion_analysis', {})
        self_assessment = checkin_data.get('self_assessment', {})
        duration = checkin_data.get('duration', 0)
        
        # Create prompt for LLM
        prompt = create_llm_prompt(emotion_analysis, self_assessment, duration)
        
        # Call Bedrock for LLM analysis
        try:
            if bedrock is None:
                logger.warning("⚠️ Bedrock client not available, using fallback report")
                report = generate_fallback_report(emotion_analysis, self_assessment)
            else:
                logger.info(f"🔗 Calling Bedrock with model: {BEDROCK_MODEL_ID}")
                response = bedrock.invoke_model(
                    modelId=BEDROCK_MODEL_ID,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    })
                )
                
                response_body = json.loads(response.get('body').read())
                llm_content = response_body['content'][0]['text']
                
                # Parse LLM response
                report = parse_llm_response(llm_content)
            
        except Exception as e:
            logger.warning(f"⚠️ LLM call failed: {str(e)}, using fallback report")
            report = generate_fallback_report(emotion_analysis, self_assessment)
        
        logger.info("✅ LLM report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"❌ Error generating LLM report: {str(e)}")
        # Always return fallback report instead of failing
        return generate_fallback_report(checkin_data.get('emotion_analysis', {}), checkin_data.get('self_assessment', {}))

def create_llm_prompt(emotion_analysis: Dict[str, Any], self_assessment: Dict[str, Any], duration: int) -> str:
    """
    Create prompt for LLM analysis
    """
    prompt = f"""
You are a compassionate mental health AI assistant. Analyze the following mental health check-in data and provide a comprehensive, empathetic report.

CHECK-IN DATA:
- Session Duration: {duration} seconds
- Emotion Analysis: {json.dumps(emotion_analysis, indent=2)}
- Self Assessment: {json.dumps(self_assessment, indent=2)}

Please provide a structured report with the following sections:

1. EMOTIONAL SUMMARY (2-3 sentences)
2. KEY INSIGHTS (3-4 bullet points)
3. WELLNESS RECOMMENDATIONS (3-4 actionable suggestions)
4. TREND ANALYSIS (if applicable)
5. OVERALL ASSESSMENT (1-2 sentences)

Be empathetic, supportive, and provide practical advice. Focus on positive aspects while acknowledging any concerns.

Respond in JSON format:
{{
    "emotional_summary": "brief emotional state summary",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "trend_analysis": "trend description if applicable",
    "overall_assessment": "overall assessment",
    "mood_score": 1-10,
    "confidence_level": "high/medium/low"
}}
"""
    return prompt

def parse_llm_response(llm_content: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured report
    """
    try:
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', llm_content, re.DOTALL)
        if json_match:
            report = json.loads(json_match.group())
        else:
            # Fallback parsing
            report = {
                "emotional_summary": "Analysis completed successfully",
                "key_insights": ["Emotional patterns detected", "Wellness factors identified"],
                "recommendations": ["Continue monitoring", "Practice self-care"],
                "trend_analysis": "Baseline established",
                "overall_assessment": "Positive engagement with mental health check-in",
                "mood_score": 7,
                "confidence_level": "medium"
            }
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Error parsing LLM response: {str(e)}")
        return generate_fallback_report({}, {})

def generate_fallback_report(emotion_analysis: Dict[str, Any], self_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate fallback report when LLM is unavailable
    """
    return {
        "emotional_summary": "Mental health check-in completed successfully. Your engagement with self-care is positive.",
        "key_insights": [
            "Regular check-ins help track emotional patterns",
            "Self-awareness is key to mental wellness",
            "Consistent monitoring supports emotional health"
        ],
        "recommendations": [
            "Continue with regular mental health check-ins",
            "Practice mindfulness or meditation",
            "Maintain healthy sleep and exercise routines",
            "Consider talking to a mental health professional if needed"
        ],
        "trend_analysis": "Establishing baseline for future comparisons",
        "overall_assessment": "Good engagement with mental health monitoring",
        "mood_score": 7,
        "confidence_level": "medium",
        "fallback_generated": True
    }

def calculate_overall_score(emotion_analysis: Dict[str, Any], self_assessment: Dict[str, Any]) -> float:
    """
    Calculate overall wellness score
    """
    try:
        # Emotion analysis score (0-100)
        emotion_score = emotion_analysis.get('average_wellbeing', 50)
        
        # Self-assessment score (0-100)
        assessment_score = 0
        if self_assessment:
            scores = [
                self_assessment.get('overall_mood', 5) * 10,
                self_assessment.get('energy_level', 5) * 10,
                self_assessment.get('stress_level', 5) * 10,
                self_assessment.get('sleep_quality', 5) * 10,
                self_assessment.get('social_connection', 5) * 10,
                self_assessment.get('motivation', 5) * 10
            ]
            assessment_score = sum(scores) / len(scores)
        
        # Weighted average (60% emotion, 40% self-assessment)
        overall_score = (emotion_score * 0.6) + (assessment_score * 0.4)
        
        return round(overall_score, 1)
        
    except Exception as e:
        logger.error(f"❌ Error calculating overall score: {str(e)}")
        return 50.0

def store_llm_report(checkin_id: str, llm_report: Dict[str, Any], user_id: str, timestamp: str) -> None:
    """
    Store LLM report in DynamoDB
    """
    try:
        logger.info(f"🔍 Attempting to store LLM report...")
        logger.info(f"📋 Table name: {CHECKINS_TABLE}")
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"🆔 Check-in ID: {checkin_id}")
        
        if dynamodb is None:
            logger.error("❌ DynamoDB client not available for LLM report storage")
            return
            
        table = dynamodb.Table(CHECKINS_TABLE)
        logger.info(f"✅ DynamoDB table reference obtained for LLM report: {table.name}")
        
        # Update the check-in record with LLM report using correct key structure
        logger.info("💾 Attempting to update item with LLM report...")
        table.update_item(
            Key={'user_id': user_id, 'timestamp': timestamp},
            UpdateExpression='SET llm_report = :report',
            ExpressionAttributeValues={':report': llm_report}
        )
        
        logger.info(f"✅ LLM report stored successfully for check-in: {checkin_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to store LLM report: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create success response with CORS headers
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create error response with CORS headers
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

def create_cors_response() -> Dict[str, Any]:
    """
    Create CORS preflight response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': ''
    } 