# Task 31: Create SMS service module

## Task Details
- **ID**: 31_sms_service_creation
- **Title**: Create SMS service module
- **Priority**: High
- **Estimate**: 25 minutes
- **Dependencies**: Configuration management

## Objective
Implement Twilio SMS service with send verification code function to enable phone number verification for the order process.

## Requirements
1. **Service File**: `backend/app/services/sms_service.py`
2. **Twilio Integration**: Use Twilio API for SMS sending
3. **Verification Codes**: Generate and send 6-digit verification codes
4. **Rate Limiting**: Basic rate limiting to prevent abuse
5. **Error Handling**: Comprehensive error handling for Twilio failures
6. **Configuration**: Use environment variables for Twilio credentials
7. **Code Storage**: Store verification codes in MongoDB with TTL

## Technical Implementation
- **Library**: Twilio Python SDK
- **Code Generation**: Random 6-digit numeric codes
- **Storage**: MongoDB collection with TTL for automatic cleanup
- **Phone Format**: E.164 format validation
- **Logging**: Log all SMS operations for monitoring

## Core Functions to Implement

### 1. SMS Service Class
```python
class SMSService:
    def __init__(self):
        # Initialize Twilio client
        pass
    
    def send_verification_code(self, phone_number: str) -> dict:
        # Generate and send verification code
        pass
    
    def verify_code(self, phone_number: str, code: str) -> bool:
        # Verify provided code against stored code
        pass
```

### 2. Verification Code Management
- Generate random 6-digit codes
- Store codes with phone number and expiry timestamp
- Automatic cleanup after 10 minutes using MongoDB TTL
- Handle duplicate phone number scenarios

### 3. Error Scenarios to Handle
- Invalid phone number format
- Twilio API failures
- Rate limiting (max 5 SMS per phone per hour)
- Database storage failures
- Invalid or expired verification codes

## Expected Service Structure
```python
from twilio.rest import Client
from app.database import get_database
import random
import logging
from datetime import datetime, timedelta

class SMSService:
    def __init__(self):
        self.client = Client(account_sid, auth_token)
        self.db = get_database()
        self.collection = self.db.verification_codes
        
    def send_verification_code(self, phone_number):
        # Implementation details
        pass
```

## Testing Criteria
1. Service can send SMS successfully via Twilio
2. Verification codes are properly generated and stored
3. Code verification works correctly
4. Rate limiting prevents abuse
5. Error handling manages all failure scenarios
6. Phone number format validation works
7. MongoDB TTL properly expires old codes

## Success Criteria
- Complete SMS service file created at `backend/app/services/sms_service.py`
- All core functions implemented and working
- Comprehensive error handling for all scenarios
- Integration with existing configuration management
- Ready for API endpoint integration