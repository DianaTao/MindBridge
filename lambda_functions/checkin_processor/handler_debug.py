import json
import logging
import os
import boto3
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        logger.info("🔍 DEBUG STARTED")
        
        # Check environment variable
        checkins_table = os.environ.get("CHECKINS_TABLE", "mindbridge-checkins")
        logger.info(f"📋 Table name: {checkins_table}")
        
        # Test DynamoDB
        try:
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(checkins_table)
            logger.info("✅ DynamoDB table accessible")
            
            # Test write
            test_item = {
                "user_id": "test_user",
                "timestamp": datetime.utcnow().isoformat(),
                "test": True
            }
            table.put_item(Item=test_item)
            logger.info("✅ Test write successful")
            
            # Clean up
            table.delete_item(Key={"user_id": "test_user", "timestamp": test_item["timestamp"]})
            logger.info("✅ Test cleanup successful")
            
        except Exception as e:
            logger.error(f"❌ DynamoDB error: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": f"DynamoDB failed: {str(e)}"})
            }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "debug_success", "table": checkins_table})
        }
        
    except Exception as e:
        logger.error(f"❌ Handler error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": f"Handler failed: {str(e)}"})
        }
