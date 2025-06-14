"""
Authentication Routes for Local Producer Web Application

This module provides authentication endpoints including user registration,
login, phone verification, password management, and admin authentication.
"""

import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, session, current_app
from app.models.user import User
from app.services.sms_service import get_sms_service
from app.services.auth_service import AuthService
from app.utils.validators import validate_json, USER_SCHEMA
from app.utils.error_handlers import (
    ValidationError, AuthenticationError, AuthorizationError, SMSError,
    success_response, create_error_response
)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize admin authentication service
admin_auth_service = AuthService()

# Rate limiting storage (in-memory for demo)
_rate_limit_storage = {}

# Rate limiting constants
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 900  # 15 minutes
REGISTER_RATE_LIMIT = 3
REGISTER_RATE_WINDOW = 3600  # 1 hour
PASSWORD_CHANGE_RATE_LIMIT = 3
PASSWORD_CHANGE_RATE_WINDOW = 3600  # 1 hour


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication
        user_id = session.get('user_id')
        if not user_id:
            raise AuthenticationError("Authentication required")
        
        # Get user from database
        user = User.find_by_id(user_id)
        if not user:
            session.clear()
            raise AuthenticationError("Invalid session")
        
        # Check if phone is verified
        if not user.is_verified:
            raise AuthorizationError("Phone verification required")
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    return decorated_function


def check_rate_limit(limit_type: str, identifier: str, limit: int, window: int) -> bool:
    """Check if request is rate limited."""
    now = datetime.utcnow()
    key = f"{limit_type}:{identifier}"
    
    # Clean up old entries
    _cleanup_rate_limits(now, window)
    
    # Check current attempts
    if key in _rate_limit_storage:
        attempts = _rate_limit_storage[key]['attempts']
        if len(attempts) >= limit:
            return True
    
    return False


def track_rate_limit(limit_type: str, identifier: str, window: int):
    """Track rate limit attempt."""
    now = datetime.utcnow()
    key = f"{limit_type}:{identifier}"
    
    if key not in _rate_limit_storage:
        _rate_limit_storage[key] = {'attempts': []}
    
    _rate_limit_storage[key]['attempts'].append(now)
    
    # Keep only attempts within window
    cutoff = now - timedelta(seconds=window)
    _rate_limit_storage[key]['attempts'] = [
        attempt for attempt in _rate_limit_storage[key]['attempts']
        if attempt > cutoff
    ]


def _cleanup_rate_limits(now: datetime, window: int):
    """Clean up old rate limit entries."""
    cutoff = now - timedelta(seconds=window)
    to_remove = []
    
    for key, entry in _rate_limit_storage.items():
        entry['attempts'] = [
            attempt for attempt in entry['attempts']
            if attempt > cutoff
        ]
        if not entry['attempts']:
            to_remove.append(key)
    
    for key in to_remove:
        del _rate_limit_storage[key]


@auth_bp.route('/register', methods=['POST'])
@validate_json(USER_SCHEMA)
def register():
    """
    Register new user account.
    
    Expects JSON with phone_number, name, and password.
    Creates user account and sends verification SMS.
    """
    try:
        data = request.validated_json
        
        # Check registration rate limiting by IP
        client_ip = request.remote_addr or 'unknown'
        if check_rate_limit('register', client_ip, REGISTER_RATE_LIMIT, REGISTER_RATE_WINDOW):
            response, status = create_error_response(
                "RATE_001",
                "Too many registration attempts. Try again later.",
                429
            )
            return jsonify(response), status
        
        # Extract user data
        phone_number = data['phone_number']
        name = data['name']
        password = data['password']
        
        # Check if user already exists
        existing_user = User.find_by_phone(phone_number)
        if existing_user:
            if existing_user.is_verified:
                response, status = create_error_response(
                    "VAL_001",
                    "Phone number already registered",
                    409
                )
                return jsonify(response), status
            else:
                # User exists but not verified, allow re-registration
                # This will update the existing user
                pass
        
        # Create or update user
        if existing_user and not existing_user.is_verified:
            # Update existing unverified user
            existing_user.name = name
            existing_user.set_password(password)
            user = existing_user
        else:
            # Create new user
            user = User.create(phone_number, name, password)
        
        # Send verification SMS
        sms_service = get_sms_service()
        verification_code = sms_service.generate_verification_code()
        
        # Store verification code in user record
        user.set_verification_code(verification_code)
        
        # Send SMS
        sms_result = sms_service.send_verification_code(phone_number, verification_code)
        
        # Track rate limit
        track_rate_limit('register', client_ip, REGISTER_RATE_WINDOW)
        
        # Log successful registration
        logging.info(f"User registered: {phone_number[-4:]} (SMS sent: {sms_result['code_sent']})")
        
        return jsonify(success_response({
            'user_id': str(user._id),
            'phone_number': user.phone_number,
            'name': user.name,
            'verification_sent': sms_result['code_sent'],
            'expires_at': sms_result['expires_at'],
            'mock_mode': sms_result.get('mock_mode', False)
        }, "Registration successful. Please verify your phone number.")), 201
        
    except SMSError as e:
        # SMS sending failed, but user was created
        logging.error(f"SMS failed during registration: {str(e)}")
        response, status = create_error_response(
            e.error_code,
            "Registration completed but SMS failed. Please try verification again.",
            e.status_code if hasattr(e, 'status_code') else 500
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Registration failed",
            500
        )
        return jsonify(response), status


@auth_bp.route('/send-verification', methods=['POST'])
def send_verification():
    """
    Send SMS verification code to phone number.
    
    Expects JSON with phone_number.
    Sends new verification code via SMS.
    """
    try:
        data = request.get_json()
        if not data or 'phone_number' not in data:
            response, status = create_error_response(
                "VAL_001",
                "Phone number is required",
                400
            )
            return jsonify(response), status
        
        phone_number = data['phone_number']
        
        # Find user
        user = User.find_by_phone(phone_number)
        if not user:
            response, status = create_error_response(
                "AUTH_001",
                "Phone number not registered",
                404
            )
            return jsonify(response), status
        
        # Don't send if already verified
        if user.is_verified:
            response, status = create_error_response(
                "VAL_001",
                "Phone number already verified",
                400
            )
            return jsonify(response), status
        
        # Send verification SMS
        sms_service = get_sms_service()
        verification_code = sms_service.generate_verification_code()
        
        # Store verification code
        user.set_verification_code(verification_code)
        
        # Send SMS (rate limiting handled by SMS service)
        sms_result = sms_service.send_verification_code(phone_number, verification_code)
        
        logging.info(f"Verification SMS sent: {phone_number[-4:]}")
        
        return jsonify(success_response({
            'phone_number': user.phone_number,
            'verification_sent': sms_result['code_sent'],
            'expires_at': sms_result['expires_at'],
            'mock_mode': sms_result.get('mock_mode', False)
        }, "Verification code sent")), 200
        
    except SMSError as e:
        logging.error(f"SMS verification send failed: {str(e)}")
        response, status = create_error_response(
            e.error_code,
            str(e),
            e.status_code if hasattr(e, 'status_code') else 500
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Send verification error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to send verification code",
            500
        )
        return jsonify(response), status


@auth_bp.route('/verify-phone', methods=['POST'])
def verify_phone():
    """
    Verify phone number with SMS code.
    
    Expects JSON with phone_number and verification_code.
    Marks user as verified if code is valid.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['phone_number', 'verification_code']):
            response, status = create_error_response(
                "VAL_001",
                "Phone number and verification code are required",
                400
            )
            return jsonify(response), status
        
        phone_number = data['phone_number']
        verification_code = data['verification_code']
        
        # Find user
        user = User.find_by_phone(phone_number)
        if not user:
            response, status = create_error_response(
                "AUTH_001",
                "Phone number not registered",
                404
            )
            return jsonify(response), status
        
        # Check if already verified
        if user.is_verified:
            return jsonify(success_response({
                'phone_number': user.phone_number,
                'verified': True
            }, "Phone number already verified")), 200
        
        # Validate verification code
        sms_service = get_sms_service()
        is_valid = sms_service.validate_verification_code(
            phone_number,
            verification_code,
            user.verification_code,
            user.verification_expires
        )
        
        if is_valid:
            # Mark user as verified
            user.verify_phone(verification_code)
            
            logging.info(f"Phone verified successfully: {phone_number[-4:]}")
            
            return jsonify(success_response({
                'phone_number': user.phone_number,
                'verified': True,
                'name': user.name
            }, "Phone number verified successfully")), 200
        else:
            # This should not happen as SMS service raises exception
            response, status = create_error_response(
                "SMS_002",
                "Invalid verification code",
                400
            )
            return jsonify(response), status
            
    except SMSError as e:
        logging.warning(f"Phone verification failed: {str(e)}")
        response, status = create_error_response(
            e.error_code,
            str(e),
            400
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Phone verification error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Phone verification failed",
            500
        )
        return jsonify(response), status


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login with phone number and password.
    
    Expects JSON with phone_number and password.
    Creates session and returns user info.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['phone_number', 'password']):
            response, status = create_error_response(
                "VAL_001",
                "Phone number and password are required",
                400
            )
            return jsonify(response), status
        
        phone_number = data['phone_number']
        password = data['password']
        
        # Check login rate limiting
        if check_rate_limit('login', phone_number, LOGIN_RATE_LIMIT, LOGIN_RATE_WINDOW):
            response, status = create_error_response(
                "RATE_001",
                "Too many login attempts. Try again later.",
                429
            )
            return jsonify(response), status
        
        # Find user
        user = User.find_by_phone(phone_number)
        if not user:
            # Track failed attempt
            track_rate_limit('login', phone_number, LOGIN_RATE_WINDOW)
            response, status = create_error_response(
                "AUTH_001",
                "Invalid phone number or password",
                401
            )
            return jsonify(response), status
        
        # Check if phone is verified
        if not user.is_verified:
            response, status = create_error_response(
                "AUTH_003",
                "Phone number not verified. Please verify your phone first.",
                403
            )
            return jsonify(response), status
        
        # Verify password
        if not user.verify_password(password):
            # Track failed attempt
            track_rate_limit('login', phone_number, LOGIN_RATE_WINDOW)
            response, status = create_error_response(
                "AUTH_001",
                "Invalid phone number or password",
                401
            )
            return jsonify(response), status
        
        # Update last login
        user.update({'last_login': datetime.utcnow()})
        
        # Create session
        session['user_id'] = str(user._id)
        session['phone_number'] = user.phone_number
        session['role'] = user.role
        session['login_time'] = datetime.utcnow().isoformat()
        
        logging.info(f"User logged in: {phone_number[-4:]} (role: {user.role})")
        
        return jsonify(success_response({
            'user': {
                'id': str(user._id),
                'phone_number': user.phone_number,
                'name': user.name,
                'role': user.role,
                'verified': user.is_verified
            },
            'session_created': True
        }, "Login successful")), 200
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Login failed",
            500
        )
        return jsonify(response), status


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    User logout and session cleanup.
    
    Requires authentication.
    Clears session and logs out user.
    """
    try:
        user = request.current_user
        
        # Clear session
        session.clear()
        
        logging.info(f"User logged out: {user.phone_number[-4:]}")
        
        return jsonify(success_response({
            'logged_out': True
        }, "Logout successful")), 200
        
    except Exception as e:
        logging.error(f"Logout error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Logout failed",
            500
        )
        return jsonify(response), status


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    Change user password.
    
    Requires authentication.
    Expects JSON with current_password and new_password.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['current_password', 'new_password']):
            response, status = create_error_response(
                "VAL_001",
                "Current password and new password are required",
                400
            )
            return jsonify(response), status
        
        current_password = data['current_password']
        new_password = data['new_password']
        user = request.current_user
        
        # Check password change rate limiting
        user_id = str(user._id)
        if check_rate_limit('password_change', user_id, PASSWORD_CHANGE_RATE_LIMIT, PASSWORD_CHANGE_RATE_WINDOW):
            response, status = create_error_response(
                "RATE_001",
                "Too many password change attempts. Try again later.",
                429
            )
            return jsonify(response), status
        
        # Verify current password
        if not user.verify_password(current_password):
            # Track failed attempt
            track_rate_limit('password_change', user_id, PASSWORD_CHANGE_RATE_WINDOW)
            response, status = create_error_response(
                "AUTH_001",
                "Current password is incorrect",
                401
            )
            return jsonify(response), status
        
        # Validate new password strength
        if len(new_password) < 8:
            response, status = create_error_response(
                "VAL_002",
                "New password must be at least 8 characters long",
                400
            )
            return jsonify(response), status
        
        # Update password
        user.set_password(new_password)
        
        # Track successful attempt
        track_rate_limit('password_change', user_id, PASSWORD_CHANGE_RATE_WINDOW)
        
        logging.info(f"Password changed: {user.phone_number[-4:]}")
        
        return jsonify(success_response({
            'password_changed': True
        }, "Password changed successfully")), 200
        
    except Exception as e:
        logging.error(f"Password change error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Password change failed",
            500
        )
        return jsonify(response), status


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current authenticated user information.
    
    Requires authentication.
    Returns user profile data.
    """
    try:
        user = request.current_user
        
        return jsonify(success_response({
            'user': {
                'id': str(user._id),
                'phone_number': user.phone_number,
                'name': user.name,
                'role': user.role,
                'verified': user.is_verified,
                'created_at': user.created_at.isoformat() + 'Z' if user.created_at else None,
                'last_login': user.last_login.isoformat() + 'Z' if user.last_login else None
            }
        }, "User information retrieved")), 200
        
    except Exception as e:
        logging.error(f"Get current user error: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to get user information",
            500
        )
        return jsonify(response), status


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """
    Admin login endpoint with JWT token authentication.
    
    Expects JSON with username (phone number) and password.
    Returns JWT access and refresh tokens for admin authentication.
    
    Request Body:
        {
            "username": "+40722123456",
            "password": "admin_password"
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Autentificare reușită",
            "data": {
                "user": {
                    "id": "user_id",
                    "name": "Admin Name",
                    "phone_number": "+40722123456",
                    "role": "admin",
                    "last_login": "2025-01-14T22:30:00Z"
                },
                "tokens": {
                    "access_token": "jwt_access_token",
                    "refresh_token": "jwt_refresh_token",
                    "token_type": "Bearer",
                    "expires_in": 28800
                }
            }
        }
    
    Response (Error - 400/401/429/500):
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Romanian error message"
            }
        }
    """
    try:
        # Validate request content type
        if not request.is_json:
            response, status = create_error_response(
                "VAL_001",
                "Cererea trebuie să fie în format JSON",
                400
            )
            return jsonify(response), status
        
        # Get JSON data
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "VAL_001",
                "Date JSON invalide sau lipsă",
                400
            )
            return jsonify(response), status
        
        # Validate required fields
        if not all(k in data for k in ['username', 'password']):
            response, status = create_error_response(
                "VAL_001",
                "Numele de utilizator și parola sunt obligatorii",
                400
            )
            return jsonify(response), status
        
        username = data['username'].strip()
        password = data['password']
        
        # Validate field values
        if not username or not password:
            response, status = create_error_response(
                "VAL_001",
                "Numele de utilizator și parola nu pot fi goale",
                400
            )
            return jsonify(response), status
        
        # Get client IP address for rate limiting
        client_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Authenticate admin using AuthService
        auth_result = admin_auth_service.authenticate_admin(
            username=username,
            password=password,
            ip_address=client_ip
        )
        
        # Log successful authentication
        logging.info(f"Admin authentication successful: {username[-4:]} from IP {client_ip}")
        
        # Return success response with tokens
        return jsonify(success_response(
            auth_result,
            auth_result['message']
        )), 200
        
    except ValidationError as e:
        logging.warning(f"Admin login validation error: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
        
    except AuthenticationError as e:
        logging.warning(f"Admin authentication failed: {str(e)} for {data.get('username', 'unknown')} from IP {request.remote_addr}")
        response, status = create_error_response(
            e.error_code,
            e.message,
            401 if e.error_code in ['AUTH_001', 'AUTH_002', 'AUTH_003'] else (429 if e.error_code == 'AUTH_015' else 500)
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Admin login error: {str(e)} for {data.get('username', 'unknown')} from IP {request.remote_addr}")
        response, status = create_error_response(
            "AUTH_999",
            "Eroare la autentificare. Încercați din nou",
            500
        )
        return jsonify(response), status


@auth_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    """
    Admin logout endpoint for JWT token invalidation.
    
    Expects Authorization header with Bearer token.
    Returns logout confirmation.
    
    Headers:
        Authorization: Bearer jwt_access_token
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Deconectare reușită",
            "data": {
                "logged_out": true
            }
        }
    
    Response (Error - 400/500):
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Romanian error message"
            }
        }
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            response, status = create_error_response(
                "AUTH_006",
                "Token de autentificare lipsește din header",
                401
            )
            return jsonify(response), status
        
        # Validate Bearer token format
        if not auth_header.startswith('Bearer '):
            response, status = create_error_response(
                "AUTH_009",
                "Format token invalid. Utilizați 'Bearer token'",
                401
            )
            return jsonify(response), status
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Logout admin using AuthService
        logout_result = admin_auth_service.logout_admin(token)
        
        # Log successful logout
        logging.info(f"Admin logout successful from IP {request.remote_addr}")
        
        # Return success response
        return jsonify(success_response(
            logout_result,
            logout_result['message']
        )), 200
        
    except Exception as e:
        logging.error(f"Admin logout error: {str(e)} from IP {request.remote_addr}")
        # Even on error, consider logout successful for security
        return jsonify(success_response(
            {'logged_out': True},
            'Deconectare reușită'
        )), 200


@auth_bp.route('/admin/refresh', methods=['POST'])
def admin_refresh_token():
    """
    Admin token refresh endpoint for renewing JWT access tokens.
    
    Expects JSON with refresh_token.
    Returns new access and refresh tokens.
    
    Request Body:
        {
            "refresh_token": "jwt_refresh_token"
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Token reînnoit cu succes",
            "data": {
                "access_token": "new_jwt_access_token",
                "refresh_token": "new_jwt_refresh_token",
                "token_type": "Bearer",
                "expires_in": 28800
            }
        }
    
    Response (Error - 400/401/500):
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Romanian error message"
            }
        }
    """
    try:
        # Validate request content type
        if not request.is_json:
            response, status = create_error_response(
                "VAL_001",
                "Cererea trebuie să fie în format JSON",
                400
            )
            return jsonify(response), status
        
        # Get JSON data
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            response, status = create_error_response(
                "VAL_001",
                "Token de reînnoire este obligatoriu",
                400
            )
            return jsonify(response), status
        
        refresh_token = data['refresh_token'].strip() if data['refresh_token'] else ''
        
        if not refresh_token:
            response, status = create_error_response(
                "VAL_001",
                "Token de reînnoire nu poate fi gol",
                400
            )
            return jsonify(response), status
        
        # Refresh tokens using AuthService
        refresh_result = admin_auth_service.refresh_access_token(refresh_token)
        
        # Log successful token refresh
        logging.info(f"Admin token refresh successful from IP {request.remote_addr}")
        
        # Return success response with new tokens
        return jsonify(success_response(
            refresh_result,
            "Token reînnoit cu succes"
        )), 200
        
    except AuthenticationError as e:
        logging.warning(f"Admin token refresh failed: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            e.error_code,
            e.message,
            401 if e.error_code in ['AUTH_011', 'AUTH_012'] else 500
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Admin token refresh error: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            "AUTH_013",
            "Eroare la reînnoirea token-ului",
            500
        )
        return jsonify(response), status


@auth_bp.route('/admin/verify', methods=['POST'])
def admin_verify_token():
    """
    Admin token verification endpoint for validating JWT tokens.
    
    Expects Authorization header with Bearer token.
    Returns token validation result and user info.
    
    Headers:
        Authorization: Bearer jwt_access_token
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Token valid",
            "data": {
                "valid": true,
                "user": {
                    "user_id": "user_id",
                    "phone_number": "+40722123456",
                    "name": "Admin Name",
                    "role": "admin"
                }
            }
        }
    
    Response (Error - 401/500):
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Romanian error message"
            }
        }
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            response, status = create_error_response(
                "AUTH_006",
                "Token de autentificare lipsește din header",
                401
            )
            return jsonify(response), status
        
        # Validate Bearer token format
        if not auth_header.startswith('Bearer '):
            response, status = create_error_response(
                "AUTH_009",
                "Format token invalid. Utilizați 'Bearer token'",
                401
            )
            return jsonify(response), status
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify token using AuthService
        payload = admin_auth_service.verify_token(token)
        
        # Log successful token verification
        logging.debug(f"Admin token verification successful for {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")
        
        # Return success response with user info
        return jsonify(success_response({
            'valid': True,
            'user': {
                'user_id': payload.get('user_id'),
                'phone_number': payload.get('phone_number'),
                'name': payload.get('name'),
                'role': payload.get('role')
            }
        }, "Token valid")), 200
        
    except AuthenticationError as e:
        logging.warning(f"Admin token verification failed: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            e.error_code,
            e.message,
            401
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Admin token verification error: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            "AUTH_010",
            "Eroare la verificarea token-ului",
            500
        )
        return jsonify(response), status


@auth_bp.route('/admin/setup', methods=['POST'])
def admin_initial_setup():
    """
    Initial admin account creation endpoint (for first-time setup).
    
    Expects JSON with name, phone_number, and password.
    Creates the first admin account if no admin exists.
    
    Request Body:
        {
            "name": "Administrator Name",
            "phone_number": "+40722123456",
            "password": "secure_admin_password"
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Administrator creat cu succes",
            "data": {
                "admin": {
                    "id": "admin_id",
                    "name": "Administrator Name",
                    "phone_number": "+40722123456",
                    "role": "admin"
                }
            }
        }
    
    Response (Error - 400/409/500):
        {
            "success": false,
            "error": {
                "code": "error_code",
                "message": "Romanian error message"
            }
        }
    """
    try:
        # Validate request content type
        if not request.is_json:
            response, status = create_error_response(
                "VAL_001",
                "Cererea trebuie să fie în format JSON",
                400
            )
            return jsonify(response), status
        
        # Get JSON data
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "VAL_001",
                "Date JSON invalide sau lipsă",
                400
            )
            return jsonify(response), status
        
        # Validate required fields
        required_fields = ['name', 'phone_number', 'password']
        if not all(k in data for k in required_fields):
            response, status = create_error_response(
                "VAL_001",
                "Numele, numărul de telefon și parola sunt obligatorii",
                400
            )
            return jsonify(response), status
        
        name = data['name'].strip()
        phone_number = data['phone_number'].strip()
        password = data['password']
        
        # Validate field values
        if not name or not phone_number or not password:
            response, status = create_error_response(
                "VAL_001",
                "Numele, numărul de telefon și parola nu pot fi goale",
                400
            )
            return jsonify(response), status
        
        # Create initial admin using AuthService
        admin_result = admin_auth_service.create_initial_admin(
            name=name,
            phone_number=phone_number,
            password=password
        )
        
        # Log successful admin creation
        logging.info(f"Initial admin created: {phone_number[-4:]} from IP {request.remote_addr}")
        
        # Return success response
        return jsonify(success_response(
            admin_result,
            admin_result['message']
        )), 201
        
    except ValidationError as e:
        logging.warning(f"Admin setup validation error: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
        
    except AuthenticationError as e:
        logging.warning(f"Admin setup failed: {str(e)} from IP {request.remote_addr}")
        status_code = 409 if e.error_code == 'AUTH_016' else 500
        response, status = create_error_response(
            e.error_code,
            e.message,
            status_code
        )
        return jsonify(response), status
        
    except Exception as e:
        logging.error(f"Admin setup error: {str(e)} from IP {request.remote_addr}")
        response, status = create_error_response(
            "AUTH_017",
            "Eroare la crearea administratorului",
            500
        )
        return jsonify(response), status