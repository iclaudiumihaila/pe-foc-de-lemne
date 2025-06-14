"""
Error Handling Middleware for Local Producer Web Application

This module provides standardized error handling, logging, and response
formatting for all Flask application errors.
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from jsonschema import ValidationError


# ============================================================================
# CUSTOM EXCEPTION CLASSES
# ============================================================================

class APIError(Exception):
    """Base class for API-specific errors."""
    
    def __init__(self, message: str, error_code: str, status_code: int = 400, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(APIError):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication required", error_code: str = "AUTH_001", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 401, details)


class AuthorizationError(APIError):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Insufficient permissions", error_code: str = "AUTH_003", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 403, details)


class ValidationError(APIError):
    """Validation-related errors."""
    
    def __init__(self, message: str = "Input validation failed", error_code: str = "VAL_002", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 400, details)


class DatabaseError(APIError):
    """Database-related errors."""
    
    def __init__(self, message: str = "Database operation failed", error_code: str = "DB_001", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 500, details)


class SMSError(APIError):
    """SMS service-related errors."""
    
    def __init__(self, message: str = "SMS service error", error_code: str = "SMS_001", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 500, details)


class RateLimitError(APIError):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_001", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 429, details)


class NotFoundError(APIError):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", error_code: str = "DB_002", details: Dict[str, Any] = None):
        super().__init__(message, error_code, 404, details)


# ============================================================================
# ERROR RESPONSE FORMATTING
# ============================================================================

def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Dict[str, Any] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create standardized error response.
    
    Args:
        error_code (str): Error code from taxonomy
        message (str): Human-readable error message
        status_code (int): HTTP status code
        details (dict): Additional error details
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return response, status_code


def log_error(error: Exception, request_info: Dict[str, Any] = None):
    """
    Log error with request context and stack trace.
    
    Args:
        error (Exception): Exception to log
        request_info (dict): Request context information
    """
    request_info = request_info or {}
    
    # Sanitize request info (remove sensitive data)
    safe_request_info = {
        "method": request_info.get("method"),
        "path": request_info.get("path"),
        "remote_addr": request_info.get("remote_addr"),
        "user_agent": request_info.get("user_agent", "").split("/")[0] if request_info.get("user_agent") else None
    }
    
    logging.error(
        f"API Error: {type(error).__name__}: {str(error)}\n"
        f"Request: {safe_request_info}\n"
        f"Traceback: {traceback.format_exc()}"
    )


def get_request_info() -> Dict[str, Any]:
    """
    Extract safe request information for logging.
    
    Returns:
        dict: Request context information
    """
    try:
        return {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "")
        }
    except Exception:
        return {}


# ============================================================================
# FLASK ERROR HANDLERS
# ============================================================================

def register_error_handlers(app: Flask):
    """
    Register all error handlers with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            error.error_code,
            error.message,
            error.status_code,
            error.details
        )[0]), error.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "VAL_001",
            "Bad request - invalid input or malformed request",
            400
        )[0]), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "AUTH_001",
            "Authentication required",
            401
        )[0]), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "AUTH_003",
            "Insufficient permissions",
            403
        )[0]), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        # Don't log 404s as errors (too noisy)
        logging.info(f"404 Not Found: {request.path}")
        return jsonify(create_error_response(
            "DB_002",
            "Resource not found",
            404
        )[0]), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "VAL_001",
            "HTTP method not allowed for this endpoint",
            405
        )[0]), 405
    
    @app.errorhandler(409)
    def handle_conflict(error):
        """Handle 409 Conflict errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "DB_001",
            "Resource conflict - duplicate or constraint violation",
            409
        )[0]), 409
    
    @app.errorhandler(413)
    def handle_payload_too_large(error):
        """Handle 413 Payload Too Large errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "VAL_003",
            "Request payload too large",
            413
        )[0]), 413
    
    @app.errorhandler(429)
    def handle_too_many_requests(error):
        """Handle 429 Too Many Requests errors."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "RATE_001",
            "Rate limit exceeded - too many requests",
            429
        )[0]), 429
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 Internal Server Error."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "DB_001",
            "Internal server error",
            500
        )[0]), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle generic HTTP exceptions."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "DB_001",
            f"HTTP error: {error.description}",
            error.code
        )[0]), error.code
    
    @app.errorhandler(DuplicateKeyError)
    def handle_duplicate_key_error(error):
        """Handle MongoDB duplicate key errors."""
        log_error(error, get_request_info())
        
        # Extract field name from error message if possible
        error_msg = str(error)
        field_name = "field"
        if "phone_number" in error_msg:
            field_name = "phone number"
        elif "email" in error_msg:
            field_name = "email"
        elif "order_number" in error_msg:
            field_name = "order number"
        
        return jsonify(create_error_response(
            "DB_001",
            f"Duplicate {field_name} - this value already exists",
            409,
            {"duplicate_field": field_name}
        )[0]), 409
    
    @app.errorhandler(ConnectionFailure)
    def handle_connection_failure(error):
        """Handle MongoDB connection failures."""
        log_error(error, get_request_info())
        return jsonify(create_error_response(
            "DB_001",
            "Database connection error - please try again",
            503
        )[0]), 503
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exceptions."""
        log_error(error, get_request_info())
        
        # In production, don't expose internal error details
        return jsonify(create_error_response(
            "DB_001",
            "An unexpected error occurred",
            500
        )[0]), 500


# ============================================================================
# ERROR UTILITY FUNCTIONS
# ============================================================================

def abort_with_error(error_code: str, message: str, status_code: int = 400, details: Dict[str, Any] = None):
    """
    Abort request with standardized error response.
    
    Args:
        error_code (str): Error code from taxonomy
        message (str): Error message
        status_code (int): HTTP status code
        details (dict): Additional error details
    """
    response, code = create_error_response(error_code, message, status_code, details)
    return jsonify(response), code


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[Tuple[Dict[str, Any], int]]:
    """
    Validate that required fields are present in data.
    
    Args:
        data (dict): Data to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: Error response if validation fails, None if valid
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return abort_with_error(
            "VAL_001",
            "Required fields missing",
            400,
            {"missing_fields": missing_fields}
        )
    
    return None


def success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message (str): Optional success message
        
    Returns:
        dict: Success response
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if message:
        response["message"] = message
    
    return response


# ============================================================================
# ERROR CODE REGISTRY
# ============================================================================

ERROR_CODES = {
    # Authentication Errors
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Session expired",
    "AUTH_003": "Insufficient permissions",
    
    # Validation Errors
    "VAL_001": "Required field missing",
    "VAL_002": "Invalid format",
    "VAL_003": "Value out of range",
    
    # SMS Errors
    "SMS_001": "SMS service unavailable",
    "SMS_002": "Invalid verification code",
    "SMS_003": "Verification code expired",
    
    # Database Errors
    "DB_001": "Database connection error",
    "DB_002": "Document not found",
    
    # Rate Limiting
    "RATE_001": "Rate limit exceeded"
}