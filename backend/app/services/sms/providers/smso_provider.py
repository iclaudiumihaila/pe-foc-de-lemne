"""
SMSO.ro SMS Provider implementation
"""

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
from app.services.sms.providers.smso_client import SmsoClient, SmsoApiError

logger = logging.getLogger(__name__)

class SmsoProvider(SmsProviderInterface):
    """
    SMSO.ro SMS provider implementation.
    Provides SMS sending via SMSO.ro API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SMSO provider"""
        # Initialize attributes first
        self.config = config
        self._client = None
        
        # Extract configuration
        self.api_key = config.get('api_key')
        self.sender_id = config.get('sender_id', 'PeFocLemne')
        self.base_url = config.get('api_base_url')
        self.webhook_url = config.get('webhook_url')
        
        # Cost configuration (eurocents)
        self.cost_per_sms_part = config.get('cost_per_sms_part', 3.5)
        self.marketing_multiplier = config.get('marketing_multiplier', 1.2)
        
        # Now validate config
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate provider configuration"""
        if not self.api_key:
            raise ValueError("SMSO API key is required")
        
        if not self.sender_id:
            raise ValueError("Sender ID is required")
    
    @property
    def client(self) -> SmsoClient:
        """Get or create SMSO client (lazy loading)"""
        if self._client is None:
            self._client = SmsoClient(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    def send_sms(self, message: SmsMessage) -> SmsResponse:
        """Send SMS message via SMSO"""
        try:
            # Validate message
            errors = message.validate()
            if errors:
                return SmsResponse(
                    success=False,
                    error_code='INVALID_MESSAGE',
                    error_message='; '.join(errors)
                )
            
            # Format phone number for SMSO
            formatted_phone = self.format_phone_number(message.to)
            
            # Validate phone number
            if not self.client.validate_phone_number(formatted_phone):
                return SmsResponse(
                    success=False,
                    error_code='INVALID_PHONE',
                    error_message='Invalid phone number format'
                )
            
            # Determine sender ID
            sender = message.sender_id or self.sender_id
            
            # Send via SMSO client
            result = self.client.send_sms(
                to=formatted_phone,
                body=message.body,
                sender_id=sender,
                message_type=message.message_type,
                webhook_url=self.webhook_url
            )
            
            # Create response
            return SmsResponse(
                success=result['success'],
                message_id=result.get('message_id'),
                status='sent' if result['success'] else 'failed',
                cost=result.get('cost', 0),
                provider_response=result.get('response', {})
            )
            
        except SmsoApiError as e:
            logger.error(f"SMSO API error: {e}")
            
            # Map SMSO errors to our error codes
            error_code = 'SMS_API_ERROR'
            if e.status_code == 401:
                error_code = 'INVALID_API_KEY'
            elif e.status_code == 402:
                error_code = 'INSUFFICIENT_CREDIT'
            elif e.status_code == 400:
                error_code = 'BAD_REQUEST'
            
            return SmsResponse(
                success=False,
                error_code=error_code,
                error_message=str(e),
                provider_response=e.response_data
            )
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return SmsResponse(
                success=False,
                error_code='PROVIDER_ERROR',
                error_message=f"Provider error: {str(e)}"
            )
    
    def get_status(self, message_id: str) -> SmsStatus:
        """Get delivery status from SMSO"""
        try:
            result = self.client.check_status(message_id)
            
            # Map delivered_at if status is delivered
            delivered_at = None
            if result['status'] == 'delivered':
                delivered_at = datetime.utcnow()  # SMSO doesn't provide exact time
            
            return SmsStatus(
                message_id=message_id,
                status=result['status'],
                delivered_at=delivered_at,
                provider_data=result.get('response', {})
            )
            
        except SmsoApiError as e:
            logger.error(f"Error checking status: {e}")
            return SmsStatus(
                message_id=message_id,
                status='unknown',
                error_code='STATUS_CHECK_FAILED',
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error checking status: {e}")
            return SmsStatus(
                message_id=message_id,
                status='unknown',
                error_code='PROVIDER_ERROR',
                error_message=str(e)
            )
    
    def get_balance(self) -> ProviderBalance:
        """Get account balance from SMSO"""
        try:
            result = self.client.check_balance()
            
            balance = result['balance']
            
            # Consider low balance under 10 EUR
            low_threshold = 10.0
            is_low = balance < low_threshold
            
            return ProviderBalance(
                balance=balance,
                currency='EUR',
                unit='money',
                low_balance_threshold=low_threshold,
                is_low=is_low
            )
            
        except SmsoApiError as e:
            logger.error(f"Error checking balance: {e}")
            # Return zero balance on error
            return ProviderBalance(
                balance=0.0,
                currency='EUR',
                unit='money',
                is_low=True
            )
        except Exception as e:
            logger.error(f"Unexpected error checking balance: {e}")
            return ProviderBalance(
                balance=0.0,
                currency='EUR',
                unit='money',
                is_low=True
            )
    
    def calculate_cost(self, message: SmsMessage) -> float:
        """Calculate cost for sending a message"""
        # Calculate number of SMS parts
        # Standard SMS: 160 chars, Unicode: 70 chars
        # Multi-part: 153 chars (standard), 67 chars (unicode)
        
        message_length = len(message.body)
        
        # Check if message contains unicode
        try:
            message.body.encode('ascii')
            is_unicode = False
        except UnicodeEncodeError:
            is_unicode = True
        
        if is_unicode:
            # Unicode message
            if message_length <= 70:
                parts = 1
            else:
                parts = ((message_length - 1) // 67) + 1
        else:
            # Standard GSM message
            if message_length <= 160:
                parts = 1
            else:
                parts = ((message_length - 1) // 153) + 1
        
        # Calculate base cost
        base_cost = self.cost_per_sms_part * parts
        
        # Apply marketing multiplier if applicable
        if message.message_type == 'marketing':
            base_cost *= self.marketing_multiplier
        
        return round(base_cost, 2)
    
    def health_check(self) -> Tuple[bool, Optional[str]]:
        """Check if SMSO provider is healthy"""
        try:
            # Check balance as health indicator
            balance = self.get_balance()
            
            if balance.balance <= 0:
                return False, "No credit balance"
            
            if balance.is_low:
                # Still healthy but warning
                logger.warning(f"SMSO balance low: {balance.balance} {balance.currency}")
            
            return True, None
            
        except Exception as e:
            return False, f"Health check failed: {str(e)}"
    
    def get_provider_name(self) -> str:
        """Get provider display name"""
        return "SMSO.ro"
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported features"""
        return [
            'otp',
            'transactional',
            'marketing',
            'unicode',
            'long_messages',
            'delivery_reports',
            'romanian_numbers',
            'custom_sender_id',
            'webhooks'
        ]
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number for SMSO"""
        # Use client's Romanian phone formatter
        if phone.startswith('07') or phone.startswith('+407'):
            return self.client.format_romanian_phone(phone)
        
        # Return as-is for international numbers
        return phone
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number for SMSO"""
        formatted = self.format_phone_number(phone)
        return self.client.validate_phone_number(formatted)
    
    def handle_webhook(self, data: Dict[str, Any]) -> Optional[SmsStatus]:
        """
        Handle SMSO webhook for delivery reports.
        
        SMSO webhook format:
        {
            "responseToken": "message-id",
            "status": "delivered",
            "timestamp": "2024-01-01 12:00:00"
        }
        """
        if not data.get('responseToken'):
            return None
        
        # Map SMSO webhook status
        smso_status = data.get('status', '')
        status_map = {
            'delivered': 'delivered',
            'undelivered': 'failed',
            'expired': 'expired',
            'error': 'failed'
        }
        
        status = status_map.get(smso_status, smso_status)
        
        # Parse timestamp if provided
        delivered_at = None
        if status == 'delivered' and data.get('timestamp'):
            try:
                delivered_at = datetime.strptime(
                    data['timestamp'],
                    '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                pass
        
        return SmsStatus(
            message_id=data['responseToken'],
            status=status,
            delivered_at=delivered_at,
            provider_data=data
        )
    
    def __del__(self):
        """Cleanup client connection"""
        if hasattr(self, '_client') and self._client:
            self._client.close()