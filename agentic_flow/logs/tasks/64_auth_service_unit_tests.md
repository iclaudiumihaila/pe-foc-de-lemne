# Task 64: Create auth service unit tests

**ID**: 64_auth_service_unit_tests  
**Title**: Create auth service unit tests  
**Description**: Write unit tests for authentication service functions  
**Dependencies**: Admin authentication service creation (Task 63)  
**Estimate**: 20 minutes  
**Deliverable**: backend/tests/test_auth_service.py with comprehensive tests

## Context

The admin authentication service is complete with secure login functionality, JWT token management, password hashing, and Romanian localization. Now we need comprehensive unit tests to ensure all authentication service functions work correctly and handle edge cases properly.

## Requirements

### Core Test Coverage
1. **Admin Authentication Tests**: Test successful and failed login scenarios
2. **JWT Token Tests**: Test token generation, verification, and expiration
3. **Password Management Tests**: Test hashing and verification functionality
4. **Rate Limiting Tests**: Test brute force protection and lockout mechanisms
5. **Error Handling Tests**: Test Romanian error messages and exception handling

### Authentication Flow Tests
1. **Successful Authentication**: Valid admin credentials return tokens
2. **Invalid Credentials**: Wrong username/password returns appropriate errors
3. **Non-Admin Users**: Customer users cannot authenticate as admin
4. **Unverified Accounts**: Unverified admin accounts cannot authenticate
5. **Account Lockout**: Multiple failed attempts trigger lockout

### Token Management Tests
1. **Token Generation**: Access and refresh tokens are generated correctly
2. **Token Verification**: Valid tokens are verified and decoded properly
3. **Token Expiration**: Expired tokens are rejected with proper errors
4. **Token Refresh**: Refresh tokens can generate new access tokens
5. **Invalid Tokens**: Malformed or invalid tokens are rejected

### Security Tests
1. **Password Hashing**: Passwords are hashed securely with bcrypt
2. **Password Verification**: Password verification works correctly
3. **Rate Limiting**: Failed attempts are tracked and lockout works
4. **JWT Security**: Tokens use proper algorithms and validation
5. **Input Validation**: Invalid inputs are rejected with proper errors

### Romanian Localization Tests
1. **Error Messages**: All error messages are in Romanian
2. **Success Messages**: All success responses are in Romanian
3. **Validation Messages**: All validation errors are in Romanian
4. **Consistency**: Romanian messaging is consistent across all functions
5. **Cultural Context**: Messages are appropriate for local producer marketplace

## Technical Implementation

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.error_handlers import AuthenticationError, ValidationError

class TestAuthService:
    def setup_method(self):
        # Setup test environment and mock dependencies
        
    def test_authenticate_admin_success(self):
        # Test successful admin authentication
        
    def test_authenticate_admin_invalid_credentials(self):
        # Test authentication with wrong credentials
        
    def test_generate_token_valid(self):
        # Test JWT token generation
        
    def test_verify_token_valid(self):
        # Test token verification
        
    def test_password_hashing_and_verification(self):
        # Test password security functions
```

### Mock Dependencies
- Mock User model methods for consistent test data
- Mock database connections for isolated testing
- Mock datetime for token expiration testing
- Mock bcrypt for password hashing consistency
- Mock environment variables for configuration

### Test Data Setup
- Create test admin users with known credentials
- Generate test tokens with predictable expiration
- Set up rate limiting scenarios with multiple attempts
- Prepare Romanian error message validation data
- Create edge case scenarios for comprehensive coverage

## Success Criteria

1. All authentication service methods have comprehensive test coverage
2. Romanian error messages are tested and validated
3. JWT token generation and verification are thoroughly tested
4. Password hashing and verification security is validated
5. Rate limiting and brute force protection is tested
6. Edge cases and error conditions are properly covered
7. Tests run independently without side effects
8. All tests pass consistently and reliably
9. Test coverage includes both positive and negative scenarios
10. Romanian localization is validated across all test cases

## Implementation Notes

- Use pytest for test framework with fixtures for setup
- Mock external dependencies like database and User model
- Test Romanian error messages with exact string matching
- Include edge cases like expired tokens and invalid formats
- Test rate limiting with time-based scenarios
- Validate JWT token structure and claims
- Test password security with various input scenarios
- Ensure tests are deterministic and don't depend on external state
- Include integration-style tests for complete authentication flows