"""
SMS Service Provider Interface and Implementations
Task ID: 06

Provides SMS sending functionality with mock implementation for development
and ready for production providers like Twilio.
"""

import os
import random
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SMSProvider(ABC):
    """Abstract base class for SMS providers"""
    
    @abstractmethod
    def send_verification_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Send verification code via SMS"""
        pass
    
    @abstractmethod
    def send_order_confirmation(self, phone: str, order_number: str) -> Dict[str, Any]:
        """Send order confirmation via SMS"""
        pass


class MockSMSProvider(SMSProvider):
    """Mock SMS provider for development"""
    
    def __init__(self):
        self.sent_messages = []
    
    def send_verification_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Mock sending verification code"""
        message = f"Codul dvs Pe Foc de Lemne: {code}. Valid 5 minute."
        
        result = {
            'success': True,
            'message_id': f"mock_{datetime.utcnow().timestamp()}",
            'phone': phone,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.sent_messages.append(result)
        
        # Log for development
        logger.info(f"[MOCK SMS] To: {phone}")
        logger.info(f"[MOCK SMS] Message: {message}")
        logger.info(f"[MOCK SMS] Code: {code}")
        
        return result
    
    def send_order_confirmation(self, phone: str, order_number: str) -> Dict[str, Any]:
        """Mock sending order confirmation"""
        message = f"Comanda dvs #{order_number} a fost înregistrată. Vă vom contacta pentru confirmare."
        
        result = {
            'success': True,
            'message_id': f"mock_{datetime.utcnow().timestamp()}",
            'phone': phone,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.sent_messages.append(result)
        
        logger.info(f"[MOCK SMS] Order confirmation to: {phone}")
        logger.info(f"[MOCK SMS] Order: {order_number}")
        
        return result


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider for production"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        
        # Import only if using Twilio
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
        except ImportError:
            logger.warning("Twilio not installed. Install with: pip install twilio")
            self.client = None
    
    def send_verification_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Send verification code via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            message = self.client.messages.create(
                body=f"Codul dvs Pe Foc de Lemne: {code}. Valid 5 minute.",
                from_=self.from_number,
                to=phone
            )
            
            return {
                'success': True,
                'message_id': message.sid,
                'phone': phone,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_order_confirmation(self, phone: str, order_number: str) -> Dict[str, Any]:
        """Send order confirmation via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            message = self.client.messages.create(
                body=f"Comanda dvs #{order_number} a fost înregistrată. Vă vom contacta pentru confirmare.",
                from_=self.from_number,
                to=phone
            )
            
            return {
                'success': True,
                'message_id': message.sid,
                'phone': phone,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SMSService:
    """SMS service factory and utilities"""
    
    _provider: Optional[SMSProvider] = None
    
    @classmethod
    def configure(cls, provider: str = 'mock', **kwargs):
        """Configure SMS provider"""
        if provider == 'mock':
            cls._provider = MockSMSProvider()
        elif provider == 'twilio':
            cls._provider = TwilioSMSProvider(
                account_sid=kwargs.get('account_sid', os.getenv('TWILIO_ACCOUNT_SID')),
                auth_token=kwargs.get('auth_token', os.getenv('TWILIO_AUTH_TOKEN')),
                from_number=kwargs.get('from_number', os.getenv('TWILIO_PHONE_NUMBER'))
            )
        else:
            raise ValueError(f"Unknown SMS provider: {provider}")
        
        logger.info(f"SMS service configured with provider: {provider}")
    
    @classmethod
    def get_provider(cls) -> SMSProvider:
        """Get configured SMS provider"""
        if not cls._provider:
            # Default to mock if not configured
            cls.configure('mock')
        return cls._provider
    
    @classmethod
    def generate_verification_code(cls) -> str:
        """Generate 6-digit verification code"""
        return str(random.randint(100000, 999999))
    
    @classmethod
    def send_verification(cls, phone: str, code: Optional[str] = None) -> Dict[str, Any]:
        """Send verification code to phone"""
        if not code:
            code = cls.generate_verification_code()
        
        provider = cls.get_provider()
        result = provider.send_verification_code(phone, code)
        
        # Add code to result for development
        if isinstance(provider, MockSMSProvider):
            result['code'] = code
        
        return result
    
    @classmethod
    def send_order_confirmation(cls, phone: str, order_number: str) -> Dict[str, Any]:
        """Send order confirmation to phone"""
        provider = cls.get_provider()
        return provider.send_order_confirmation(phone, order_number)


# Configure SMS service on module load
# Use environment variable or default to mock
sms_provider = os.getenv('SMS_PROVIDER', 'mock')
if sms_provider == 'twilio':
    SMSService.configure('twilio')
else:
    SMSService.configure('mock')