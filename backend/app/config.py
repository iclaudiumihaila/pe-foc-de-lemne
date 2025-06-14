"""
Configuration Management for Local Producer Web Application

This module handles environment variable loading and provides configuration
classes for different deployment environments.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv


# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """
    Base configuration class that loads environment variables and provides
    default values for the Flask application.
    """
    
    # =============================================================================
    # FLASK APPLICATION CONFIGURATION
    # =============================================================================
    
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 8080))
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'local_producer_app')
    MONGODB_MAX_POOL_SIZE = int(os.environ.get('MONGODB_MAX_POOL_SIZE', 10))
    MONGODB_MIN_POOL_SIZE = int(os.environ.get('MONGODB_MIN_POOL_SIZE', 1))
    
    # =============================================================================
    # SMS SERVICE CONFIGURATION (TWILIO)
    # =============================================================================
    
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    SMS_CODE_EXPIRES_MINUTES = int(os.environ.get('SMS_CODE_EXPIRES_MINUTES', 10))
    
    # =============================================================================
    # AUTHENTICATION & SECURITY CONFIGURATION
    # =============================================================================
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 2)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)))
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    
    # =============================================================================
    # RATE LIMITING CONFIGURATION
    # =============================================================================
    
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 100))
    SMS_RATE_LIMIT_PER_HOUR = int(os.environ.get('SMS_RATE_LIMIT_PER_HOUR', 10))
    RATE_LIMIT_STORAGE = os.environ.get('RATE_LIMIT_STORAGE', 'memory')
    
    # SMS endpoint specific rate limits
    RATE_LIMIT_SMS_VERIFY_LIMIT = int(os.environ.get('RATE_LIMIT_SMS_VERIFY_LIMIT', 10))
    RATE_LIMIT_SMS_VERIFY_WINDOW = int(os.environ.get('RATE_LIMIT_SMS_VERIFY_WINDOW', 3600))
    RATE_LIMIT_SMS_CONFIRM_LIMIT = int(os.environ.get('RATE_LIMIT_SMS_CONFIRM_LIMIT', 50))
    RATE_LIMIT_SMS_CONFIRM_WINDOW = int(os.environ.get('RATE_LIMIT_SMS_CONFIRM_WINDOW', 3600))
    
    # Rate limiting enabled/disabled flag
    RATE_LIMITING_ENABLED = os.environ.get('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
    
    # =============================================================================
    # SESSION CONFIGURATION
    # =============================================================================
    
    CUSTOMER_SESSION_EXPIRES = timedelta(hours=int(os.environ.get('CUSTOMER_SESSION_EXPIRES_HOURS', 24)))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Strict')
    
    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    
    CORS_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')]
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH')
    STRUCTURED_LOGGING = os.environ.get('STRUCTURED_LOGGING', 'true').lower() == 'true'
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    APP_NAME = os.environ.get('APP_NAME', 'Local Producer Web Application')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    MAX_UPLOAD_SIZE_MB = int(os.environ.get('MAX_UPLOAD_SIZE_MB', 5))
    ALLOWED_IMAGE_EXTENSIONS = [ext.strip() for ext in os.environ.get('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,webp').split(',')]
    
    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    
    DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'true').lower() == 'true'
    SEED_SAMPLE_DATA = os.environ.get('SEED_SAMPLE_DATA', 'false').lower() == 'true'
    SKIP_SMS_VERIFICATION = os.environ.get('SKIP_SMS_VERIFICATION', 'false').lower() == 'true'
    
    # =============================================================================
    # PRODUCTION SETTINGS
    # =============================================================================
    
    SSL_REDIRECT = os.environ.get('SSL_REDIRECT', 'false').lower() == 'true'
    SECURITY_HEADERS_ENABLED = os.environ.get('SECURITY_HEADERS_ENABLED', 'true').lower() == 'true'
    ERROR_TRACKING_DSN = os.environ.get('ERROR_TRACKING_DSN')
    PERFORMANCE_MONITORING_ENABLED = os.environ.get('PERFORMANCE_MONITORING_ENABLED', 'false').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """
        Validate that all required configuration variables are set.
        
        Returns:
            list: List of validation errors, empty if all valid
        """
        errors = []
        
        # Check required Twilio configuration in production
        if not cls.DEVELOPMENT_MODE and not cls.SKIP_SMS_VERIFICATION:
            if not cls.TWILIO_ACCOUNT_SID:
                errors.append("TWILIO_ACCOUNT_SID is required for SMS functionality")
            if not cls.TWILIO_AUTH_TOKEN:
                errors.append("TWILIO_AUTH_TOKEN is required for SMS functionality")
            if not cls.TWILIO_PHONE_NUMBER:
                errors.append("TWILIO_PHONE_NUMBER is required for SMS functionality")
        
        # Check secret keys are not using default values in production
        if not cls.DEVELOPMENT_MODE:
            if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
                errors.append("FLASK_SECRET_KEY must be set to a secure value in production")
            if cls.JWT_SECRET_KEY == 'dev-jwt-secret-change-in-production':
                errors.append("JWT_SECRET_KEY must be set to a secure value in production")
        
        return errors


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    DEVELOPMENT_MODE = True
    SKIP_SMS_VERIFICATION = True
    BCRYPT_LOG_ROUNDS = 4  # Faster for development


class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    MONGODB_DB_NAME = 'local_producer_app_test'
    SKIP_SMS_VERIFICATION = True
    BCRYPT_LOG_ROUNDS = 4  # Faster for testing
    RATE_LIMIT_REQUESTS_PER_MINUTE = 1000  # No rate limiting in tests


class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False
    DEVELOPMENT_MODE = False
    SKIP_SMS_VERIFICATION = False
    SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}