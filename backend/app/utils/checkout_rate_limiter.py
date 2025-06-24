"""
Checkout Rate Limiter
Task ID: 07

Simple rate limiter for checkout flow with Redis support and in-memory fallback.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict
import redis
import os

logger = logging.getLogger(__name__)


class CheckoutRateLimiter:
    """Rate limiter specifically for checkout flow operations"""
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.memory_store: Dict[str, list] = defaultdict(list)
        
        # Rate limit configurations (matching our architecture)
        self.limits = {
            'sms_per_phone_per_day': {'max': 3, 'window': 86400},
            'sms_per_ip_per_hour': {'max': 5, 'window': 3600},
            'verify_attempts_per_code': {'max': 5, 'window': 300},
            'addresses_per_customer': {'max': 50, 'window': None}  # No time window
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection if available"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("Checkout rate limiter connected to Redis")
            return client
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {str(e)}")
            return None
    
    def _get_key(self, limit_type: str, identifier: str) -> str:
        """Generate key for rate limit storage"""
        return f"checkout_rate:{limit_type}:{identifier}"
    
    def _clean_memory_store(self, key: str, window: int):
        """Remove expired entries from memory store"""
        if window is None:  # No expiry
            return
        
        now = time.time()
        cutoff = now - window
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if timestamp > cutoff
        ]
    
    def check_limit(self, limit_type: str, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if action is within rate limit
        
        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        if limit_type not in self.limits:
            logger.warning(f"Unknown rate limit type: {limit_type}")
            return True, {'error': 'Unknown limit type'}
        
        config = self.limits[limit_type]
        max_requests = config['max']
        window = config['window']
        key = self._get_key(limit_type, identifier)
        now = time.time()
        
        try:
            if self.redis_client:
                # Redis implementation
                if window is None:
                    # For non-expiring limits (like address count)
                    current_count = int(self.redis_client.get(key) or 0)
                    
                    if current_count >= max_requests:
                        return False, {
                            'remaining': 0,
                            'limit': max_requests,
                            'current': current_count
                        }
                    
                    return True, {
                        'remaining': max_requests - current_count,
                        'limit': max_requests,
                        'current': current_count
                    }
                
                else:
                    # For time-windowed limits
                    pipe = self.redis_client.pipeline()
                    pipe.zremrangebyscore(key, 0, now - window)
                    pipe.zcard(key)
                    results = pipe.execute()
                    
                    current_count = results[1]
                    
                    if current_count >= max_requests:
                        # Get oldest timestamp for reset time
                        oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                        if oldest:
                            reset_time = oldest[0][1] + window
                        else:
                            reset_time = now + window
                        
                        return False, {
                            'remaining': 0,
                            'reset_time': datetime.fromtimestamp(reset_time),
                            'limit': max_requests,
                            'window_hours': window / 3600
                        }
                    
                    return True, {
                        'remaining': max_requests - current_count,
                        'limit': max_requests,
                        'window_hours': window / 3600
                    }
            
            else:
                # In-memory fallback
                if window is None:
                    current_count = len(self.memory_store[key])
                    
                    if current_count >= max_requests:
                        return False, {
                            'remaining': 0,
                            'limit': max_requests,
                            'current': current_count
                        }
                    
                    return True, {
                        'remaining': max_requests - current_count,
                        'limit': max_requests,
                        'current': current_count
                    }
                
                else:
                    self._clean_memory_store(key, window)
                    current_count = len(self.memory_store[key])
                    
                    if current_count >= max_requests:
                        if self.memory_store[key]:
                            reset_time = self.memory_store[key][0] + window
                        else:
                            reset_time = now + window
                        
                        return False, {
                            'remaining': 0,
                            'reset_time': datetime.fromtimestamp(reset_time),
                            'limit': max_requests,
                            'window_hours': window / 3600
                        }
                    
                    return True, {
                        'remaining': max_requests - current_count,
                        'limit': max_requests,
                        'window_hours': window / 3600
                    }
                
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            # Allow request on error
            return True, {'error': str(e)}
    
    def record_usage(self, limit_type: str, identifier: str, increment: int = 1):
        """Record usage for rate limiting"""
        if limit_type not in self.limits:
            return
        
        config = self.limits[limit_type]
        window = config['window']
        key = self._get_key(limit_type, identifier)
        now = time.time()
        
        try:
            if self.redis_client:
                if window is None:
                    # For non-expiring limits
                    self.redis_client.incrby(key, increment)
                else:
                    # For time-windowed limits
                    self.redis_client.zadd(key, {str(now): now})
                    self.redis_client.expire(key, window)
            else:
                # In-memory fallback
                if window is None:
                    # Just append for counting
                    for _ in range(increment):
                        self.memory_store[key].append(now)
                else:
                    self.memory_store[key].append(now)
        
        except Exception as e:
            logger.error(f"Error recording usage: {str(e)}")
    
    def get_error_message(self, limit_type: str, info: Dict[str, any]) -> Dict[str, str]:
        """Get user-friendly error message in Romanian"""
        messages = {
            'sms_per_phone_per_day': {
                'code': 'SMS_LIMIT_EXCEEDED',
                'message': f"Ați depășit limita zilnică de SMS-uri ({info.get('limit', 3)} pe zi). "
                          f"Încercați din nou mâine."
            },
            'sms_per_ip_per_hour': {
                'code': 'IP_LIMIT_EXCEEDED',
                'message': "Prea multe cereri de la această adresă. Încercați din nou într-o oră."
            },
            'verify_attempts_per_code': {
                'code': 'INVALID_VERIFICATION_CODE',
                'message': "Prea multe încercări. Solicitați un cod nou."
            },
            'addresses_per_customer': {
                'code': 'ADDRESS_LIMIT_EXCEEDED',
                'message': f"Ați atins limita maximă de {info.get('limit', 50)} adrese salvate."
            }
        }
        
        default = {
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': "Limită depășită. Încercați din nou mai târziu."
        }
        
        error_info = messages.get(limit_type, default)
        
        # Add reset time if available
        if 'reset_time' in info:
            reset_time = info['reset_time']
            if isinstance(reset_time, datetime):
                # Show time for today's limits
                if reset_time.date() == datetime.now().date():
                    error_info['message'] += f" Încercați după {reset_time.strftime('%H:%M')}."
                else:
                    error_info['message'] += f" Încercați mâine."
        
        return error_info
    
    def reset_limit(self, limit_type: str, identifier: str):
        """Reset rate limit for testing purposes"""
        key = self._get_key(limit_type, identifier)
        
        if self.redis_client:
            self.redis_client.delete(key)
        else:
            self.memory_store[key] = []
        
        logger.info(f"Reset rate limit {limit_type} for {identifier}")


# Global instance
_rate_limiter: Optional[CheckoutRateLimiter] = None


def get_checkout_rate_limiter() -> CheckoutRateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = CheckoutRateLimiter()
    return _rate_limiter


# Convenience functions
def check_sms_limit_phone(phone: str) -> Tuple[bool, Dict[str, any]]:
    """Check daily SMS limit for phone"""
    limiter = get_checkout_rate_limiter()
    return limiter.check_limit('sms_per_phone_per_day', phone)


def check_sms_limit_ip(ip: str) -> Tuple[bool, Dict[str, any]]:
    """Check hourly SMS limit for IP"""
    limiter = get_checkout_rate_limiter()
    return limiter.check_limit('sms_per_ip_per_hour', ip)


def check_verify_attempts(phone: str, code: str) -> Tuple[bool, Dict[str, any]]:
    """Check verification attempts for code"""
    limiter = get_checkout_rate_limiter()
    return limiter.check_limit('verify_attempts_per_code', f"{phone}:{code}")


def record_sms_sent(phone: str, ip: str):
    """Record that SMS was sent"""
    limiter = get_checkout_rate_limiter()
    limiter.record_usage('sms_per_phone_per_day', phone)
    limiter.record_usage('sms_per_ip_per_hour', ip)


def record_verify_attempt(phone: str, code: str):
    """Record verification attempt"""
    limiter = get_checkout_rate_limiter()
    limiter.record_usage('verify_attempts_per_code', f"{phone}:{code}")