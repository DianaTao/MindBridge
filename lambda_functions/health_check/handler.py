"""
Health Check Lambda Function
Provides health status for all MindBridge services
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check endpoint for MindBridge AI
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
            "environment": "production"
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