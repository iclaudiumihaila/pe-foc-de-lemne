# Task 35: Create SMS API integration tests

## Task Details
- **ID**: 35_sms_endpoints_integration_tests
- **Title**: Create SMS API integration tests
- **Priority**: High
- **Estimate**: 25 minutes
- **Dependencies**: SMS verification confirm endpoint

## Objective
Write comprehensive integration tests for SMS verification endpoints including sending codes, confirming codes, status checking, and rate limiting functionality with proper mocking and error scenario testing.

## Requirements
1. **Test File**: `backend/tests/test_sms_api.py`
2. **Test Framework**: pytest with Flask test client integration
3. **Coverage**: All SMS API endpoints and error scenarios
4. **Mocking Strategy**: Mock SMS service and database operations
5. **Test Scenarios**: Success cases, error cases, rate limiting, validation
6. **Integration**: Test complete SMS verification flow

## Technical Implementation
- **Framework**: pytest with comprehensive mocking
- **Client**: Flask test client for HTTP requests
- **Mocking**: Mock SMS service, database operations, and external dependencies
- **Assertions**: Validate HTTP status codes, response structure, and data integrity

## Test Scenarios to Cover

### 1. POST /api/sms/verify Tests
- ✅ Send verification code successfully
- ✅ Handle invalid phone number format
- ✅ Handle rate limiting (5 SMS per hour exceeded)
- ✅ Handle SMS service failures
- ✅ Handle database errors
- ✅ Validate response format and data

### 2. POST /api/sms/confirm Tests
- ✅ Confirm verification code successfully with session creation
- ✅ Handle invalid verification code format
- ✅ Handle incorrect verification codes
- ✅ Handle expired verification codes
- ✅ Handle missing verification codes
- ✅ Validate session creation and response format

### 3. GET /api/sms/status/{phone_number} Tests
- ✅ Get verification status successfully
- ✅ Handle invalid phone number format
- ✅ Handle phone numbers with no verification history
- ✅ Validate status data format

### 4. GET /api/sms/rate-limit/{phone_number} Tests
- ✅ Get rate limit information successfully
- ✅ Handle invalid phone number format
- ✅ Validate rate limit data format

### 5. Error Handling Tests
- ✅ Malformed JSON requests
- ✅ Missing required fields
- ✅ Invalid field formats
- ✅ SMS service unavailable scenarios
- ✅ Database connection failures

### 6. Integration Flow Tests
- ✅ Complete verification flow (send → confirm)
- ✅ Multiple verification attempts
- ✅ Session management workflow

## Expected Test Structure
```python
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

class TestSMSAPI:
    def test_send_verification_code_success(self, client):
        # Test successful verification code sending
        pass
    
    def test_confirm_verification_code_success(self, client):
        # Test successful code confirmation
        pass
    
    def test_complete_verification_flow(self, client):
        # Test end-to-end verification process
        pass
    
    def test_rate_limiting_behavior(self, client):
        # Test rate limiting functionality
        pass
```

## Mocking Strategy

### 1. SMS Service Mocking
```python
@patch('app.routes.sms.get_sms_service')
def test_sms_service_integration(self, mock_get_sms_service, client):
    mock_service = MagicMock()
    mock_get_sms_service.return_value = mock_service
    # Test SMS service operations
```

### 2. Database Operations Mocking
```python
@patch('app.routes.sms.get_database')
def test_database_operations(self, mock_get_database, client):
    mock_db = MagicMock()
    mock_get_database.return_value = mock_db
    # Test database operations
```

### 3. Session Creation Mocking
```python
@patch('app.routes.sms.create_verification_session')
def test_session_management(self, mock_create_session, client):
    mock_create_session.return_value = {
        'session_id': 'test_session_id',
        'expires_at': datetime.utcnow() + timedelta(hours=2)
    }
    # Test session creation
```

## Response Validation

### 1. Success Response Structure
```python
def validate_success_response(self, response_data):
    assert 'success' in response_data
    assert response_data['success'] is True
    assert 'data' in response_data
    assert 'message' in response_data
```

### 2. Error Response Structure
```python
def validate_error_response(self, response_data):
    assert 'success' in response_data
    assert response_data['success'] is False
    assert 'error' in response_data
    assert 'code' in response_data['error']
    assert 'message' in response_data['error']
```

## Test Data

### 1. Valid Test Data
```python
VALID_PHONE_NUMBERS = [
    '+1234567890',
    '+44123456789',
    '+33123456789'
]

VALID_VERIFICATION_CODES = [
    '123456',
    '000000',
    '999999'
]
```

### 2. Invalid Test Data
```python
INVALID_PHONE_NUMBERS = [
    '1234567890',    # Missing +
    '+1234',         # Too short
    'invalid',       # Non-numeric
    '',              # Empty
]

INVALID_VERIFICATION_CODES = [
    '12345',         # Too short
    '1234567',       # Too long
    'abcdef',        # Non-numeric
    '',              # Empty
]
```

## Error Scenario Testing

### 1. Rate Limiting Tests
- Test successful sending within rate limit
- Test rate limit exceeded scenario
- Test rate limit reset behavior
- Validate rate limit error response format

### 2. SMS Service Error Tests
- Test SMS service unavailable
- Test Twilio API failures
- Test invalid phone number responses
- Validate error code mapping

### 3. Database Error Tests
- Test database connection failures
- Test session creation failures
- Test verification storage failures
- Validate error handling and recovery

## Integration Flow Testing

### 1. Complete Verification Flow
```python
def test_complete_sms_verification_flow(self, client):
    # 1. Send verification code
    # 2. Confirm verification code
    # 3. Verify session creation
    # 4. Check verification status
```

### 2. Multiple Attempt Scenarios
```python
def test_multiple_verification_attempts(self, client):
    # Test multiple send attempts
    # Test rate limiting enforcement
    # Test code expiry and renewal
```

## Testing Criteria
1. All test cases pass successfully
2. HTTP status codes are validated correctly
3. Response format consistency across all endpoints
4. Error scenarios are comprehensively tested
5. Rate limiting behavior is properly validated
6. Session management works correctly
7. Complete verification flow integration works
8. Proper mocking isolates external dependencies

## Mock Response Examples

### 1. SMS Service Responses
```python
mock_send_result = {
    'success': True,
    'code_sent': True,
    'message_sid': 'SM123456789',
    'mock_mode': True,
    'verification_code': '123456'  # Only in mock mode
}

mock_validation_result = True  # or raises SMSError
```

### 2. Database Responses
```python
mock_session_data = {
    'session_id': '507f1f77bcf86cd799439011',
    'expires_at': datetime.utcnow() + timedelta(hours=2)
}
```

## Success Criteria
- Complete test file created at `backend/tests/test_sms_api.py`
- All SMS API endpoints thoroughly tested
- Comprehensive mocking strategy implemented
- All integration scenarios covered
- Error handling validated for all failure cases
- Rate limiting behavior properly tested
- Session management functionality verified