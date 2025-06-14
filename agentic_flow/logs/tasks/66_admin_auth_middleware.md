# Task 66: Create admin authentication middleware

**ID**: 66_admin_auth_middleware  
**Title**: Create admin authentication middleware  
**Description**: Implement JWT validation middleware for admin routes  
**Dependencies**: Admin login endpoint creation (Task 65)  
**Estimate**: 20 minutes  
**Deliverable**: backend/app/utils/auth_middleware.py with JWT validation

## Context

The admin authentication endpoints are complete with JWT-based authentication API. Now we need middleware to protect admin routes by validating JWT tokens and ensuring only authenticated admin users can access protected admin functionality in the local producer marketplace backend.

## Requirements

### Core Middleware Functionality
1. **JWT Token Validation**: Extract and validate JWT tokens from Authorization header
2. **Admin Role Verification**: Ensure authenticated user has admin role
3. **Token Expiration Check**: Verify tokens haven't expired
4. **Request Context Enhancement**: Add admin user info to request context
5. **Error Handling**: Return appropriate HTTP status codes with Romanian messages

### Authentication Flow
1. **Header Extraction**: Extract Bearer token from Authorization header
2. **Token Validation**: Use AuthService to verify JWT token
3. **Admin Authorization**: Verify user has admin role
4. **Context Setup**: Add admin user data to Flask request context
5. **Route Protection**: Allow or deny access based on authentication

### Security Features
1. **Token Security**: Validate JWT signature and claims
2. **Role-Based Access**: Only admin users can access protected routes
3. **Expiration Handling**: Reject expired tokens with appropriate errors
4. **Invalid Token Handling**: Secure error responses for malformed tokens
5. **Missing Token Handling**: Clear error messages for missing authentication

### Romanian Localization
1. **Error Messages**: All authentication errors in Romanian
2. **Authorization Messages**: Access denied messages in Romanian
3. **Token Error Messages**: JWT-related errors in Romanian
4. **Consistent Terminology**: Use established Romanian business terms
5. **Local Context**: Messages appropriate for local producer marketplace

### Integration Requirements
1. **AuthService Integration**: Use existing AuthService for token validation
2. **Flask Middleware**: Standard Flask decorator pattern for route protection
3. **Error Handler Integration**: Use existing error handling utilities
4. **Request Context**: Flask request context for admin user data
5. **Blueprint Compatibility**: Work with existing Flask blueprint structure

## Technical Implementation

### Middleware Decorator Structure
```python
from functools import wraps
from flask import request, g
from app.services.auth_service import AuthService
from app.utils.error_handlers import AuthenticationError, create_error_response

def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract and validate JWT token
        # Verify admin role
        # Add user to request context
        # Call protected route
        return f(*args, **kwargs)
    return decorated_function
```

### Token Extraction and Validation
- Extract Bearer token from Authorization header
- Validate token format and structure
- Use AuthService.verify_token() for JWT validation
- Handle various token error scenarios

### Admin Role Authorization
- Verify user role is 'admin' from token payload
- Reject non-admin users with appropriate error
- Ensure only admin users can access protected routes

### Request Context Enhancement
- Add admin user information to Flask request context
- Make user data available to protected route handlers
- Include user ID, name, phone, and role in context

## Success Criteria

1. Middleware successfully validates JWT tokens from Authorization header
2. Admin role verification works correctly for access control
3. Invalid or expired tokens are rejected with Romanian error messages
4. Admin user information is added to request context for protected routes
5. Missing Authorization header returns appropriate Romanian error
6. Malformed tokens are handled with secure error responses
7. Middleware integrates seamlessly with Flask route decorators
8. AuthService integration works without modification
9. Error responses follow established API response format
10. Romanian localization is complete and culturally appropriate

## Implementation Notes

- Use Flask's request context (g object) to store admin user data
- Follow existing error handling patterns from auth endpoints
- Integrate with AuthService for token validation consistency
- Use functools.wraps to preserve original function metadata
- Handle edge cases like malformed Authorization headers
- Provide clear Romanian error messages for all failure scenarios
- Design middleware to be reusable across different admin routes
- Ensure middleware doesn't interfere with non-admin routes