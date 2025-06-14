# Task 36: Add SMS rate limiting protection

## Task Details
- **ID**: 36_sms_rate_limiting
- **Title**: Add SMS rate limiting protection
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: SMS endpoints integration tests (Task 35)

## Objective
Implement rate limiting middleware for SMS verification endpoints to prevent abuse, reduce costs, and ensure compliance with Twilio best practices while maintaining legitimate user access.

## Requirements
1. **Rate Limiting Middleware**: `backend/app/utils/rate_limiter.py`
2. **Configuration**: Configurable rate limits (default: 10 SMS/hour per phone)
3. **Storage**: MongoDB-based rate limit tracking with TTL cleanup
4. **Integration**: Apply to SMS verification endpoints
5. **Error Handling**: Clear rate limit exceeded responses
6. **Flexibility**: Support different rate limits for different endpoints

## Technical Implementation
- **Framework**: Flask request middleware with MongoDB storage
- **Rate Limit**: 10 SMS per hour per phone number (configurable)
- **Storage**: MongoDB collection with TTL indexes for automatic cleanup
- **Key**: Phone number-based rate limiting
- **Algorithm**: Token bucket or sliding window approach
- **Integration**: Decorator pattern for easy endpoint application

## Rate Limiting Strategy

### 1. Rate Limit Configuration
```python
SMS_RATE_LIMITS = {
    'sms_verify': {
        'limit': 10,           # 10 SMS per window
        'window_seconds': 3600, # 1 hour window
        'bucket_size': 10      # Token bucket size
    },
    'sms_confirm': {
        'limit': 50,           # 50 confirmation attempts per window  
        'window_seconds': 3600, # 1 hour window
        'bucket_size': 50      # Token bucket size
    }
}
```

### 2. Storage Schema
```python
{
    "phone_number": "+1234567890",
    "endpoint": "sms_verify",
    "attempts": 3,
    "window_start": "2025-01-13T14:00:00Z", 
    "expires_at": "2025-01-13T15:00:00Z",
    "last_attempt": "2025-01-13T14:15:00Z"
}
```

### 3. Rate Limiting Middleware
```python
def rate_limit(endpoint_name, limit=None, window_seconds=None):
    """Decorator for rate limiting endpoints by phone number."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract phone number from request
            # Check rate limit
            # Update attempt count
            # Return rate limit error if exceeded
            # Continue to endpoint if allowed
            pass
        return decorated_function
    return decorator
```

## Middleware Implementation

### 1. Rate Limit Checker
- **Input**: Phone number, endpoint name
- **Logic**: Check current attempts against limit within time window
- **Output**: Allow/deny decision with remaining attempts info
- **Storage**: MongoDB collection with automatic TTL cleanup

### 2. Rate Limit Updater
- **Timing**: Update attempt count after successful request processing
- **Atomicity**: Use MongoDB atomic operations to prevent race conditions
- **Cleanup**: Automatic cleanup via TTL indexes

### 3. Error Response Format
```python
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Try again in 45 minutes.",
        "details": {
            "phone_number": "+****7890",
            "limit": 10,
            "window_hours": 1,
            "attempts_used": 10,
            "reset_in_seconds": 2700,
            "reset_in_minutes": 45,
            "reset_at": "2025-01-13T15:00:00Z"
        }
    }
}
```

## Integration Points

### 1. SMS Verification Endpoint
```python
@sms_bp.route('/verify', methods=['POST'])
@rate_limit('sms_verify', limit=10, window_seconds=3600)
@validate_json(SMS_VERIFY_SCHEMA)
def send_verification_code():
    # Existing implementation
    pass
```

### 2. SMS Confirmation Endpoint
```python
@sms_bp.route('/confirm', methods=['POST'])  
@rate_limit('sms_confirm', limit=50, window_seconds=3600)
@validate_json(SMS_CONFIRM_SCHEMA)
def confirm_verification_code():
    # Existing implementation
    pass
```

## Database Design

### 1. Rate Limits Collection
- **Collection Name**: `sms_rate_limits`
- **Indexes**: TTL index on `expires_at`, compound index on `phone_number + endpoint`
- **TTL**: Automatic cleanup after window expiry
- **Atomicity**: Use MongoDB `$inc` for atomic counter updates

### 2. Index Configuration
```python
# TTL index for automatic cleanup
db.sms_rate_limits.create_index("expires_at", expireAfterSeconds=0)

# Compound index for efficient queries
db.sms_rate_limits.create_index([
    ("phone_number", 1),
    ("endpoint", 1)
])
```

## Rate Limiting Algorithms

### 1. Sliding Window Approach
- **Window**: Fixed time window (1 hour)
- **Tracking**: Count attempts within sliding window
- **Reset**: Automatic reset when window expires
- **Precision**: More accurate but slightly more complex

### 2. Token Bucket Approach (Alternative)
- **Bucket**: Each phone number has a token bucket
- **Refill**: Tokens refill at fixed rate (10 tokens/hour)
- **Consumption**: Each SMS request consumes 1 token
- **Overflow**: Excess tokens are discarded

## Security Considerations

### 1. Phone Number Privacy
- **Logging**: Log only last 4 digits for privacy
- **Storage**: Store full phone number for rate limiting accuracy
- **Responses**: Mask phone number in error responses

### 2. Bypass Prevention
- **Key Consistency**: Use normalized phone numbers (E.164 format)
- **Multiple Endpoints**: Apply rate limiting across all SMS endpoints
- **Distributed Protection**: Rate limits apply per phone number globally

### 3. Configuration Security
- **Environment Variables**: Rate limits configurable via environment
- **Defaults**: Secure default values (10 SMS/hour)
- **Monitoring**: Log rate limit violations for security monitoring

## Error Scenarios

### 1. Rate Limit Exceeded
- **HTTP Status**: 429 Too Many Requests
- **Response**: Detailed rate limit information
- **Headers**: Include rate limit headers (X-RateLimit-*)
- **Logging**: Log rate limit violations

### 2. Database Errors
- **Fallback**: Allow request if rate limit check fails
- **Logging**: Log database connection issues
- **Monitoring**: Alert on rate limiter failures

### 3. Configuration Errors
- **Defaults**: Use safe default values
- **Validation**: Validate rate limit configuration on startup
- **Graceful Degradation**: Disable rate limiting if configuration invalid

## Testing Strategy

### 1. Unit Tests
- **Rate Limit Logic**: Test rate limiting calculations
- **Window Behavior**: Test window reset and sliding behavior
- **Error Conditions**: Test database errors and configuration issues

### 2. Integration Tests
- **Endpoint Integration**: Test rate limiting on actual endpoints
- **Multiple Requests**: Test sequential request handling
- **Time-based Testing**: Test window reset behavior

### 3. Load Testing
- **Concurrent Requests**: Test race condition handling
- **High Volume**: Test performance under load
- **Memory Usage**: Verify efficient resource usage

## Monitoring and Alerting

### 1. Metrics Collection
- **Rate Limit Hits**: Count rate limit violations by phone/endpoint
- **Attempt Distribution**: Track usage patterns
- **Error Rates**: Monitor rate limiter failure rates

### 2. Logging Strategy
```python
# Rate limit exceeded
logger.warning(f"Rate limit exceeded for phone ending in {phone_number[-4:]} on {endpoint}")

# Rate limit reset
logger.info(f"Rate limit window reset for phone ending in {phone_number[-4:]}")

# Database errors
logger.error(f"Rate limiter database error: {str(e)}")
```

## Configuration Options

### 1. Environment Variables
```bash
# SMS rate limiting configuration
SMS_RATE_LIMIT_VERIFY_PER_HOUR=10
SMS_RATE_LIMIT_CONFIRM_PER_HOUR=50
SMS_RATE_LIMIT_WINDOW_SECONDS=3600
SMS_RATE_LIMIT_ENABLED=true
```

### 2. Default Configuration
```python
DEFAULT_RATE_LIMITS = {
    'sms_verify': {'limit': 10, 'window_seconds': 3600},
    'sms_confirm': {'limit': 50, 'window_seconds': 3600},
    'enabled': True
}
```

## Implementation Checklist

### 1. Core Implementation
- [ ] Create rate limiting middleware in `backend/app/utils/rate_limiter.py`
- [ ] Implement MongoDB storage with TTL indexes
- [ ] Create rate limit decorator for endpoint protection
- [ ] Implement proper error responses and logging

### 2. Integration
- [ ] Apply rate limiting to SMS verification endpoints
- [ ] Update existing SMS routes with rate limit decorators
- [ ] Ensure rate limit information in SMS service responses
- [ ] Update error handling for rate limit scenarios

### 3. Configuration
- [ ] Add rate limit configuration to config.py
- [ ] Create environment variable support
- [ ] Implement configuration validation
- [ ] Add graceful degradation for misconfigurations

### 4. Testing
- [ ] Create unit tests for rate limiting logic
- [ ] Create integration tests for endpoint protection
- [ ] Test rate limit reset and cleanup behavior
- [ ] Verify rate limit information in responses

## Success Criteria
- Rate limiting middleware blocks excessive SMS requests (>10/hour per phone)
- Clear error responses with rate limit information
- Automatic cleanup of expired rate limit records
- Configurable rate limits via environment variables
- No impact on legitimate user verification flows
- Proper logging and monitoring of rate limit events