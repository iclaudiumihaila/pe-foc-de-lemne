"""
Integration tests for SMS API endpoints.

This module contains comprehensive integration tests for all SMS verification
endpoints including sending codes, confirming codes, status checking, and
rate limiting functionality with proper mocking and error scenario testing.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.utils.error_handlers import SMSError, ValidationError


class TestSMSVerifyEndpoint:
    """Test POST /api/sms/verify endpoint."""
    
    @patch('app.routes.sms.get_sms_service')
    def test_send_verification_code_success(self, mock_get_sms_service, client):
        """Test successful verification code sending."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.send_verification_code.return_value = {
            'success': True,
            'code_sent': True,
            'message_sid': 'SM123456789',
            'mock_mode': True,
            'verification_code': '123456'
        }
        
        # Make request
        response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['phone_number'] == '+1234567890'
        assert data['data']['code_sent'] is True
        assert data['data']['expires_in_minutes'] == 10
        assert data['data']['message_id'] == 'SM123456789'
        assert data['data']['mock_mode'] is True
        assert 'verification_code' in data['data']  # Only in mock mode
        assert data['message'] == 'Verification code sent successfully'
        
        # Verify SMS service was called
        mock_service.send_verification_code.assert_called_once_with('+1234567890')
    
    def test_send_verification_code_invalid_phone_format(self, client):
        """Test sending verification code with invalid phone number format."""
        # Test various invalid phone number formats
        invalid_phones = [
            '1234567890',    # Missing +
            '+1234',         # Too short
            'invalid',       # Non-numeric
            '',              # Empty
            '+',             # Just plus sign
        ]
        
        for invalid_phone in invalid_phones:
            response = client.post('/api/sms/verify',
                json={'phone_number': invalid_phone},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'VAL_001'
            assert 'phone_number' in data['error']['field']
    
    def test_send_verification_code_missing_phone_number(self, client):
        """Test sending verification code with missing phone number field."""
        response = client.post('/api/sms/verify',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    @patch('app.routes.sms.get_sms_service')
    def test_send_verification_code_rate_limited(self, mock_get_sms_service, client):
        """Test rate limiting behavior when sending verification codes."""
        # Setup SMS service mock to raise rate limit error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        # Create rate limit error
        rate_limit_error = SMSError("Rate limit exceeded. Try again in 30 minutes.")
        rate_limit_error.error_code = "SMS_001"
        rate_limit_error.status_code = 429
        mock_service.send_verification_code.side_effect = rate_limit_error
        
        # Mock rate limit info
        mock_service.get_rate_limit_info.return_value = {
            'attempts_count': 5,
            'rate_limit': 5,
            'reset_in_minutes': 30
        }
        
        # Make request
        response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 429
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_001'
        assert 'Rate limit exceeded' in data['error']['message']
        assert data['error']['details']['attempts_count'] == 5
        assert data['error']['details']['rate_limit'] == 5
        assert data['error']['details']['reset_in_minutes'] == 30
        assert data['error']['details']['window_hours'] == 1
    
    @patch('app.routes.sms.get_sms_service')
    def test_send_verification_code_sms_service_error(self, mock_get_sms_service, client):
        """Test SMS service error handling."""
        # Setup SMS service mock to raise service error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        service_error = SMSError("Twilio service temporarily unavailable")
        service_error.error_code = "SMS_001"
        service_error.status_code = 503
        mock_service.send_verification_code.side_effect = service_error
        
        # Make request
        response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_001'
        assert 'temporarily unavailable' in data['error']['message']
    
    @patch('app.routes.sms.get_sms_service')
    def test_send_verification_code_unexpected_error(self, mock_get_sms_service, client):
        """Test unexpected error handling."""
        # Setup SMS service mock to raise unexpected error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.send_verification_code.side_effect = Exception("Unexpected error")
        
        # Make request
        response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_500'
        assert 'temporarily unavailable' in data['error']['message']


class TestSMSConfirmEndpoint:
    """Test POST /api/sms/confirm endpoint."""
    
    @patch('app.routes.sms.create_verification_session')
    @patch('app.routes.sms.get_sms_service')
    def test_confirm_verification_code_success(self, mock_get_sms_service, mock_create_session, client):
        """Test successful verification code confirmation."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.validate_recent_code.return_value = True
        
        # Setup session creation mock
        session_expires = datetime.utcnow() + timedelta(hours=2)
        mock_create_session.return_value = {
            'session_id': '507f1f77bcf86cd799439011',
            'expires_at': session_expires
        }
        
        # Make request
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': '123456'
            },
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['phone_number'] == '+1234567890'
        assert data['data']['verified'] is True
        assert data['data']['session_id'] == '507f1f77bcf86cd799439011'
        assert 'verified_at' in data['data']
        assert 'expires_at' in data['data']
        assert data['message'] == 'Phone number verified successfully'
        
        # Verify service calls
        mock_service.validate_recent_code.assert_called_once_with('+1234567890', '123456')
        mock_create_session.assert_called_once_with('+1234567890')
    
    def test_confirm_verification_code_invalid_phone_format(self, client):
        """Test confirming with invalid phone number format."""
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': 'invalid_phone',
                'verification_code': '123456'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
    
    def test_confirm_verification_code_invalid_code_format(self, client):
        """Test confirming with invalid verification code format."""
        # Test various invalid code formats
        invalid_codes = [
            '12345',     # Too short
            '1234567',   # Too long
            'abcdef',    # Non-numeric
            '',          # Empty
            '12345a',    # Mixed alphanumeric
        ]
        
        for invalid_code in invalid_codes:
            response = client.post('/api/sms/confirm',
                json={
                    'phone_number': '+1234567890',
                    'verification_code': invalid_code
                },
                content_type='application/json'
            )
            
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'VAL_001'
    
    @patch('app.routes.sms.get_sms_service')
    def test_confirm_verification_code_invalid_code(self, mock_get_sms_service, client):
        """Test confirming with incorrect verification code."""
        # Setup SMS service mock to raise invalid code error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        invalid_code_error = SMSError("Invalid verification code")
        invalid_code_error.error_code = "SMS_002"
        mock_service.validate_recent_code.side_effect = invalid_code_error
        
        # Make request
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': '654321'
            },
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_002'
        assert 'Invalid verification code' in data['error']['message']
    
    @patch('app.routes.sms.get_sms_service')
    def test_confirm_verification_code_not_found(self, mock_get_sms_service, client):
        """Test confirming when no verification code exists."""
        # Setup SMS service mock to raise code not found error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        not_found_error = SMSError("No verification code found for this phone number")
        not_found_error.error_code = "SMS_002"
        mock_service.validate_recent_code.side_effect = not_found_error
        
        # Make request
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': '123456'
            },
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_002'
        assert 'not found' in data['error']['message']
    
    @patch('app.routes.sms.get_sms_service')
    def test_confirm_verification_code_expired(self, mock_get_sms_service, client):
        """Test confirming with expired verification code."""
        # Setup SMS service mock to raise expired code error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        expired_error = SMSError("Verification code has expired")
        expired_error.error_code = "SMS_003"
        mock_service.validate_recent_code.side_effect = expired_error
        
        # Make request
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': '123456'
            },
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 410
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_003'
        assert 'expired' in data['error']['message']
    
    @patch('app.routes.sms.create_verification_session')
    @patch('app.routes.sms.get_sms_service')
    def test_confirm_verification_code_session_creation_failure(self, mock_get_sms_service, mock_create_session, client):
        """Test session creation failure handling."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.validate_recent_code.return_value = True
        
        # Setup session creation mock to fail
        mock_create_session.side_effect = Exception("Failed to create verification session")
        
        # Make request
        response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': '123456'
            },
            content_type='application/json'
        )
        
        # Assertions
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_500'


class TestSMSStatusEndpoint:
    """Test GET /api/sms/status/{phone_number} endpoint."""
    
    @patch('app.routes.sms.get_sms_service')
    def test_get_verification_status_success(self, mock_get_sms_service, client):
        """Test successful verification status retrieval."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.get_verification_status.return_value = {
            'verified': True,
            'code_sent': True,
            'expired': False,
            'created_at': '2025-01-13T14:00:00Z',
            'expires_at': '2025-01-13T14:10:00Z',
            'verified_at': '2025-01-13T14:05:00Z'
        }
        
        # Make request
        response = client.get('/api/sms/status/+1234567890')
        
        # Assertions
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['phone_number'] == '+1234567890'
        assert data['data']['verified'] is True
        assert data['data']['code_sent'] is True
        assert data['data']['expired'] is False
        assert data['data']['created_at'] == '2025-01-13T14:00:00Z'
        assert data['data']['expires_at'] == '2025-01-13T14:10:00Z'
        assert data['data']['verified_at'] == '2025-01-13T14:05:00Z'
        assert data['message'] == 'Verification status retrieved successfully'
        
        # Verify service call
        mock_service.get_verification_status.assert_called_once_with('+1234567890')
    
    def test_get_verification_status_invalid_phone_format(self, client):
        """Test getting status with invalid phone number format."""
        response = client.get('/api/sms/status/invalid_phone')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert 'Invalid phone number format' in data['error']['message']
    
    @patch('app.routes.sms.get_sms_service')
    def test_get_verification_status_service_error(self, mock_get_sms_service, client):
        """Test status retrieval service error."""
        # Setup SMS service mock to raise error
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.get_verification_status.side_effect = Exception("Service error")
        
        # Make request
        response = client.get('/api/sms/status/+1234567890')
        
        # Assertions
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_500'


class TestSMSRateLimitEndpoint:
    """Test GET /api/sms/rate-limit/{phone_number} endpoint."""
    
    @patch('app.routes.sms.get_sms_service')
    def test_get_rate_limit_info_success(self, mock_get_sms_service, client):
        """Test successful rate limit info retrieval."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        mock_service.get_rate_limit_info.return_value = {
            'attempts_count': 2,
            'rate_limit': 5,
            'window_seconds': 3600,
            'is_rate_limited': False,
            'reset_at': '2025-01-13T15:00:00Z',
            'reset_in_seconds': 1800,
            'reset_in_minutes': 30
        }
        
        # Make request
        response = client.get('/api/sms/rate-limit/+1234567890')
        
        # Assertions
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['phone_number'] == '+1234567890'
        assert data['data']['attempts_count'] == 2
        assert data['data']['rate_limit'] == 5
        assert data['data']['window_seconds'] == 3600
        assert data['data']['window_hours'] == 1
        assert data['data']['is_rate_limited'] is False
        assert data['data']['reset_at'] == '2025-01-13T15:00:00Z'
        assert data['data']['reset_in_seconds'] == 1800
        assert data['data']['reset_in_minutes'] == 30
        assert data['message'] == 'Rate limit information retrieved successfully'
        
        # Verify service call
        mock_service.get_rate_limit_info.assert_called_once_with('+1234567890')
    
    def test_get_rate_limit_info_invalid_phone_format(self, client):
        """Test getting rate limit info with invalid phone number format."""
        response = client.get('/api/sms/rate-limit/invalid_phone')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert 'Invalid phone number format' in data['error']['message']


class TestSMSIntegrationFlow:
    """Test complete SMS verification integration flows."""
    
    @patch('app.routes.sms.create_verification_session')
    @patch('app.routes.sms.get_sms_service')
    def test_complete_sms_verification_flow(self, mock_get_sms_service, mock_create_session, client):
        """Test complete SMS verification flow from send to confirm."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        # Step 1: Send verification code
        mock_service.send_verification_code.return_value = {
            'success': True,
            'code_sent': True,
            'message_sid': 'SM123456789',
            'mock_mode': True,
            'verification_code': '123456'
        }
        
        send_response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        assert send_response.status_code == 200
        send_data = json.loads(send_response.data)
        assert send_data['success'] is True
        verification_code = send_data['data']['verification_code']
        
        # Step 2: Confirm verification code
        mock_service.validate_recent_code.return_value = True
        session_expires = datetime.utcnow() + timedelta(hours=2)
        mock_create_session.return_value = {
            'session_id': '507f1f77bcf86cd799439011',
            'expires_at': session_expires
        }
        
        confirm_response = client.post('/api/sms/confirm',
            json={
                'phone_number': '+1234567890',
                'verification_code': verification_code
            },
            content_type='application/json'
        )
        
        assert confirm_response.status_code == 200
        confirm_data = json.loads(confirm_response.data)
        assert confirm_data['success'] is True
        assert confirm_data['data']['verified'] is True
        assert confirm_data['data']['session_id'] == '507f1f77bcf86cd799439011'
        
        # Step 3: Check verification status
        mock_service.get_verification_status.return_value = {
            'verified': True,
            'code_sent': True,
            'expired': False
        }
        
        status_response = client.get('/api/sms/status/+1234567890')
        
        assert status_response.status_code == 200
        status_data = json.loads(status_response.data)
        assert status_data['success'] is True
        assert status_data['data']['verified'] is True
        
        # Verify all service calls were made
        mock_service.send_verification_code.assert_called_with('+1234567890')
        mock_service.validate_recent_code.assert_called_with('+1234567890', verification_code)
        mock_service.get_verification_status.assert_called_with('+1234567890')
        mock_create_session.assert_called_with('+1234567890')
    
    @patch('app.routes.sms.get_sms_service')
    def test_multiple_verification_attempts_rate_limiting(self, mock_get_sms_service, client):
        """Test multiple verification attempts and rate limiting behavior."""
        # Setup SMS service mock
        mock_service = MagicMock()
        mock_get_sms_service.return_value = mock_service
        
        # First 4 attempts should succeed
        mock_service.send_verification_code.return_value = {
            'success': True,
            'code_sent': True,
            'message_sid': 'SM123456789'
        }
        
        for i in range(4):
            response = client.post('/api/sms/verify',
                json={'phone_number': '+1234567890'},
                content_type='application/json'
            )
            assert response.status_code == 200
        
        # 5th attempt should trigger rate limiting
        rate_limit_error = SMSError("Rate limit exceeded")
        rate_limit_error.error_code = "SMS_001"
        rate_limit_error.status_code = 429
        mock_service.send_verification_code.side_effect = rate_limit_error
        mock_service.get_rate_limit_info.return_value = {
            'attempts_count': 5,
            'rate_limit': 5,
            'reset_in_minutes': 60
        }
        
        response = client.post('/api/sms/verify',
            json={'phone_number': '+1234567890'},
            content_type='application/json'
        )
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SMS_001'
        assert data['error']['details']['attempts_count'] == 5


class TestSMSErrorHandling:
    """Test SMS API error handling scenarios."""
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON requests."""
        response = client.post('/api/sms/verify',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test handling of requests with missing content type."""
        response = client.post('/api/sms/verify',
            data='{"phone_number": "+1234567890"}'
        )
        
        assert response.status_code == 400
    
    def test_method_not_allowed(self, client):
        """Test method not allowed error handling."""
        # Try GET on verify endpoint (should only accept POST)
        response = client.get('/api/sms/verify')
        
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'HTTP_405'