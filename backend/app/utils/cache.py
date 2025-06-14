"""
Caching utilities for performance optimization
"""
import json
import time
import hashlib
from functools import wraps
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InMemoryCache:
    """
    Simple in-memory cache implementation with TTL support
    """
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
            max_size: Maximum number of cache entries
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        return time.time() > entry['expires_at']
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
            
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_oldest(self):
        """Evict oldest entries when cache is full"""
        if len(self.cache) >= self.max_size:
            # Sort by timestamp and remove oldest
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]['timestamp']
            )[:len(self.cache) - self.max_size + 1]
            
            for key in oldest_keys:
                del self.cache[key]
                
            logger.debug(f"Evicted {len(oldest_keys)} oldest cache entries")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set cache entry
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        # Cleanup expired entries before adding new ones
        self._cleanup_expired()
        
        # Evict oldest entries if cache is full
        self._evict_oldest()
        
        ttl = ttl or self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'expires_at': time.time() + ttl,
            'hit_count': 0
        }
        
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache entry
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            logger.debug(f"Cache MISS: {key}")
            return None
            
        entry = self.cache[key]
        
        if self._is_expired(entry):
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None
            
        # Update hit count
        entry['hit_count'] += 1
        logger.debug(f"Cache HIT: {key} (hits: {entry['hit_count']})")
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache DELETE: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._cleanup_expired()
        
        total_hits = sum(entry['hit_count'] for entry in self.cache.values())
        
        return {
            'total_entries': len(self.cache),
            'max_size': self.max_size,
            'total_hits': total_hits,
            'memory_usage_estimate': sum(
                len(str(entry['value'])) for entry in self.cache.values()
            )
        }


# Global cache instance
_cache_instance = InMemoryCache()


def get_cache() -> InMemoryCache:
    """Get global cache instance"""
    return _cache_instance


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        SHA256 hash of serialized arguments
    """
    # Create a deterministic string from arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @cache_result(ttl=600, key_prefix="products")
        def get_products():
            return expensive_operation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cache = get_cache()
            cached_result = cache.get(func_key)
            
            if cached_result is not None:
                logger.debug(f"Returning cached result for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                cache.set(func_key, result, ttl)
                logger.debug(f"Cached result for {func.__name__} (TTL: {ttl}s)")
                return result
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator


def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """
    Decorator to cache Flask response
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @app.route('/products')
        @cache_response(ttl=600, key_prefix="products")
        def get_products():
            return jsonify(products)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Generate cache key based on request
            request_key = f"{request.method}:{request.path}:{request.query_string.decode()}"
            cache_key = f"{key_prefix}:{func.__name__}:{generate_cache_key(request_key)}"
            
            # Try to get from cache
            cache = get_cache()
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                logger.debug(f"Returning cached response for {request.path}")
                response = jsonify(cached_response)
                response.headers['X-Cache'] = 'HIT'
                return response
            
            # Execute function and cache response
            try:
                result = func(*args, **kwargs)
                
                # Extract data from response for caching
                if hasattr(result, 'get_json'):
                    cache_data = result.get_json()
                    cache.set(cache_key, cache_data, ttl)
                    result.headers['X-Cache'] = 'MISS'
                    logger.debug(f"Cached response for {request.path} (TTL: {ttl}s)")
                
                return result
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Pattern to match (supports wildcards)
        
    Returns:
        Number of entries invalidated
    """
    import fnmatch
    
    cache = get_cache()
    keys_to_delete = []
    
    for key in cache.cache.keys():
        if fnmatch.fnmatch(key, pattern):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)
    
    logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
    return len(keys_to_delete)


def warm_cache(data_loaders: Dict[str, callable], ttl: int = 3600):
    """
    Warm cache with frequently accessed data
    
    Args:
        data_loaders: Dictionary of cache_key -> loader_function
        ttl: Time-to-live for cached data
    """
    cache = get_cache()
    
    for cache_key, loader_func in data_loaders.items():
        try:
            logger.info(f"Warming cache: {cache_key}")
            data = loader_func()
            cache.set(cache_key, data, ttl)
        except Exception as e:
            logger.error(f"Error warming cache for {cache_key}: {e}")


class CacheMetrics:
    """Cache performance metrics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.requests = 0
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.start_time = datetime.now()
    
    def record_hit(self):
        """Record cache hit"""
        self.requests += 1
        self.hits += 1
    
    def record_miss(self):
        """Record cache miss"""
        self.requests += 1
        self.misses += 1
    
    def record_error(self):
        """Record cache error"""
        self.errors += 1
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        if self.requests == 0:
            return 0.0
        return self.hits / self.requests
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.requests,
            'hits': self.hits,
            'misses': self.misses,
            'errors': self.errors,
            'hit_rate': self.get_hit_rate(),
            'requests_per_second': self.requests / uptime if uptime > 0 else 0
        }


# Global metrics instance
_metrics_instance = CacheMetrics()


def get_cache_metrics() -> CacheMetrics:
    """Get global cache metrics instance"""
    return _metrics_instance