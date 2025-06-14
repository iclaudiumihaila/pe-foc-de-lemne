"""
Performance monitoring and optimization utilities for Flask backend
"""
import time
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring for Flask applications"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_history = deque(maxlen=max_history)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'error_count': 0
        })
        self.start_time = datetime.now()
    
    def record_request(self, endpoint: str, method: str, duration: float, 
                      status_code: int, error: Optional[str] = None):
        """Record request performance metrics"""
        timestamp = datetime.now()
        
        # Record in history
        request_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'error': error
        }
        self.request_history.append(request_data)
        
        # Update endpoint statistics
        key = f"{method} {endpoint}"
        stats = self.endpoint_stats[key]
        
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        if status_code >= 400 or error:
            stats['error_count'] += 1
        
        logger.debug(f"Request recorded: {method} {endpoint} - {duration:.3f}s - {status_code}")
    
    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics for endpoints"""
        if endpoint:
            return dict(self.endpoint_stats.get(endpoint, {}))
        
        return {
            endpoint: dict(stats) 
            for endpoint, stats in self.endpoint_stats.items()
        }
    
    def get_slow_endpoints(self, threshold: float = 1.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest endpoints"""
        slow_endpoints = [
            {
                'endpoint': endpoint,
                'avg_time': stats['avg_time'],
                'max_time': stats['max_time'],
                'count': stats['count'],
                'error_rate': stats['error_count'] / stats['count'] if stats['count'] > 0 else 0
            }
            for endpoint, stats in self.endpoint_stats.items()
            if stats['avg_time'] > threshold
        ]
        
        # Sort by average time descending
        slow_endpoints.sort(key=lambda x: x['avg_time'], reverse=True)
        return slow_endpoints[:limit]
    
    def get_error_endpoints(self, min_error_rate: float = 0.1) -> List[Dict[str, Any]]:
        """Get endpoints with high error rates"""
        error_endpoints = []
        
        for endpoint, stats in self.endpoint_stats.items():
            if stats['count'] > 0:
                error_rate = stats['error_count'] / stats['count']
                if error_rate >= min_error_rate:
                    error_endpoints.append({
                        'endpoint': endpoint,
                        'error_rate': error_rate,
                        'error_count': stats['error_count'],
                        'total_count': stats['count'],
                        'avg_time': stats['avg_time']
                    })
        
        # Sort by error rate descending
        error_endpoints.sort(key=lambda x: x['error_rate'], reverse=True)
        return error_endpoints
    
    def get_recent_requests(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent requests within specified time window"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_requests = [
            req for req in self.request_history
            if req['timestamp'] > cutoff_time
        ]
        
        return recent_requests
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        total_requests = sum(stats['count'] for stats in self.endpoint_stats.values())
        total_errors = sum(stats['error_count'] for stats in self.endpoint_stats.values())
        
        return {
            'uptime_seconds': uptime,
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': total_errors / total_requests if total_requests > 0 else 0,
            'requests_per_second': total_requests / uptime if uptime > 0 else 0,
            'endpoints_monitored': len(self.endpoint_stats),
            'system_metrics': self.get_system_metrics()
        }


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _performance_monitor


def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        error = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            duration = time.time() - start_time
            
            # Record performance metric
            monitor = get_performance_monitor()
            
            # For Flask routes, extract endpoint info
            from flask import request, has_request_context
            if has_request_context():
                endpoint = request.endpoint or func.__name__
                method = request.method
                status_code = 500 if error else 200
                
                monitor.record_request(endpoint, method, duration, status_code, error)
            
            logger.debug(f"Function {func.__name__} executed in {duration:.3f}s")
    
    return wrapper


def time_function(func):
    """Simple timing decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.info(f"⏱️ {func.__name__} executed in {duration:.3f}s")
        return result
    
    return wrapper


class DatabaseQueryMonitor:
    """Monitor database query performance"""
    
    def __init__(self):
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
        self.slow_queries = deque(maxlen=100)
    
    def record_query(self, query: str, duration: float, params: Optional[Dict] = None):
        """Record database query performance"""
        # Normalize query for statistics (remove dynamic values)
        normalized_query = self._normalize_query(query)
        
        stats = self.query_stats[normalized_query]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        # Record slow queries (>100ms)
        if duration > 0.1:
            self.slow_queries.append({
                'query': query,
                'duration': duration,
                'params': params,
                'timestamp': datetime.now()
            })
            logger.warning(f"Slow query detected: {duration:.3f}s - {query[:100]}...")
        
        logger.debug(f"Query recorded: {duration:.3f}s - {normalized_query[:50]}...")
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing dynamic values"""
        import re
        
        # Remove string literals
        query = re.sub(r"'[^']*'", "'?'", query)
        
        # Remove numeric literals
        query = re.sub(r'\b\d+\b', '?', query)
        
        # Remove IN clauses with multiple values
        query = re.sub(r'IN\s*\([^)]+\)', 'IN (?)', query, flags=re.IGNORECASE)
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        return query
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries"""
        sorted_queries = sorted(
            self.slow_queries,
            key=lambda x: x['duration'],
            reverse=True
        )
        return list(sorted_queries[:limit])
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return dict(self.query_stats)


# Global database monitor instance
_db_monitor = DatabaseQueryMonitor()


def get_db_monitor() -> DatabaseQueryMonitor:
    """Get global database monitor instance"""
    return _db_monitor


def monitor_query(query: str, params: Optional[Dict] = None):
    """Context manager for monitoring database queries"""
    class QueryMonitor:
        def __init__(self, query: str, params: Optional[Dict] = None):
            self.query = query
            self.params = params
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = time.time() - self.start_time
                get_db_monitor().record_query(self.query, duration, self.params)
    
    return QueryMonitor(query, params)


class MemoryMonitor:
    """Monitor memory usage"""
    
    def __init__(self):
        self.memory_snapshots = deque(maxlen=100)
        self.threshold_mb = 500  # Alert threshold in MB
    
    def take_snapshot(self, label: str = ""):
        """Take memory usage snapshot"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            snapshot = {
                'timestamp': datetime.now(),
                'label': label,
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
            
            self.memory_snapshots.append(snapshot)
            
            # Alert on high memory usage
            if snapshot['rss_mb'] > self.threshold_mb:
                logger.warning(f"High memory usage: {snapshot['rss_mb']:.1f} MB ({snapshot['percent']:.1f}%)")
            
            return snapshot
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")
            return None
    
    def get_memory_trend(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get memory usage trend"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_snapshots = [
            snapshot for snapshot in self.memory_snapshots
            if snapshot['timestamp'] > cutoff_time
        ]
        
        return recent_snapshots
    
    def detect_memory_leak(self, threshold_increase: float = 50.0) -> bool:
        """Detect potential memory leaks"""
        if len(self.memory_snapshots) < 10:
            return False
        
        # Compare first and last 5 snapshots
        first_5 = list(self.memory_snapshots)[:5]
        last_5 = list(self.memory_snapshots)[-5:]
        
        avg_first = sum(s['rss_mb'] for s in first_5) / len(first_5)
        avg_last = sum(s['rss_mb'] for s in last_5) / len(last_5)
        
        increase = avg_last - avg_first
        
        if increase > threshold_increase:
            logger.warning(f"Potential memory leak detected: {increase:.1f} MB increase")
            return True
        
        return False


# Global memory monitor instance
_memory_monitor = MemoryMonitor()


def get_memory_monitor() -> MemoryMonitor:
    """Get global memory monitor instance"""
    return _memory_monitor


def monitor_memory(label: str = ""):
    """Decorator to monitor memory usage of functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_memory_monitor()
            
            # Take snapshot before execution
            monitor.take_snapshot(f"{label}_before_{func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Take snapshot after execution
                monitor.take_snapshot(f"{label}_after_{func.__name__}")
        
        return wrapper
    return decorator