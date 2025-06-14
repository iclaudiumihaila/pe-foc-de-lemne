"""
Response compression middleware for Flask
"""
import gzip
import brotli
import json
from io import BytesIO
from flask import request, Response, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CompressionMiddleware:
    """Flask middleware for response compression"""
    
    def __init__(self, app=None, compression_level=6, min_size=500):
        """
        Initialize compression middleware
        
        Args:
            app: Flask application instance
            compression_level: Compression level (1-9, higher = better compression)
            min_size: Minimum response size to compress (bytes)
        """
        self.compression_level = compression_level
        self.min_size = min_size
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.config.setdefault('COMPRESS_MIMETYPES', [
            'text/html',
            'text/css',
            'text/xml',
            'text/javascript',
            'text/plain',
            'application/json',
            'application/javascript',
            'application/xml+rss',
            'application/atom+xml',
            'image/svg+xml'
        ])
        
        app.config.setdefault('COMPRESS_LEVEL', self.compression_level)
        app.config.setdefault('COMPRESS_MIN_SIZE', self.min_size)
        
        # Register after_request handler
        app.after_request(self.compress_response)
    
    def should_compress(self, response):
        """Determine if response should be compressed"""
        # Don't compress if already compressed
        if response.headers.get('Content-Encoding'):
            return False
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        allowed_types = current_app.config['COMPRESS_MIMETYPES']
        
        if not any(content_type.startswith(mime_type) for mime_type in allowed_types):
            return False
        
        # Check response size
        if len(response.get_data()) < current_app.config['COMPRESS_MIN_SIZE']:
            return False
        
        # Check if client accepts compression
        accept_encoding = request.headers.get('Accept-Encoding', '').lower()
        if 'gzip' not in accept_encoding and 'br' not in accept_encoding:
            return False
        
        return True
    
    def get_compression_method(self):
        """Get preferred compression method based on client support"""
        accept_encoding = request.headers.get('Accept-Encoding', '').lower()
        
        # Prefer Brotli if supported (better compression)
        if 'br' in accept_encoding:
            return 'br'
        elif 'gzip' in accept_encoding:
            return 'gzip'
        
        return None
    
    def compress_data(self, data, method):
        """Compress data using specified method"""
        if method == 'br':
            return brotli.compress(data, quality=self.compression_level)
        elif method == 'gzip':
            buffer = BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=self.compression_level) as f:
                f.write(data)
            return buffer.getvalue()
        
        return data
    
    def compress_response(self, response):
        """Compress Flask response if applicable"""
        try:
            if not self.should_compress(response):
                return response
            
            compression_method = self.get_compression_method()
            if not compression_method:
                return response
            
            # Get original data
            original_data = response.get_data()
            original_size = len(original_data)
            
            # Compress data
            compressed_data = self.compress_data(original_data, compression_method)
            compressed_size = len(compressed_data)
            
            # Only use compression if it actually reduces size
            if compressed_size < original_size:
                response.set_data(compressed_data)
                response.headers['Content-Encoding'] = compression_method
                response.headers['Content-Length'] = str(compressed_size)
                
                # Add vary header
                vary = response.headers.get('Vary', '')
                if 'Accept-Encoding' not in vary:
                    response.headers['Vary'] = f"{vary}, Accept-Encoding".strip(', ')
                
                # Calculate compression ratio
                ratio = (1 - compressed_size / original_size) * 100
                logger.debug(f"Response compressed: {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)")
            
            return response
            
        except Exception as e:
            logger.error(f"Error compressing response: {e}")
            return response


def compress_json_response(data, status_code=200, headers=None):
    """
    Create compressed JSON response
    
    Args:
        data: Data to serialize as JSON
        status_code: HTTP status code
        headers: Additional headers
        
    Returns:
        Flask Response object
    """
    try:
        # Serialize to JSON
        json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        
        # Create response
        response = Response(
            json_data,
            status=status_code,
            mimetype='application/json',
            headers=headers
        )
        
        # Add UTF-8 encoding
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating JSON response: {e}")
        return Response(
            json.dumps({'error': 'Eroare la crearea răspunsului'}),
            status=500,
            mimetype='application/json'
        )


def minify_json_response(func):
    """Decorator to minify JSON responses"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If result is a dict, create minified JSON response
            if isinstance(result, dict):
                return compress_json_response(result)
            
            # If result is a tuple with (data, status_code)
            elif isinstance(result, tuple) and len(result) >= 2:
                data, status_code = result[:2]
                headers = result[2] if len(result) > 2 else None
                
                if isinstance(data, dict):
                    return compress_json_response(data, status_code, headers)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in minify_json_response: {e}")
            return result
    
    return wrapper


class StaticFileCompression:
    """Handle static file compression"""
    
    def __init__(self, app=None, static_folder=None):
        self.static_folder = static_folder
        self.compressed_files = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.static_folder = self.static_folder or app.static_folder
        
        # Pre-compress static files if enabled
        if app.config.get('PRECOMPRESS_STATIC_FILES', False):
            self.precompress_static_files()
    
    def precompress_static_files(self):
        """Pre-compress static files for better performance"""
        import os
        from pathlib import Path
        
        if not self.static_folder or not os.path.exists(self.static_folder):
            return
        
        static_path = Path(self.static_folder)
        
        # File extensions to compress
        compressible_extensions = {'.js', '.css', '.html', '.svg', '.json', '.xml'}
        
        for file_path in static_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in compressible_extensions:
                try:
                    # Read original file
                    with open(file_path, 'rb') as f:
                        original_data = f.read()
                    
                    # Skip small files
                    if len(original_data) < 1024:  # 1KB
                        continue
                    
                    # Compress with gzip
                    gzip_path = file_path.with_suffix(file_path.suffix + '.gz')
                    if not gzip_path.exists():
                        with gzip.open(gzip_path, 'wb', compresslevel=9) as f:
                            f.write(original_data)
                        logger.debug(f"Pre-compressed: {file_path} -> {gzip_path}")
                    
                    # Compress with brotli if available
                    try:
                        br_path = file_path.with_suffix(file_path.suffix + '.br')
                        if not br_path.exists():
                            compressed_data = brotli.compress(original_data, quality=11)
                            with open(br_path, 'wb') as f:
                                f.write(compressed_data)
                            logger.debug(f"Pre-compressed: {file_path} -> {br_path}")
                    except ImportError:
                        pass  # Brotli not available
                        
                except Exception as e:
                    logger.error(f"Error pre-compressing {file_path}: {e}")


def setup_compression(app, **kwargs):
    """
    Setup compression for Flask app
    
    Args:
        app: Flask application
        **kwargs: Additional configuration options
    """
    # Initialize compression middleware
    compression = CompressionMiddleware(app, **kwargs)
    
    # Initialize static file compression
    static_compression = StaticFileCompression(app)
    
    # Add performance headers
    @app.after_request
    def add_performance_headers(response):
        """Add performance-related headers"""
        # Cache control for static files
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    logger.info("Compression middleware configured")
    return compression