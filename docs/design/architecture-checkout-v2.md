# Simplified Checkout Architecture (Revised)

## System Design

### Data Model

#### Collection: `customer_phones`
```javascript
{
  "_id": ObjectId,
  "phone": String (unique, indexed),
  "name": String,
  "addresses": [{
    "_id": ObjectId,
    "street": String,
    "city": String,
    "county": String,
    "postal_code": String,
    "notes": String (optional),
    "is_default": Boolean,
    "usage_count": Number,
    "last_used": Date,
    "created_at": Date
  }],
  "verification": {
    "last_code_sent": Date,
    "attempts_today": Number,
    "blocked_until": Date (optional)
  },
  "created_at": Date,
  "updated_at": Date,
  "total_orders": Number,
  "last_order_date": Date,
  "__v": Number // Version for optimistic locking
}

// Indexes:
- phone: unique
- phone + verification.last_code_sent: compound
- verification.blocked_until: TTL (auto-cleanup)
```

#### Orders Collection Update
```javascript
{
  // ... existing fields ...
  "customer_phone_id": ObjectId, // Reference to customer_phones
  "delivery_address": {
    // Denormalized copy of address at order time
    "street": String,
    "city": String,
    "county": String,
    "postal_code": String,
    "notes": String
  }
}
```

### Session Management

#### Token Structure (JWT)
```javascript
{
  "phone": "+40775156791",
  "phone_id": "ObjectId",
  "verified": true,
  "exp": 1719057600, // 30 minutes
  "iat": 1719055800
}
```

#### Storage
- Store in HTTP-only cookie
- Backup in Redis with TTL
- Key format: `session:phone:+40775156791`

### Error Handling

#### Error Response Format
```javascript
{
  "success": false,
  "error": {
    "code": "SMS_LIMIT_EXCEEDED",
    "message": "Ați depășit limita zilnică de SMS-uri",
    "details": {
      "limit": 3,
      "reset_time": "2025-06-23T00:00:00Z"
    }
  }
}
```

#### Error Codes
- `SMS_LIMIT_EXCEEDED` (429) - Daily SMS limit reached
- `INVALID_VERIFICATION_CODE` (400) - Wrong or expired code
- `PHONE_BLOCKED` (403) - Too many failed attempts
- `SESSION_EXPIRED` (401) - Token expired
- `ADDRESS_LIMIT_EXCEEDED` (400) - Too many addresses (50 max)
- `CONCURRENT_UPDATE` (409) - Version mismatch

### Validation Rules

#### Phone Number
- Pattern: `/^(\+40|0)7[0-9]{8}$/`
- Normalize to international format: +40...

#### Name
- Min length: 3 characters
- Max length: 100 characters
- Pattern: `/^[a-zA-ZăîâșțĂÎÂȘȚ\s\-']+$/`

#### Address Fields
- Street: Required, 5-200 chars
- City: Required, 2-50 chars
- County: Required, must match enum
- Postal Code: Required, 6 digits

### API Endpoints

#### Phone Verification
- `POST /api/checkout/phone/send-code`
  - Body: `{ phone, name }`
  - Returns: `{ codeSent: true, expiresIn: 300 }`
  
- `POST /api/checkout/phone/verify-code`
  - Body: `{ phone, code }`
  - Returns: `{ verified: true, token, addresses: [] }`

#### Address Management
- `GET /api/checkout/addresses`
  - Headers: `Authorization: Bearer <token>`
  - Returns: `{ addresses: [...] }`
  
- `POST /api/checkout/addresses`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ street, city, county, postal_code, notes, is_default }`
  - Returns: `{ address: {...}, total_addresses: 5 }`
  
- `PUT /api/checkout/addresses/:id`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ ...fields, __v }`
  - Returns: `{ address: {...} }`
  
- `DELETE /api/checkout/addresses/:id`
  - Headers: `Authorization: Bearer <token>`
  - Returns: `{ deleted: true }`

#### Order Creation
- `POST /api/checkout/create-order`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ address_id, cart_items, payment_method }`
  - Returns: `{ order: {...}, redirect_url }`

### SMS Service Integration

#### Provider: Twilio (configurable)
```python
SMS_CONFIG = {
    'provider': 'twilio',
    'account_sid': env('TWILIO_ACCOUNT_SID'),
    'auth_token': env('TWILIO_AUTH_TOKEN'),
    'from_number': env('TWILIO_PHONE_NUMBER'),
    'templates': {
        'verification': 'Codul dvs Pe Foc de Lemne: {code}. Valid 5 minute.'
    }
}
```

### Rate Limiting

#### Implementation: Redis-based
```python
RATE_LIMITS = {
    'sms_per_phone_per_day': 3,
    'sms_per_ip_per_hour': 5,
    'verify_attempts_per_code': 5,
    'addresses_per_customer': 50
}
```

### Frontend State Management

```javascript
const checkoutReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CUSTOMER_INFO':
      return { ...state, name, phone };
    case 'CODE_SENT':
      return { ...state, codeSent: true, codeExpiry };
    case 'PHONE_VERIFIED':
      return { ...state, verified: true, token, addresses };
    case 'SELECT_ADDRESS':
      return { ...state, selectedAddress };
    case 'ORDER_CREATED':
      return { ...state, order, redirecting: true };
    default:
      return state;
  }
}
```

### Security Considerations

1. **Rate Limiting**: Redis-based with sliding window
2. **CSRF Protection**: Double-submit cookie pattern
3. **XSS Prevention**: Input sanitization, CSP headers
4. **SQL Injection**: Parameterized queries, input validation
5. **Phone Privacy**: Show only last 4 digits in UI
6. **PII Handling**: Encrypt phone numbers at rest