"""
Security Utilities for Local Producer Web Application

This module provides comprehensive security utilities including input validation,
sanitization, encryption, and Romanian GDPR compliance measures.
"""

import re
import html
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
from werkzeug.security import check_password_hash, generate_password_hash
import bleach
from email_validator import validate_email, EmailNotValidError


# Romanian phone number regex
ROMANIAN_PHONE_REGEX = re.compile(r'^(\+4|0040|0)([0-9]{9})$')

# Romanian postal code regex  
ROMANIAN_POSTAL_CODE_REGEX = re.compile(r'^[0-9]{6}$')

# Strong password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIREMENTS = {
    'min_length': PASSWORD_MIN_LENGTH,
    'max_length': PASSWORD_MAX_LENGTH,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digits': True,
    'require_special': True,
    'forbidden_patterns': [
        'password', 'parola', '123456', 'qwerty', 'admin',
        'test', 'user', 'guest', 'demo'
    ]
}

# Allowed file extensions for uploads
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Security headers configuration
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://www.google-analytics.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ),
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}


class SecurityValidator:
    """Security validation and sanitization utilities"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength according to security requirements.
        
        Args:
            password (str): Password to validate
            
        Returns:
            Dict containing validation result and details
        """
        result = {
            'is_valid': True,
            'errors': [],
            'strength_score': 0,
            'recommendations': []
        }
        
        if not password:
            result['is_valid'] = False
            result['errors'].append("Parola este obligatorie")
            return result
        
        # Length validation
        if len(password) < PASSWORD_REQUIREMENTS['min_length']:
            result['is_valid'] = False
            result['errors'].append(f"Parola trebuie să aibă cel puțin {PASSWORD_REQUIREMENTS['min_length']} caractere")
        
        if len(password) > PASSWORD_REQUIREMENTS['max_length']:
            result['is_valid'] = False
            result['errors'].append(f"Parola nu poate avea mai mult de {PASSWORD_REQUIREMENTS['max_length']} caractere")
        
        # Character requirements
        if PASSWORD_REQUIREMENTS['require_uppercase'] and not re.search(r'[A-Z]', password):
            result['is_valid'] = False
            result['errors'].append("Parola trebuie să conțină cel puțin o literă mare")
            result['recommendations'].append("Adaugă cel puțin o literă mare (A-Z)")
        
        if PASSWORD_REQUIREMENTS['require_lowercase'] and not re.search(r'[a-z]', password):
            result['is_valid'] = False
            result['errors'].append("Parola trebuie să conțină cel puțin o literă mică")
            result['recommendations'].append("Adaugă cel puțin o literă mică (a-z)")
        
        if PASSWORD_REQUIREMENTS['require_digits'] and not re.search(r'[0-9]', password):
            result['is_valid'] = False
            result['errors'].append("Parola trebuie să conțină cel puțin o cifră")
            result['recommendations'].append("Adaugă cel puțin o cifră (0-9)")
        
        if PASSWORD_REQUIREMENTS['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['is_valid'] = False
            result['errors'].append("Parola trebuie să conțină cel puțin un caracter special")
            result['recommendations'].append("Adaugă cel puțin un caracter special (!@#$%^&*)")
        
        # Forbidden patterns
        password_lower = password.lower()
        for pattern in PASSWORD_REQUIREMENTS['forbidden_patterns']:
            if pattern in password_lower:
                result['is_valid'] = False
                result['errors'].append(f"Parola nu poate conține '{pattern}'")
        
        # Calculate strength score
        strength_score = 0
        if len(password) >= 8:
            strength_score += 20
        if len(password) >= 12:
            strength_score += 10
        if re.search(r'[A-Z]', password):
            strength_score += 15
        if re.search(r'[a-z]', password):
            strength_score += 15
        if re.search(r'[0-9]', password):
            strength_score += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength_score += 15
        if len(set(password)) > len(password) * 0.7:  # Character diversity
            strength_score += 10
        
        result['strength_score'] = min(strength_score, 100)
        
        return result
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, Any]:
        """
        Validate email address format and security.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            Dict containing validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'normalized_email': None
        }
        
        if not email:
            result['is_valid'] = False
            result['errors'].append("Adresa de email este obligatorie")
            return result
        
        try:
            # Use email-validator library for comprehensive validation
            validation = validate_email(email)
            result['normalized_email'] = validation.email
            
            # Additional Romanian domain validation
            domain = validation.domain
            if len(domain) > 253:  # RFC limit
                result['is_valid'] = False
                result['errors'].append("Domeniul email-ului este prea lung")
            
        except EmailNotValidError as e:
            result['is_valid'] = False
            result['errors'].append("Formatul adresei de email nu este valid")
        
        return result
    
    @staticmethod
    def validate_romanian_phone(phone: str) -> Dict[str, Any]:
        """
        Validate Romanian phone number format.
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            Dict containing validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'normalized_phone': None
        }
        
        if not phone:
            result['is_valid'] = False
            result['errors'].append("Numărul de telefon este obligatoriu")
            return result
        
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not ROMANIAN_PHONE_REGEX.match(clean_phone):
            result['is_valid'] = False
            result['errors'].append("Formatul numărului de telefon nu este valid pentru România")
            return result
        
        # Normalize to +40 format
        if clean_phone.startswith('0040'):
            result['normalized_phone'] = '+4' + clean_phone[4:]
        elif clean_phone.startswith('+4'):
            result['normalized_phone'] = clean_phone
        elif clean_phone.startswith('0'):
            result['normalized_phone'] = '+4' + clean_phone[1:]
        else:
            result['normalized_phone'] = '+4' + clean_phone
        
        return result
    
    @staticmethod
    def sanitize_input(input_text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks.
        
        Args:
            input_text (str): Input text to sanitize
            max_length (int): Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not input_text:
            return ""
        
        # Truncate if too long
        if len(input_text) > max_length:
            input_text = input_text[:max_length]
        
        # HTML escape
        sanitized = html.escape(input_text)
        
        # Use bleach for additional sanitization
        allowed_tags = []  # No HTML tags allowed in general input
        sanitized = bleach.clean(sanitized, tags=allowed_tags, strip=True)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_product_name(name: str) -> Dict[str, Any]:
        """
        Validate product name with Romanian context.
        
        Args:
            name (str): Product name to validate
            
        Returns:
            Dict containing validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'sanitized_name': None
        }
        
        if not name:
            result['is_valid'] = False
            result['errors'].append("Numele produsului este obligatoriu")
            return result
        
        # Sanitize
        sanitized_name = SecurityValidator.sanitize_input(name, max_length=100)
        
        if len(sanitized_name) < 2:
            result['is_valid'] = False
            result['errors'].append("Numele produsului trebuie să aibă cel puțin 2 caractere")
        
        if len(sanitized_name) > 100:
            result['is_valid'] = False
            result['errors'].append("Numele produsului nu poate depăși 100 de caractere")
        
        # Check for inappropriate content (basic Romanian profanity filter)
        forbidden_words = ['test', 'spam', 'fake']  # Add Romanian inappropriate words
        name_lower = sanitized_name.lower()
        for word in forbidden_words:
            if word in name_lower:
                result['is_valid'] = False
                result['errors'].append("Numele produsului conține conținut neadecvat")
        
        result['sanitized_name'] = sanitized_name
        return result
    
    @staticmethod
    def validate_price(price: Union[str, float, int]) -> Dict[str, Any]:
        """
        Validate product price.
        
        Args:
            price: Price to validate
            
        Returns:
            Dict containing validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'normalized_price': None
        }
        
        try:
            price_float = float(price)
            
            if price_float < 0:
                result['is_valid'] = False
                result['errors'].append("Prețul nu poate fi negativ")
            elif price_float == 0:
                result['is_valid'] = False
                result['errors'].append("Prețul trebuie să fie mai mare decât 0")
            elif price_float > 99999.99:
                result['is_valid'] = False
                result['errors'].append("Prețul nu poate depăși 99,999.99 RON")
            else:
                # Round to 2 decimal places
                result['normalized_price'] = round(price_float, 2)
                
        except (ValueError, TypeError):
            result['is_valid'] = False
            result['errors'].append("Prețul trebuie să fie un număr valid")
        
        return result
    
    @staticmethod
    def validate_file_upload(filename: str, file_size: int) -> Dict[str, Any]:
        """
        Validate file upload security.
        
        Args:
            filename (str): Name of uploaded file
            file_size (int): Size of uploaded file in bytes
            
        Returns:
            Dict containing validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'safe_filename': None
        }
        
        if not filename:
            result['is_valid'] = False
            result['errors'].append("Numele fișierului este obligatoriu")
            return result
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            result['is_valid'] = False
            result['errors'].append(f"Fișierul este prea mare. Mărimea maximă permisă este {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Check extension
        file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            result['is_valid'] = False
            result['errors'].append(f"Tipul de fișier nu este permis. Extensii permise: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
        
        # Generate safe filename
        safe_name = SecurityValidator.sanitize_input(filename, max_length=255)
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
        
        # Prevent directory traversal
        safe_name = safe_name.replace('..', '_').replace('/', '_').replace('\\', '_')
        
        result['safe_filename'] = safe_name
        return result


class SecurityLogger:
    """Security event logging"""
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], 
                          severity: str = 'INFO', user_id: str = None,
                          ip_address: str = None):
        """
        Log security events for monitoring and compliance.
        
        Args:
            event_type (str): Type of security event
            details (Dict): Event details
            severity (str): Event severity (INFO, WARNING, ERROR, CRITICAL)
            user_id (str): User ID if applicable
            ip_address (str): Client IP address
        """
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': user_id,
            'ip_address': ip_address,
            'application': 'local_producer_app'
        }
        
        # Log based on severity
        logger = logging.getLogger('security')
        if severity == 'CRITICAL':
            logger.critical(f"SECURITY EVENT: {event_type}", extra=log_entry)
        elif severity == 'ERROR':
            logger.error(f"SECURITY EVENT: {event_type}", extra=log_entry)
        elif severity == 'WARNING':
            logger.warning(f"SECURITY EVENT: {event_type}", extra=log_entry)
        else:
            logger.info(f"SECURITY EVENT: {event_type}", extra=log_entry)
    
    @staticmethod
    def log_authentication_event(event_type: str, phone_number: str = None,
                                success: bool = True, ip_address: str = None,
                                details: Dict[str, Any] = None):
        """Log authentication events"""
        SecurityLogger.log_security_event(
            event_type=f"authentication_{event_type}",
            details={
                'phone_number': phone_number[-4:] if phone_number else None,  # Log only last 4 digits
                'success': success,
                'details': details or {}
            },
            severity='WARNING' if not success else 'INFO',
            ip_address=ip_address
        )
    
    @staticmethod
    def log_data_access(data_type: str, operation: str, user_id: str = None,
                       ip_address: str = None, details: Dict[str, Any] = None):
        """Log data access events for GDPR compliance"""
        SecurityLogger.log_security_event(
            event_type='data_access',
            details={
                'data_type': data_type,
                'operation': operation,
                'details': details or {}
            },
            severity='INFO',
            user_id=user_id,
            ip_address=ip_address
        )


class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # In-memory storage (use Redis in production)
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = datetime.now(timezone.utc)
    
    def is_allowed(self, identifier: str, limit: int, window: int) -> Dict[str, Any]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier (str): Unique identifier (IP, user ID, etc.)
            limit (int): Maximum requests allowed
            window (int): Time window in seconds
            
        Returns:
            Dict with allowed status and metadata
        """
        now = datetime.now(timezone.utc)
        
        # Cleanup old entries periodically
        if (now - self.last_cleanup).seconds > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now
        
        # Get request history for identifier
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        request_times = self.requests[identifier]
        
        # Remove requests outside the window
        cutoff_time = now - timedelta(seconds=window)
        request_times = [t for t in request_times if t > cutoff_time]
        self.requests[identifier] = request_times
        
        # Check if limit exceeded
        if len(request_times) >= limit:
            return {
                'allowed': False,
                'requests_made': len(request_times),
                'limit': limit,
                'window': window,
                'retry_after': window
            }
        
        # Record this request
        request_times.append(now)
        
        return {
            'allowed': True,
            'requests_made': len(request_times),
            'limit': limit,
            'window': window,
            'remaining': limit - len(request_times)
        }
    
    def _cleanup_old_entries(self):
        """Remove old rate limit entries"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                t for t in self.requests[identifier] if t > cutoff_time
            ]
            
            # Remove empty entries
            if not self.requests[identifier]:
                del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for storage"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def validate_csrf_token(token: str, session_token: str) -> bool:
    """Validate CSRF token"""
    return secrets.compare_digest(token, session_token)


def apply_security_headers(response):
    """Apply security headers to response"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response