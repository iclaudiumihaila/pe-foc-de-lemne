"""
Rate Limiting Middleware for Local Producer Web Application

This module provides flexible rate limiting middleware that can be applied
to any endpoint with configurable limits and time windows. Uses MongoDB
for distributed rate limiting with automatic TTL cleanup.
"""

import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify, current_app
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.database import get_database
from app.utils.error_handlers import ValidationError


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Flexible rate limiting service for API endpoints.
    
    Supports different rate limits for different endpoints with MongoDB
    storage and automatic TTL cleanup. Uses sliding window algorithm
    for accurate rate limiting.
    """
    
    # Default rate limit configurations
    DEFAULT_LIMITS = {
        'sms_verify': {
            'limit': 10,           # 10 requests per window
            'window_seconds': 3600, # 1 hour window
            'description': 'SMS verification endpoint'
        },
        'sms_confirm': {
            'limit': 50,           # 50 attempts per window
            'window_seconds': 3600, # 1 hour window
            'description': 'SMS confirmation endpoint'
        },
        'default': {
            'limit': 100,          # 100 requests per window
            'window_seconds': 3600, # 1 hour window
            'description': 'Default endpoint limit'
        }
    }
    
    def __init__(self):
        """Initialize rate limiter with MongoDB connection."""
        self.db = None
        self.rate_limit_collection: Optional[Collection] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize MongoDB collections and indexes for rate limiting."""
        try:
            self.db = get_database()
            self.rate_limit_collection = self.db.api_rate_limits
            
            # Create TTL index for automatic cleanup
            self.rate_limit_collection.create_index(
                "expires_at", 
                expireAfterSeconds=0,
                background=True
            )
            
            # Create compound index for efficient queries
            self.rate_limit_collection.create_index(
                [("key", 1), ("endpoint", 1)],
                background=True
            )
            
            logger.info("Rate limiter MongoDB collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter database: {str(e)}")
            # Don't throw error - allow graceful degradation
            self.db = None
            self.rate_limit_collection = None
            # Graceful degradation without throwing exception
    
    def _extract_phone_number(self, request_data: Dict) -> Optional[str]:
        """
        Extract phone number from request data.
        
        Args:
            request_data: Request JSON data
            
        Returns:
            str: Normalized phone number or None if not found
        """
        if not request_data:
            return None
            
        phone_number = request_data.get('phone_number')
        if not phone_number:
            return None
            
        # Normalize phone number to E.164 format
        return self._normalize_phone_number(phone_number)
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normalize phone number to consistent format.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            str: Normalized phone number
        """
        if not phone_number:
            return ""
            
        # Remove all non-digits except leading +
        clean_phone = re.sub(r'[^\d+]', '', phone_number)
        
        # Ensure E.164 format
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
            
        return clean_phone
    
    def _get_rate_limit_key(self, request_data: Dict, endpoint: str) -> str:
        """
        Generate rate limit key based on request data and endpoint.
        
        For SMS endpoints, use phone number as key.
        For other endpoints, use IP address or user ID.
        
        Args:
            request_data: Request JSON data
            endpoint: Endpoint name
            
        Returns:
            str: Rate limit key
        """
        # For SMS endpoints, use phone number
        if endpoint.startswith('sms_'):
            phone_number = self._extract_phone_number(request_data)
            if phone_number:
                return f"phone:{phone_number}"
        
        # For other endpoints, use IP address as fallback
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        return f"ip:{client_ip}"
    
    def _get_rate_limit_config(self, endpoint: str, custom_limit: Optional[int] = None, 
                              custom_window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get rate limit configuration for endpoint.
        
        Args:
            endpoint: Endpoint name
            custom_limit: Custom request limit override
            custom_window: Custom window seconds override
            
        Returns:
            dict: Rate limit configuration
        """
        # Start with endpoint-specific config or default
        config = self.DEFAULT_LIMITS.get(endpoint, self.DEFAULT_LIMITS['default']).copy()
        
        # Apply custom overrides
        if custom_limit is not None:
            config['limit'] = custom_limit
        if custom_window is not None:
            config['window_seconds'] = custom_window
            
        # Check for environment variable overrides
        try:
            env_limit = current_app.config.get(f'RATE_LIMIT_{endpoint.upper()}_LIMIT')
            env_window = current_app.config.get(f'RATE_LIMIT_{endpoint.upper()}_WINDOW')
            
            if env_limit:
                config['limit'] = int(env_limit)
            if env_window:
                config['window_seconds'] = int(env_window)
        except (ValueError, AttributeError):
            # Invalid config values, use defaults
            pass
            
        return config
    
    def check_rate_limit(self, key: str, endpoint: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Rate limit key (phone number, IP, etc.)
            endpoint: Endpoint name
            limit: Request limit
            window_seconds: Time window in seconds
            
        Returns:
            dict: Rate limit check result
        """
        try:
            if self.rate_limit_collection is None:
                # Database unavailable, allow request
                return {
                    'allowed': True,
                    'reason': 'rate_limiter_unavailable'
                }
            
            # Calculate window start time
            window_start = datetime.utcnow() - timedelta(seconds=window_seconds)
            
            # Count requests in current window
            current_count = self.rate_limit_collection.count_documents({
                'key': key,
                'endpoint': endpoint,
                'created_at': {'$gte': window_start}
            })
            
            # Check if limit exceeded
            if current_count >= limit:
                # Get oldest request for reset time calculation
                oldest_request = self.rate_limit_collection.find_one({
                    'key': key,
                    'endpoint': endpoint,
                    'created_at': {'$gte': window_start}
                }, sort=[('created_at', 1)])
                
                if oldest_request:
                    reset_time = oldest_request['created_at'] + timedelta(seconds=window_seconds)
                    reset_in_seconds = max(0, (reset_time - datetime.utcnow()).total_seconds())
                else:
                    reset_time = datetime.utcnow() + timedelta(seconds=window_seconds)
                    reset_in_seconds = window_seconds
                
                return {
                    'allowed': False,
                    'current_count': current_count,
                    'limit': limit,
                    'window_seconds': window_seconds,
                    'reset_at': reset_time.isoformat() + 'Z',
                    'reset_in_seconds': int(reset_in_seconds),
                    'reset_in_minutes': int(reset_in_seconds / 60),
                    'reason': 'rate_limit_exceeded'
                }
            
            return {
                'allowed': True,
                'current_count': current_count,
                'limit': limit,
                'remaining': limit - current_count,
                'window_seconds': window_seconds
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # On error, allow request to avoid blocking legitimate users
            # Do not throw exception - graceful degradation
            return {
                'allowed': True,
                'reason': 'rate_limiter_error'
            }
    
    def record_request(self, key: str, endpoint: str, window_seconds: int):
        """
        Record a request for rate limiting tracking.
        
        Args:
            key: Rate limit key
            endpoint: Endpoint name
            window_seconds: Time window for TTL
        """
        try:
            if self.rate_limit_collection is None:
                return
                
            now = datetime.utcnow()
            
            # Create rate limit record with TTL
            record = {
                'key': key,
                'endpoint': endpoint,
                'created_at': now,
                'expires_at': now + timedelta(seconds=window_seconds)
            }
            
            self.rate_limit_collection.insert_one(record)
            
        except Exception as e:
            logger.error(f"Error recording rate limit request: {str(e)}")
            # Do not throw exception - graceful degradation
    
    def get_rate_limit_info(self, key: str, endpoint: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """
        Get detailed rate limit information for a key.
        
        Args:
            key: Rate limit key
            endpoint: Endpoint name
            limit: Request limit
            window_seconds: Time window in seconds
            
        Returns:
            dict: Detailed rate limit information
        """
        try:
            if self.rate_limit_collection is None:
                return {
                    'attempts_count': 0,
                    'rate_limit': limit,
                    'window_seconds': window_seconds,
                    'reset_at': None,
                    'reset_in_seconds': 0,
                    'reset_in_minutes': 0,
                    'is_rate_limited': False
                }
            
            # Calculate window start time
            window_start = datetime.utcnow() - timedelta(seconds=window_seconds)
            
            # Get all requests in current window
            requests = list(self.rate_limit_collection.find({
                'key': key,
                'endpoint': endpoint,
                'created_at': {'$gte': window_start}
            }).sort('created_at', 1))
            
            attempts_count = len(requests)
            
            if requests:
                oldest_request = requests[0]['created_at']
                reset_time = oldest_request + timedelta(seconds=window_seconds)
                reset_in_seconds = max(0, (reset_time - datetime.utcnow()).total_seconds())
            else:
                reset_time = None
                reset_in_seconds = 0
            
            return {
                'attempts_count': attempts_count,
                'rate_limit': limit,
                'window_seconds': window_seconds,
                'window_hours': window_seconds / 3600,
                'reset_at': reset_time.isoformat() + 'Z' if reset_time else None,
                'reset_in_seconds': int(reset_in_seconds),
                'reset_in_minutes': int(reset_in_seconds / 60),
                'is_rate_limited': attempts_count >= limit
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit info: {str(e)}")
            # Do not throw exception - return safe defaults
            return {
                'attempts_count': 0,
                'rate_limit': limit,
                'window_seconds': window_seconds,
                'reset_at': None,
                'reset_in_seconds': 0,
                'reset_in_minutes': 0,
                'is_rate_limited': False
            }


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def rate_limit(endpoint: str, limit: Optional[int] = None, window_seconds: Optional[int] = None):
    """
    Decorator for applying rate limiting to Flask endpoints.
    
    Args:
        endpoint: Endpoint name for rate limit configuration
        limit: Custom request limit (overrides default)
        window_seconds: Custom time window (overrides default)
        
    Returns:
        Decorated function with rate limiting
        
    Example:
        @rate_limit('sms_verify', limit=10, window_seconds=3600)
        @app.route('/api/sms/verify', methods=['POST'])
        def send_verification():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get rate limiter instance
            limiter = get_rate_limiter()
            
            # Get rate limit configuration
            config = limiter._get_rate_limit_config(endpoint, limit, window_seconds)
            
            # Get request data for key extraction
            try:
                request_data = request.get_json() or {}
            except Exception:
                request_data = {}
            
            # Generate rate limit key
            rate_limit_key = limiter._get_rate_limit_key(request_data, endpoint)
            
            # Check rate limit
            check_result = limiter.check_rate_limit(
                rate_limit_key, 
                endpoint, 
                config['limit'], 
                config['window_seconds']
            )
            
            # Handle rate limit exceeded
            if not check_result['allowed']:
                # Log rate limit violation
                masked_key = rate_limit_key
                if rate_limit_key.startswith('phone:'):
                    phone = rate_limit_key.split(':', 1)[1]
                    masked_key = f"phone:****{phone[-4:]}" if len(phone) >= 4 else "phone:****"
                
                logger.warning(f"Rate limit exceeded for {masked_key} on endpoint {endpoint}")
                
                # Get detailed rate limit info
                rate_info = limiter.get_rate_limit_info(
                    rate_limit_key,
                    endpoint,
                    config['limit'],
                    config['window_seconds']
                )
                
                # Return rate limit error response
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': f"Rate limit exceeded. Try again in {rate_info['reset_in_minutes']} minutes.",
                        'details': {
                            'endpoint': endpoint,
                            'limit': config['limit'],
                            'window_hours': config['window_seconds'] / 3600,
                            'attempts_count': rate_info['attempts_count'],
                            'reset_in_seconds': rate_info['reset_in_seconds'],
                            'reset_in_minutes': rate_info['reset_in_minutes'],
                            'reset_at': rate_info['reset_at']
                        }
                    }
                }
                
                # Add rate limit headers
                response = jsonify(error_response)
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(config['limit'])
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset_in_seconds'])
                response.headers['Retry-After'] = str(rate_info['reset_in_seconds'])
                
                return response
            
            # Record this request for rate limiting
            limiter.record_request(
                rate_limit_key,
                endpoint,
                config['window_seconds']
            )
            
            # Add rate limit headers to successful responses
            result = f(*args, **kwargs)
            
            # Add rate limit info to response headers if result is a Response
            if hasattr(result, 'headers'):
                result.headers['X-RateLimit-Limit'] = str(config['limit'])
                result.headers['X-RateLimit-Remaining'] = str(check_result.get('remaining', 0))
                result.headers['X-RateLimit-Reset'] = str(config['window_seconds'])
            
            return result
            
        return decorated_function
    return decorator


def get_endpoint_rate_limit_info(endpoint: str, request_data: Dict) -> Dict[str, Any]:
    """
    Get rate limit information for an endpoint and request data.
    
    Args:
        endpoint: Endpoint name
        request_data: Request JSON data
        
    Returns:
        dict: Rate limit information
    """
    limiter = get_rate_limiter()
    config = limiter._get_rate_limit_config(endpoint)
    rate_limit_key = limiter._get_rate_limit_key(request_data, endpoint)
    
    return limiter.get_rate_limit_info(
        rate_limit_key,
        endpoint,
        config['limit'],
        config['window_seconds']
    )