"""
SMS Verification Service for Local Producer Web Application

This module provides SMS verification functionality using Twilio API
for phone number verification with rate limiting and error handling.
Features MongoDB integration with TTL for automatic cleanup.
"""

import re
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from flask import current_app
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from app.utils.error_handlers import SMSError, ValidationError
from app.utils.validators import validate_phone_number
from app.database import get_database


class SMSService:
    """
    SMS verification service using Twilio for phone number verification.
    
    This service handles sending verification codes, validating codes,
    rate limiting, and error handling for SMS operations.
    """
    
    # Verification code constants
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_CODE_EXPIRY_MINUTES = 10
    
    # Rate limiting constants (internal service limits - higher than middleware limits)
    DEFAULT_RATE_LIMIT_PER_PHONE = 15  # Higher internal limit
    DEFAULT_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    # Message templates
    VERIFICATION_MESSAGE_TEMPLATE = "Your verification code is: {code}. This code expires in {minutes} minutes."
    
    def __init__(self):
        """
        Initialize SMS service with Twilio configuration and MongoDB.
        """
        self._twilio_client = None
        self._phone_number = None
        self._mock_mode = False
        self._rate_limit_per_phone = self.DEFAULT_RATE_LIMIT_PER_PHONE
        self._rate_limit_window = self.DEFAULT_RATE_LIMIT_WINDOW
        
        # Initialize MongoDB collections
        self._initialize_database()
        self._initialize_twilio()
    
    def _initialize_database(self):
        """Initialize MongoDB collections and indexes."""
        try:
            self.db = get_database()
            self.verification_collection: Collection = self.db.sms_verification_codes
            self.rate_limit_collection: Collection = self.db.sms_rate_limits
            
            # Create TTL index for verification codes (auto-expire after 10 minutes)
            self.verification_collection.create_index(
                "expires_at", 
                expireAfterSeconds=0,
                background=True
            )
            
            # Create unique index for phone number in verification codes
            self.verification_collection.create_index(
                "phone_number", 
                unique=True,
                background=True
            )
            
            # Create TTL index for rate limits (auto-expire after 1 hour)
            self.rate_limit_collection.create_index(
                "expires_at", 
                expireAfterSeconds=0,
                background=True
            )
            
            # Create index for rate limit lookup
            self.rate_limit_collection.create_index(
                "phone_number",
                background=True
            )
            
            logging.info("SMS service MongoDB collections initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize SMS service database: {str(e)}")
            raise SMSError(f"Database initialization failed: {str(e)}", "SMS_DB_001")
    
    def send_verification_code(self, phone_number: str, code: str = None) -> Dict[str, Any]:
        """
        Send verification code to phone number.
        
        Args:
            phone_number (str): Phone number in E.164 format
            code (str): Optional custom verification code
            
        Returns:
            dict: Result with success status and details
            
        Raises:
            ValidationError: If phone number is invalid
            SMSError: If SMS sending fails or rate limited
        """
        try:
            # Validate phone number
            if not validate_phone_number(phone_number):
                raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
            
            # Normalize phone number
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Check rate limiting
            if self.is_rate_limited(normalized_phone):
                rate_info = self.get_rate_limit_info(normalized_phone)
                raise SMSError(
                    f"Rate limit exceeded. Try again in {rate_info['reset_in_minutes']} minutes.",
                    "SMS_001",
                    429,
                    rate_info
                )
            
            # Generate verification code if not provided
            if code is None:
                code = self.generate_verification_code()
            
            # Format message
            message = self._format_message(code)
            
            # Send SMS
            if self._mock_mode:
                result = self._send_mock_sms(normalized_phone, message, code)
            else:
                result = self._send_twilio_sms(normalized_phone, message)
            
            # Track rate limiting
            self._track_sms_attempt(normalized_phone)
            
            # Log successful SMS
            self._log_sms_attempt(normalized_phone, code, True, result.get('message_sid'))
            
            # Store verification code in MongoDB for later validation
            self._store_verification_code(normalized_phone, code)
            
            return {
                'success': True,
                'phone_number': normalized_phone,
                'code_sent': True,
                'expires_at': (datetime.utcnow() + timedelta(minutes=self.VERIFICATION_CODE_EXPIRY_MINUTES)).isoformat() + 'Z',
                'message_sid': result.get('message_sid'),
                'mock_mode': self._mock_mode
            }
            
        except (ValidationError, SMSError):
            raise
        except Exception as e:
            logging.error(f"Unexpected error sending SMS: {str(e)}")
            raise SMSError("Failed to send verification code", "SMS_001")
    
    def generate_verification_code(self) -> str:
        """
        Generate a random 6-digit verification code.
        
        Returns:
            str: 6-digit verification code
        """
        return ''.join([str(random.randint(0, 9)) for _ in range(self.VERIFICATION_CODE_LENGTH)])
    
    def validate_verification_code(self, phone_number: str, code: str, stored_code: str, 
                                 code_expires: datetime) -> bool:
        """
        Validate verification code against stored code and expiry.
        
        Args:
            phone_number (str): Phone number being verified
            code (str): Code entered by user
            stored_code (str): Code stored in database
            code_expires (datetime): Code expiration time
            
        Returns:
            bool: True if code is valid and not expired
            
        Raises:
            ValidationError: If input validation fails
            SMSError: If verification fails
        """
        try:
            # Validate inputs
            if not phone_number or not code or not stored_code:
                raise ValidationError("Phone number, code, and stored code are required")
            
            # Validate phone number format
            if not validate_phone_number(phone_number):
                raise ValidationError("Invalid phone number format")
            
            # Validate code format
            if not re.match(r'^\d{6}$', code):
                raise ValidationError("Verification code must be 6 digits")
            
            # Check if code matches
            if code != stored_code:
                self._log_verification_attempt(phone_number, code, False, "Code mismatch")
                raise SMSError("Invalid verification code", "SMS_002")
            
            # Check if code has expired
            if datetime.utcnow() > code_expires:
                self._log_verification_attempt(phone_number, code, False, "Code expired")
                raise SMSError("Verification code has expired", "SMS_003")
            
            # Log successful verification
            self._log_verification_attempt(phone_number, code, True)
            
            return True
            
        except (ValidationError, SMSError):
            raise
        except Exception as e:
            logging.error(f"Unexpected error validating verification code: {str(e)}")
            raise SMSError("Failed to validate verification code", "SMS_002")
    
    def is_rate_limited(self, phone_number: str) -> bool:
        """
        Check if phone number is rate limited.
        
        Args:
            phone_number (str): Phone number to check
            
        Returns:
            bool: True if rate limited
        """
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Count SMS attempts in the last hour
            cutoff_time = datetime.utcnow() - timedelta(seconds=self._rate_limit_window)
            
            count = self.rate_limit_collection.count_documents({
                'phone_number': normalized_phone,
                'created_at': {'$gte': cutoff_time}
            })
            
            return count >= self._rate_limit_per_phone
            
        except Exception as e:
            logging.error(f"Error checking rate limit: {str(e)}")
            return False
    
    def validate_recent_code(self, phone_number: str, code: str) -> bool:
        """
        Validate verification code against recently sent codes.
        
        This method checks if the provided code matches any recently sent
        verification codes for the phone number within the expiry window.
        
        Args:
            phone_number (str): Phone number to validate
            code (str): Verification code to validate
            
        Returns:
            bool: True if code is valid and recent
            
        Raises:
            ValidationError: If input validation fails
            SMSError: If verification fails
        """
        try:
            # Validate inputs
            if not phone_number or not code:
                raise ValidationError("Phone number and code are required")
            
            # Normalize phone number
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Validate code format
            if not re.match(r'^\d{6}$', code):
                raise ValidationError("Verification code must be 6 digits")
            
            # Check against MongoDB stored codes
            verification_record = self.verification_collection.find_one({
                'phone_number': normalized_phone
            })
            
            if not verification_record:
                self._log_verification_attempt(normalized_phone, code, False, "No verification code found")
                raise SMSError("No verification code found for this phone number", "SMS_002")
            
            stored_code = verification_record.get('code')
            expires_at = verification_record.get('expires_at')
            
            # Check if code has expired
            if datetime.utcnow() > expires_at:
                self._log_verification_attempt(normalized_phone, code, False, "Code expired")
                raise SMSError("Verification code has expired", "SMS_003")
            
            # Check if code matches
            if code == stored_code:
                # Mark as verified
                self.verification_collection.update_one(
                    {'phone_number': normalized_phone},
                    {'$set': {'verified': True, 'verified_at': datetime.utcnow()}}
                )
                self._log_verification_attempt(normalized_phone, code, True)
                return True
            else:
                self._log_verification_attempt(normalized_phone, code, False, "Code mismatch")
                raise SMSError("Invalid verification code", "SMS_002")
            
        except (ValidationError, SMSError):
            raise
        except Exception as e:
            logging.error(f"Unexpected error validating recent code: {str(e)}")
            raise SMSError("Failed to validate verification code", "SMS_002")
    
    def send_notification(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send notification SMS to phone number.
        
        Args:
            phone_number (str): Phone number in E.164 format
            message (str): Message to send
            
        Returns:
            dict: Result with success status and details
            
        Raises:
            ValidationError: If phone number is invalid
            SMSError: If SMS sending fails
        """
        try:
            # Validate phone number
            if not validate_phone_number(phone_number):
                raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
            
            # Normalize phone number
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Send SMS (notifications bypass rate limiting)
            if self._mock_mode:
                result = self._send_mock_sms(normalized_phone, message)
            else:
                result = self._send_twilio_sms(normalized_phone, message)
            
            # Log successful SMS
            self._log_sms_attempt(normalized_phone, "", True, result.get('message_sid'))
            
            return {
                'success': True,
                'phone_number': normalized_phone,
                'message_sent': True,
                'message_sid': result.get('message_sid'),
                'mock_mode': self._mock_mode
            }
            
        except (ValidationError, SMSError):
            raise
        except Exception as e:
            logging.error(f"Unexpected error sending notification SMS: {str(e)}")
            raise SMSError("Failed to send notification", "SMS_001")
    
    def get_rate_limit_info(self, phone_number: str) -> Dict[str, Any]:
        """
        Get rate limit information for phone number.
        
        Args:
            phone_number (str): Phone number to check
            
        Returns:
            dict: Rate limit information
        """
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            
            # Count attempts in the current window
            cutoff_time = datetime.utcnow() - timedelta(seconds=self._rate_limit_window)
            
            attempts = list(self.rate_limit_collection.find({
                'phone_number': normalized_phone,
                'created_at': {'$gte': cutoff_time}
            }).sort('created_at', 1))
            
            attempts_count = len(attempts)
            
            if attempts_count > 0:
                oldest_attempt = attempts[0]['created_at']
                reset_time = oldest_attempt + timedelta(seconds=self._rate_limit_window)
                reset_in_seconds = max(0, (reset_time - datetime.utcnow()).total_seconds())
            else:
                reset_time = None
                reset_in_seconds = 0
            
            return {
                'attempts_count': attempts_count,
                'rate_limit': self._rate_limit_per_phone,
                'window_seconds': self._rate_limit_window,
                'reset_at': reset_time.isoformat() + 'Z' if reset_time else None,
                'reset_in_seconds': int(reset_in_seconds),
                'reset_in_minutes': int(reset_in_seconds / 60),
                'is_rate_limited': attempts_count >= self._rate_limit_per_phone
            }
            
        except Exception as e:
            logging.error(f"Error getting rate limit info: {str(e)}")
            return {
                'attempts_count': 0,
                'rate_limit': self._rate_limit_per_phone,
                'window_seconds': self._rate_limit_window,
                'reset_at': None,
                'reset_in_seconds': 0,
                'reset_in_minutes': 0,
                'is_rate_limited': False
            }
    
    def _initialize_twilio(self):
        """Initialize Twilio client with configuration."""
        try:
            # Get configuration from Flask app
            if current_app:
                account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
                auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
                self._phone_number = current_app.config.get('TWILIO_PHONE_NUMBER')
                self._mock_mode = current_app.config.get('SMS_MOCK_MODE', False)
                self._rate_limit_per_phone = current_app.config.get('SMS_RATE_LIMIT_PER_PHONE', self.DEFAULT_RATE_LIMIT_PER_PHONE)
                self._rate_limit_window = current_app.config.get('SMS_RATE_LIMIT_WINDOW', self.DEFAULT_RATE_LIMIT_WINDOW)
            else:
                # Fallback for testing without Flask context
                account_sid = None
                auth_token = None
                self._phone_number = None
                self._mock_mode = True
            
            # Initialize Twilio client if not in mock mode
            if not self._mock_mode and account_sid and auth_token:
                try:
                    from twilio.rest import Client
                    self._twilio_client = Client(account_sid, auth_token)
                    logging.info("Twilio SMS service initialized successfully")
                except ImportError:
                    logging.warning("Twilio library not available, using mock mode")
                    self._mock_mode = True
                except Exception as e:
                    logging.error(f"Failed to initialize Twilio client: {str(e)}")
                    self._mock_mode = True
            else:
                logging.info("SMS service running in mock mode")
                self._mock_mode = True
                
        except Exception as e:
            logging.error(f"Error initializing SMS service: {str(e)}")
            self._mock_mode = True
    
    def _send_twilio_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using Twilio API."""
        try:
            if not self._twilio_client:
                raise SMSError("Twilio client not initialized", "SMS_001")
            
            if not self._phone_number:
                raise SMSError("Twilio phone number not configured", "SMS_001")
            
            # Send SMS via Twilio
            message_instance = self._twilio_client.messages.create(
                body=message,
                from_=self._phone_number,
                to=phone_number
            )
            
            return {
                'message_sid': message_instance.sid,
                'status': message_instance.status,
                'direction': message_instance.direction
            }
            
        except Exception as e:
            logging.error(f"Twilio API error: {str(e)}")
            if "phone number" in str(e).lower():
                raise SMSError("Invalid phone number", "SMS_001", 400)
            elif "unverified" in str(e).lower():
                raise SMSError("Phone number not verified in Twilio account", "SMS_001", 403)
            else:
                raise SMSError("SMS service temporarily unavailable", "SMS_001", 503)
    
    def _send_mock_sms(self, phone_number: str, message: str, code: str) -> Dict[str, Any]:
        """Send mock SMS for testing."""
        import uuid
        
        # Generate mock message SID
        mock_sid = f"SM{uuid.uuid4().hex[:32]}"
        
        logging.info(f"MOCK SMS to {phone_number}: {message}")
        
        return {
            'message_sid': mock_sid,
            'status': 'sent',
            'direction': 'outbound-api',
            'mock': True,
            'verification_code': code  # Only included in mock mode for testing
        }
    
    def _format_message(self, code: str) -> str:
        """Format verification message."""
        return self.VERIFICATION_MESSAGE_TEMPLATE.format(
            code=code,
            minutes=self.VERIFICATION_CODE_EXPIRY_MINUTES
        )
    
    def _track_sms_attempt(self, phone_number: str):
        """Track SMS attempt for rate limiting in MongoDB."""
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            now = datetime.utcnow()
            
            # Store rate limit record with TTL
            rate_limit_record = {
                'phone_number': normalized_phone,
                'created_at': now,
                'expires_at': now + timedelta(seconds=self._rate_limit_window)
            }
            
            self.rate_limit_collection.insert_one(rate_limit_record)
            
        except Exception as e:
            logging.error(f"Error tracking SMS attempt: {str(e)}")
    
    def _store_verification_code(self, phone_number: str, code: str):
        """Store verification code in MongoDB with TTL."""
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            expires_at = datetime.utcnow() + timedelta(minutes=self.VERIFICATION_CODE_EXPIRY_MINUTES)
            
            verification_record = {
                'phone_number': normalized_phone,
                'code': code,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at,
                'verified': False
            }
            
            # Use upsert to replace existing code for same phone number
            self.verification_collection.replace_one(
                {'phone_number': normalized_phone},
                verification_record,
                upsert=True
            )
            
            logging.info(f"Verification code stored for phone number: {normalized_phone}")
            
        except Exception as e:
            logging.error(f"Error storing verification code: {str(e)}")
            raise SMSError(f"Failed to store verification code: {str(e)}", "SMS_DB_001")
    
    
    def _log_sms_attempt(self, phone_number: str, code: str, success: bool, message_sid: str = None):
        """Log SMS sending attempt."""
        log_data = {
            'phone_number': phone_number[-4:],  # Log only last 4 digits for privacy
            'code_length': len(code),
            'success': success,
            'mock_mode': self._mock_mode,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if message_sid:
            log_data['message_sid'] = message_sid
        
        if success:
            logging.info(f"SMS sent successfully: {log_data}")
        else:
            logging.error(f"SMS send failed: {log_data}")
    
    def _log_verification_attempt(self, phone_number: str, code: str, success: bool, reason: str = None):
        """Log verification attempt."""
        log_data = {
            'phone_number': phone_number[-4:],  # Log only last 4 digits for privacy
            'code_provided': len(code),
            'success': success,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if reason:
            log_data['reason'] = reason
        
        if success:
            logging.info(f"Phone verification successful: {log_data}")
        else:
            logging.warning(f"Phone verification failed: {log_data}")
    
    @staticmethod
    def _normalize_phone_number(phone_number: str) -> str:
        """Normalize phone number to E.164 format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            else:
                raise ValidationError("Phone number must include country code or be in E.164 format")
        
        return cleaned
    
    def is_phone_verified(self, phone_number: str) -> bool:
        """
        Check if phone number has been verified.
        
        Args:
            phone_number (str): Phone number to check
            
        Returns:
            bool: True if phone number is verified, False otherwise
        """
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            
            verification_record = self.verification_collection.find_one({
                'phone_number': normalized_phone,
                'verified': True
            })
            
            return verification_record is not None
            
        except Exception as e:
            logging.error(f"Error checking phone verification status: {str(e)}")
            return False
    
    def get_verification_status(self, phone_number: str) -> Dict[str, Any]:
        """
        Get verification status and details for phone number.
        
        Args:
            phone_number (str): Phone number to check
            
        Returns:
            dict: Verification status details
        """
        try:
            normalized_phone = self._normalize_phone_number(phone_number)
            
            verification_record = self.verification_collection.find_one({
                'phone_number': normalized_phone
            })
            
            if not verification_record:
                return {
                    'verified': False,
                    'code_sent': False,
                    'message': 'No verification code sent'
                }
            
            # Check if expired
            is_expired = datetime.utcnow() > verification_record['expires_at']
            
            return {
                'verified': verification_record.get('verified', False),
                'code_sent': True,
                'expired': is_expired,
                'created_at': verification_record['created_at'].isoformat() + 'Z',
                'expires_at': verification_record['expires_at'].isoformat() + 'Z',
                'verified_at': verification_record.get('verified_at', '').isoformat() + 'Z' if verification_record.get('verified_at') else None
            }
            
        except Exception as e:
            logging.error(f"Error getting verification status: {str(e)}")
            return {
                'verified': False,
                'code_sent': False,
                'error': str(e)
            }
    
    def __repr__(self) -> str:
        """String representation of SMS service."""
        return f"SMSService(mock_mode={self._mock_mode}, rate_limit={self._rate_limit_per_phone}/{self._rate_limit_window}s)"


# Global SMS service instance
_sms_service = None

def get_sms_service() -> SMSService:
    """
    Get SMS service instance (singleton pattern).
    
    Returns:
        SMSService: SMS service instance
    """
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service