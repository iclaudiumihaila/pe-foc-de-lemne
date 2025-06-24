"""
SMSO.ro API Client for SMS operations
"""

import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class SmsoApiError(Exception):
    """SMSO API error"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

class SmsoClient:
    """
    Client for SMSO.ro SMS API.
    Handles authentication and API communication.
    """
    
    BASE_URL = "https://app.smso.ro/api/v1/"
    
    # API Status codes
    STATUS_OK = 200
    STATUS_BAD_REQUEST = 400
    STATUS_UNAUTHORIZED = 401
    STATUS_INSUFFICIENT_CREDIT = 402
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        Initialize SMSO client.
        
        Args:
            api_key: SMSO API key
            base_url: Optional custom base URL
        """
        if not api_key:
            raise ValueError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'X-Authorization': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make API request to SMSO.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            SmsoApiError: On API errors
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            
            # Log request for debugging
            logger.debug(f"SMSO API {method} {url}: {response.status_code}")
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {'raw': response.text}
            
            # Check for errors
            if response.status_code != self.STATUS_OK:
                error_message = self._get_error_message(response.status_code, response_data)
                logger.error(f"SMSO API error response: {response_data}")
                raise SmsoApiError(
                    error_message,
                    status_code=response.status_code,
                    response_data=response_data
                )
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise SmsoApiError("Request timeout", status_code=408)
        except requests.exceptions.ConnectionError:
            raise SmsoApiError("Connection error", status_code=0)
        except requests.exceptions.RequestException as e:
            raise SmsoApiError(f"Request failed: {str(e)}", status_code=0)
    
    def _get_error_message(self, status_code: int, response_data: Dict) -> str:
        """Get user-friendly error message based on status code"""
        error_messages = {
            self.STATUS_BAD_REQUEST: "Invalid request parameters",
            self.STATUS_UNAUTHORIZED: "Invalid API key",
            self.STATUS_INSUFFICIENT_CREDIT: "Insufficient credit balance"
        }
        
        # Try to get message from response
        if isinstance(response_data, dict):
            if 'message' in response_data:
                return response_data['message']
            elif 'error' in response_data:
                return response_data['error']
        
        # Fallback to status code message
        return error_messages.get(status_code, f"API error (status {status_code})")
    
    def send_sms(self, to: str, body: str, sender_id: str = None,
                 message_type: str = 'transactional',
                 webhook_url: str = None) -> Dict[str, Any]:
        """
        Send SMS message.
        
        Args:
            to: Phone number in E.164 format
            body: Message content
            sender_id: Sender name/number (optional)
            message_type: Type of message (marketing, transactional, otp)
            webhook_url: URL for delivery notifications
            
        Returns:
            Response with message ID and cost
        """
        # Prepare request data
        data = {
            'to': to,
            'body': body,
            'type': message_type
        }
        
        if sender_id:
            data['sender'] = sender_id
        
        if webhook_url:
            data['webhook'] = webhook_url
        
        # Additional options
        data['remove_special_chars'] = False  # Keep Romanian chars
        
        logger.info(f"SMSO API request data: {data}")
        
        # Send request
        response = self._make_request('POST', 'send', data=data)
        
        return {
            'success': response.get('status') == self.STATUS_OK,
            'message_id': response.get('responseToken'),
            'cost': response.get('transaction_cost', 0),  # in eurocents
            'response': response
        }
    
    def check_status(self, message_id: str) -> Dict[str, Any]:
        """
        Check message delivery status.
        
        Args:
            message_id: Response token from send_sms
            
        Returns:
            Status information
        """
        params = {'responseToken': message_id}
        
        response = self._make_request('GET', 'status', params=params)
        
        # Map SMSO status to our standard status
        smso_status = response.get('status', 'unknown')
        status_map = {
            'dispatched': 'sent',
            'sent': 'sent',
            'delivered': 'delivered',
            'undelivered': 'failed',
            'expired': 'expired',
            'error': 'failed'
        }
        
        return {
            'message_id': message_id,
            'status': status_map.get(smso_status, smso_status),
            'smso_status': smso_status,
            'response': response
        }
    
    def check_balance(self) -> Dict[str, Any]:
        """
        Check account credit balance.
        
        Returns:
            Balance information
        """
        response = self._make_request('GET', 'credit-check')
        
        # SMSO returns balance in euros
        balance = float(response.get('credit_value', 0))
        
        return {
            'balance': balance,
            'currency': 'EUR',
            'response': response
        }
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate if phone number is acceptable for SMSO.
        Focuses on Romanian numbers.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid
        """
        # Must be E.164 format
        if not phone.startswith('+'):
            return False
        
        # Romanian numbers: +40 followed by 9 digits
        # Mobile prefixes: 7xx xxx xxx
        if phone.startswith('+40'):
            # Remove country code
            national = phone[3:]
            # Should be 9 digits starting with 7
            if len(national) == 9 and national[0] == '7':
                return national.isdigit()
        
        # Allow other international numbers (basic check)
        if len(phone) >= 10 and phone[1:].isdigit():
            return True
        
        return False
    
    def format_romanian_phone(self, phone: str) -> str:
        """
        Format Romanian phone number to E.164.
        
        Args:
            phone: Phone number in various formats
            
        Returns:
            E.164 formatted number
        """
        # Remove all non-digits
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Handle Romanian numbers
        if digits.startswith('40'):
            # Already has country code
            return f"+{digits}"
        elif digits.startswith('07') and len(digits) == 10:
            # National format: 07xx xxx xxx
            return f"+4{digits}"
        elif digits.startswith('7') and len(digits) == 9:
            # Without leading 0: 7xx xxx xxx
            return f"+40{digits}"
        
        # Return as-is if not recognized
        return phone if phone.startswith('+') else f"+{phone}"
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()