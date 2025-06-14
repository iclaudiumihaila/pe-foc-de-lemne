"""
Unit tests for rate limiting middleware.

This module tests the rate limiting functionality including different
rate limits for different endpoints, proper error responses, and
MongoDB integration with TTL cleanup.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

from app.utils.rate_limiter import RateLimiter, rate_limit, get_rate_limiter, get_endpoint_rate_limit_info


class TestRateLimiter:
    """Test RateLimiter class functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.rate_limiter = RateLimiter()
        # Mock database for testing
        self.rate_limiter.db = MagicMock()
        self.rate_limiter.rate_limit_collection = MagicMock()
    
    def test_initialization_success(self):
        """Test successful RateLimiter initialization."""
        with patch('app.utils.rate_limiter.get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_db.api_rate_limits = mock_collection
            mock_get_db.return_value = mock_db
            
            limiter = RateLimiter()
            
            assert limiter.db == mock_db
            assert limiter.rate_limit_collection == mock_collection
            
            # Verify indexes were created
            mock_collection.create_index.assert_any_call(
                "expires_at", 
                expireAfterSeconds=0,
                background=True
            )
            mock_collection.create_index.assert_any_call(
                [("key", 1), ("endpoint", 1)],
                background=True
            )
    
    def test_initialization_database_error(self):
        """Test RateLimiter initialization with database error."""
        with patch('app.utils.rate_limiter.get_database') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            limiter = RateLimiter()
            
            # Should gracefully handle database errors
            assert limiter.db is None
            assert limiter.rate_limit_collection is None
    
    def test_normalize_phone_number(self):
        """Test phone number normalization."""
        test_cases = [
            ('+1234567890', '+1234567890'),
            ('1234567890', '+1234567890'),
            ('+1 (234) 567-8900', '+12345678900'),
            ('+44 20 1234 5678', '+442012345678'),
            ('', ''),
            (None, '')
        ]
        
        for input_phone, expected in test_cases:
            result = self.rate_limiter._normalize_phone_number(input_phone)
            assert result == expected
    
    def test_extract_phone_number(self):
        """Test phone number extraction from request data."""
        # Valid phone number
        request_data = {'phone_number': '+1234567890'}
        result = self.rate_limiter._extract_phone_number(request_data)
        assert result == '+1234567890'
        
        # Missing phone number
        request_data = {'other_field': 'value'}
        result = self.rate_limiter._extract_phone_number(request_data)
        assert result is None
        
        # Empty request data
        result = self.rate_limiter._extract_phone_number({})
        assert result is None
        
        # None request data
        result = self.rate_limiter._extract_phone_number(None)
        assert result is None
    
    def test_get_rate_limit_key_sms_endpoint(self):
        """Test rate limit key generation for SMS endpoints."""
        with patch.object(self.rate_limiter, '_extract_phone_number', return_value='+1234567890'):
            request_data = {'phone_number': '+1234567890'}
            
            # SMS verify endpoint
            key = self.rate_limiter._get_rate_limit_key(request_data, 'sms_verify')
            assert key == 'phone:+1234567890'
            
            # SMS confirm endpoint
            key = self.rate_limiter._get_rate_limit_key(request_data, 'sms_confirm')
            assert key == 'phone:+1234567890'
    
    def test_get_rate_limit_key_non_sms_endpoint(self):
        """Test rate limit key generation for non-SMS endpoints."""
        with patch('app.utils.rate_limiter.request') as mock_request:
            mock_request.environ = {'REMOTE_ADDR': '192.168.1.1'}
            
            request_data = {}
            key = self.rate_limiter._get_rate_limit_key(request_data, 'other_endpoint')
            
            assert key == 'ip:192.168.1.1'
    
    def test_get_rate_limit_config_default(self):
        """Test getting default rate limit configuration."""
        config = self.rate_limiter._get_rate_limit_config('sms_verify')
        
        assert config['limit'] == 10
        assert config['window_seconds'] == 3600
        assert config['description'] == 'SMS verification endpoint'
    
    def test_get_rate_limit_config_custom_overrides(self):
        """Test rate limit configuration with custom overrides."""
        config = self.rate_limiter._get_rate_limit_config(
            'sms_verify', 
            custom_limit=20, 
            custom_window=7200
        )
        
        assert config['limit'] == 20
        assert config['window_seconds'] == 7200
    
    def test_get_rate_limit_config_environment_overrides(self):
        """Test rate limit configuration with environment variable overrides."""
        with patch('app.utils.rate_limiter.current_app') as mock_app:
            mock_app.config = {
                'RATE_LIMIT_SMS_VERIFY_LIMIT': 15,
                'RATE_LIMIT_SMS_VERIFY_WINDOW': 7200
            }
            
            config = self.rate_limiter._get_rate_limit_config('sms_verify')
            
            assert config['limit'] == 15
            assert config['window_seconds'] == 7200
    
    def test_check_rate_limit_allowed(self):
        """Test rate limit check when request is allowed."""
        # Mock database collection to return count below limit
        self.rate_limiter.rate_limit_collection.count_documents.return_value = 5
        
        result = self.rate_limiter.check_rate_limit(
            'phone:+1234567890', 
            'sms_verify', 
            10, 
            3600
        )
        
        assert result['allowed'] is True
        assert result['current_count'] == 5
        assert result['limit'] == 10
        assert result['remaining'] == 5
    
    def test_check_rate_limit_exceeded(self):
        """Test rate limit check when limit is exceeded."""
        # Mock database collection to return count at limit
        self.rate_limiter.rate_limit_collection.count_documents.return_value = 10
        
        # Mock oldest request for reset time calculation
        oldest_request = {
            'created_at': datetime.utcnow() - timedelta(minutes=30)
        }
        self.rate_limiter.rate_limit_collection.find_one.return_value = oldest_request
        
        result = self.rate_limiter.check_rate_limit(
            'phone:+1234567890', 
            'sms_verify', 
            10, 
            3600
        )
        
        assert result['allowed'] is False
        assert result['current_count'] == 10
        assert result['limit'] == 10
        assert 'reset_at' in result
        assert 'reset_in_seconds' in result
        assert result['reason'] == 'rate_limit_exceeded'
    
    def test_check_rate_limit_database_unavailable(self):
        """Test rate limit check when database is unavailable."""
        self.rate_limiter.rate_limit_collection = None
        
        result = self.rate_limiter.check_rate_limit(
            'phone:+1234567890', 
            'sms_verify', 
            10, 
            3600
        )
        
        assert result['allowed'] is True
        assert result['reason'] == 'rate_limiter_unavailable'
    
    def test_check_rate_limit_database_error(self):
        """Test rate limit check with database error."""
        # Mock database to raise exception
        self.rate_limiter.rate_limit_collection.count_documents.side_effect = Exception("DB Error")
        
        result = self.rate_limiter.check_rate_limit(
            'phone:+1234567890', 
            'sms_verify', 
            10, 
            3600
        )
        
        assert result['allowed'] is True
        assert result['reason'] == 'rate_limiter_error'
    
    def test_record_request_success(self):
        """Test successful request recording."""
        self.rate_limiter.record_request(
            'phone:+1234567890',
            'sms_verify',
            3600
        )
        
        # Verify insert_one was called with correct data
        self.rate_limiter.rate_limit_collection.insert_one.assert_called_once()
        
        # Check the inserted record structure
        call_args = self.rate_limiter.rate_limit_collection.insert_one.call_args[0][0]
        assert call_args['key'] == 'phone:+1234567890'
        assert call_args['endpoint'] == 'sms_verify'
        assert 'created_at' in call_args
        assert 'expires_at' in call_args
    
    def test_record_request_database_unavailable(self):
        """Test request recording when database is unavailable."""
        self.rate_limiter.rate_limit_collection = None
        
        # Should not raise exception
        self.rate_limiter.record_request(
            'phone:+1234567890',
            'sms_verify',
            3600
        )
    
    def test_record_request_database_error(self):
        """Test request recording with database error."""
        self.rate_limiter.rate_limit_collection.insert_one.side_effect = Exception("DB Error")
        
        # Should not raise exception
        self.rate_limiter.record_request(
            'phone:+1234567890',
            'sms_verify',
            3600
        )
    
    def test_get_rate_limit_info_with_requests(self):
        """Test getting rate limit info when requests exist."""
        # Mock database to return request history
        mock_requests = [
            {'created_at': datetime.utcnow() - timedelta(minutes=45)},
            {'created_at': datetime.utcnow() - timedelta(minutes=30)},
            {'created_at': datetime.utcnow() - timedelta(minutes=15)}
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_requests
        self.rate_limiter.rate_limit_collection.find.return_value = mock_cursor
        
        result = self.rate_limiter.get_rate_limit_info(
            'phone:+1234567890',
            'sms_verify',
            10,
            3600
        )
        
        assert result['attempts_count'] == 3
        assert result['rate_limit'] == 10
        assert result['window_seconds'] == 3600
        assert result['window_hours'] == 1.0
        assert result['is_rate_limited'] is False
        assert 'reset_at' in result
        assert 'reset_in_seconds' in result
    
    def test_get_rate_limit_info_no_requests(self):
        """Test getting rate limit info when no requests exist."""
        # Mock database to return empty list
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = []
        self.rate_limiter.rate_limit_collection.find.return_value = mock_cursor
        
        result = self.rate_limiter.get_rate_limit_info(
            'phone:+1234567890',
            'sms_verify',
            10,
            3600
        )
        
        assert result['attempts_count'] == 0
        assert result['rate_limit'] == 10
        assert result['reset_at'] is None
        assert result['reset_in_seconds'] == 0
        assert result['is_rate_limited'] is False
    
    def test_get_rate_limit_info_database_unavailable(self):
        """Test getting rate limit info when database is unavailable."""
        self.rate_limiter.rate_limit_collection = None
        
        result = self.rate_limiter.get_rate_limit_info(
            'phone:+1234567890',
            'sms_verify',
            10,
            3600
        )
        
        assert result['attempts_count'] == 0
        assert result['rate_limit'] == 10
        assert result['is_rate_limited'] is False


class TestRateLimitDecorator:
    """Test rate_limit decorator functionality."""
    
    def setup_method(self):
        """Setup test Flask app and environment."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Create test endpoint with rate limiting
        @self.app.route('/test', methods=['POST'])
        @rate_limit('test_endpoint', limit=2, window_seconds=60)
        def test_endpoint():
            return jsonify({'success': True, 'message': 'Request processed'})
        
        self.client = self.app.test_client()
    
    def test_rate_limit_decorator_allowed_request(self):
        """Test rate limit decorator allowing valid requests."""
        with patch('app.utils.rate_limiter.get_rate_limiter') as mock_get_limiter:
            mock_limiter = MagicMock()
            mock_get_limiter.return_value = mock_limiter
            
            # Mock configuration and check result
            mock_limiter._get_rate_limit_config.return_value = {
                'limit': 2,
                'window_seconds': 60
            }
            mock_limiter._get_rate_limit_key.return_value = 'test:key'
            mock_limiter.check_rate_limit.return_value = {
                'allowed': True,
                'current_count': 1,
                'remaining': 1
            }
            
            with self.app.test_request_context('/test', method='POST', json={}):
                response = self.client.post('/test', json={})
                
                assert response.status_code == 200
                assert response.get_json()['success'] is True
                
                # Verify rate limit was checked and recorded
                mock_limiter.check_rate_limit.assert_called_once()
                mock_limiter.record_request.assert_called_once()
    
    def test_rate_limit_decorator_exceeded_request(self):
        """Test rate limit decorator blocking exceeded requests."""
        with patch('app.utils.rate_limiter.get_rate_limiter') as mock_get_limiter:
            mock_limiter = MagicMock()
            mock_get_limiter.return_value = mock_limiter
            
            # Mock configuration and check result
            mock_limiter._get_rate_limit_config.return_value = {
                'limit': 2,
                'window_seconds': 60
            }
            mock_limiter._get_rate_limit_key.return_value = 'test:key'
            mock_limiter.check_rate_limit.return_value = {
                'allowed': False,
                'current_count': 2,
                'limit': 2,
                'reason': 'rate_limit_exceeded'
            }
            mock_limiter.get_rate_limit_info.return_value = {
                'attempts_count': 2,
                'reset_in_minutes': 5,
                'reset_in_seconds': 300,
                'reset_at': '2025-01-13T15:00:00Z'
            }
            
            with self.app.test_request_context('/test', method='POST', json={}):
                response = self.client.post('/test', json={})
                
                assert response.status_code == 429
                
                data = response.get_json()
                assert data['success'] is False
                assert data['error']['code'] == 'RATE_LIMIT_EXCEEDED'
                assert 'Rate limit exceeded' in data['error']['message']
                assert data['error']['details']['limit'] == 2
                
                # Verify rate limit headers
                assert response.headers['X-RateLimit-Limit'] == '2'
                assert response.headers['X-RateLimit-Remaining'] == '0'
                assert 'Retry-After' in response.headers
    
    def test_rate_limit_decorator_phone_masking(self):
        """Test phone number masking in rate limit logs."""
        with patch('app.utils.rate_limiter.get_rate_limiter') as mock_get_limiter:
            with patch('app.utils.rate_limiter.logger') as mock_logger:
                mock_limiter = MagicMock()
                mock_get_limiter.return_value = mock_limiter
                
                # Mock configuration and check result for rate limit exceeded
                mock_limiter._get_rate_limit_config.return_value = {
                    'limit': 1,
                    'window_seconds': 60
                }
                mock_limiter._get_rate_limit_key.return_value = 'phone:+1234567890'
                mock_limiter.check_rate_limit.return_value = {
                    'allowed': False,
                    'reason': 'rate_limit_exceeded'
                }
                mock_limiter.get_rate_limit_info.return_value = {
                    'reset_in_minutes': 5,
                    'reset_in_seconds': 300,
                    'reset_at': '2025-01-13T15:00:00Z'
                }
                
                with self.app.test_request_context('/test', method='POST', json={'phone_number': '+1234567890'}):
                    response = self.client.post('/test', json={'phone_number': '+1234567890'})
                    
                    # Verify phone number was masked in logs
                    mock_logger.warning.assert_called_once()
                    log_call = mock_logger.warning.call_args[0][0]
                    assert 'phone:****7890' in log_call
                    assert '+1234567890' not in log_call


class TestRateLimitIntegration:
    """Test rate limiting integration functionality."""
    
    def test_get_rate_limiter_singleton(self):
        """Test that get_rate_limiter returns singleton instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        
        assert limiter1 is limiter2
    
    def test_get_endpoint_rate_limit_info(self):
        """Test getting endpoint rate limit information."""
        with patch('app.utils.rate_limiter.get_rate_limiter') as mock_get_limiter:
            mock_limiter = MagicMock()
            mock_get_limiter.return_value = mock_limiter
            
            mock_limiter._get_rate_limit_config.return_value = {
                'limit': 10,
                'window_seconds': 3600
            }
            mock_limiter._get_rate_limit_key.return_value = 'phone:+1234567890'
            mock_limiter.get_rate_limit_info.return_value = {
                'attempts_count': 3,
                'rate_limit': 10,
                'is_rate_limited': False
            }
            
            request_data = {'phone_number': '+1234567890'}
            result = get_endpoint_rate_limit_info('sms_verify', request_data)
            
            assert result['attempts_count'] == 3
            assert result['rate_limit'] == 10
            assert result['is_rate_limited'] is False
            
            # Verify method calls
            mock_limiter._get_rate_limit_config.assert_called_once_with('sms_verify')
            mock_limiter._get_rate_limit_key.assert_called_once_with(request_data, 'sms_verify')
            mock_limiter.get_rate_limit_info.assert_called_once()


class TestRateLimitConfiguration:
    """Test rate limit configuration handling."""
    
    def test_default_rate_limit_configurations(self):
        """Test default rate limit configurations are correct."""
        limiter = RateLimiter()
        
        # Test SMS verify defaults
        config = limiter._get_rate_limit_config('sms_verify')
        assert config['limit'] == 10
        assert config['window_seconds'] == 3600
        
        # Test SMS confirm defaults
        config = limiter._get_rate_limit_config('sms_confirm')
        assert config['limit'] == 50
        assert config['window_seconds'] == 3600
        
        # Test unknown endpoint defaults
        config = limiter._get_rate_limit_config('unknown_endpoint')
        assert config['limit'] == 100
        assert config['window_seconds'] == 3600
    
    def test_rate_limit_config_validation(self):
        """Test rate limit configuration validation with invalid values."""
        limiter = RateLimiter()
        
        with patch('app.utils.rate_limiter.current_app') as mock_app:
            # Test invalid environment values
            mock_app.config = {
                'RATE_LIMIT_SMS_VERIFY_LIMIT': 'invalid',
                'RATE_LIMIT_SMS_VERIFY_WINDOW': 'invalid'
            }
            
            # Should use defaults when environment values are invalid
            config = limiter._get_rate_limit_config('sms_verify')
            assert config['limit'] == 10
            assert config['window_seconds'] == 3600