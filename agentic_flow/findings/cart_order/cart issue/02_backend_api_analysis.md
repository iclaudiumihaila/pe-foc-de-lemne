# Backend Cart/Order API Analysis

## Executive Summary

The backend implementation reveals a sophisticated cart and order system with the following key features:
- Session-based shopping cart without authentication requirements
- Phone-based checkout flow with SMS verification
- JWT-based checkout authentication
- Atomic order creation with inventory management
- Comprehensive validation and error handling
- Support for both authenticated and guest checkout

## Database Schema and Relationships

### Cart Sessions Collection (`cart_sessions`)
```javascript
{
  _id: ObjectId,
  session_id: String (unique, 24 chars),
  items: [{
    product_id: String,
    product_name: String,
    quantity: Number,
    price: Number,
    subtotal: Number
  }],
  created_at: DateTime,
  updated_at: DateTime,
  expires_at: DateTime // TTL index - 24 hours
}
```

### Orders Collection (`orders`)
```javascript
{
  _id: ObjectId,
  order_number: String (unique, format: "ORD-YYYYMMDD-NNNNNN"),
  customer_phone: String (E.164 format),
  customer_name: String,
  status: String (enum: pending/confirmed/preparing/ready/delivered/cancelled),
  items: [{
    product_id: ObjectId,
    product_name: String,
    quantity: Number,
    unit_price: Decimal,
    total_price: Decimal
  }],
  subtotal: Decimal,
  total: Decimal,
  delivery_type: String (enum: pickup/delivery),
  delivery_address: {
    street: String,
    city: String,
    county: String,
    postal_code: String,
    notes: String
  },
  delivery_phone: String,
  requested_time: DateTime,
  special_instructions: String,
  created_at: DateTime,
  updated_at: DateTime,
  confirmed_at: DateTime,
  ready_at: DateTime,
  delivered_at: DateTime
}
```

### Customer Phone Collection (`customer_phones`)
```javascript
{
  _id: ObjectId,
  phone: String (unique, normalized),
  name: String,
  addresses: [{
    _id: ObjectId,
    street: String,
    city: String,
    county: String,
    postal_code: String,
    notes: String,
    is_default: Boolean,
    usage_count: Number,
    last_used: DateTime,
    created_at: DateTime
  }],
  verification: {
    code: String,
    code_expires: DateTime,
    attempts: Number,
    attempts_today: Number,
    last_code_sent: DateTime,
    verified_at: DateTime
  },
  total_orders: Number,
  last_order_date: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

## API Endpoint Documentation

### Cart Management APIs

#### 1. Add to Cart
- **Endpoint**: `POST /api/cart/`
- **Authentication**: None required
- **Request**:
```json
{
  "product_id": "507f1f77bcf86cd799439011",
  "quantity": 2,
  "session_id": "507f1f77bcf86cd799439012" // Optional
}
```
- **Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "507f1f77bcf86cd799439012",
    "cart": {
      "session_id": "507f1f77bcf86cd799439012",
      "items": [...],
      "total_items": 2,
      "total_amount": 100.50,
      "expires_at": "2024-01-02T10:00:00Z"
    }
  }
}
```
- **Validation**:
  - Product exists and is available
  - Stock quantity check
  - Max items per cart: 50
  - Max quantity per item: 100

#### 2. Get Cart Contents
- **Endpoint**: `GET /api/cart/{session_id}`
- **Authentication**: None required
- **Response**: Cart object with items and totals

#### 3. Update Cart Item
- **Endpoint**: `PUT /api/cart/{session_id}/item/{product_id}`
- **Request**:
```json
{
  "quantity": 3  // 0 to remove item
}
```

#### 4. Clear Cart
- **Endpoint**: `DELETE /api/cart/{session_id}`

### Checkout Flow APIs

#### 1. Send Verification Code
- **Endpoint**: `POST /api/checkout/phone/send-code`
- **Rate Limits**:
  - 3 SMS per phone per day
  - 5 SMS per IP per hour
- **Request**:
```json
{
  "phone": "0712345678"  // Romanian format
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Cod de verificare trimis",
  "phone_masked": "****5678",
  "expires_in_seconds": 300
}
```

#### 2. Verify Code
- **Endpoint**: `POST /api/checkout/phone/verify-code`
- **Rate Limit**: 5 attempts per code
- **Request**:
```json
{
  "phone": "0712345678",
  "code": "123456"
}
```
- **Response**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "customer": {
    "phone_masked": "****5678",
    "name": "Ion Popescu",
    "addresses": [...],
    "has_ordered_before": true
  }
}
```

#### 3. Address Management
- **Get Addresses**: `GET /api/checkout/addresses` (Auth required)
- **Add Address**: `POST /api/checkout/addresses` (Auth required)
- **Update Address**: `PUT /api/checkout/addresses/{address_id}` (Auth required)
- **Delete Address**: `DELETE /api/checkout/addresses/{address_id}` (Auth required)

### Order Creation APIs

#### 1. Create Order (New Flow)
- **Endpoint**: `POST /api/orders`
- **Authentication**: Optional (JWT from checkout flow)
- **Request**:
```json
{
  "cart_session_id": "507f1f77bcf86cd799439012",
  "customer_info": {
    "customer_name": "Ion Popescu",
    "phone_number": "0712345678",  // For guests
    "delivery_address": {           // For guests
      "street": "Str. Principală 123",
      "city": "București",
      "county": "București",
      "postal_code": "010101",
      "notes": "Etaj 2"
    },
    "special_instructions": "Sunați înainte de livrare"
  },
  "address_id": "507f1f77bcf86cd799439013"  // For authenticated users
}
```

#### 2. Get Order Status (Public)
- **Endpoint**: `GET /api/orders/status`
- **Query Parameters**:
  - `phone`: Customer phone number
  - `order_number`: Order number
- **Response**: Order details with status timeline

#### 3. Admin Order Management
- **List Orders**: `GET /api/orders/admin/orders` (Admin auth required)
- **Update Status**: `PUT /api/orders/admin/orders/{order_id}/status` (Admin auth required)

## Authentication and Authorization Flow

### 1. Guest Checkout Flow
```
1. User adds items to cart (no auth)
2. At checkout, user provides phone number
3. SMS verification code sent
4. User enters code
5. JWT token issued (valid 24 hours)
6. User completes order with delivery address
```

### 2. Returning Customer Flow
```
1. User adds items to cart
2. User verifies phone via SMS
3. JWT token issued with customer data
4. User sees saved addresses
5. User selects address and completes order
```

### 3. JWT Token Structure
```javascript
{
  "phone": "+40712345678",
  "customer_id": "507f1f77bcf86cd799439011",
  "exp": 1704196800,  // Expires after 24 hours
  "iat": 1704110400,
  "type": "checkout_session"
}
```

## Cart Session Lifecycle

1. **Creation**: Cart session created on first item add
2. **Session ID**: 24-character unique identifier
3. **Expiry**: 24 hours from creation (TTL index)
4. **Updates**: Session expiry extended on each update
5. **Cleanup**: Expired carts automatically removed by MongoDB

## Order Creation Process Step-by-Step

### OrderService Implementation

1. **Validate SMS Verification**
   - Check verification session exists and is valid
   - Ensure phone number matches
   - Verify session hasn't been used

2. **Validate Cart**
   - Retrieve cart by session ID
   - Check cart hasn't expired
   - Ensure cart has items

3. **Validate Customer Info**
   - Phone number in E.164 format
   - Customer name minimum 2 characters
   - Address validation for Romanian format

4. **Validate Products and Inventory**
   - Check each product exists and is available
   - Verify sufficient stock
   - Update prices to current database values

5. **Calculate Order Totals**
   - Subtotal from items
   - Tax (8%)
   - Delivery fee (5 RON, free over 50 RON)
   - Total amount

6. **Generate Order Number**
   - Format: `ORD-YYYYMMDD-NNNNNN`
   - Uses atomic sequence counter per day

7. **Atomic Order Creation**
   - MongoDB transaction ensures:
     - Order created
     - Inventory decremented
     - SMS verification marked as used
     - Cart session deleted

## Error Handling and Validation Rules

### Cart Validation
- **Product availability**: Must be active and in stock
- **Quantity limits**: 1-100 per item
- **Cart size**: Maximum 50 different products
- **Price validation**: Current DB price used

### Phone Validation
- Romanian format: `07XXXXXXXX` or `+407XXXXXXXX`
- Normalized to E.164: `+40712345678`
- Regex pattern: `^(0|\+40)7[0-9]{8}$`

### Address Validation
- Required fields: street, city, county, postal_code
- Postal code: 6 digits
- Maximum 50 addresses per customer
- First address set as default

### Order Status Transitions
```
pending → confirmed → preparing → ready → delivered
     ↓                    ↓           ↓         ↓
  cancelled           cancelled   cancelled    (final)
```

## Security Considerations

### Rate Limiting
- SMS sending: IP and phone-based limits
- Code verification: 5 attempts per code
- Prevents SMS bombing and brute force

### Data Protection
- Phone numbers stored normalized
- Masked display: `****5678`
- JWT tokens expire after 24 hours
- Verification codes expire after 5 minutes

### Inventory Management
- Atomic transactions prevent overselling
- Stock checked at cart add and order creation
- Cancelled orders restore inventory

### Price Security
- Prices validated against database
- Cart prices updated on order creation
- Prevents price manipulation

## Performance Optimizations

### Database Indexes
- `cart_sessions`: session_id (unique), created_at (TTL)
- `orders`: order_number (unique), customer_phone, status, created_at
- `customer_phones`: phone (unique)

### Session Management
- Cart sessions expire automatically (TTL)
- Cleanup job for expired verification codes
- Efficient session lookup by ID

### Transaction Handling
- MongoDB transactions for atomic operations
- Rollback on any failure
- Ensures data consistency

## Integration Points

### SMS Service
- Provider interface for multiple SMS gateways
- SMSO provider implementation
- Mock provider for development
- Queueing for reliability

### Product Service
- Real-time stock checking
- Price validation
- Availability verification

### Admin Interface
- Order status management
- Customer order history
- Analytics and reporting

## Key Business Logic

### Free Delivery Threshold
- Orders over 50 RON get free delivery
- Otherwise 5 RON delivery fee
- Calculated at order creation

### Order Numbering
- Daily sequence reset
- Format ensures uniqueness
- Human-readable format

### Address Management
- Smart sorting (default first, then by usage)
- Usage tracking for recommendations
- Automatic default assignment

This comprehensive backend implementation provides a robust foundation for the e-commerce platform's cart and order functionality, with careful attention to security, performance, and user experience.