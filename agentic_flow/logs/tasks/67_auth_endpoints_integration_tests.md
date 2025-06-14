# Task 67: Create auth API integration tests

**ID**: 67_auth_endpoints_integration_tests  
**Title**: Create auth API integration tests  
**Description**: Write integration tests for authentication endpoints  
**Dependencies**: Admin authentication middleware creation (Task 66)  
**Estimate**: 20 minutes  
**Deliverable**: backend/tests/test_auth_api.py with integration tests

## Context

The admin authentication system is complete with endpoints, middleware, and service layer. Now we need comprehensive integration tests to validate the complete authentication API including admin login, logout, token refresh, token verification, and initial admin setup endpoints with their request/response flows.

## Requirements

### Core Integration Test Coverage
1. **Admin Login API Tests**: Test POST /api/auth/admin/login endpoint functionality
2. **Admin Logout API Tests**: Test POST /api/auth/admin/logout endpoint functionality
3. **Token Refresh API Tests**: Test POST /api/auth/admin/refresh endpoint functionality
4. **Token Verification API Tests**: Test POST /api/auth/admin/verify endpoint functionality
5. **Initial Setup API Tests**: Test POST /api/auth/admin/setup endpoint functionality

### Authentication Flow Tests
1. **Complete Login Flow**: Test full authentication cycle from login to protected route access
2. **Token Lifecycle**: Test token generation, usage, refresh, and expiration
3. **Error Scenarios**: Test various failure modes and error responses
4. **Security Features**: Test rate limiting, IP tracking, and role verification
5. **Romanian Localization**: Test all Romanian error and success messages

### Request/Response Validation
1. **Request Format Validation**: Test JSON payload validation and required fields
2. **Response Structure Validation**: Test consistent API response format
3. **HTTP Status Codes**: Test appropriate status codes for different scenarios
4. **Content Type Handling**: Test JSON content type requirements
5. **Header Processing**: Test Authorization header handling

### Security Testing
1. **Invalid Token Handling**: Test malformed, expired, and missing tokens
2. **Role-Based Access**: Test admin role verification and non-admin rejection
3. **Rate Limiting**: Test brute force protection and lockout mechanisms
4. **IP Tracking**: Test client IP logging and rate limiting by IP
5. **Error Information**: Test secure error responses without sensitive data exposure

### Romanian Message Testing
1. **Error Message Validation**: Test all Romanian error messages are returned correctly
2. **Success Message Validation**: Test Romanian success messages
3. **Validation Error Messages**: Test Romanian field validation errors
4. **Consistency Testing**: Test consistent Romanian terminology across endpoints
5. **Cultural Appropriateness**: Test messages are appropriate for local producer marketplace

## Technical Implementation

### Test Structure
```python
import pytest
from flask import json
from app import create_app
from app.config import TestingConfig
from app.services.auth_service import AuthService

class TestAdminAuthAPI:
    def setup_method(self):
        # Setup test environment
        
    def test_admin_login_success(self):
        # Test successful admin login
        
    def test_admin_login_invalid_credentials(self):
        # Test login with wrong credentials
        
    def test_token_refresh_success(self):
        # Test successful token refresh
        
    def test_token_verification_success(self):
        # Test token verification
        
    def test_admin_setup_success(self):
        # Test initial admin creation
```

### Mock Strategy
- Mock AuthService for consistent test behavior
- Mock database operations for isolated testing
- Mock JWT token generation for predictable tokens
- Mock IP address tracking for rate limiting tests
- Mock datetime for token expiration testing

### Test Data Setup
- Create test admin users with known credentials
- Generate test JWT tokens with controlled expiration
- Prepare Romanian error message validation data
- Set up rate limiting scenarios
- Create invalid request payloads for error testing

## Success Criteria

1. All admin authentication endpoints have comprehensive integration test coverage
2. Romanian error and success messages are tested and validated
3. Complete authentication flows are tested end-to-end
4. Token lifecycle management is thoroughly tested
5. Security features like rate limiting and role verification are validated
6. Error scenarios and edge cases are properly covered
7. Request/response validation works correctly
8. HTTP status codes are appropriate for all scenarios
9. API response format is consistent across all endpoints
10. Romanian localization is validated across all test cases

## Implementation Notes

- Use Flask test client for API endpoint testing
- Mock external dependencies like database and AuthService
- Test Romanian error messages with exact string matching
- Include edge cases like malformed JSON and missing headers
- Test rate limiting with time-based scenarios
- Validate JWT token structure and claims in responses
- Test authentication middleware integration
- Ensure tests are deterministic and don't depend on external state
- Include performance timing validation for authentication operations