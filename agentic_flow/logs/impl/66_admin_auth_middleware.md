# Implementation 66: Create admin authentication middleware

## Implementation Summary
Successfully created comprehensive admin authentication middleware for the Romanian local producer marketplace with JWT token validation, role-based access control, request context enhancement, optional authentication support, and complete Romanian localization for the Pe Foc de Lemne admin system backend.

## Files Created/Modified

### 1. Admin Authentication Middleware - `/backend/app/utils/auth_middleware.py`
- **JWT Token Validation**: Complete Bearer token extraction and verification
- **Role-Based Access Control**: Admin role verification and authorization
- **Request Context Enhancement**: Admin user data integration with Flask context
- **Optional Authentication**: Flexible middleware for mixed-access routes
- **Romanian Localization**: All error messages and responses in Romanian

## Key Middleware Functions Implemented

### 1. Core Authentication Decorator - require_admin_auth
```python
@require_admin_auth
def admin_dashboard():
    admin_user = g.current_admin_user
    return jsonify({'admin': admin_user['name']})

def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return create_error_response("AUTH_006", "Token de autentificare lipsește", 401)
        
        # Validate Bearer token format
        if not auth_header.startswith('Bearer '):
            return create_error_response("AUTH_009", "Format token invalid. Utilizați 'Bearer token'", 401)
        
        # Extract and verify token
        token = auth_header[7:]
        payload = admin_auth_service.verify_token(token)
        
        # Verify admin role
        if payload.get('role') != 'admin':
            return create_error_response("AUTH_002", "Acces interzis. Doar administratorii pot accesa această secțiune", 403)
        
        # Add admin user to request context
        g.current_admin_user = {
            'user_id': payload.get('user_id'),
            'phone_number': payload.get('phone_number'),
            'name': payload.get('name'),
            'role': payload.get('role'),
            'authenticated_at': payload.get('iat'),
            'expires_at': payload.get('exp')
        }
        
        return f(*args, **kwargs)
    return decorated_function
```

### 2. Optional Authentication Decorator - require_admin_auth_optional
```python
@require_admin_auth_optional
def public_stats():
    if hasattr(g, 'current_admin_user'):
        return jsonify({'detailed_stats': True})  # Enhanced for admin
    else:
        return jsonify({'basic_stats': True})     # Basic for non-admin

def require_admin_auth_optional(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Attempt authentication without blocking access
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
            try:
                payload = admin_auth_service.verify_token(token)
                
                if payload.get('role') == 'admin':
                    g.current_admin_user = {
                        'user_id': payload.get('user_id'),
                        'phone_number': payload.get('phone_number'),
                        'name': payload.get('name'),
                        'role': payload.get('role')
                    }
            except AuthenticationError:
                pass  # Silently ignore auth errors for optional auth
        
        return f(*args, **kwargs)  # Always call function
    return decorated_function
```

### 3. Context Helper Functions
```python
def get_current_admin_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated admin user from request context."""
    return getattr(g, 'current_admin_user', None)

def get_current_admin_token() -> Optional[Dict[str, Any]]:
    """Get current JWT token information from request context."""
    return getattr(g, 'current_admin_token', None)

def is_admin_authenticated() -> bool:
    """Check if current request has an authenticated admin user."""
    return hasattr(g, 'current_admin_user') and g.current_admin_user is not None

def admin_has_permission(permission: str = None) -> bool:
    """Check if current admin user has specific permission."""
    if not is_admin_authenticated():
        return False
    
    admin_user = get_current_admin_user()
    return admin_user and admin_user.get('role') == 'admin'
```

## JWT Token Processing Implementation

### 1. Authorization Header Extraction
```python
# Extract Authorization header with validation
auth_header = request.headers.get('Authorization', '')

if not auth_header:
    return create_error_response("AUTH_006", "Token de autentificare lipsește", 401)

# Validate Bearer token format
if not auth_header.startswith('Bearer '):
    return create_error_response("AUTH_009", "Format token invalid. Utilizați 'Bearer token'", 401)

# Extract token safely
token = auth_header[7:]  # Remove 'Bearer ' prefix

if not token:
    return create_error_response("AUTH_009", "Token de autentificare gol", 401)
```

### 2. JWT Token Verification
```python
# Verify JWT token using AuthService
try:
    payload = admin_auth_service.verify_token(token)
except AuthenticationError as e:
    # Map specific authentication errors to Romanian messages
    if e.error_code == "AUTH_008":
        error_message = "Token-ul de autentificare a expirat"
    elif e.error_code in ["AUTH_009", "AUTH_010"]:
        error_message = "Token de autentificare invalid"
    elif e.error_code == "AUTH_007":
        error_message = "Token invalid pentru admin"
    else:
        error_message = "Token expirat sau invalid"
    
    return create_error_response(e.error_code, error_message, 401)
```

### 3. Admin Role Verification
```python
# Verify admin role (additional check beyond AuthService)
user_role = payload.get('role')
if user_role != 'admin':
    logging.warning(f"Admin route access denied - non-admin role '{user_role}' for user {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")
    return create_error_response(
        "AUTH_002",
        "Acces interzis. Doar administratorii pot accesa această secțiune",
        403
    )
```

## Flask Request Context Integration

### 1. Admin User Context Setup
```python
# Add comprehensive admin user information to request context
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
```

### 2. Context Access in Protected Routes
```python
# Protected route can access admin user data
@auth_bp.route('/admin/dashboard', methods=['GET'])
@require_admin_auth
def admin_dashboard():
    admin_user = g.current_admin_user
    token_info = g.current_admin_token
    
    return jsonify({
        'welcome': f"Bun venit, {admin_user['name']}",
        'user_id': admin_user['user_id'],
        'token_expires': token_info['expires_at']
    })
```

### 3. Helper Function Usage
```python
# Use helper functions for cleaner code
@auth_bp.route('/admin/profile', methods=['GET'])
@require_admin_auth
def admin_profile():
    admin_user = get_current_admin_user()
    
    if admin_has_permission('view_profile'):
        return jsonify({'profile': admin_user})
    else:
        return jsonify({'error': 'Permission denied'}), 403
```

## Romanian Localization Implementation

### 1. Authentication Error Messages
```python
# Missing token errors
"Token de autentificare lipsește"  # Authentication token missing
"Token de autentificare gol"  # Authentication token empty

# Token format errors
"Format token invalid. Utilizați 'Bearer token'"  # Invalid token format
"Token de autentificare invalid"  # Invalid authentication token

# Token status errors
"Token-ul de autentificare a expirat"  # Authentication token expired
"Token expirat sau invalid"  # Expired or invalid token
"Token invalid pentru admin"  # Invalid admin token
```

### 2. Authorization Error Messages
```python
# Role-based access control
"Acces interzis. Doar administratorii pot accesa această secțiune"  # Admin access only
"Permisiuni insuficiente pentru această operațiune"  # Insufficient permissions
```

### 3. System Error Messages
```python
# System and unexpected errors
"Eroare de autentificare. Încercați din nou"  # Authentication error, try again
"Eroare de autentificare neașteptată"  # Unexpected authentication error
```

## Security Features Implementation

### 1. Comprehensive Security Logging
```python
# Authentication attempt logging
logging.warning(f"Admin route access denied - missing token from IP {request.remote_addr}")
logging.warning(f"Admin token verification failed: {str(e)} from IP {request.remote_addr}")
logging.warning(f"Admin route access denied - non-admin role '{user_role}' for user {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")

# Success logging for monitoring
logging.debug(f"Admin authentication successful for {payload.get('phone_number', 'unknown')} accessing {request.endpoint} from IP {request.remote_addr}")
```

### 2. Error Information Sanitization
```python
# Don't expose system details in errors
except Exception as e:
    logging.error(f"Admin authentication middleware error: {str(e)} from IP {request.remote_addr}")
    return create_error_response("AUTH_999", "Eroare de autentificare. Încercați din nou", 500)
```

### 3. Role Verification with Logging
```python
# Log role-based access denials
if user_role != 'admin':
    logging.warning(f"Admin route access denied - non-admin role '{user_role}' for user {payload.get('phone_number', 'unknown')} from IP {request.remote_addr}")
    return create_error_response("AUTH_002", "Acces interzis. Doar administratorii pot accesa această secțiune", 403)
```

## Advanced Middleware Features

### 1. Auth Context Response Helper
```python
def create_auth_context_response(data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create API response with admin authentication context."""
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
        response['auth_context'] = {'authenticated': False}
    
    return response
```

### 2. Admin Action Logging
```python
def log_admin_action(action: str, details: Dict[str, Any] = None) -> None:
    """Log admin actions for audit trail and security monitoring."""
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
        'details': details or {}
    }
    
    logging.info(f"Admin action: {action}", extra=log_data)

# Usage example
@auth_bp.route('/admin/products', methods=['POST'])
@require_admin_auth
def create_product():
    # Create product logic
    product_id = create_new_product(request.json)
    
    # Log admin action
    log_admin_action("Product created", {
        "product_id": product_id,
        "name": request.json.get('name')
    })
    
    return jsonify({'product_id': product_id})
```

### 3. Permission-Based Access Control
```python
def admin_has_permission(permission: str = None) -> bool:
    """Check if current admin user has specific permission."""
    if not is_admin_authenticated():
        return False
    
    # For now, all authenticated admins have all permissions
    # This can be extended in the future with granular permissions
    admin_user = get_current_admin_user()
    return admin_user and admin_user.get('role') == 'admin'

# Future extension for granular permissions
# def admin_has_permission(permission: str = None) -> bool:
#     admin_user = get_current_admin_user()
#     if not admin_user:
#         return False
#     
#     user_permissions = admin_user.get('permissions', [])
#     return permission in user_permissions
```

## Integration with AuthService

### 1. Service Integration
```python
# Initialize AuthService at module level
from app.services.auth_service import AuthService
admin_auth_service = AuthService()

# Use service methods directly
payload = admin_auth_service.verify_token(token)
```

### 2. Error Handling Integration
```python
# Handle AuthService exceptions
try:
    payload = admin_auth_service.verify_token(token)
except AuthenticationError as e:
    # Map AuthService errors to appropriate middleware responses
    error_message = map_auth_error_to_romanian(e.error_code)
    return create_error_response(e.error_code, error_message, 401)
```

### 3. Consistent Error Response Format
```python
# Use existing error handling utilities
from app.utils.error_handlers import create_error_response

response, status = create_error_response(
    error_code,
    romanian_message,
    http_status_code
)
return jsonify(response), status
```

## Usage Examples and Patterns

### 1. Basic Protected Route
```python
@auth_bp.route('/admin/dashboard', methods=['GET'])
@require_admin_auth
def admin_dashboard():
    admin_user = g.current_admin_user
    
    return jsonify({
        'welcome': f"Bun venit, {admin_user['name']}",
        'dashboard_data': get_dashboard_data()
    })
```

### 2. Mixed Access Route
```python
@api_bp.route('/api/products', methods=['GET'])
@require_admin_auth_optional
def list_products():
    if is_admin_authenticated():
        # Include admin-only data
        products = get_products_with_admin_data()
    else:
        # Basic product listing
        products = get_public_products()
    
    return jsonify({'products': products})
```

### 3. Permission-Based Route
```python
@auth_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@require_admin_auth
def delete_user(user_id):
    if not admin_has_permission('delete_users'):
        return jsonify({'error': 'Permisiuni insuficiente'}), 403
    
    # Delete user logic
    result = delete_user_by_id(user_id)
    
    # Log admin action
    log_admin_action("User deleted", {"user_id": user_id})
    
    return jsonify({'deleted': result})
```

### 4. Context-Enhanced Response
```python
@auth_bp.route('/admin/stats', methods=['GET'])
@require_admin_auth
def admin_stats():
    stats_data = get_admin_statistics()
    
    # Include auth context in response
    response = create_auth_context_response({'stats': stats_data})
    
    return jsonify(response)
```

## Quality Assurance

- Middleware follows Flask decorator patterns with functools.wraps preservation
- Complete Romanian localization with culturally appropriate error messages
- Comprehensive JWT token validation with AuthService integration
- Role-based access control with admin verification
- Request context enhancement for seamless admin data access
- Optional authentication support for flexible route protection
- Security logging for authentication events and access attempts
- Error handling with appropriate HTTP status codes and secure messages
- Helper functions for common authentication checks and context access
- Admin action logging for audit trail and security monitoring
- Future-ready permission system for granular access control
- Integration with existing error handling and response formatting utilities

## Next Integration Opportunities

Ready for immediate integration with:
- Admin route protection across all admin endpoints
- Admin panel frontend with authentication state management
- Role-based access control for different admin permission levels
- Admin action audit logging with database persistence
- Security monitoring dashboard for authentication events
- Admin session management with token refresh automation
- Multi-factor authentication integration for enhanced security
- Admin account management with permission assignments
- API rate limiting with admin exemptions
- Admin-specific error handling and monitoring systems