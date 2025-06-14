# Task 65: Create POST /api/auth/login endpoint

**ID**: 65_admin_login_endpoint  
**Title**: Create POST /api/auth/login endpoint  
**Description**: Implement admin login endpoint with credentials validation  
**Dependencies**: Auth service creation (Task 63), Basic API blueprint (Task 12)  
**Estimate**: 20 minutes  
**Deliverable**: POST /api/auth/login route in backend/app/routes/auth.py

## Context

The admin authentication service is complete and fully tested. Now we need to create the Flask endpoint that exposes the admin login functionality through an HTTP API route for the admin panel frontend to consume. This endpoint will handle admin login requests, validate credentials, and return JWT tokens.

## Requirements

### Core Endpoint Functionality
1. **POST /api/auth/login**: Accept admin login credentials and return JWT tokens
2. **Request Validation**: Validate JSON payload with username and password
3. **Authentication Integration**: Use AuthService for credential validation
4. **Token Response**: Return access and refresh tokens on successful login
5. **Error Handling**: Return appropriate HTTP status codes and Romanian error messages

### Request/Response Format
1. **Request Body**: JSON with username (phone number) and password fields
2. **Success Response**: JWT tokens, user info, and expiration details
3. **Error Response**: Romanian error messages with appropriate status codes
4. **Content Type**: application/json for both request and response
5. **CORS Support**: Proper headers for frontend integration

### Security Features
1. **Input Validation**: Validate request payload structure and content
2. **Rate Limiting**: Protect against brute force attacks
3. **IP Tracking**: Include client IP in authentication attempts
4. **Secure Headers**: Set appropriate security headers in responses
5. **Error Sanitization**: Don't expose sensitive system information

### Romanian Localization
1. **Error Messages**: All error responses in Romanian
2. **Success Messages**: Authentication success messages in Romanian
3. **Validation Messages**: Input validation errors in Romanian
4. **Consistent Terminology**: Use established Romanian business terms
5. **Local Context**: Messages appropriate for local producer marketplace

### Integration Requirements
1. **AuthService Integration**: Use existing AuthService for authentication
2. **Blueprint Registration**: Register route with existing API blueprint
3. **Error Handler Integration**: Use existing error handling middleware
4. **Logging Integration**: Log authentication attempts for security monitoring
5. **CORS Integration**: Work with existing CORS configuration

## Technical Implementation

### Endpoint Structure
```python
@api_bp.route('/auth/login', methods=['POST'])
def admin_login():
    # Validate request payload
    # Extract credentials
    # Authenticate using AuthService
    # Return tokens and user info
    # Handle errors with Romanian messages
```

### Request Validation
- Validate JSON payload structure
- Check required fields (username, password)
- Sanitize input data
- Return validation errors in Romanian

### Authentication Flow
- Extract client IP address for rate limiting
- Use AuthService.authenticate_admin() method
- Handle authentication success and failure cases
- Return appropriate HTTP status codes

### Response Format
- Success: 200 with tokens and user info
- Invalid input: 400 with validation errors
- Authentication failure: 401 with Romanian error message
- Rate limited: 429 with lockout information
- Server error: 500 with generic Romanian error message

## Success Criteria

1. Endpoint accepts POST requests to /api/auth/login
2. Request validation works correctly for JSON payload
3. AuthService integration authenticates admin credentials successfully
4. JWT tokens are returned on successful authentication
5. Romanian error messages are returned for all failure scenarios
6. Appropriate HTTP status codes are used for different scenarios
7. Rate limiting protection is implemented and functional
8. Client IP tracking works for security monitoring
9. Endpoint integrates properly with existing Flask blueprint
10. CORS headers allow frontend integration

## Implementation Notes

- Use Flask request object to access JSON payload and client IP
- Integrate with existing AuthService without modification
- Follow established error handling patterns from other endpoints
- Use existing API blueprint structure and registration
- Include comprehensive logging for security monitoring
- Set appropriate HTTP headers for security and CORS
- Handle edge cases like malformed JSON and missing fields
- Return consistent JSON response format across all scenarios