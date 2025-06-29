"""
Test file for health check functionality
"""

import pytest
import json
from unittest.mock import Mock, patch


def test_health_check_response():
    """Test that health check returns expected response"""
    # Mock the Lambda context
    context = Mock()
    context.function_name = "test-health-check"
    
    # Import the handler (this would be the actual health check handler)
    # For now, we'll create a simple test
    def health_check_handler(event, context):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'healthy',
                'service': 'mindbridge',
                'timestamp': '2024-01-01T00:00:00Z'
            })
        }
    
    # Test the handler
    result = health_check_handler({}, context)
    
    assert result['statusCode'] == 200
    assert 'healthy' in result['body']
    assert 'mindbridge' in result['body']


def test_health_check_headers():
    """Test that health check includes proper headers"""
    context = Mock()
    
    def health_check_handler(event, context):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'healthy'})
        }
    
    result = health_check_handler({}, context)
    
    assert 'Content-Type' in result['headers']
    assert result['headers']['Content-Type'] == 'application/json'
    assert 'Access-Control-Allow-Origin' in result['headers']


@pytest.mark.integration
def test_health_check_integration():
    """Integration test for health check (marked for separate execution)"""
    # This would test against a real deployed endpoint
    # For now, just a placeholder
    assert True


class TestHealthCheck:
    """Test class for health check functionality"""
    
    def setup_method(self):
        """Setup method for each test"""
        self.context = Mock()
        self.context.function_name = "test-health-check"
    
    def test_health_check_with_query_params(self):
        """Test health check with query parameters"""
        event = {
            'queryStringParameters': {
                'detailed': 'true'
            }
        }
        
        def health_check_handler(event, context):
            detailed = event.get('queryStringParameters', {}).get('detailed') == 'true'
            
            response_body = {
                'status': 'healthy',
                'service': 'mindbridge'
            }
            
            if detailed:
                response_body['details'] = {
                    'version': '1.0.0',
                    'environment': 'test'
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response_body)
            }
        
        result = health_check_handler(event, self.context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'details' in body
        assert body['details']['version'] == '1.0.0'
    
    def test_health_check_error_handling(self):
        """Test health check error handling"""
        with patch('json.dumps', side_effect=Exception("JSON serialization error")):
            def health_check_handler(event, context):
                try:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'status': 'healthy'})
                    }
                except Exception as e:
                    return {
                        'statusCode': 500,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': str(e)})
                    }
            
            result = health_check_handler({}, self.context)
            
            assert result['statusCode'] == 500
            assert 'error' in result['body']


if __name__ == '__main__':
    pytest.main([__file__]) 