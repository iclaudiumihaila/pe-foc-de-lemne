# Task 33: Create POST /api/sms/verify endpoint

## Task Details
- **ID**: 33_sms_verification_send_endpoint
- **Title**: Create POST /api/sms/verify endpoint
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: SMS service creation, Basic API blueprint

## Objective
Implement POST /api/sms/verify endpoint to send SMS verification codes to phone numbers using the SMS service, with proper validation, rate limiting, and error handling.

## Requirements
1. **Endpoint**: `POST /api/sms/verify`
2. **Route File**: `backend/app/routes/sms.py`
3. **Request Validation**: JSON schema validation for phone number
4. **Rate Limiting**: Leverage SMS service rate limiting (5 SMS per hour)
5. **Error Handling**: Comprehensive error responses with standard format
6. **Integration**: Use existing SMS service and validation middleware
7. **Logging**: Log all SMS verification attempts

## Technical Implementation
- **HTTP Method**: POST
- **Content Type**: application/json
- **Request Body**: `{"phone_number": "+1234567890"}`
- **Response Format**: Standard API response format
- **Status Codes**: 200 (success), 400 (validation error), 429 (rate limited), 500 (service error)

## Request/Response Specifications

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "phone_number": {
      "type": "string",
      "pattern": "^\\+[1-9]\\d{1,14}$",
      "description": "Phone number in E.164 format"
    }
  },
  "required": ["phone_number"],
  "additionalProperties": false
}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "phone_number": "+1234567890",
    "code_sent": true,
    "expires_in_minutes": 10,
    "message_id": "SM123456789"
  },
  "message": "Verification code sent successfully"
}
```

### Rate Limited Response (429)
```json
{
  "success": false,
  "error": {
    "code": "SMS_001",
    "message": "Rate limit exceeded. Try again in 30 minutes.",
    "details": {
      "attempts_count": 5,
      "rate_limit": 5,
      "reset_in_minutes": 30
    }
  }
}
```

### Validation Error Response (400)
```json
{
  "success": false,
  "error": {
    "code": "VAL_001",
    "message": "Invalid phone number format. Use E.164 format (+1234567890)",
    "field": "phone_number"
  }
}
```

## Route Implementation Structure
```python
from flask import Blueprint, request, jsonify
from app.services.sms_service import get_sms_service
from app.utils.validators import validate_json
from app.utils.error_handlers import handle_api_error
import logging

# JSON Schema for request validation
SMS_VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": "^\\+[1-9]\\d{1,14}$"
        }
    },
    "required": ["phone_number"],
    "additionalProperties": False
}

sms_bp = Blueprint('sms', __name__)

@sms_bp.route('/verify', methods=['POST'])
@validate_json(SMS_VERIFY_SCHEMA)
def send_verification_code():
    """Send SMS verification code to phone number."""
    # Implementation details
```

## Error Scenarios to Handle
1. **Validation Errors**:
   - Missing phone_number field
   - Invalid phone number format
   - Malformed JSON request

2. **Rate Limiting**:
   - Phone number exceeded 5 SMS per hour
   - Return rate limit info and reset time

3. **SMS Service Errors**:
   - Twilio API failures
   - Database storage failures
   - Invalid phone number for SMS service

4. **System Errors**:
   - SMS service unavailable
   - Database connection issues
   - Unexpected service errors

## Integration Points
1. **SMS Service**: Use `get_sms_service().send_verification_code()`
2. **Validation Middleware**: Use `@validate_json` decorator
3. **Error Handling**: Use existing error handler infrastructure
4. **Logging**: Use Flask logging for audit trail
5. **Blueprint Registration**: Register with main Flask app

## Security Considerations
1. **Rate Limiting**: Prevent SMS abuse with phone-based limits
2. **Input Validation**: Strict phone number format validation
3. **Error Responses**: Don't leak sensitive information
4. **Logging**: Log attempts without exposing full phone numbers
5. **CORS**: Ensure proper CORS configuration for frontend

## Testing Criteria
1. Successful SMS sending returns proper response format
2. Invalid phone numbers return validation errors
3. Rate limiting prevents abuse (5 SMS per hour per phone)
4. Twilio failures return appropriate error responses
5. Database errors are handled gracefully
6. All responses follow standard API format
7. Proper HTTP status codes for all scenarios

## Success Criteria
- Complete route file created at `backend/app/routes/sms.py`
- POST /api/sms/verify endpoint fully functional
- Integration with SMS service working properly
- Comprehensive error handling for all scenarios
- Ready for frontend integration and testing