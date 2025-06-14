"""
Unit tests for SMS Service functionality.

This module contains comprehensive unit tests for the SMS service including
verification code sending, validation, rate limiting, and error handling.
All external dependencies (Twilio, MongoDB) are mocked for isolated testing.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
from twilio.base.exceptions import TwilioException

from app.services.sms_service import SMSService, get_sms_service
from app.utils.error_handlers import SMSError, ValidationError


class TestSMSServiceInitialization:
    """Test SMS service initialization and configuration."""
    
    @patch('app.services.sms_service.get_database')
    @patch('app.services.sms_service.current_app')
    @patch('app.services.sms_service.Client')
    def test_initialization_success_with_twilio(self, mock_client, mock_app, mock_get_db):
        """Test successful SMS service initialization with Twilio configuration."""
        # Setup mocks
        mock_app.config = {
            'TWILIO_ACCOUNT_SID': 'test_account_sid',
            'TWILIO_AUTH_TOKEN': 'test_auth_token',
            'TWILIO_PHONE_NUMBER': '+1234567890',
            'SMS_MOCK_MODE': False
        }
        
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_twilio_client = MagicMock()
        mock_client.return_value = mock_twilio_client
        
        # Initialize service
        service = SMSService()
        
        # Assertions
        assert service._twilio_client == mock_twilio_client
        assert service._phone_number == '+1234567890'
        assert service._mock_mode is False
        mock_client.assert_called_once_with('test_account_sid', 'test_auth_token')
    
    @patch('app.services.sms_service.get_database')
    @patch('app.services.sms_service.current_app')
    def test_initialization_mock_mode_no_config(self, mock_app, mock_get_db):
        """Test SMS service initialization falls back to mock mode without Twilio config."""
        # Setup mocks
        mock_app.config = {}
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Initialize service
        service = SMSService()
        
        # Assertions
        assert service._twilio_client is None
        assert service._mock_mode is True
    
    @patch('app.services.sms_service.get_database')
    @patch('app.services.sms_service.current_app')
    def test_initialization_database_setup(self, mock_app, mock_get_db):
        """Test database collections and indexes are created during initialization."""
        # Setup mocks
        mock_app.config = {'SMS_MOCK_MODE': True}
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_verification_collection = MagicMock()
        mock_rate_limit_collection = MagicMock()
        mock_db.sms_verification_codes = mock_verification_collection
        mock_db.sms_rate_limits = mock_rate_limit_collection
        
        # Initialize service
        service = SMSService()
        
        # Assertions
        assert service.verification_collection == mock_verification_collection
        assert service.rate_limit_collection == mock_rate_limit_collection
        
        # Check index creation calls
        mock_verification_collection.create_index.assert_any_call(
            "expires_at", expireAfterSeconds=0, background=True
        )
        mock_verification_collection.create_index.assert_any_call(
            "phone_number", unique=True, background=True
        )
        mock_rate_limit_collection.create_index.assert_any_call(
            "expires_at", expireAfterSeconds=0, background=True
        )
        mock_rate_limit_collection.create_index.assert_any_call(
            "phone_number", background=True
        )
    
    @patch('app.services.sms_service.get_database')
    def test_initialization_database_failure(self, mock_get_db):
        """Test SMS service initialization handles database failures."""
        # Setup mock to raise exception
        mock_get_db.side_effect = Exception("Database connection failed")
        
        # Test initialization failure
        with pytest.raises(SMSError) as exc_info:
            SMSService()
        
        assert "Database initialization failed" in str(exc_info.value)
        assert exc_info.value.error_code == "SMS_DB_001"


class TestSMSServiceSendVerificationCode:
    """Test verification code sending functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_verification_code_success_new_phone(self, mock_validate):
        """Test successful verification code sending to new phone number."""
        # Setup mocks
        mock_validate.return_value = True
        self.service.verification_collection = MagicMock()
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 0  # No rate limiting
        
        # Mock the private methods
        with patch.object(self.service, '_send_mock_sms') as mock_send_sms, \
             patch.object(self.service, '_store_verification_code') as mock_store:
            
            mock_send_sms.return_value = {
                'message_sid': 'SM123456789',
                'status': 'sent',
                'verification_code': '123456'
            }
            
            # Test sending code
            result = self.service.send_verification_code('+1234567890')
            
            # Assertions
            assert result['success'] is True
            assert result['phone_number'] == '+1234567890'
            assert result['code_sent'] is True
            assert 'expires_at' in result
            assert result['mock_mode'] is True
            
            # Verify methods were called
            mock_validate.assert_called_once_with('+1234567890')
            mock_send_sms.assert_called_once()
            mock_store.assert_called_once()
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_verification_code_invalid_phone(self, mock_validate):
        """Test sending verification code with invalid phone number."""
        # Setup mock to return invalid
        mock_validate.return_value = False
        
        # Test sending code with invalid phone
        with pytest.raises(ValidationError) as exc_info:
            self.service.send_verification_code('invalid_phone')
        
        assert "Invalid phone number format" in str(exc_info.value)
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_verification_code_rate_limited(self, mock_validate):
        """Test sending verification code when rate limited."""
        # Setup mocks
        mock_validate.return_value = True
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 5  # Rate limit exceeded
        
        # Mock rate limit info
        with patch.object(self.service, 'get_rate_limit_info') as mock_rate_info:
            mock_rate_info.return_value = {
                'reset_in_minutes': 30,
                'attempts_count': 5,
                'rate_limit': 5
            }
            
            # Test rate limited sending
            with pytest.raises(SMSError) as exc_info:
                self.service.send_verification_code('+1234567890')
            
            assert exc_info.value.error_code == "SMS_001"
            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in str(exc_info.value)
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_verification_code_twilio_failure(self, mock_validate):
        """Test handling Twilio API failures."""
        # Setup mocks
        mock_validate.return_value = True
        self.service._mock_mode = False
        self.service._twilio_client = MagicMock()
        self.service._phone_number = '+1234567890'
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 0
        
        # Mock Twilio failure
        self.service._twilio_client.messages.create.side_effect = TwilioException("Invalid phone number")
        
        # Test Twilio failure
        with pytest.raises(SMSError) as exc_info:
            self.service.send_verification_code('+1234567890')
        
        assert "Failed to send SMS" in str(exc_info.value)
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_verification_code_custom_code(self, mock_validate):
        """Test sending verification code with custom code."""
        # Setup mocks
        mock_validate.return_value = True
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 0
        
        # Mock the private methods
        with patch.object(self.service, '_send_mock_sms') as mock_send_sms, \
             patch.object(self.service, '_store_verification_code') as mock_store:
            
            mock_send_sms.return_value = {'message_sid': 'SM123456789'}
            
            # Test sending with custom code
            result = self.service.send_verification_code('+1234567890', code='555666')
            
            # Assertions
            assert result['success'] is True
            
            # Verify custom code was used
            args, kwargs = mock_send_sms.call_args
            assert '555666' in args[1]  # Message body contains custom code
            mock_store.assert_called_with('+1234567890', '555666')


class TestSMSServiceCodeValidation:
    """Test verification code validation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    def test_validate_recent_code_success(self):
        """Test successful verification code validation."""
        # Setup verification record
        verification_record = {
            'phone_number': '+1234567890',
            'code': '123456',
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'verified': False
        }
        
        # Mock database operations
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = verification_record
        
        # Test validation
        result = self.service.validate_recent_code('+1234567890', '123456')
        
        # Assertions
        assert result is True
        self.service.verification_collection.update_one.assert_called_once()
        
        # Check that verified flag was set
        update_call = self.service.verification_collection.update_one.call_args
        assert update_call[0][0] == {'phone_number': '+1234567890'}
        assert update_call[0][1]['$set']['verified'] is True
    
    def test_validate_recent_code_expired(self):
        """Test validation of expired verification code."""
        # Setup expired verification record
        verification_record = {
            'phone_number': '+1234567890',
            'code': '123456',
            'created_at': datetime.utcnow() - timedelta(minutes=15),
            'expires_at': datetime.utcnow() - timedelta(minutes=5),  # Expired
            'verified': False
        }
        
        # Mock database operations
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = verification_record
        
        # Test validation of expired code
        with pytest.raises(SMSError) as exc_info:
            self.service.validate_recent_code('+1234567890', '123456')
        
        assert exc_info.value.error_code == "SMS_003"
        assert "expired" in str(exc_info.value)
    
    def test_validate_recent_code_invalid_code(self):
        """Test validation with incorrect verification code."""
        # Setup verification record
        verification_record = {
            'phone_number': '+1234567890',
            'code': '123456',
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'verified': False
        }
        
        # Mock database operations
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = verification_record
        
        # Test validation with wrong code
        with pytest.raises(SMSError) as exc_info:
            self.service.validate_recent_code('+1234567890', '654321')
        
        assert exc_info.value.error_code == "SMS_002"
        assert "Invalid verification code" in str(exc_info.value)
    
    def test_validate_recent_code_not_found(self):
        """Test validation when no verification code exists."""
        # Mock database operations - no record found
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = None
        
        # Test validation with no existing code
        with pytest.raises(SMSError) as exc_info:
            self.service.validate_recent_code('+1234567890', '123456')
        
        assert exc_info.value.error_code == "SMS_002"
        assert "No verification code found" in str(exc_info.value)
    
    def test_validate_recent_code_invalid_format(self):
        """Test validation with invalid code format."""
        # Test various invalid code formats
        invalid_codes = ['12345', '1234567', 'abcdef', '12345a', '']
        
        for invalid_code in invalid_codes:
            with pytest.raises(ValidationError) as exc_info:
                self.service.validate_recent_code('+1234567890', invalid_code)
            
            assert "6 digits" in str(exc_info.value)


class TestSMSServiceRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    def test_is_rate_limited_no_attempts(self):
        """Test rate limiting check with no previous attempts."""
        # Mock database operations - no previous attempts
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 0
        
        # Test rate limiting check
        result = self.service.is_rate_limited('+1234567890')
        
        # Assertions
        assert result is False
        self.service.rate_limit_collection.count_documents.assert_called_once()
    
    def test_is_rate_limited_within_limit(self):
        """Test rate limiting check with attempts within limit."""
        # Mock database operations - 3 attempts (within limit of 5)
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 3
        
        # Test rate limiting check
        result = self.service.is_rate_limited('+1234567890')
        
        # Assertions
        assert result is False
    
    def test_is_rate_limited_exceeded(self):
        """Test rate limiting check when limit is exceeded."""
        # Mock database operations - 5 attempts (at limit)
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.return_value = 5
        
        # Test rate limiting check
        result = self.service.is_rate_limited('+1234567890')
        
        # Assertions
        assert result is True
    
    def test_get_rate_limit_info_no_attempts(self):
        """Test getting rate limit info with no previous attempts."""
        # Mock database operations - no attempts
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.find.return_value = []
        
        # Test getting rate limit info
        info = self.service.get_rate_limit_info('+1234567890')
        
        # Assertions
        assert info['attempts_count'] == 0
        assert info['rate_limit'] == 5
        assert info['is_rate_limited'] is False
        assert info['reset_at'] is None
        assert info['reset_in_seconds'] == 0
    
    def test_get_rate_limit_info_with_attempts(self):
        """Test getting rate limit info with existing attempts."""
        # Mock database operations - 3 attempts
        now = datetime.utcnow()
        mock_attempts = [
            {'created_at': now - timedelta(minutes=30)},
            {'created_at': now - timedelta(minutes=20)},
            {'created_at': now - timedelta(minutes=10)}
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_attempts
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.find.return_value = mock_cursor
        
        # Test getting rate limit info
        info = self.service.get_rate_limit_info('+1234567890')
        
        # Assertions
        assert info['attempts_count'] == 3
        assert info['rate_limit'] == 5
        assert info['is_rate_limited'] is False
        assert info['reset_at'] is not None
        assert info['reset_in_seconds'] > 0


class TestSMSServicePhoneNumberValidation:
    """Test phone number validation and normalization."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    def test_normalize_phone_number_e164_format(self):
        """Test normalization of E.164 format phone numbers."""
        # Test valid E.164 formats
        valid_numbers = [
            ('+1234567890', '+1234567890'),
            ('+44123456789', '+44123456789'),
            ('+33123456789', '+33123456789')
        ]
        
        for input_num, expected in valid_numbers:
            result = self.service._normalize_phone_number(input_num)
            assert result == expected
    
    def test_normalize_phone_number_us_format(self):
        """Test normalization of US phone numbers without country code."""
        # Test US numbers without country code
        us_numbers = [
            ('1234567890', '+11234567890'),
            ('(123) 456-7890', '+11234567890'),
            ('123-456-7890', '+11234567890'),
            ('123.456.7890', '+11234567890')
        ]
        
        for input_num, expected in us_numbers:
            result = self.service._normalize_phone_number(input_num)
            assert result == expected
    
    def test_normalize_phone_number_invalid_format(self):
        """Test normalization of invalid phone number formats."""
        # Test invalid formats
        invalid_numbers = [
            '123',  # Too short
            '12345678901234567',  # Too long
            'abcdefghij',  # Non-numeric
            '',  # Empty
            '+',  # Just plus sign
        ]
        
        for invalid_num in invalid_numbers:
            with pytest.raises(ValidationError):
                self.service._normalize_phone_number(invalid_num)


class TestSMSServiceUtilityMethods:
    """Test utility methods and helper functions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    def test_is_phone_verified_true(self):
        """Test checking verified phone number status."""
        # Mock database operations - verified record exists
        verification_record = {
            'phone_number': '+1234567890',
            'verified': True
        }
        
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = verification_record
        
        # Test verification status check
        result = self.service.is_phone_verified('+1234567890')
        
        # Assertions
        assert result is True
    
    def test_is_phone_verified_false(self):
        """Test checking unverified phone number status."""
        # Mock database operations - no verified record
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = None
        
        # Test verification status check
        result = self.service.is_phone_verified('+1234567890')
        
        # Assertions
        assert result is False
    
    def test_get_verification_status_verified(self):
        """Test getting detailed verification status for verified phone."""
        # Mock verification record
        now = datetime.utcnow()
        verification_record = {
            'phone_number': '+1234567890',
            'verified': True,
            'created_at': now - timedelta(minutes=5),
            'expires_at': now + timedelta(minutes=5),
            'verified_at': now
        }
        
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = verification_record
        
        # Test getting verification status
        status = self.service.get_verification_status('+1234567890')
        
        # Assertions
        assert status['verified'] is True
        assert status['code_sent'] is True
        assert status['expired'] is False
        assert 'created_at' in status
        assert 'expires_at' in status
        assert 'verified_at' in status
    
    def test_get_verification_status_no_code_sent(self):
        """Test getting verification status when no code was sent."""
        # Mock database operations - no record
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.return_value = None
        
        # Test getting verification status
        status = self.service.get_verification_status('+1234567890')
        
        # Assertions
        assert status['verified'] is False
        assert status['code_sent'] is False
        assert status['message'] == 'No verification code sent'
    
    def test_generate_verification_code_format(self):
        """Test verification code generation format."""
        # Generate multiple codes to test format
        for _ in range(10):
            code = self.service.generate_verification_code()
            
            # Assertions
            assert len(code) == 6
            assert code.isdigit()
            assert int(code) >= 0
            assert int(code) <= 999999
    
    def test_service_string_representation(self):
        """Test SMS service string representation."""
        # Test string representation
        repr_str = repr(self.service)
        
        # Assertions
        assert 'SMSService' in repr_str
        assert 'mock_mode=True' in repr_str
        assert 'rate_limit=5' in repr_str


class TestSMSServiceErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    def test_database_error_handling(self):
        """Test handling of database operation errors."""
        # Mock database operation to raise exception
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.find_one.side_effect = PyMongoError("Database connection lost")
        
        # Test database error handling
        with pytest.raises(SMSError) as exc_info:
            self.service.validate_recent_code('+1234567890', '123456')
        
        assert "Failed to validate verification code" in str(exc_info.value)
    
    def test_store_verification_code_database_error(self):
        """Test error handling when storing verification code fails."""
        # Mock database operation to raise exception
        self.service.verification_collection = MagicMock()
        self.service.verification_collection.replace_one.side_effect = PyMongoError("Insert failed")
        
        # Test storage error handling
        with pytest.raises(SMSError) as exc_info:
            self.service._store_verification_code('+1234567890', '123456')
        
        assert exc_info.value.error_code == "SMS_DB_001"
        assert "Failed to store verification code" in str(exc_info.value)
    
    def test_rate_limit_check_error_handling(self):
        """Test error handling in rate limit checking."""
        # Mock database operation to raise exception
        self.service.rate_limit_collection = MagicMock()
        self.service.rate_limit_collection.count_documents.side_effect = Exception("Database error")
        
        # Test rate limit error handling (should return False, not raise)
        result = self.service.is_rate_limited('+1234567890')
        
        # Should return False on error for safety
        assert result is False


class TestSMSServiceSingleton:
    """Test SMS service singleton functionality."""
    
    @patch('app.services.sms_service.SMSService')
    def test_get_sms_service_singleton(self, mock_sms_service_class):
        """Test that get_sms_service returns singleton instance."""
        # Mock SMS service instance
        mock_instance = MagicMock()
        mock_sms_service_class.return_value = mock_instance
        
        # Get service instances
        service1 = get_sms_service()
        service2 = get_sms_service()
        
        # Assertions
        assert service1 == service2
        assert service1 == mock_instance
        
        # Should only create instance once
        mock_sms_service_class.assert_called_once()


class TestSMSServiceNotificationSending:
    """Test notification SMS sending functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        with patch('app.services.sms_service.get_database'), \
             patch('app.services.sms_service.current_app') as mock_app:
            mock_app.config = {'SMS_MOCK_MODE': True}
            self.service = SMSService()
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_notification_success(self, mock_validate):
        """Test successful notification SMS sending."""
        # Setup mocks
        mock_validate.return_value = True
        
        # Mock the private method
        with patch.object(self.service, '_send_mock_sms') as mock_send_sms:
            mock_send_sms.return_value = {
                'message_sid': 'SM123456789',
                'status': 'sent'
            }
            
            # Test sending notification
            result = self.service.send_notification('+1234567890', 'Test notification message')
            
            # Assertions
            assert result['success'] is True
            assert result['phone_number'] == '+1234567890'
            assert result['message_sent'] is True
            assert result['mock_mode'] is True
            
            # Verify methods were called
            mock_validate.assert_called_once_with('+1234567890')
            mock_send_sms.assert_called_once()
    
    @patch('app.services.sms_service.validate_phone_number')
    def test_send_notification_invalid_phone(self, mock_validate):
        """Test sending notification with invalid phone number."""
        # Setup mock to return invalid
        mock_validate.return_value = False
        
        # Test sending notification with invalid phone
        with pytest.raises(ValidationError) as exc_info:
            self.service.send_notification('invalid_phone', 'Test message')
        
        assert "Invalid phone number format" in str(exc_info.value)