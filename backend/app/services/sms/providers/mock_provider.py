"""
Mock SMS Provider for development and testing
"""

import uuid
import time
import random
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from app.services.sms.provider_interface import (
    SmsProviderInterface, 
    SmsMessage, 
    SmsResponse, 
    SmsStatus,
    ProviderBalance
)

logger = logging.getLogger(__name__)

class MockProvider(SmsProviderInterface):
    """
    Mock SMS provider for development and testing.
    Simulates SMS sending without actual API calls.
    """
    
    # Class-level storage for sent messages (for testing)
    _sent_messages: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mock provider"""
        # Configuration with defaults - set before parent init
        self.config = config
        self.success_rate = self.config.get('success_rate', 1.0)
        self.delivery_delay = self.config.get('delivery_delay', 0)
        self.cost_per_sms = self.config.get('cost_per_sms', 3.5)  # eurocents
        self.balance = self.config.get('initial_balance', 1000.0)  # euros
        self.log_messages = self.config.get('log_messages', True)
        self.fixed_otp_code = self.config.get('fixed_otp_code', '123456')
        
        # Now validate config
        self._validate_config()
        
    def _validate_config(self) -> None:
        """Validate mock provider configuration"""
        if not isinstance(self.success_rate, (int, float)) or not 0 <= self.success_rate <= 1:
            raise ValueError("success_rate must be between 0 and 1")
            
        if not isinstance(self.delivery_delay, (int, float)) or self.delivery_delay < 0:
            raise ValueError("delivery_delay must be non-negative")
    
    def send_sms(self, message: SmsMessage) -> SmsResponse:
        """Send mock SMS message"""
        # Validate message
        errors = message.validate()
        if errors:
            return SmsResponse(
                success=False,
                error_code='INVALID_MESSAGE',
                error_message='; '.join(errors)
            )
        
        # Check balance
        cost = self.calculate_cost(message)
        if self.balance * 100 < cost:  # Convert euros to cents
            return SmsResponse(
                success=False,
                error_code='INSUFFICIENT_BALANCE',
                error_message='Insufficient balance'
            )
        
        # Simulate success/failure based on configured rate
        if random.random() > self.success_rate:
            return SmsResponse(
                success=False,
                error_code='MOCK_RANDOM_FAILURE',
                error_message='Mock provider simulated failure',
                cost=0
            )
        
        # Generate message ID
        message_id = f"MOCK_{uuid.uuid4().hex[:12]}"
        
        # Store message for testing
        self._sent_messages[message_id] = {
            'message': message,
            'sent_at': datetime.utcnow(),
            'status': 'sent',
            'cost': cost
        }
        
        # Deduct cost from balance
        self.balance -= cost / 100  # Convert cents to euros
        
        # Log message if enabled
        if self.log_messages:
            logger.info(f"[MOCK SMS] To: {message.to}")
            logger.info(f"[MOCK SMS] Body: {message.body}")
            logger.info(f"[MOCK SMS] Type: {message.message_type}")
            logger.info(f"[MOCK SMS] Message ID: {message_id}")
            logger.info(f"[MOCK SMS] Cost: {cost} eurocents")
            
            # Extract and log OTP code if present
            if message.message_type == 'otp' and 'cod' in message.body.lower():
                # Try to extract 6-digit code from message
                import re
                code_match = re.search(r'\b\d{6}\b', message.body)
                if code_match:
                    logger.info(f"[MOCK SMS] OTP Code: {code_match.group()}")
                else:
                    logger.info(f"[MOCK SMS] OTP Code: {self.fixed_otp_code} (fixed)")
        
        # Simulate delivery after delay
        if self.delivery_delay > 0:
            # In real implementation, this would be async
            time.sleep(self.delivery_delay)
        
        # Update status to delivered
        self._sent_messages[message_id]['status'] = 'delivered'
        self._sent_messages[message_id]['delivered_at'] = datetime.utcnow()
        
        return SmsResponse(
            success=True,
            message_id=message_id,
            status='sent',
            cost=cost,
            provider_response={
                'mock': True,
                'balance_remaining': self.balance
            }
        )
    
    def get_status(self, message_id: str) -> SmsStatus:
        """Get delivery status of a message"""
        if message_id not in self._sent_messages:
            return SmsStatus(
                message_id=message_id,
                status='not_found',
                error_code='MESSAGE_NOT_FOUND',
                error_message='Message ID not found'
            )
        
        msg_data = self._sent_messages[message_id]
        
        return SmsStatus(
            message_id=message_id,
            status=msg_data['status'],
            delivered_at=msg_data.get('delivered_at'),
            provider_data={
                'mock': True,
                'sent_at': msg_data['sent_at'].isoformat()
            }
        )
    
    def get_balance(self) -> ProviderBalance:
        """Get current account balance"""
        return ProviderBalance(
            balance=self.balance,
            currency='EUR',
            unit='money',
            low_balance_threshold=10.0,
            is_low=self.balance < 10.0
        )
    
    def calculate_cost(self, message: SmsMessage) -> float:
        """Calculate cost for sending a message"""
        # Simple calculation based on message length
        # 1 SMS = 160 chars, each additional part costs more
        message_parts = max(1, (len(message.body) + 159) // 160)
        
        # Base cost per SMS part
        base_cost = self.cost_per_sms * message_parts
        
        # Add premium for marketing messages
        if message.message_type == 'marketing':
            base_cost *= 1.2
        
        return round(base_cost, 2)
    
    def health_check(self) -> Tuple[bool, Optional[str]]:
        """Check if provider is healthy"""
        # Mock provider is always healthy unless balance is too low
        if self.balance < 1.0:
            return False, "Balance too low (< 1 EUR)"
        
        return True, None
    
    def get_provider_name(self) -> str:
        """Get provider display name"""
        return "Mock SMS Provider"
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported features"""
        return [
            'otp',
            'transactional', 
            'marketing',
            'unicode',
            'long_messages',
            'delivery_reports',
            'test_mode'
        ]
    
    def generate_otp_code(self) -> str:
        """Generate OTP code for testing"""
        if self.config.get('random_otp', False):
            return ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return self.fixed_otp_code
    
    @classmethod
    def clear_sent_messages(cls):
        """Clear sent messages (for testing)"""
        cls._sent_messages.clear()
    
    @classmethod
    def get_sent_messages(cls) -> Dict[str, Dict[str, Any]]:
        """Get all sent messages (for testing)"""
        return cls._sent_messages.copy()
    
    @classmethod
    def get_last_message_to(cls, phone: str) -> Optional[Dict[str, Any]]:
        """Get last message sent to a phone number (for testing)"""
        for msg_id in reversed(list(cls._sent_messages.keys())):
            msg_data = cls._sent_messages[msg_id]
            if msg_data['message'].to == phone:
                return {
                    'message_id': msg_id,
                    **msg_data
                }
        return None