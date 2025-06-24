# Authentication & Session Analysis Report

## Executive Summary

The Pe Foc de Lemne application implements a dual authentication system:
1. **Admin Authentication**: Traditional JWT-based authentication for admin users
2. **Checkout Authentication**: Phone-based authentication for customers during checkout

Both systems use JWT tokens but have distinct characteristics, security measures, and use cases. The checkout system prioritizes user convenience with phone-based verification, while the admin system uses standard username/password authentication.

## Authentication Flow Diagram

### Checkout Authentication Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Customer  │     │   Frontend  │     │   Backend   │     │ SMS Provider│
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                     │                    │
       │ Enter Phone/Name  │                     │                    │
       │──────────────────>│                     │                    │
       │                   │                     │                    │
       │                   │ POST /send-code     │                    │
       │                   │────────────────────>│                    │
       │                   │                     │                    │
       │                   │                     │ Validate & Generate │
       │                   │                     │ 6-digit code       │
       │                   │                     │                    │
       │                   │                     │ Send SMS           │
       │                   │                     │───────────────────>│
       │                   │                     │                    │
       │                   │ Response            │                    │
       │                   │<────────────────────│                    │
       │                   │                     │                    │
       │ Show Code Input   │                     │                    │
       │<──────────────────│                     │                    │
       │                   │                     │                    │
       │ Enter 6-digit code│                     │                    │
       │──────────────────>│                     │                    │
       │                   │                     │                    │
       │                   │ POST /verify-code   │                    │
       │                   │────────────────────>│                    │
       │                   │                     │                    │
       │                   │                     │ Verify code        │
       │                   │                     │ Generate JWT       │
       │                   │                     │                    │
       │                   │ JWT Token           │                    │
       │                   │<────────────────────│                    │
       │                   │                     │                    │
       │                   │ Store in localStorage│                   │
       │                   │                     │                    │
       │ Authenticated     │                     │                    │
       │<──────────────────│                     │                    │
```

### Admin Authentication Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Admin    │     │   Frontend  │     │   Backend   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                     │
       │ Enter Credentials │                     │
       │──────────────────>│                     │
       │                   │                     │
       │                   │ POST /auth/login    │
       │                   │────────────────────>│
       │                   │                     │
       │                   │                     │ Verify password
       │                   │                     │ Generate JWT
       │                   │                     │
       │                   │ Access & Refresh    │
       │                   │<────────────────────│
       │                   │                     │
       │                   │ Store tokens        │
       │                   │                     │
       │ Admin Dashboard   │                     │
       │<──────────────────│                     │
```

## JWT Token Structure

### Checkout Token Claims
```json
{
  "phone": "+40712345678",      // Normalized phone number
  "customer_id": "507f1f77...",  // MongoDB ObjectId
  "exp": 1704067200,             // Expires in 24 hours
  "iat": 1703980800,             // Issued at timestamp
  "type": "checkout_session"     // Token type identifier
}
```

### Admin Token Claims
```json
{
  "user_id": "507f1f77...",      // MongoDB ObjectId
  "phone_number": "+40712345678", // Admin phone
  "name": "Admin Name",          // Full name
  "role": "admin",               // Role (always "admin")
  "exp": 1704067200,             // Expiration timestamp
  "iat": 1703980800,             // Issued at timestamp
  "iss": "pe-foc-de-lemne",     // Issuer
  "aud": "admin-dashboard"       // Audience
}
```

## Session Lifecycle

### Checkout Session
1. **Creation**: Generated after successful phone verification
2. **Duration**: 24 hours from verification
3. **Storage**: localStorage key `checkout_token`
4. **Refresh**: No refresh mechanism, requires re-verification
5. **Invalidation**: Manual logout or token expiration

### Admin Session
1. **Creation**: Generated after successful login
2. **Duration**: Access token (15 min), Refresh token (7 days)
3. **Storage**: 
   - Access: localStorage key `auth_access_token`
   - Refresh: localStorage key `auth_refresh_token`
4. **Refresh**: Automatic refresh using refresh token
5. **Invalidation**: Logout endpoint or token expiration

## Security Measures

### Rate Limiting

#### SMS Rate Limits
- **Per Phone**: 3 SMS per day
- **Per IP**: 5 SMS per hour
- **Verification Attempts**: 5 attempts per code
- **Address Limit**: 50 addresses per customer

#### Implementation
```python
# CheckoutRateLimiter configuration
limits = {
    'sms_per_phone_per_day': {'max': 3, 'window': 86400},
    'sms_per_ip_per_hour': {'max': 5, 'window': 3600},
    'verify_attempts_per_code': {'max': 5, 'window': 300},
    'addresses_per_customer': {'max': 50, 'window': None}
}
```

### Token Security
1. **HS256 Algorithm**: Symmetric key signing
2. **Secret Key**: Configured via environment variable
3. **Token Validation**: Checks type, expiration, and required fields
4. **IP Tracking**: Client IP logged for security monitoring

### Phone Number Security
1. **Normalization**: Converts to international format (+40)
2. **Validation**: Regex pattern for Romanian mobile numbers
3. **Masking**: Shows only last 4 digits in responses
4. **Privacy**: Full number stored encrypted in database

## Frontend Token Management

### Storage Strategy
```javascript
// Token priority in API requests (from api.js)
if ((config.url?.includes('/checkout/') || config.url?.includes('/orders')) && checkoutToken) {
  config.headers.Authorization = `Bearer ${checkoutToken}`;
} else if (adminToken) {
  config.headers.Authorization = `Bearer ${adminToken}`;
} else if (authToken) {
  config.headers.Authorization = `Bearer ${authToken}`;
} else if (checkoutToken) {
  config.headers.Authorization = `Bearer ${checkoutToken}`;
}
```

### Token Storage Locations
- **Checkout Token**: `localStorage.getItem('checkout_token')`
- **Admin Access Token**: `localStorage.getItem('auth_access_token')`
- **Admin Refresh Token**: `localStorage.getItem('auth_refresh_token')`
- **Legacy Auth Token**: `localStorage.getItem('authToken')`

## Guest vs Authenticated Checkout

### Guest Checkout
- Not implemented in current system
- All checkouts require phone verification
- No anonymous ordering capability

### Authenticated Checkout
- Phone verification required
- Access to saved addresses
- Order history tracking
- Automatic address suggestions

## Security Vulnerabilities Identified

### 1. Weak Secret Key in Development
```python
secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
```
**Risk**: Hardcoded fallback secret key in production
**Recommendation**: Enforce SECRET_KEY configuration, fail if missing

### 2. Token Storage in localStorage
**Risk**: XSS attacks can access tokens
**Recommendation**: Consider httpOnly cookies for token storage

### 3. No Token Revocation Mechanism
**Risk**: Cannot invalidate compromised tokens
**Recommendation**: Implement token blacklist or use shorter expiration

### 4. SMS Code Predictability
**Risk**: 6-digit numeric codes are relatively weak
**Recommendation**: Increase code length or add alphanumeric characters

### 5. Extensive Logging of Sensitive Data
```python
logger.info(f"Decoded payload: {payload}")  # Logs full token payload
```
**Risk**: Token contents in logs
**Recommendation**: Remove or mask sensitive data in logs

## Recommendations for Improvement

### 1. Enhanced Security
- Implement CSRF protection for state-changing operations
- Add token refresh mechanism for checkout sessions
- Implement device fingerprinting for additional security
- Add optional 2FA for high-value orders

### 2. Performance Optimization
- Cache customer data to reduce database queries
- Implement connection pooling for Redis
- Add request deduplication for SMS sending

### 3. User Experience
- Add "Remember Me" option for checkout sessions
- Implement magic link authentication as alternative
- Add social login options (Google, Facebook)
- Allow email-based authentication as fallback

### 4. Monitoring & Analytics
- Track authentication success/failure rates
- Monitor SMS delivery rates by provider
- Alert on unusual authentication patterns
- Implement fraud detection for suspicious activity

### 5. Code Quality
- Centralize token management in a dedicated service
- Add comprehensive error handling for edge cases
- Implement proper token refresh logic
- Add integration tests for authentication flows

## Middleware Comparison

| Feature | Checkout Auth | Admin Auth |
|---------|--------------|------------|
| Decorator | `@checkout_auth_required` | `@require_admin_auth` |
| Optional Auth | `@checkout_auth_optional` | `@require_admin_auth_optional` |
| Token Type | `checkout_session` | Standard JWT |
| Expiration | 24 hours | 15 min (access) / 7 days (refresh) |
| Refresh | No | Yes |
| Context Variables | `g.customer_phone`, `g.customer_id` | `g.current_admin_user` |
| Error Messages | Romanian | Romanian |
| Rate Limited | Yes | No |

## Session Data Model

### CustomerPhone Collection
```javascript
{
  _id: ObjectId,
  phone: "+40712345678",        // Normalized
  name: "Customer Name",
  addresses: [{
    _id: ObjectId,
    street: "Strada Example 123",
    city: "București",
    county: "București",
    postal_code: "012345",
    notes: "",
    is_default: true,
    usage_count: 5,
    created_at: ISODate,
    last_used: ISODate
  }],
  verification: {
    code: "123456",              // Current code
    code_expires: ISODate,       // 5 min expiry
    attempts: 0,
    last_code_sent: ISODate,
    attempts_today: 1,
    blocked_until: ISODate,      // Rate limit block
    verified_at: ISODate
  },
  total_orders: 10,
  last_order_date: ISODate,
  created_at: ISODate,
  updated_at: ISODate,
  __v: 0                         // Version for optimistic locking
}
```

## Conclusion

The authentication system successfully implements a user-friendly phone-based checkout flow while maintaining security through rate limiting and JWT tokens. However, several security enhancements are recommended, particularly around token storage, secret key management, and logging practices. The dual authentication system (admin vs checkout) is well-separated but could benefit from unified token management and consistent security policies.