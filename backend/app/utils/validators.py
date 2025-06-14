"""
Input Validation Middleware for Local Producer Web Application

This module provides JSON schema validation, input sanitization, and security
validation for all API endpoints.
"""

import re
import html
import logging
from functools import wraps
from typing import Dict, Any, List, Optional
from flask import request, jsonify
from jsonschema import validate, ValidationError, FormatChecker
from bson import ObjectId


# Custom format checker for MongoDB ObjectId
format_checker = FormatChecker()

@format_checker.checks('objectid')
def check_objectid(instance):
    """Check if string is a valid MongoDB ObjectId."""
    try:
        ObjectId(instance)
        return True
    except Exception:
        return False


# Phone number validation regex (E.164 format)
PHONE_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')

# XSS prevention patterns
XSS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
]


# ============================================================================
# JSON SCHEMA DEFINITIONS
# ============================================================================

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": r"^\+[1-9]\d{1,14}$",
            "description": "Phone number in E.164 format"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "description": "User's full name"
        },
        "role": {
            "type": "string",
            "enum": ["customer", "admin"],
            "description": "User role"
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "description": "Password for admin users"
        }
    },
    "required": ["phone_number", "name"],
    "additionalProperties": False
}

PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "description": "Product name"
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1000,
            "description": "Product description"
        },
        "price": {
            "type": "number",
            "minimum": 0,
            "multipleOf": 0.01,
            "description": "Product price with max 2 decimal places"
        },
        "category_id": {
            "type": "string",
            "format": "objectid",
            "description": "Category ObjectId"
        },
        "images": {
            "type": "array",
            "items": {"type": "string", "format": "uri"},
            "maxItems": 5,
            "description": "Array of image URLs"
        },
        "stock_quantity": {
            "type": "integer",
            "minimum": 0,
            "description": "Available stock quantity"
        },
        "active": {
            "type": "boolean",
            "description": "Product active status"
        },
        "featured": {
            "type": "boolean",
            "description": "Product featured status"
        }
    },
    "required": ["name", "description", "price", "category_id", "stock_quantity"],
    "additionalProperties": False
}

CATEGORY_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "description": "Category name"
        },
        "description": {
            "type": "string",
            "maxLength": 500,
            "description": "Category description"
        },
        "display_order": {
            "type": "integer",
            "minimum": 0,
            "description": "Display order for sorting"
        },
        "active": {
            "type": "boolean",
            "description": "Category active status"
        }
    },
    "required": ["name"],
    "additionalProperties": False
}

ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "customer_phone": {
            "type": "string",
            "pattern": r"^\+[1-9]\d{1,14}$",
            "description": "Customer phone number"
        },
        "customer_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "description": "Customer name"
        },
        "delivery_type": {
            "type": "string",
            "enum": ["pickup", "delivery"],
            "description": "Delivery method"
        },
        "delivery_address": {
            "type": "object",
            "properties": {
                "street": {"type": "string", "minLength": 1, "maxLength": 200},
                "city": {"type": "string", "minLength": 1, "maxLength": 100},
                "postal_code": {"type": "string", "maxLength": 20},
                "notes": {"type": "string", "maxLength": 200}
            },
            "required": ["street", "city"],
            "additionalProperties": False
        },
        "preferred_time": {
            "type": "string",
            "maxLength": 100,
            "description": "Preferred pickup/delivery time"
        },
        "special_instructions": {
            "type": "string",
            "maxLength": 500,
            "description": "Special instructions or notes"
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "format": "objectid",
                        "description": "Product ObjectId"
                    },
                    "quantity": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Quantity ordered"
                    }
                },
                "required": ["product_id", "quantity"],
                "additionalProperties": False
            }
        }
    },
    "required": ["customer_phone", "customer_name", "delivery_type", "items"],
    "additionalProperties": False
}

SMS_VERIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": r"^\+[1-9]\d{1,14}$",
            "description": "Phone number for SMS verification"
        },
        "verification_code": {
            "type": "string",
            "pattern": r"^\d{4}$",
            "description": "4-digit verification code"
        }
    },
    "required": ["phone_number"],
    "additionalProperties": False
}

CART_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "product_id": {
            "type": "string",
            "format": "objectid",
            "description": "Product ObjectId"
        },
        "quantity": {
            "type": "integer",
            "minimum": 1,
            "maximum": 999,
            "description": "Quantity to add to cart"
        },
        "session_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "description": "Cart session identifier"
        }
    },
    "required": ["product_id", "quantity", "session_id"],
    "additionalProperties": False
}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number against E.164 format.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(PHONE_REGEX.match(phone))


def sanitize_string(text: str) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        text (str): Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(text, str):
        return text
    
    # HTML encode the text
    sanitized = html.escape(text)
    
    # Remove potentially dangerous patterns
    for pattern in XSS_PATTERNS:
        sanitized = pattern.sub('', sanitized)
    
    return sanitized.strip()


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize all string values in a dictionary.
    
    Args:
        data (dict): Dictionary to sanitize
        
    Returns:
        dict: Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item) if isinstance(item, dict)
                else sanitize_string(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate data against JSON schema and return list of errors.
    
    Args:
        data (dict): Data to validate
        schema (dict): JSON schema to validate against
        
    Returns:
        list: List of validation error messages
    """
    try:
        validate(data, schema, format_checker=format_checker)
        return []
    except ValidationError as e:
        # Parse validation error into user-friendly message
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        return [f"Validation error at {error_path}: {e.message}"]


# ============================================================================
# FLASK VALIDATION DECORATORS
# ============================================================================

def validate_json(schema: Dict[str, Any], sanitize: bool = True):
    """
    Decorator to validate Flask request JSON against a schema.
    
    Args:
        schema (dict): JSON schema to validate against
        sanitize (bool): Whether to sanitize string inputs
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if request has JSON content
            if not request.is_json:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "VAL_001",
                        "message": "Request must contain valid JSON",
                        "details": {}
                    }
                }), 400
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({
                        "success": False,
                        "error": {
                            "code": "VAL_001",
                            "message": "Request body is empty or invalid JSON",
                            "details": {}
                        }
                    }), 400
                
                # Sanitize input if requested
                if sanitize:
                    data = sanitize_dict(data)
                
                # Validate against schema
                validation_errors = validate_json_schema(data, schema)
                if validation_errors:
                    return jsonify({
                        "success": False,
                        "error": {
                            "code": "VAL_002",
                            "message": "Input validation failed",
                            "details": {"validation_errors": validation_errors}
                        }
                    }), 400
                
                # Add validated data to request context
                request.validated_json = data
                return f(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Validation error: {e}")
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "VAL_003",
                        "message": "Internal validation error",
                        "details": {}
                    }
                }), 500
        
        return wrapper
    return decorator


def validate_query_params(required_params: List[str] = None, optional_params: List[str] = None):
    """
    Decorator to validate query parameters.
    
    Args:
        required_params (list): List of required parameter names
        optional_params (list): List of optional parameter names
        
    Returns:
        function: Decorated function
    """
    required_params = required_params or []
    optional_params = optional_params or []
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check required parameters
            missing_params = []
            for param in required_params:
                if param not in request.args:
                    missing_params.append(param)
            
            if missing_params:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "VAL_001",
                        "message": "Required query parameters missing",
                        "details": {"missing_params": missing_params}
                    }
                }), 400
            
            # Sanitize all query parameters
            validated_params = {}
            all_params = required_params + optional_params
            
            for param in request.args:
                if param in all_params:
                    validated_params[param] = sanitize_string(request.args.get(param))
            
            # Add validated params to request context
            request.validated_params = validated_params
            return f(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# SCHEMA REGISTRY
# ============================================================================

VALIDATION_SCHEMAS = {
    'user': USER_SCHEMA,
    'product': PRODUCT_SCHEMA,
    'category': CATEGORY_SCHEMA,
    'order': ORDER_SCHEMA,
    'sms_verification': SMS_VERIFICATION_SCHEMA,
    'cart_item': CART_ITEM_SCHEMA,
}