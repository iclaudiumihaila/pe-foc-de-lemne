"""
SMS Verification Routes for Local Producer Web Application

This module provides SMS verification endpoints for phone number verification
including sending verification codes and confirming codes with proper
rate limiting, validation, and error handling.
"""

import logging
import uuid
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId

from app.services.sms_service import get_sms_service
from app.utils.validators import validate_json
from app.utils.error_handlers import ValidationError, SMSError
from app.utils.rate_limiter import rate_limit
from app.database import get_database


# Setup logging
logger = logging.getLogger(__name__)

# Create SMS blueprint
sms_bp = Blueprint('sms', __name__)

# JSON Schema for SMS verification request
SMS_VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": "^\\+[1-9]\\d{1,14}$",
            "description": "Phone number in E.164 format (+1234567890)"
        }
    },
    "required": ["phone_number"],
    "additionalProperties": False
}

# JSON Schema for SMS confirmation request
SMS_CONFIRM_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": "^\\+[1-9]\\d{1,14}$",
            "description": "Phone number in E.164 format (+1234567890)"
        },
        "verification_code": {
            "type": "string",
            "pattern": "^\\d{6}$",
            "description": "6-digit verification code"
        }
    },
    "required": ["phone_number", "verification_code"],
    "additionalProperties": False
}


@sms_bp.route('/verify', methods=['POST'])
@rate_limit('sms_verify', limit=10, window_seconds=3600)
@validate_json(SMS_VERIFY_SCHEMA)
def send_verification_code():
    """
    Send SMS verification code to phone number.
    
    Request Body:
    {
        "phone_number": "+1234567890"
    }
    
    Returns:
        200: Verification code sent successfully
        400: Invalid phone number format or validation error
        429: Rate limit exceeded
        500: SMS service error
    """
    try:
        # Get request data (already validated by decorator)
        data = request.get_json()
        phone_number = data['phone_number']
        
        # Log SMS verification attempt (last 4 digits for privacy)
        logger.info(f"SMS verification requested for phone ending in: {phone_number[-4:]}")
        
        # Get SMS service instance
        sms_service = get_sms_service()
        
        # Send verification code
        result = sms_service.send_verification_code(phone_number)
        
        # Prepare success response
        response_data = {
            'success': True,
            'data': {
                'phone_number': phone_number,
                'code_sent': result.get('code_sent', True),
                'expires_in_minutes': 10,  # SMS service uses 10-minute expiry
                'message_id': result.get('message_sid'),
                'mock_mode': result.get('mock_mode', False)
            },
            'message': 'Verification code sent successfully'
        }
        
        # Include verification code in response for mock mode (testing only)
        if result.get('mock_mode') and 'verification_code' in result:
            response_data['data']['verification_code'] = result['verification_code']
        
        logger.info(f"SMS verification code sent successfully to phone ending in: {phone_number[-4:]}")
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        logger.warning(f"SMS verification validation error: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'VAL_001',
                'message': str(e),
                'field': 'phone_number'
            }
        }
        
        return jsonify(error_response), 400
        
    except SMSError as e:
        logger.error(f"SMS service error: {str(e)}")
        
        # Handle rate limiting specifically
        if e.error_code == "SMS_001" and e.status_code == 429:
            # Get rate limit information for detailed response
            try:
                sms_service = get_sms_service()
                rate_info = sms_service.get_rate_limit_info(phone_number)
                
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'SMS_001',
                        'message': str(e),
                        'details': {
                            'attempts_count': rate_info.get('attempts_count', 0),
                            'rate_limit': rate_info.get('rate_limit', 5),
                            'reset_in_minutes': rate_info.get('reset_in_minutes', 0),
                            'window_hours': 1
                        }
                    }
                }
                
                return jsonify(error_response), 429
                
            except Exception:
                # Fallback rate limit response
                error_response = {
                    'success': False,
                    'error': {
                        'code': 'SMS_001',
                        'message': 'Rate limit exceeded. Please try again later.',
                        'details': {
                            'rate_limit': 5,
                            'window_hours': 1
                        }
                    }
                }
                
                return jsonify(error_response), 429
        
        # Handle other SMS errors
        status_code = getattr(e, 'status_code', 500)
        error_code = getattr(e, 'error_code', 'SMS_001')
        
        error_response = {
            'success': False,
            'error': {
                'code': error_code,
                'message': str(e)
            }
        }
        
        return jsonify(error_response), status_code
        
    except Exception as e:
        logger.error(f"Unexpected error in SMS verification: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'SMS_500',
                'message': 'SMS verification service temporarily unavailable'
            }
        }
        
        return jsonify(error_response), 500


@sms_bp.route('/confirm', methods=['POST'])
@rate_limit('sms_confirm', limit=50, window_seconds=3600)
@validate_json(SMS_CONFIRM_SCHEMA)
def confirm_verification_code():
    """
    Confirm SMS verification code and validate phone number.
    
    Request Body:
    {
        "phone_number": "+1234567890",
        "verification_code": "123456"
    }
    
    Returns:
        200: Phone number verified successfully with session
        400: Invalid code format or validation error
        404: No verification code found for phone number
        410: Verification code has expired
        500: SMS service error
    """
    try:
        # Get request data (already validated by decorator)
        data = request.get_json()
        phone_number = data['phone_number']
        verification_code = data['verification_code']
        
        # Log SMS confirmation attempt (last 4 digits for privacy)
        logger.info(f"SMS verification confirmation for phone ending in: {phone_number[-4:]}")
        
        # Get SMS service instance
        sms_service = get_sms_service()
        
        # Validate verification code
        is_valid = sms_service.validate_recent_code(phone_number, verification_code)
        
        if is_valid:
            # Create verification session for successful verification
            session_data = create_verification_session(phone_number)
            
            # Prepare success response
            response_data = {
                'success': True,
                'data': {
                    'phone_number': phone_number,
                    'verified': True,
                    'verified_at': datetime.utcnow().isoformat() + 'Z',
                    'session_id': session_data['session_id'],
                    'expires_at': session_data['expires_at'].isoformat() + 'Z'
                },
                'message': 'Phone number verified successfully'
            }
            
            logger.info(f"SMS verification successful for phone ending in: {phone_number[-4:]}")
            
            return jsonify(response_data), 200
        else:
            # This shouldn't happen as validate_recent_code raises exceptions
            logger.warning(f"SMS verification failed for phone ending in: {phone_number[-4:]}")
            
            error_response = {
                'success': False,
                'error': {
                    'code': 'SMS_002',
                    'message': 'Invalid verification code',
                    'field': 'verification_code'
                }
            }
            
            return jsonify(error_response), 400
        
    except ValidationError as e:
        logger.warning(f"SMS confirmation validation error: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'VAL_001',
                'message': str(e),
                'field': 'verification_code' if 'code' in str(e).lower() else 'phone_number'
            }
        }
        
        return jsonify(error_response), 400
        
    except SMSError as e:
        logger.warning(f"SMS confirmation error: {str(e)}")
        
        # Handle specific SMS error codes
        if e.error_code == "SMS_002":
            # Invalid verification code or code not found
            if "not found" in str(e).lower():
                status_code = 404
                error_message = "No verification code found for this phone number"
            else:
                status_code = 400
                error_message = str(e)
        elif e.error_code == "SMS_003":
            # Expired verification code
            status_code = 410
            error_message = "Verification code has expired"
        else:
            # Other SMS errors
            status_code = getattr(e, 'status_code', 500)
            error_message = str(e)
        
        error_response = {
            'success': False,
            'error': {
                'code': e.error_code,
                'message': error_message
            }
        }
        
        return jsonify(error_response), status_code
        
    except Exception as e:
        logger.error(f"Unexpected error in SMS confirmation: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'SMS_500',
                'message': 'SMS verification confirmation service temporarily unavailable'
            }
        }
        
        return jsonify(error_response), 500


def create_verification_session(phone_number):
    """
    Create verification session for successfully verified phone number.
    
    Args:
        phone_number (str): Verified phone number
        
    Returns:
        dict: Session data with session_id and expiry
    """
    try:
        # Generate unique session ID
        session_id = str(ObjectId())
        expires_at = datetime.utcnow() + timedelta(hours=2)  # 2-hour session
        
        # Create session document
        session_data = {
            'session_id': session_id,
            'phone_number': phone_number,
            'verified': True,
            'verified_at': datetime.utcnow(),
            'expires_at': expires_at,
            'created_at': datetime.utcnow(),
            'session_type': 'phone_verification'
        }
        
        # Store session in database
        db = get_database()
        verification_sessions = db.verification_sessions
        
        # Create TTL index for automatic cleanup if it doesn't exist
        try:
            verification_sessions.create_index(
                "expires_at", 
                expireAfterSeconds=0,
                background=True
            )
        except Exception:
            # Index might already exist, ignore error
            pass
        
        # Insert session
        verification_sessions.insert_one(session_data)
        
        logger.info(f"Verification session created for phone ending in: {phone_number[-4:]} with session: {session_id}")
        
        return {
            'session_id': session_id,
            'expires_at': expires_at
        }
        
    except Exception as e:
        logger.error(f"Failed to create verification session: {str(e)}")
        raise Exception("Failed to create verification session")


@sms_bp.route('/status/<phone_number>', methods=['GET'])
def get_verification_status(phone_number):
    """
    Get verification status for a phone number.
    
    Args:
        phone_number: Phone number in E.164 format
        
    Returns:
        200: Verification status retrieved successfully
        400: Invalid phone number format
        500: Service error
    """
    try:
        # Basic phone number format validation
        if not phone_number or not phone_number.startswith('+'):
            raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
        
        # Get SMS service instance
        sms_service = get_sms_service()
        
        # Get verification status
        status = sms_service.get_verification_status(phone_number)
        
        # Prepare response
        response_data = {
            'success': True,
            'data': {
                'phone_number': phone_number,
                'verified': status.get('verified', False),
                'code_sent': status.get('code_sent', False),
                'expired': status.get('expired', False),
                'created_at': status.get('created_at'),
                'expires_at': status.get('expires_at'),
                'verified_at': status.get('verified_at')
            },
            'message': 'Verification status retrieved successfully'
        }
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        logger.warning(f"SMS status validation error: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'VAL_001',
                'message': str(e),
                'field': 'phone_number'
            }
        }
        
        return jsonify(error_response), 400
        
    except Exception as e:
        logger.error(f"Error getting SMS verification status: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'SMS_500',
                'message': 'Unable to retrieve verification status'
            }
        }
        
        return jsonify(error_response), 500


@sms_bp.route('/rate-limit/<phone_number>', methods=['GET'])
def get_rate_limit_info(phone_number):
    """
    Get rate limit information for a phone number.
    
    Args:
        phone_number: Phone number in E.164 format
        
    Returns:
        200: Rate limit info retrieved successfully
        400: Invalid phone number format
        500: Service error
    """
    try:
        # Basic phone number format validation
        if not phone_number or not phone_number.startswith('+'):
            raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
        
        # Get SMS service instance
        sms_service = get_sms_service()
        
        # Get rate limit information
        rate_info = sms_service.get_rate_limit_info(phone_number)
        
        # Prepare response
        response_data = {
            'success': True,
            'data': {
                'phone_number': phone_number,
                'attempts_count': rate_info.get('attempts_count', 0),
                'rate_limit': rate_info.get('rate_limit', 5),
                'window_seconds': rate_info.get('window_seconds', 3600),
                'window_hours': 1,
                'is_rate_limited': rate_info.get('is_rate_limited', False),
                'reset_at': rate_info.get('reset_at'),
                'reset_in_seconds': rate_info.get('reset_in_seconds', 0),
                'reset_in_minutes': rate_info.get('reset_in_minutes', 0)
            },
            'message': 'Rate limit information retrieved successfully'
        }
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        logger.warning(f"Rate limit info validation error: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'VAL_001',
                'message': str(e),
                'field': 'phone_number'
            }
        }
        
        return jsonify(error_response), 400
        
    except Exception as e:
        logger.error(f"Error getting rate limit info: {str(e)}")
        
        error_response = {
            'success': False,
            'error': {
                'code': 'SMS_500',
                'message': 'Unable to retrieve rate limit information'
            }
        }
        
        return jsonify(error_response), 500


# Error handlers for the SMS blueprint
@sms_bp.errorhandler(400)
def handle_bad_request(error):
    """Handle bad request errors."""
    logger.warning(f"SMS API bad request: {str(error)}")
    
    return jsonify({
        'success': False,
        'error': {
            'code': 'VAL_001',
            'message': 'Invalid request format or missing required fields'
        }
    }), 400


@sms_bp.errorhandler(405)
def handle_method_not_allowed(error):
    """Handle method not allowed errors."""
    logger.warning(f"SMS API method not allowed: {str(error)}")
    
    return jsonify({
        'success': False,
        'error': {
            'code': 'HTTP_405',
            'message': 'Method not allowed for this endpoint'
        }
    }), 405


@sms_bp.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors."""
    logger.error(f"SMS API internal error: {str(error)}")
    
    return jsonify({
        'success': False,
        'error': {
            'code': 'SMS_500',
            'message': 'SMS service temporarily unavailable'
        }
    }), 500