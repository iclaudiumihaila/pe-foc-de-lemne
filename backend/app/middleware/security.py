"""
Security Middleware for Local Producer Web Application

This module provides comprehensive security middleware including rate limiting,
CSRF protection, security headers, and request validation for the Flask application.
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import TooManyRequests, Forbidden, BadRequest
from app.utils.security import (
    SecurityValidator, SecurityLogger, rate_limiter, 
    validate_csrf_token, apply_security_headers,
    SECURITY_HEADERS
)


class SecurityMiddleware:
    """Security middleware for request processing"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Configure security logging
        self._configure_security_logging(app)
    
    def _configure_security_logging(self, app):
        """Configure security event logging"""
        security_logger = logging.getLogger('security')
        security_logger.setLevel(logging.INFO)
        
        if not security_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            security_logger.addHandler(handler)
    
    def before_request(self):
        """Process request before routing"""
        # Store request start time for performance monitoring
        g.request_start_time = time.time()
        
        # Get client information
        g.client_ip = self._get_client_ip()
        g.user_agent = request.headers.get('User-Agent', '')
        
        # Log request for security monitoring
        self._log_request()
        
        # Validate request security
        validation_result = self._validate_request_security()
        if not validation_result['is_valid']:
            return self._security_error_response(validation_result)
    
    def after_request(self, response):
        """Process response after routing"""
        # Apply security headers
        response = apply_security_headers(response)
        
        # Log response for security monitoring
        self._log_response(response)
        
        return response
    
    def _get_client_ip(self) -> str:
        """Get real client IP address"""
        # Check for forwarded headers (behind proxy)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or 'unknown'
    
    def _validate_request_security(self) -> Dict[str, Any]:
        """Validate request security parameters"""
        result = {'is_valid': True, 'errors': []}
        
        # Validate request size
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
            result['is_valid'] = False
            result['errors'].append('Request too large')
            SecurityLogger.log_security_event(
                'request_too_large',
                {'content_length': request.content_length},
                severity='WARNING',
                ip_address=g.client_ip
            )
        
        # Validate user agent
        if not g.user_agent or len(g.user_agent) > 500:
            result['is_valid'] = False
            result['errors'].append('Invalid user agent')
            SecurityLogger.log_security_event(
                'invalid_user_agent',
                {'user_agent': g.user_agent[:100] if g.user_agent else None},
                severity='WARNING',
                ip_address=g.client_ip
            )
        
        # Check for suspicious patterns
        suspicious_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'SELECT * FROM', 'UNION SELECT', 'DROP TABLE', '../', '..\\',
            'eval(', 'alert(', 'document.cookie', 'document.write'
        ]
        
        request_data = str(request.get_data(as_text=True))
        for pattern in suspicious_patterns:
            if pattern.lower() in request_data.lower():
                result['is_valid'] = False
                result['errors'].append('Suspicious content detected')
                SecurityLogger.log_security_event(
                    'suspicious_content',
                    {'pattern': pattern, 'ip': g.client_ip},
                    severity='ERROR',
                    ip_address=g.client_ip
                )
                break
        
        return result
    
    def _log_request(self):
        """Log incoming request for security monitoring"""
        SecurityLogger.log_security_event(
            'request_received',
            {
                'method': request.method,
                'path': request.path,
                'user_agent': g.user_agent[:100],
                'content_length': request.content_length,
                'referrer': request.headers.get('Referer', '')
            },
            severity='INFO',
            ip_address=g.client_ip
        )
    
    def _log_response(self, response):
        """Log response for security monitoring"""
        duration = time.time() - g.request_start_time if hasattr(g, 'request_start_time') else 0
        
        SecurityLogger.log_security_event(
            'response_sent',
            {
                'status_code': response.status_code,
                'duration': round(duration, 3),
                'content_length': len(response.get_data())
            },
            severity='INFO',
            ip_address=g.client_ip
        )
    
    def _security_error_response(self, validation_result):
        """Return security error response"""
        return jsonify({
            'error': 'Security validation failed',
            'message': 'Cererea nu îndeplinește criteriile de securitate',
            'errors': validation_result['errors']
        }), 400


def rate_limit(requests_per_minute: int = 60, per_ip: bool = True):
    """
    Rate limiting decorator for API endpoints.
    
    Args:
        requests_per_minute (int): Maximum requests allowed per minute
        per_ip (bool): Whether to limit per IP address or globally
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine identifier for rate limiting
            if per_ip:
                identifier = g.client_ip if hasattr(g, 'client_ip') else request.remote_addr
            else:
                identifier = 'global'
            
            # Check rate limit
            limit_result = rate_limiter.is_allowed(
                identifier=identifier,
                limit=requests_per_minute,
                window=60  # 1 minute
            )
            
            if not limit_result['allowed']:
                SecurityLogger.log_security_event(
                    'rate_limit_exceeded',
                    {
                        'identifier': identifier,
                        'requests_made': limit_result['requests_made'],
                        'limit': limit_result['limit']
                    },
                    severity='WARNING',
                    ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                )
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Prea multe cereri. Încercați din nou mai târziu.',
                    'retry_after': limit_result['retry_after']
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(limit_result['retry_after'])
                return response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_csrf_token():
    """
    CSRF protection decorator for state-changing operations.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # Get CSRF token from header or form data
                csrf_token = (
                    request.headers.get('X-CSRF-Token') or
                    request.form.get('csrf_token') or
                    request.json.get('csrf_token') if request.is_json else None
                )
                
                # Get session token (should be stored in session)
                session_token = request.headers.get('X-Session-Token')
                
                if not csrf_token or not session_token:
                    SecurityLogger.log_security_event(
                        'csrf_token_missing',
                        {'method': request.method, 'path': request.path},
                        severity='WARNING',
                        ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                    )
                    
                    return jsonify({
                        'error': 'CSRF token required',
                        'message': 'Token de securitate lipsă'
                    }), 403
                
                if not validate_csrf_token(csrf_token, session_token):
                    SecurityLogger.log_security_event(
                        'csrf_token_invalid',
                        {'method': request.method, 'path': request.path},
                        severity='ERROR',
                        ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                    )
                    
                    return jsonify({
                        'error': 'Invalid CSRF token',
                        'message': 'Token de securitate invalid'
                    }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json_input(required_fields: list = None, max_size: int = 1024):
    """
    JSON input validation decorator.
    
    Args:
        required_fields (list): List of required field names
        max_size (int): Maximum JSON payload size in KB
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'JSON required',
                    'message': 'Cererea trebuie să fie în format JSON'
                }), 400
            
            # Check payload size
            if request.content_length and request.content_length > max_size * 1024:
                SecurityLogger.log_security_event(
                    'json_payload_too_large',
                    {'content_length': request.content_length, 'max_size': max_size},
                    severity='WARNING',
                    ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                )
                
                return jsonify({
                    'error': 'Payload too large',
                    'message': f'Datele sunt prea mari. Mărimea maximă: {max_size}KB'
                }), 413
            
            try:
                data = request.get_json()
            except Exception as e:
                SecurityLogger.log_security_event(
                    'invalid_json',
                    {'error': str(e)},
                    severity='WARNING',
                    ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                )
                
                return jsonify({
                    'error': 'Invalid JSON',
                    'message': 'Format JSON invalid'
                }), 400
            
            # Validate required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'message': 'Câmpuri obligatorii lipsă',
                        'missing_fields': missing_fields
                    }), 400
            
            # Sanitize input data
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = SecurityValidator.sanitize_input(value)
            
            # Store sanitized data in g for use in view function
            g.json_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin_auth():
    """
    Admin authentication decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                SecurityLogger.log_security_event(
                    'admin_auth_missing',
                    {'path': request.path},
                    severity='WARNING',
                    ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                )
                
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Autentificare necesară'
                }), 401
            
            token = auth_header.split(' ')[1]
            
            # Validate admin token (implement your token validation logic)
            # This is a placeholder - implement actual JWT validation
            if not token or len(token) < 10:
                SecurityLogger.log_security_event(
                    'admin_auth_invalid',
                    {'path': request.path},
                    severity='ERROR',
                    ip_address=g.client_ip if hasattr(g, 'client_ip') else None
                )
                
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Token invalid'
                }), 401
            
            # Store admin info in g for use in view function
            g.admin_authenticated = True
            g.admin_token = token
            
            SecurityLogger.log_security_event(
                'admin_access',
                {'path': request.path},
                severity='INFO',
                ip_address=g.client_ip if hasattr(g, 'client_ip') else None
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_sensitive_operation(operation_type: str, data_type: str = None):
    """
    Decorator to log sensitive operations for compliance.
    
    Args:
        operation_type (str): Type of operation (create, read, update, delete)
        data_type (str): Type of data being accessed
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log the operation
            SecurityLogger.log_data_access(
                data_type=data_type or 'unknown',
                operation=operation_type,
                user_id=getattr(g, 'admin_token', None),
                ip_address=g.client_ip if hasattr(g, 'client_ip') else None,
                details={
                    'endpoint': request.endpoint,
                    'path': request.path,
                    'method': request.method
                }
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Rate limiting configurations for different endpoints
RATE_LIMITS = {
    'auth': 5,          # 5 login attempts per minute
    'api_general': 60,  # 60 API calls per minute
    'api_search': 30,   # 30 search requests per minute
    'api_order': 10,    # 10 order operations per minute
    'api_upload': 5,    # 5 file uploads per minute
}


def get_rate_limit_for_endpoint(endpoint: str) -> int:
    """Get appropriate rate limit for endpoint"""
    if 'auth' in endpoint or 'login' in endpoint:
        return RATE_LIMITS['auth']
    elif 'search' in endpoint:
        return RATE_LIMITS['api_search']
    elif 'order' in endpoint:
        return RATE_LIMITS['api_order']
    elif 'upload' in endpoint:
        return RATE_LIMITS['api_upload']
    else:
        return RATE_LIMITS['api_general']


def security_headers_only():
    """Middleware to add security headers without other security checks"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            return apply_security_headers(response)
        return decorated_function
    return decorator