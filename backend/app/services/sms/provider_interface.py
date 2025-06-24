"""
SMS Provider Interface - Abstract base class for all SMS providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class SmsMessage:
    """Standard SMS message format"""
    to: str  # Phone number in E.164 format
    body: str  # Message content
    message_type: str = 'transactional'  # otp, transactional, marketing
    sender_id: Optional[str] = None  # Sender name/number
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate message data"""
        errors = []
        
        if not self.to:
            errors.append("Recipient phone number is required")
        elif not self.to.startswith('+'):
            errors.append("Phone number must be in E.164 format")
            
        if not self.body:
            errors.append("Message body is required")
        elif len(self.body) > 1600:  # SMS limit
            errors.append("Message body exceeds 1600 characters")
            
        if self.message_type not in ['otp', 'transactional', 'marketing']:
            errors.append("Invalid message type")
            
        return errors

@dataclass
class SmsResponse:
    """Standard SMS send response"""
    success: bool
    message_id: Optional[str] = None  # Provider's message ID
    status: str = 'pending'  # pending, sent, failed
    cost: Optional[float] = None  # Cost in eurocents
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider_response: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'message_id': self.message_id,
            'status': self.status,
            'cost': self.cost,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'provider_response': self.provider_response
        }

@dataclass
class SmsStatus:
    """SMS delivery status"""
    message_id: str
    status: str  # pending, sent, delivered, failed, expired
    delivered_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProviderBalance:
    """Provider account balance"""
    balance: float  # Current balance
    currency: str  # Currency code
    unit: str  # 'credits' or 'money'
    low_balance_threshold: Optional[float] = None
    is_low: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'balance': self.balance,
            'currency': self.currency,
            'unit': self.unit,
            'low_balance_threshold': self.low_balance_threshold,
            'is_low': self.is_low
        }

class SmsProviderInterface(ABC):
    """
    Abstract base class for SMS provider implementations.
    All SMS providers must implement this interface.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate provider configuration.
        Should raise ValueError if config is invalid.
        """
        pass
    
    @abstractmethod
    def send_sms(self, message: SmsMessage) -> SmsResponse:
        """
        Send SMS message.
        
        Args:
            message: SMS message to send
            
        Returns:
            SmsResponse with send result
        """
        pass
    
    @abstractmethod
    def get_status(self, message_id: str) -> SmsStatus:
        """
        Get delivery status of a message.
        
        Args:
            message_id: Provider's message ID
            
        Returns:
            SmsStatus with current status
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> ProviderBalance:
        """
        Get current account balance.
        
        Returns:
            ProviderBalance with account info
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, message: SmsMessage) -> float:
        """
        Calculate cost for sending a message.
        
        Args:
            message: SMS message to calculate cost for
            
        Returns:
            Cost in eurocents
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Tuple[bool, Optional[str]]:
        """
        Check if provider is healthy and can send messages.
        
        Returns:
            Tuple of (is_healthy, error_message)
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get provider display name.
        
        Returns:
            Provider name for display
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features.
        
        Returns:
            List of feature strings (e.g., ['otp', 'unicode', 'delivery_reports'])
        """
        pass
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number for provider.
        Default implementation returns as-is.
        
        Args:
            phone: Phone number to format
            
        Returns:
            Formatted phone number
        """
        return phone
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate if phone number is acceptable.
        Default implementation checks for E.164 format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid
        """
        import re
        # E.164 format: + followed by 1-15 digits
        return bool(re.match(r'^\+[1-9]\d{1,14}$', phone))
    
    def handle_webhook(self, data: Dict[str, Any]) -> Optional[SmsStatus]:
        """
        Handle provider webhook for delivery reports.
        Default implementation returns None (not supported).
        
        Args:
            data: Webhook payload from provider
            
        Returns:
            SmsStatus if webhook is valid, None otherwise
        """
        return None
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get provider rate limits.
        
        Returns:
            Dict with rate limit info (e.g., {'per_second': 10, 'per_minute': 100})
        """
        return {
            'per_second': 1,
            'per_minute': 60,
            'per_hour': 1000,
            'per_day': 10000
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(name={self.get_provider_name()})"