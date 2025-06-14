"""
Admin Authentication Middleware for Local Producer Web Application

This module provides JWT-based authentication middleware for protecting admin routes
with token validation, role verification, and Romanian localized error messages
for the local producer marketplace admin system.
"""

import logging
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, jsonify, g, current_app
from app.services.auth_service import AuthService
from app.utils.error_handlers import (
    AuthenticationError, AuthorizationError, create_error_response
)


# Initialize admin authentication service
admin_auth_service = AuthService()


def require_admin_auth(f):
    """
    Decorator to require admin authentication for protected routes.
    
    This middleware validates JWT tokens from the Authorization header,
    verifies admin role, and adds admin user information to the request context.
    Protected routes can access admin user data through g.current_admin_user.
    
    Usage:
        @auth_bp.route('/admin/dashboard', methods=['GET'])
        @require_admin_auth
        def admin_dashboard():
            admin_user = g.current_admin_user
            return jsonify({'admin': admin_user['name']})
    
    Headers Required:
        Authorization: Bearer <jwt_access_token>
    
    Returns:
        - 401: Missing, invalid, or expired token
        - 403: Valid token but non-admin user
        - Calls protected function if authentication succeeds
    
    Romanian Error Messages:
        - "Token de autentificare lipsește" - Missing auth token
        - "Format token invalid" - Invalid Bearer format
        - "Token expirat sau invalid" - Expired/invalid token
        - "Acces interzis pentru non-administratori" - Non-admin access denied
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Extract Authorization header
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header:
                logging.warning(f"Admin route access denied - missing token from IP {request.remote_addr}")
                response, status = create_error_response(
                    "AUTH_006",
                    "Token de autentificare lipsește",
                    401
                )
                return jsonify(response), status
            
            # Validate Bearer token format
            if not auth_header.startswith('Bearer '):
                logging.warning(f"Admin route access denied - invalid token format from IP {request.remote_addr}")
                response, status = create_error_response(
                    "AUTH_009",
                    "Format token invalid. Utilizați 'Bearer token'",
                    401
                )
                return jsonify(response), status
            
            # Extract token
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            if not token:
                logging.warning(f"Admin route access denied - empty token from IP {request.remote_addr}")
                response, status = create_error_response(
                    "AUTH_009",
                    "Token de autentificare gol",
                    401
                )
                return jsonify(response), status
            
            # Verify JWT token using AuthService
            try:
                payload = admin_auth_service.verify_token(token)
            except AuthenticationError as e:
                logging.warning(f"Admin token verification failed: {str(e)} from IP {request.remote_addr}")
                
                # Map specific authentication errors to appropriate messages
                if e.error_code == "AUTH_008":
                    error_message = "Token-ul de autentificare a expirat"
                elif e.error_code in ["AUTH_009", "AUTH_010"]:
                    error_message = "Token de autentificare invalid"
                elif e.error_code == "AUTH_007":
                    error_message = "Token invalid pentru admin"
                else:
                    error_message = "Token expirat sau invalid"
                
                response, status = create_error_response(
                    e.error_code,
                    error_message,
                    401
                )
                return jsonify(response), status
            
            # Verify admin role (additional check beyond AuthService)
            user_role = payload.get('role')
            if user_role != 'admin':
                logging.warning(f"Admin route access denied - non-admin role '{user_role}' for user {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")
                response, status = create_error_response(
                    "AUTH_002",
                    "Acces interzis. Doar administratorii pot accesa această secțiune",
                    403
                )
                return jsonify(response), status
            
            # Add admin user information to request context
            g.current_admin_user = {
                'user_id': payload.get('user_id'),
                'phone_number': payload.get('phone_number'),
                'name': payload.get('name'),
                'role': payload.get('role'),
                'authenticated_at': payload.get('iat'),
                'expires_at': payload.get('exp')
            }
            
            # Add token information for potential use
            g.current_admin_token = {
                'raw_token': token,
                'payload': payload,
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp'),
                'issuer': payload.get('iss'),
                'audience': payload.get('aud')
            }
            
            # Log successful authentication for security monitoring
            logging.debug(f"Admin authentication successful for {payload.get('phone_number', 'unknown')} accessing {request.endpoint} from IP {request.remote_addr}")
            
            # Call the protected function
            return f(*args, **kwargs)
            
        except Exception as e:
            # Log unexpected errors but don't expose system details
            logging.error(f"Admin authentication middleware error: {str(e)} from IP {request.remote_addr}")
            response, status = create_error_response(
                "AUTH_999",
                "Eroare de autentificare. Încercați din nou",
                500
            )
            return jsonify(response), status
    
    return decorated_function


def require_admin_auth_optional(f):
    """
    Optional admin authentication decorator for routes that can benefit from admin context.
    
    This middleware attempts to authenticate admin users but doesn't block access
    if authentication fails. Useful for routes that provide enhanced functionality
    for authenticated admins but remain accessible to others.
    
    Usage:
        @api_bp.route('/api/public/stats', methods=['GET'])
        @require_admin_auth_optional
        def public_stats():
            if hasattr(g, 'current_admin_user'):
                # Enhanced stats for admin
                return jsonify({'detailed_stats': True})
            else:
                # Basic stats for non-admin
                return jsonify({'basic_stats': True})
    
    Returns:
        - Always calls the protected function
        - Sets g.current_admin_user if valid admin token provided
        - Logs authentication attempts for security monitoring
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Extract Authorization header
            auth_header = request.headers.get('Authorization', '')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                
                if token:
                    try:
                        # Attempt token verification
                        payload = admin_auth_service.verify_token(token)
                        
                        # Verify admin role
                        if payload.get('role') == 'admin':
                            # Add admin user information to request context
                            g.current_admin_user = {
                                'user_id': payload.get('user_id'),
                                'phone_number': payload.get('phone_number'),
                                'name': payload.get('name'),
                                'role': payload.get('role'),
                                'authenticated_at': payload.get('iat'),
                                'expires_at': payload.get('exp')
                            }
                            
                            logging.debug(f"Optional admin authentication successful for {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")
                    
                    except AuthenticationError:
                        # Silently ignore authentication errors for optional auth
                        logging.debug(f"Optional admin authentication failed from IP {request.remote_addr}")
                        pass
            
            # Always call the protected function regardless of authentication result
            return f(*args, **kwargs)
            
        except Exception as e:
            # Log unexpected errors but continue execution
            logging.warning(f"Optional admin authentication middleware error: {str(e)} from IP {request.remote_addr}")
            return f(*args, **kwargs)
    
    return decorated_function


def get_current_admin_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated admin user from request context.
    
    Returns:
        dict: Admin user information if authenticated, None otherwise
        
    Example:
        admin_user = get_current_admin_user()
        if admin_user:
            print(f"Admin: {admin_user['name']}")
        else:
            print("No admin authenticated")
    """
    return getattr(g, 'current_admin_user', None)


def get_current_admin_token() -> Optional[Dict[str, Any]]:
    """
    Get current JWT token information from request context.
    
    Returns:
        dict: Token information if authenticated, None otherwise
        
    Example:
        token_info = get_current_admin_token()
        if token_info:
            print(f"Token expires at: {token_info['expires_at']}")
    """
    return getattr(g, 'current_admin_token', None)


def is_admin_authenticated() -> bool:
    """
    Check if current request has an authenticated admin user.
    
    Returns:
        bool: True if admin is authenticated, False otherwise
        
    Example:
        if is_admin_authenticated():
            # Admin-specific logic
            pass
        else:
            # Non-admin logic
            pass
    """
    return hasattr(g, 'current_admin_user') and g.current_admin_user is not None


def admin_has_permission(permission: str = None) -> bool:
    """
    Check if current admin user has specific permission.
    
    For future extension when role-based permissions are implemented.
    Currently returns True for any authenticated admin.
    
    Args:
        permission (str): Permission to check (future use)
        
    Returns:
        bool: True if admin has permission, False otherwise
        
    Example:
        if admin_has_permission('manage_users'):
            # Allow user management
            pass
    """
    if not is_admin_authenticated():
        return False
    
    # For now, all authenticated admins have all permissions
    # This can be extended in the future with granular permissions
    admin_user = get_current_admin_user()
    return admin_user and admin_user.get('role') == 'admin'


def create_auth_context_response(data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create API response with admin authentication context.
    
    Adds current admin user information to response data for client context.
    Useful for API responses that need to include authentication state.
    
    Args:
        data (dict): Response data to enhance with auth context
        
    Returns:
        dict: Enhanced response data with admin context
        
    Example:
        response_data = create_auth_context_response({'products': products})
        # Response includes admin context for frontend state management
    """
    response = data or {}
    
    if is_admin_authenticated():
        admin_user = get_current_admin_user()
        token_info = get_current_admin_token()
        
        response['auth_context'] = {
            'authenticated': True,
            'user': {
                'name': admin_user.get('name'),
                'role': admin_user.get('role'),
                'phone_number': admin_user.get('phone_number')
            },
            'token': {
                'expires_at': token_info.get('expires_at') if token_info else None,
                'issued_at': token_info.get('issued_at') if token_info else None
            }
        }
    else:
        response['auth_context'] = {
            'authenticated': False
        }
    
    return response


def log_admin_action(action: str, details: Dict[str, Any] = None) -> None:
    """
    Log admin actions for audit trail and security monitoring.
    
    Creates structured log entries for admin actions with user context,
    request information, and action details for security auditing.
    
    Args:
        action (str): Description of the admin action performed
        details (dict): Additional details about the action
        
    Example:
        log_admin_action("Product created", {"product_id": "123", "name": "New Product"})
        log_admin_action("User deleted", {"user_id": "456", "phone": "+40722123456"})
    """
    if not is_admin_authenticated():
        logging.warning(f"Attempted to log admin action '{action}' without authentication from IP {request.remote_addr}")
        return
    
    admin_user = get_current_admin_user()
    
    log_data = {
        'action': action,
        'admin_user': {
            'user_id': admin_user.get('user_id'),
            'phone_number': admin_user.get('phone_number'),
            'name': admin_user.get('name')
        },
        'request': {
            'endpoint': request.endpoint,
            'method': request.method,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        },
        'details': details or {},
        'timestamp': request.headers.get('X-Request-ID', 'unknown')
    }
    
    # Use structured logging for better log processing
    logging.info(f"Admin action: {action}", extra=log_data)


# Error handler for authentication middleware exceptions
def handle_auth_middleware_error(error: Exception) -> tuple:
    """
    Handle authentication middleware errors with appropriate responses.
    
    Args:
        error (Exception): The authentication error that occurred
        
    Returns:
        tuple: (response_dict, status_code) for Flask error handling
    """
    if isinstance(error, AuthenticationError):
        response, status = create_error_response(
            error.error_code,
            error.message,
            error.status_code
        )
        return response, status
    
    elif isinstance(error, AuthorizationError):
        response, status = create_error_response(
            error.error_code,
            error.message,
            error.status_code
        )
        return response, status
    
    else:
        # Generic error for unexpected exceptions
        logging.error(f"Unexpected auth middleware error: {str(error)}")
        response, status = create_error_response(
            "AUTH_999",
            "Eroare de autentificare neașteptată",
            500
        )
        return response, status