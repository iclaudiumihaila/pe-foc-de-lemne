# Ultra-Simplified Checkout Architecture

## Overview
Two-step checkout process with maximum simplicity:
1. Phone verification
2. Address confirmation/creation → Order placement

## Core Principles
- **One page checkout** - Everything happens on a single page
- **Smart defaults** - Auto-select last used address
- **Minimal friction** - No unnecessary steps or confirmations
- **Real SMS** - Production SMS provider even in development

## User Flow

### Step 1: Phone Verification
```
[Phone Input] → [Send Code] → [Enter Code] → [Verify]
```

### Step 2: Address & Order
```
If has addresses:
  → Show last used address (pre-selected)
  → [Place Order] button

If no addresses:
  → Show inline address form
  → [Place Order] button (saves address + creates order)
```

## API Design

### 1. Send Verification Code
```
POST /api/checkout/send-code
{
  "phone": "+40775156791",
  "name": "Ion Popescu"  // Required for new customers
}

Response:
{
  "success": true,
  "message": "Cod trimis"
}
```

### 2. Verify Code
```
POST /api/checkout/verify-code
{
  "phone": "+40775156791",
  "code": "123456"
}

Response:
{
  "success": true,
  "token": "jwt...",
  "customer": {
    "phone": "+40775156791",
    "name": "Ion Popescu",
    "last_address": {
      "_id": "...",
      "street": "Str. Mihai Viteazu 10",
      "city": "București",
      "county": "București",
      "postal_code": "010101"
    }
  }
}

// Or if no addresses:
{
  "success": true,
  "token": "jwt...",
  "customer": {
    "phone": "+40775156791",
    "name": null,
    "last_address": null
  }
}
```

### 3. Validate Cart
```
POST /api/checkout/validate-cart
Headers: Authorization: Bearer <token>
{
  "cart_items": [
    {
      "product_id": "...",
      "quantity": 2
    }
  ]
}

Response:
{
  "success": true,
  "valid": true,
  "total": 125.50,
  "items": [...]
}
```

### 4. Create Order (with optional address)
```
POST /api/checkout/create-order
Headers: Authorization: Bearer <token>
Headers: X-CSRF-Token: <csrf_token>
{
  "cart_items": [         // Required, validated against server
    {
      "product_id": "...",
      "quantity": 2
    }
  ],
  "address": {            // Required if no address_id
    "street": "Str. Mihai Viteazu 10",
    "city": "București",
    "county": "București",
    "postal_code": "010101"
  },
  "address_id": "...",    // Optional, use existing address
  "payment_method": "cash"
}

Response:
{
  "success": true,
  "order": {
    "order_number": "PFL-2025-0001",
    "total": 125.50,
    "items": [...],
    "delivery_address": {...}
  }
}
```

## Frontend Component Structure

### CheckoutPage.jsx
```jsx
<div className="checkout-container">
  {/* Step 1: Phone Verification */}
  {!verified && (
    <PhoneVerification 
      onVerified={handleVerified}
    />
  )}
  
  {/* Step 2: Address & Order */}
  {verified && (
    <OrderFinalization
      customer={customer}
      cart={cart}
      onOrderComplete={handleOrderComplete}
    />
  )}
</div>
```

### PhoneVerification.jsx
- Simple phone input with country code
- SMS code input (6 digits)
- Auto-focus and auto-submit on 6th digit
- Countdown timer for resend

### OrderFinalization.jsx
```jsx
{customer.last_address ? (
  <AddressDisplay 
    address={customer.last_address}
    onEdit={() => setShowAddressForm(true)}
  />
) : (
  <AddressForm 
    compact={true}
    autoFocus={true}
  />
)}

<OrderSummary cart={cart} />
<PlaceOrderButton loading={loading} />
```

## Database Schema Updates

### customer_phones Collection
```javascript
{
  "_id": ObjectId,
  "phone": "+40775156791",
  "name": "Ion Popescu",
  "addresses": [{
    "_id": ObjectId,
    "street": String,
    "city": String,
    "county": String,
    "postal_code": String,
    "is_default": Boolean,
    "last_used": Date,
    "created_at": Date
  }],
  "last_address_id": ObjectId,  // Quick reference to last used
  "created_at": Date,
  "updated_at": Date
}
```

## SMS Provider Configuration

### Use SMSO Provider (Production)
```python
# backend/app/config.py
SMS_PROVIDER = 'smso'  # Always use real provider

SMSO_CONFIG = {
    'api_key': os.getenv('SMSO_API_KEY'),
    'sender': os.getenv('SMSO_SENDER', 'PeFocLemne'),
    'test_mode': False  # Always send real SMS
}
```

## Implementation Tasks

### Backend Tasks
1. Update checkout routes to merge address creation with order
2. Configure SMSO as default SMS provider
3. Add last_address_id field to customer_phones
4. Simplify JWT token structure

### Frontend Tasks
1. Create single-page checkout component
2. Remove multi-step navigation
3. Implement inline address form
4. Add address auto-save on order creation

## UI/UX Guidelines

### Design Principles
- **Mobile-first**: Optimized for touch and small screens
- **Large touch targets**: 48px minimum
- **Clear CTAs**: Single primary action per screen
- **Inline validation**: Immediate feedback
- **Smart defaults**: Pre-fill, auto-select, auto-focus

### Visual Design
- Clean white background
- Single column layout
- Large, readable fonts (16px minimum)
- High contrast (WCAG AA)
- Minimal form fields
- Clear error states

### Micro-interactions
- Phone number formatting as you type
- Auto-advance after code entry
- Loading states with progress indication
- Success animations on order completion

## Error Handling

### User-Friendly Messages
```javascript
const ERROR_MESSAGES = {
  'SMS_LIMIT_EXCEEDED': 'Ați atins limita de SMS-uri. Încercați din nou mâine.',
  'INVALID_CODE': 'Cod incorect. Mai aveți {attempts} încercări.',
  'SESSION_EXPIRED': 'Sesiune expirată. Verificați din nou telefonul.',
  'NETWORK_ERROR': 'Probleme de conexiune. Încercați din nou.',
  'CART_INVALID': 'Coșul de cumpărături a fost modificat. Reîncărcați pagina.',
  'PRODUCT_UNAVAILABLE': 'Produsul {name} nu mai este disponibil.',
  'INSUFFICIENT_STOCK': 'Stoc insuficient pentru {name}.',
  'CSRF_TOKEN_INVALID': 'Token de securitate invalid. Reîncărcați pagina.'
}
```

## Testing Strategy

### Manual Testing Checklist
- [ ] Phone verification with real SMS
- [ ] New customer with no address
- [ ] Returning customer with address
- [ ] Address validation errors
- [ ] Order creation success
- [ ] Network error handling
- [ ] Session expiration

## Security Measures

1. **Rate Limiting**: 
   - 3 SMS per phone per day
   - 10 order attempts per hour per IP
2. **Session Security**: 30-minute JWT expiration
3. **HTTPS Only**: Enforce TLS for all requests
4. **Input Validation**: Server-side validation for all fields
5. **CSRF Protection**: Double-submit cookie pattern
6. **Cart Validation**: 
   - Server-side price calculation
   - Stock verification before order
   - Cart signature to prevent tampering