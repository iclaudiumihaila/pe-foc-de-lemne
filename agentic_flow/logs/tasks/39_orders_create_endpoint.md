# Task 39: Create POST /api/orders endpoint

## Task Details
- **ID**: 39_orders_create_endpoint
- **Title**: Create POST /api/orders endpoint
- **Priority**: High
- **Estimate**: 25 minutes
- **Dependencies**: Order service creation (Task 37), SMS verification confirm endpoint (Task 34)

## Objective
Implement the POST /api/orders endpoint that integrates the OrderService with SMS verification validation to enable secure order creation from cart data with customer information verification.

## Requirements
1. **Endpoint**: POST /api/orders
2. **Location**: `backend/app/routes/orders.py`
3. **Integration**: OrderService and SMS verification
4. **Validation**: JSON schema validation for request payload
5. **Security**: SMS verification session requirement
6. **Response**: Standard API response format with order confirmation

## Technical Implementation

### 1. Endpoint Specification
```python
@orders_bp.route('', methods=['POST'])
@validate_json(ORDER_CREATE_SCHEMA)
def create_order():
    """
    Create new order from cart with SMS verification.
    
    Required payload:
    - cart_session_id: String
    - customer_info: Object with phone_number, customer_name, email (optional), special_instructions (optional)
    - phone_verification_session_id: String
    
    Returns: Order confirmation with order number and details
    """
```

### 2. Request Schema Validation
```python
ORDER_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "cart_session_id": {
            "type": "string",
            "minLength": 1,
            "description": "Session ID for the shopping cart"
        },
        "customer_info": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "pattern": "^\\+[1-9]\\d{1,14}$",
                    "description": "Customer phone number in E.164 format"
                },
                "customer_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "description": "Customer full name"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Customer email address (optional)"
                },
                "special_instructions": {
                    "type": "string",
                    "maxLength": 500,
                    "description": "Special delivery instructions (optional)"
                }
            },
            "required": ["phone_number", "customer_name"],
            "additionalProperties": False
        },
        "phone_verification_session_id": {
            "type": "string",
            "minLength": 1,
            "description": "Session ID for phone verification"
        }
    },
    "required": ["cart_session_id", "customer_info", "phone_verification_session_id"],
    "additionalProperties": False
}
```

### 3. OrderService Integration
```python
def create_order():
    try:
        data = request.get_json()
        
        # Extract validated data
        cart_session_id = data['cart_session_id']
        customer_info = data['customer_info']
        phone_verification_session_id = data['phone_verification_session_id']
        
        # Create order using OrderService
        order_service = get_order_service()
        result = order_service.create_order(
            cart_session_id=cart_session_id,
            customer_info=customer_info,
            phone_verification_session_id=phone_verification_session_id
        )
        
        return jsonify(result), 201
        
    except OrderValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': e.error_code,
            'details': e.details
        }), 400
        
    except OrderCreationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': e.error_code,
            'details': e.details
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while creating the order',
            'error_code': 'ORDER_500'
        }), 500
```

### 4. Blueprint Structure
```python
from flask import Blueprint, request, jsonify
from app.utils.validators import validate_json
from app.services.order_service import get_order_service, OrderValidationError, OrderCreationError

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

# Order creation schema
ORDER_CREATE_SCHEMA = { ... }

@orders_bp.route('', methods=['POST'])
@validate_json(ORDER_CREATE_SCHEMA)
def create_order():
    # Implementation
```

### 5. Success Response Format
```json
{
    "success": true,
    "message": "Order ORD-20250113-000001 created successfully. You will receive SMS confirmation shortly.",
    "order": {
        "order_number": "ORD-20250113-000001",
        "status": "pending",
        "customer_phone": "+1234567890",
        "customer_name": "John Doe",
        "items": [
            {
                "product_id": "507f1f77bcf86cd799439011",
                "product_name": "Organic Apples",
                "quantity": 2,
                "unit_price": 4.99,
                "total_price": 9.98
            }
        ],
        "totals": {
            "subtotal": 9.98,
            "tax": 0.80,
            "delivery_fee": 5.00,
            "total": 15.78,
            "tax_rate": 0.08,
            "free_delivery_threshold": 50.00
        },
        "created_at": "2025-01-13T15:30:00Z"
    }
}
```

### 6. Error Response Formats

#### Validation Error (400)
```json
{
    "success": false,
    "error": "Invalid or expired phone verification session",
    "error_code": "ORDER_003",
    "details": {
        "session_id": "session_123",
        "suggestion": "Please verify your phone number again"
    }
}
```

#### Creation Error (500)
```json
{
    "success": false,
    "error": "Product not found during inventory update",
    "error_code": "ORDER_019",
    "details": {
        "product_id": "product_123",
        "operation": "inventory_update"
    }
}
```

## Integration Points

### 1. OrderService Integration
- Use `get_order_service()` to obtain singleton instance
- Pass validated request data directly to `create_order()` method
- Handle all custom exceptions from OrderService

### 2. SMS Verification Integration
- Rely on OrderService to validate phone verification sessions
- No direct SMS service calls in endpoint (handled by OrderService)
- Phone verification session ID passed through to OrderService

### 3. Cart Integration
- Cart session ID passed to OrderService for cart validation
- OrderService handles cart expiration and empty cart validation
- Automatic cart cleanup after successful order creation

### 4. Database Integration
- OrderService handles all database operations atomically
- No direct database calls in endpoint code
- Automatic rollback on any failure in order creation process

## Error Handling Strategy

### 1. Validation Errors (400 responses)
- `ORDER_001-006`: SMS verification errors
- `ORDER_007-011`: Cart validation errors
- `ORDER_012-014`: Customer information errors
- `ORDER_015-018`: Product and inventory errors

### 2. Creation Errors (500 responses)
- `ORDER_019-027`: Order creation and system errors
- Database connection failures
- Transaction rollback scenarios

### 3. Unexpected Errors (500 responses)
- Generic error handling for uncaught exceptions
- Standard error format maintenance
- Error logging for debugging

## Security Considerations

### 1. SMS Verification Requirement
- Phone verification session must be valid and verified
- Session must match customer phone number
- Session must not be expired or already used

### 2. Input Validation
- Comprehensive JSON schema validation
- Phone number format validation (E.164)
- Customer name length validation
- Email format validation (if provided)

### 3. Rate Limiting
- Inherits rate limiting from existing infrastructure
- No additional rate limiting required at endpoint level
- OrderService handles business logic rate limiting

## Testing Requirements

### 1. Success Scenarios
- Valid order creation with all required fields
- Order creation with optional fields
- Different cart sizes and product combinations
- Various phone number formats

### 2. Validation Error Scenarios
- Invalid cart session ID
- Expired cart session
- Invalid phone verification session
- Missing required customer information
- Invalid phone number formats

### 3. System Error Scenarios
- Database connection failures
- SMS service unavailability
- Product inventory changes during order creation
- Concurrent order creation attempts

## Blueprint Registration
```python
# In backend/app/__init__.py
from app.routes.orders import orders_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(orders_bp)
    
    return app
```

## File Structure
```
backend/app/routes/
├── __init__.py
├── products.py
├── categories.py
├── cart.py
├── sms.py
└── orders.py          # New file for order endpoints
```

## Success Criteria
- POST /api/orders endpoint accepts valid order creation requests
- Proper integration with OrderService for business logic
- Comprehensive error handling with appropriate HTTP status codes
- JSON schema validation for all request data
- Standard API response format for success and error cases
- Proper SMS verification session validation
- Cart session validation and cleanup
- Atomic order creation with inventory updates