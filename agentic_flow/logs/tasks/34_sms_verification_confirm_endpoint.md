# Task 34: Create POST /api/sms/confirm endpoint

## Task Details
- **ID**: 34_sms_verification_confirm_endpoint
- **Title**: Create POST /api/sms/confirm endpoint
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: SMS verification send endpoint

## Objective
Implement POST /api/sms/confirm endpoint to confirm SMS verification codes and validate phone numbers, with proper validation, error handling, and session creation for verified phone numbers.

## Requirements
1. **Endpoint**: `POST /api/sms/confirm`
2. **Route File**: `backend/app/routes/sms.py` (add to existing file)
3. **Request Validation**: JSON schema validation for phone number and verification code
4. **Code Verification**: Use SMS service to validate verification codes
5. **Error Handling**: Comprehensive error responses for invalid/expired codes
6. **Session Creation**: Create verification session for successful confirmations
7. **Integration**: Use existing SMS service and validation middleware

## Technical Implementation
- **HTTP Method**: POST
- **Content Type**: application/json
- **Request Body**: `{"phone_number": "+1234567890", "verification_code": "123456"}`
- **Response Format**: Standard API response format
- **Status Codes**: 200 (success), 400 (validation error), 404 (code not found), 410 (expired), 500 (service error)

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
    },
    "verification_code": {
      "type": "string",
      "pattern": "^\\d{6}$",
      "description": "6-digit verification code"
    }
  },
  "required": ["phone_number", "verification_code"],
  "additionalProperties": false
}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "phone_number": "+1234567890",
    "verified": true,
    "verified_at": "2025-01-13T14:30:00Z",
    "session_id": "507f1f77bcf86cd799439011",
    "expires_at": "2025-01-13T16:30:00Z"
  },
  "message": "Phone number verified successfully"
}
```

### Invalid Code Response (400)
```json
{
  "success": false,
  "error": {
    "code": "SMS_002",
    "message": "Invalid verification code",
    "field": "verification_code"
  }
}
```

### Code Not Found Response (404)
```json
{
  "success": false,
  "error": {
    "code": "SMS_002",
    "message": "No verification code found for this phone number"
  }
}
```

### Expired Code Response (410)
```json
{
  "success": false,
  "error": {
    "code": "SMS_003",
    "message": "Verification code has expired"
  }
}
```

## Route Implementation Structure
```python
# JSON Schema for confirm request validation
SMS_CONFIRM_SCHEMA = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "pattern": "^\\+[1-9]\\d{1,14}$"
        },
        "verification_code": {
            "type": "string",
            "pattern": "^\\d{6}$"
        }
    },
    "required": ["phone_number", "verification_code"],
    "additionalProperties": False
}

@sms_bp.route('/confirm', methods=['POST'])
@validate_json(SMS_CONFIRM_SCHEMA)
def confirm_verification_code():
    """Confirm SMS verification code and validate phone number."""
    # Implementation details
```

## Error Scenarios to Handle
1. **Validation Errors**:
   - Missing phone_number or verification_code fields
   - Invalid phone number format
   - Invalid verification code format (not 6 digits)
   - Malformed JSON request

2. **Verification Errors**:
   - No verification code found for phone number
   - Verification code has expired
   - Incorrect verification code
   - Code already used/verified

3. **System Errors**:
   - SMS service unavailable
   - Database connection issues
   - Unexpected service errors

## Verification Session Management
1. **Session Creation**: Generate session ID for verified phone numbers
2. **Session Expiry**: Set appropriate expiry time (2 hours for verification sessions)
3. **Session Storage**: Store verification session in database
4. **Session Validation**: Prevent duplicate verifications

## Integration Points
1. **SMS Service**: Use `get_sms_service().validate_recent_code()`
2. **Validation Middleware**: Use `@validate_json` decorator
3. **Error Handling**: Use existing error handler infrastructure
4. **Session Management**: Create verification sessions for order process
5. **Database**: Store verification sessions with TTL

## Security Considerations
1. **Code Validation**: Strict 6-digit numeric code validation
2. **Single Use**: Prevent code reuse after successful verification
3. **Time Limits**: Enforce code expiry (10 minutes)
4. **Rate Limiting**: Leverage existing SMS service rate limiting
5. **Session Security**: Generate secure session IDs

## Testing Criteria
1. Successful code confirmation returns proper response format
2. Invalid codes return appropriate error responses
3. Expired codes return 410 status with proper message
4. Missing codes return 404 status
5. Malformed requests return validation errors
6. Session creation works correctly for verified phones
7. All responses follow standard API format

## Session Data Structure
```python
verification_session = {
    "session_id": "507f1f77bcf86cd799439011",
    "phone_number": "+1234567890",
    "verified": True,
    "verified_at": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(hours=2),
    "created_at": datetime.utcnow()
}
```

## Success Criteria
- POST /api/sms/confirm endpoint added to existing SMS routes
- Integration with SMS service working properly
- Comprehensive error handling for all verification scenarios
- Session creation for verified phone numbers
- Ready for order process integration