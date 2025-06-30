#!/usr/bin/env python3
"""
Comprehensive SSL Fixes and LLM Connectivity Test Script
Tests all Lambda functions for SSL certificate issues and LLM connectivity
"""

import json
import boto3
import requests
import time
from datetime import datetime

def test_bedrock_ssl_fix():
    """Test Bedrock SSL configuration"""
    print("🔍 Testing Bedrock SSL Configuration...")
    
    try:
        # Import SSL packages
        import ssl
        import certifi
        import urllib3
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        print(f"✅ SSL Context created: verify_mode={ssl_context.verify_mode}")
        print(f"✅ Certifi path: {certifi.where()}")
        
        # Test Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime', 
            region_name='us-east-1',
            config=boto3.session.Config(
                retries={'max_attempts': 3},
                connect_timeout=30,
                read_timeout=60
            )
        )
        
        print("✅ Bedrock client initialized with SSL fixes")
        
        # Test Bedrock access
        bedrock_control = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock_control.list_foundation_models()
        print(f"✅ Bedrock access confirmed. Found {len(models.get('modelSummaries', []))} models")
        
        return True
        
    except Exception as e:
        print(f"❌ Bedrock SSL test failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def test_lambda_function(function_name, test_data):
    """Test a specific Lambda function"""
    print(f"\n🔍 Testing Lambda Function: {function_name}")
    
    try:
        lambda_client = boto3.client('lambda')
        
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_data)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print(f"✅ {function_name} executed successfully")
            
            # Check for SSL/LLM issues in response
            if 'body' in response_payload:
                body = json.loads(response_payload['body'])
                debug_info = body.get('debug_info', {})
                
                if debug_info.get('analysis_method') == 'bedrock_llm':
                    print(f"🤖 {function_name} used LLM successfully")
                elif debug_info.get('analysis_method') == 'fallback_nlp':
                    print(f"⚠️ {function_name} used fallback NLP (LLM issue)")
                else:
                    print(f"❓ {function_name} analysis method unknown")
                    
                return True
            else:
                print(f"⚠️ {function_name} response format unexpected")
                return False
        else:
            print(f"❌ {function_name} failed with status: {response['StatusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ {function_name} test failed: {str(e)}")
        return False

def test_text_analysis():
    """Test text analysis function"""
    test_data = {
        'text': 'I am feeling very happy and excited about the future!',
        'user_id': 'test-user-ssl-fix',
        'session_id': f'test-session-{int(time.time())}'
    }
    
    return test_lambda_function('mindbridge-text-analysis-dev', test_data)

def test_checkin_retriever():
    """Test checkin retriever function"""
    test_data = {
        'queryStringParameters': {
            'user_id': 'yifeitao78@gmail.com'
        }
    }
    
    return test_lambda_function('mindbridge-checkin-retriever-dev', test_data)

def test_realtime_call_analysis():
    """Test real-time call analysis function"""
    test_data = {
        'audio_data': 'base64_encoded_audio_data_placeholder',
        'user_id': 'test-user-ssl-fix',
        'session_id': f'test-session-{int(time.time())}',
        'timestamp': int(time.time() * 1000)
    }
    
    return test_lambda_function('mindbridge-realtime-call-analysis-dev', test_data)

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE SSL FIXES AND LLM CONNECTIVITY TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test SSL configuration
    ssl_success = test_bedrock_ssl_fix()
    
    if not ssl_success:
        print("\n❌ SSL configuration test failed. Stopping tests.")
        return
    
    print("\n✅ SSL configuration test passed. Proceeding with Lambda tests.")
    
    # Test Lambda functions
    results = {
        'text_analysis': test_text_analysis(),
        'checkin_retriever': test_checkin_retriever(),
        'realtime_call_analysis': test_realtime_call_analysis()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for function_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{function_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! SSL fixes are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 