# Simplified Checkout Architecture

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
    "attempts_today": Number
  },
  "created_at": Date,
  "updated_at": Date,
  "total_orders": Number,
  "last_order_date": Date
}
```

### API Endpoints

#### Phone Management
- `POST /api/customer-phones/verify-start` - Send SMS code
- `POST /api/customer-phones/verify-complete` - Validate code
- `GET /api/customer-phones/addresses` - Get saved addresses

#### Address Management  
- `POST /api/customer-phones/addresses` - Add new address
- `PUT /api/customer-phones/addresses/:id` - Update address
- `DELETE /api/customer-phones/addresses/:id` - Remove address

### Frontend Components

#### Checkout Page Structure
```
/frontend/src/pages/Checkout.jsx (modified)
/frontend/src/components/checkout/
  ├── PhoneVerification.jsx (new)
  ├── AddressSelector.jsx (new)
  ├── AddressForm.jsx (new)
  └── CheckoutFlow.jsx (new)
```

### State Management
```javascript
checkoutState: {
  currentStep: 'info' | 'verify' | 'address' | 'confirm',
  customerData: {
    name: '',
    phone: '',
    phoneVerified: false
  },
  verificationData: {
    codeSent: false,
    sessionToken: null
  },
  addressData: {
    savedAddresses: [],
    selectedAddress: null,
    newAddress: {}
  }
}
```

### Security Considerations
1. Rate limiting: 3 SMS per phone per day
2. Session tokens expire after 30 minutes
3. Verification codes expire after 5 minutes
4. Phone numbers hashed for privacy logs