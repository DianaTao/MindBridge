"""
Dashboard Lambda Function
Handles WebSocket connections for real-time emotion analytics dashboard
"""

import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-query')
apigateway = boto3.client('apigatewaymanagementapi')

# Environment variables
EMOTIONS_TABLE = os.environ.get('EMOTIONS_TABLE', 'mindbridge-emotions')
TIMESTREAM_DB = os.environ.get('TIMESTREAM_DB', 'MindBridge')
TIMESTREAM_TABLE = os.environ.get('TIMESTREAM_TABLE', 'emotions')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for dashboard WebSocket API
    
    Handles:
    - WebSocket connections/disconnections
    - Real-time emotion data requests
    - Analytics queries
    - Dashboard updates
    - Health check endpoint
    """
    try:
        # Check if this is an HTTP request (API Gateway) or WebSocket request
        http_method = event.get('httpMethod')
        
        if http_method == 'GET':
            # Handle HTTP GET request (health check)
            return handle_health_check()
        
        # Handle WebSocket requests
        route_key = event.get('requestContext', {}).get('routeKey', '$default')
        connection_id = event.get('requestContext', {}).get('connectionId')
        domain_name = event.get('requestContext', {}).get('domainName')
        stage = event.get('requestContext', {}).get('stage')
        
        logger.info(f"Processing route: {route_key} for connection: {connection_id}")
        
        # Initialize API Gateway Management API client with endpoint
        if domain_name and stage:
            global apigateway
            apigateway = boto3.client(
                'apigatewaymanagementapi',
                endpoint_url=f"https://{domain_name}/{stage}"
            )
        
        if route_key == '$connect':
            return handle_connect(connection_id)
        elif route_key == '$disconnect':
            return handle_disconnect(connection_id)
        elif route_key == '$default':
            return handle_message(event, connection_id)
        else:
            return handle_custom_route(event, connection_id, route_key)
        
    except Exception as e:
        logger.error(f"Error processing dashboard request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_connect(connection_id: str) -> Dict[str, Any]:
    """
    Handle new WebSocket connection
    """
    try:
        logger.info(f"New connection established: {connection_id}")
        
        # Store connection information (could be enhanced with user authentication)
        # For now, just log the connection
        
        return {'statusCode': 200}
        
    except Exception as e:
        logger.error(f"Error handling connection: {str(e)}")
        return {'statusCode': 500}

def handle_disconnect(connection_id: str) -> Dict[str, Any]:
    """
    Handle WebSocket disconnection
    """
    try:
        logger.info(f"Connection disconnected: {connection_id}")
        
        # Clean up any connection-specific resources
        
        return {'statusCode': 200}
        
    except Exception as e:
        logger.error(f"Error handling disconnection: {str(e)}")
        return {'statusCode': 500}

def handle_message(event: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
    """
    Handle incoming WebSocket messages
    """
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'unknown')
        
        logger.info(f"Processing action: {action} for connection: {connection_id}")
        
        if action == 'get_current_state':
            response = get_current_emotion_state(body)
        elif action == 'get_historical_data':
            response = get_historical_emotions(body)
        elif action == 'get_analytics':
            response = get_emotion_analytics(body)
        elif action == 'get_session_summary':
            response = get_session_summary(body)
        else:
            response = {'error': f'Unknown action: {action}'}
        
        # Send response back to client
        send_message_to_connection(connection_id, response)
        
        return {'statusCode': 200}
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        return {'statusCode': 500}

def handle_custom_route(event: Dict[str, Any], connection_id: str, route_key: str) -> Dict[str, Any]:
    """
    Handle custom WebSocket routes
    """
    try:
        logger.info(f"Processing custom route: {route_key}")
        
        response = {'message': f'Processed route: {route_key}'}
        send_message_to_connection(connection_id, response)
        
        return {'statusCode': 200}
        
    except Exception as e:
        logger.error(f"Error handling custom route: {str(e)}")
        return {'statusCode': 500}

def get_current_emotion_state(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the most recent emotion analysis for a user/session
    """
    try:
        user_id = request.get('user_id', 'anonymous')
        session_id = request.get('session_id', 'default')
        
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        # Query most recent unified emotion state
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            FilterExpression='session_id = :session_id AND modality = :modality',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':session_id': session_id,
                ':modality': 'unified'
            },
            ScanIndexForward=False,  # Most recent first
            Limit=1
        )
        
        if response['Items']:
            latest_emotion = response['Items'][0]
            emotion_data = latest_emotion.get('emotion_data', {})
            
            return {
                'action': 'current_state',
                'data': {
                    'user_id': user_id,
                    'session_id': session_id,
                    'emotion_state': emotion_data.get('unified_emotion', {}),
                    'recommendations': emotion_data.get('recommendations', {}),
                    'timestamp': latest_emotion.get('timestamp'),
                    'confidence': emotion_data.get('unified_emotion', {}).get('confidence', 0.5)
                }
            }
        else:
            return {
                'action': 'current_state',
                'data': {
                    'emotion': 'neutral',
                    'confidence': 0.0,
                    'message': 'No recent emotion data available'
                }
            }
        
    except Exception as e:
        logger.error(f"Error getting current emotion state: {str(e)}")
        return {'error': str(e)}

def get_historical_emotions(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get historical emotion data from TimeStream
    """
    try:
        user_id = request.get('user_id', 'anonymous')
        timeframe = request.get('timeframe', '1h')  # 1h, 1d, 1w
        
        # Build TimeStream query based on timeframe
        if timeframe == '1h':
            query = f"""
            SELECT time, emotion, intensity, confidence
            FROM "{TIMESTREAM_DB}"."{TIMESTREAM_TABLE}" 
            WHERE user_id = '{user_id}' AND time >= ago(1h)
            ORDER BY time DESC
            LIMIT 100
            """
        elif timeframe == '1d':
            query = f"""
            SELECT bin(time, 1h) as hour, 
                   avg(intensity) as avg_intensity,
                   mode(emotion) as dominant_emotion,
                   avg(confidence) as avg_confidence
            FROM "{TIMESTREAM_DB}"."{TIMESTREAM_TABLE}" 
            WHERE user_id = '{user_id}' AND time >= ago(1d)
            GROUP BY bin(time, 1h)
            ORDER BY hour DESC
            """
        elif timeframe == '1w':
            query = f"""
            SELECT bin(time, 1d) as day, 
                   avg(intensity) as avg_intensity,
                   mode(emotion) as dominant_emotion,
                   count(*) as data_points
            FROM "{TIMESTREAM_DB}"."{TIMESTREAM_TABLE}" 
            WHERE user_id = '{user_id}' AND time >= ago(7d)
            GROUP BY bin(time, 1d)
            ORDER BY day DESC
            """
        else:
            return {'error': 'Invalid timeframe. Use 1h, 1d, or 1w'}
        
        # Execute TimeStream query
        response = timestream.query(QueryString=query)
        
        # Parse results
        emotions_data = parse_timestream_response(response)
        
        return {
            'action': 'historical_data',
            'data': {
                'timeframe': timeframe,
                'user_id': user_id,
                'data_points': len(emotions_data),
                'emotions': emotions_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting historical emotions: {str(e)}")
        return {'error': str(e)}

def get_emotion_analytics(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get emotion analytics and insights
    """
    try:
        user_id = request.get('user_id', 'anonymous')
        
        # Get emotion distribution over last 24 hours
        query = f"""
        SELECT emotion, 
               count(*) as frequency,
               avg(intensity) as avg_intensity,
               avg(confidence) as avg_confidence
        FROM "{TIMESTREAM_DB}"."{TIMESTREAM_TABLE}" 
        WHERE user_id = '{user_id}' AND time >= ago(24h)
        GROUP BY emotion
        ORDER BY frequency DESC
        """
        
        response = timestream.query(QueryString=query)
        distribution_data = parse_timestream_response(response)
        
        # Get emotion trends
        trend_query = f"""
        SELECT bin(time, 2h) as time_bucket,
               avg(intensity) as avg_intensity,
               mode(emotion) as dominant_emotion
        FROM "{TIMESTREAM_DB}"."{TIMESTREAM_TABLE}" 
        WHERE user_id = '{user_id}' AND time >= ago(24h)
        GROUP BY bin(time, 2h)
        ORDER BY time_bucket ASC
        """
        
        trend_response = timestream.query(QueryString=trend_query)
        trend_data = parse_timestream_response(trend_response)
        
        # Calculate insights
        insights = calculate_emotion_insights(distribution_data, trend_data)
        
        return {
            'action': 'analytics',
            'data': {
                'user_id': user_id,
                'emotion_distribution': distribution_data,
                'emotion_trends': trend_data,
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting emotion analytics: {str(e)}")
        return {'error': str(e)}

def get_session_summary(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get summary of a specific session
    """
    try:
        user_id = request.get('user_id', 'anonymous')
        session_id = request.get('session_id', 'default')
        
        table = dynamodb.Table(EMOTIONS_TABLE)
        
        # Get all emotion data for this session
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            FilterExpression='session_id = :session_id',
            ExpressionAttributeValues={
                ':user_id': user_id,
                ':session_id': session_id
            }
        )
        
        session_emotions = response['Items']
        
        if not session_emotions:
            return {
                'action': 'session_summary',
                'data': {'message': 'No data found for this session'}
            }
        
        # Analyze session data
        session_analysis = analyze_session_emotions(session_emotions)
        
        return {
            'action': 'session_summary',
            'data': {
                'user_id': user_id,
                'session_id': session_id,
                'analysis': session_analysis,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting session summary: {str(e)}")
        return {'error': str(e)}

def parse_timestream_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse TimeStream query response into readable format
    """
    try:
        columns = [col['Name'] for col in response['ColumnInfo']]
        rows = []
        
        for row in response['Rows']:
            row_data = {}
            for i, cell in enumerate(row['Data']):
                column_name = columns[i]
                
                # Extract value based on data type
                if 'ScalarValue' in cell:
                    value = cell['ScalarValue']
                    # Try to convert numeric values
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass  # Keep as string
                else:
                    value = None
                
                row_data[column_name] = value
            
            rows.append(row_data)
        
        return rows
        
    except Exception as e:
        logger.error(f"Error parsing TimeStream response: {str(e)}")
        return []

def calculate_emotion_insights(distribution_data: List[Dict[str, Any]], 
                              trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate insights from emotion data
    """
    try:
        insights = {
            'dominant_emotion': 'neutral',
            'emotion_variability': 'stable',
            'average_intensity': 5.0,
            'recommendations': []
        }
        
        if distribution_data:
            # Find dominant emotion
            dominant = max(distribution_data, key=lambda x: x.get('frequency', 0))
            insights['dominant_emotion'] = dominant.get('emotion', 'neutral')
            
            # Calculate average intensity
            total_intensity = sum(item.get('avg_intensity', 0) * item.get('frequency', 0) 
                                for item in distribution_data)
            total_frequency = sum(item.get('frequency', 0) for item in distribution_data)
            
            if total_frequency > 0:
                insights['average_intensity'] = round(total_intensity / total_frequency, 1)
        
        if trend_data and len(trend_data) > 1:
            # Analyze emotion variability
            intensities = [item.get('avg_intensity', 5.0) for item in trend_data]
            intensity_range = max(intensities) - min(intensities)
            
            if intensity_range > 3.0:
                insights['emotion_variability'] = 'high'
            elif intensity_range > 1.5:
                insights['emotion_variability'] = 'moderate'
            else:
                insights['emotion_variability'] = 'stable'
        
        # Generate basic recommendations
        if insights['dominant_emotion'] in ['sad', 'angry', 'frustrated']:
            insights['recommendations'].append('Consider stress management techniques')
        if insights['average_intensity'] > 7.0:
            insights['recommendations'].append('High emotional intensity detected - consider taking breaks')
        if insights['emotion_variability'] == 'high':
            insights['recommendations'].append('Emotional variability is high - mindfulness may help')
        
        return insights
        
    except Exception as e:
        logger.error(f"Error calculating insights: {str(e)}")
        return {'error': 'Could not calculate insights'}

def analyze_session_emotions(session_emotions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze emotions for a specific session
    """
    try:
        analysis = {
            'total_data_points': len(session_emotions),
            'modalities_used': set(),
            'emotion_progression': [],
            'session_summary': 'stable'
        }
        
        # Group by modality
        for emotion_item in session_emotions:
            modality = emotion_item.get('modality', 'unknown')
            analysis['modalities_used'].add(modality)
            
            if modality == 'unified':
                emotion_data = emotion_item.get('emotion_data', {})
                unified_emotion = emotion_data.get('unified_emotion', {})
                
                analysis['emotion_progression'].append({
                    'timestamp': emotion_item.get('timestamp'),
                    'emotion': unified_emotion.get('unified_emotion', 'neutral'),
                    'intensity': unified_emotion.get('intensity', 5),
                    'confidence': unified_emotion.get('confidence', 0.5)
                })
        
        # Convert set to list for JSON serialization
        analysis['modalities_used'] = list(analysis['modalities_used'])
        
        # Determine session summary
        if analysis['emotion_progression']:
            intensities = [item['intensity'] for item in analysis['emotion_progression']]
            avg_intensity = sum(intensities) / len(intensities)
            
            if avg_intensity > 7:
                analysis['session_summary'] = 'high_intensity'
            elif avg_intensity < 3:
                analysis['session_summary'] = 'low_energy'
            else:
                analysis['session_summary'] = 'balanced'
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing session emotions: {str(e)}")
        return {'error': 'Could not analyze session'}

def send_message_to_connection(connection_id: str, message: Dict[str, Any]) -> None:
    """
    Send message to a specific WebSocket connection
    """
    try:
        apigateway.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        logger.info(f"Message sent to connection {connection_id}")
        
    except apigateway.exceptions.GoneException:
        logger.warning(f"Connection {connection_id} is no longer available")
    except Exception as e:
        logger.error(f"Error sending message to connection {connection_id}: {str(e)}") 

def handle_health_check() -> Dict[str, Any]:
    """
    Handle health check endpoint
    """
    try:
        logger.info("🔍 Health check request received")
        
        # Check if all handlers are available
        handlers_status = {
            "video": True,
            "audio": True, 
            "text": True,
            "fusion": True,
            "dashboard": True
        }
        
        # Prepare response
        response_data = {
            "service": "MindBridge AI",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "handlers": handlers_status,
            "version": "1.0.0",
            "environment": os.environ.get('STAGE', 'dev')
        }
        
        logger.info("✅ Health check completed successfully")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type", 
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            "body": json.dumps({
                "service": "MindBridge AI",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        } 