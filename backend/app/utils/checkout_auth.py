"""
Checkout JWT Authentication Middleware
Task ID: 10

Provides JWT-based authentication for checkout flow without traditional user accounts.
"""

import jwt
import logging
from functools import wraps
from flask import request, jsonify, g, current_app
from datetime import datetime
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)


def decode_checkout_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate checkout JWT token.
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        logger.info(f"=== DECODING CHECKOUT TOKEN ===")
        logger.info(f"Token (first 20 chars): {token[:20]}...")
        
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        logger.info(f"Decoded payload: {payload}")
        
        # Verify token type
        token_type = payload.get('type')
        logger.info(f"Token type: {token_type}")
        if token_type != 'checkout_session':
            logger.warning(f"Invalid token type: expected 'checkout_session', got '{token_type}'")
            return None
        
        # Check required fields
        required_fields = ['phone', 'customer_id', 'exp']
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            logger.warning(f"Missing required token fields: {missing_fields}")
            logger.warning(f"Token has fields: {list(payload.keys())}")
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.info("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        return None


def get_auth_token() -> Optional[str]:
    """
    Extract JWT token from request headers.
    
    Supports:
    - Authorization: Bearer <token>
    - Authorization: <token>
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        return None
    
    # Handle "Bearer <token>" format
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Handle direct token format
    return auth_header


def checkout_auth_required(f: Callable) -> Callable:
    """
    Decorator for endpoints requiring checkout authentication.
    
    Adds to g:
    - g.customer_phone: Normalized phone number
    - g.customer_id: Customer database ID
    - g.token_payload: Full token payload
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_token()
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_REQUIRED',
                    'message': 'Autentificare necesară. Verificați numărul de telefon.'
                }
            }), 401
        
        payload = decode_checkout_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Token invalid sau expirat. Verificați din nou telefonul.'
                }
            }), 401
        
        # Add customer info to request context
        g.customer_phone = payload['phone']
        g.customer_id = payload['customer_id']
        g.token_payload = payload
        
        # Log authenticated request
        masked_phone = f"****{payload['phone'][-4:]}" if len(payload['phone']) >= 4 else "****"
        logger.info(f"Authenticated request from {masked_phone}")
        
        return f(*args, **kwargs)
        
    return decorated_function


def checkout_auth_optional(f: Callable) -> Callable:
    """
    Decorator for endpoints with optional checkout authentication.
    
    If valid token provided, adds to g:
    - g.customer_phone: Normalized phone number
    - g.customer_id: Customer database ID
    - g.token_payload: Full token payload
    - g.is_authenticated: True
    
    If no token or invalid token:
    - g.is_authenticated: False
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Initialize as unauthenticated
        g.is_authenticated = False
        g.customer_phone = None
        g.customer_id = None
        g.token_payload = None
        
        logger.info(f"=== CHECKOUT AUTH OPTIONAL ===")
        token = get_auth_token()
        logger.info(f"Token found: {bool(token)}")
        
        if token:
            payload = decode_checkout_token(token)
            logger.info(f"Payload decoded: {bool(payload)}")
            
            if payload:
                # Valid token - set authentication info
                g.is_authenticated = True
                g.customer_phone = payload['phone']
                g.customer_id = payload['customer_id']
                g.token_payload = payload
                
                masked_phone = f"****{payload['phone'][-4:]}" if len(payload['phone']) >= 4 else "****"
                logger.info(f"Optional auth: authenticated request from {masked_phone}")
            else:
                logger.info("Optional auth: invalid token provided")
        else:
            logger.info("Optional auth: no token provided")
        
        return f(*args, **kwargs)
        
    return decorated_function


def refresh_checkout_token() -> Optional[str]:
    """
    Refresh an existing checkout token with new expiry.
    
    Returns:
        New token or None if current token invalid
    """
    token = get_auth_token()
    if not token:
        return None
    
    payload = decode_checkout_token(token)
    if not payload:
        return None
    
    # Create new token with extended expiry
    from datetime import timedelta
    
    new_payload = {
        'phone': payload['phone'],
        'customer_id': payload['customer_id'],
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'type': 'checkout_session'
    }
    
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    new_token = jwt.encode(new_payload, secret_key, algorithm='HS256')
    
    return new_token


def get_current_customer() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated customer info from request context.
    
    Returns:
        Dict with customer info or None if not authenticated
    """
    if not hasattr(g, 'is_authenticated') or not g.is_authenticated:
        return None
    
    return {
        'phone': g.customer_phone,
        'customer_id': g.customer_id,
        'phone_masked': f"****{g.customer_phone[-4:]}" if len(g.customer_phone) >= 4 else "****"
    }


# Error response helpers
def auth_error_response(code: str = 'AUTH_REQUIRED', 
                       message: str = 'Autentificare necesară') -> tuple:
    """
    Create standardized auth error response.
    
    Returns:
        Tuple of (response_json, status_code)
    """
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }), 401