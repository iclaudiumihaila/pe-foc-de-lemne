# Task 37: Create order processing service

## Task Details
- **ID**: 37_order_service_creation
- **Title**: Create order processing service
- **Priority**: High
- **Estimate**: 30 minutes
- **Dependencies**: Order model creation (Task 21), Cart model creation (Task 19)

## Objective
Implement comprehensive business logic service for creating orders from cart data with validation, inventory checking, pricing calculations, and SMS verification integration.

## Requirements
1. **Service File**: `backend/app/services/order_service.py`
2. **Core Functionality**: Create orders from cart sessions
3. **Validation**: Cart validation, product availability, pricing verification
4. **Integration**: SMS verification, inventory management, order numbering
5. **Error Handling**: Comprehensive validation and business rule enforcement
6. **Database**: MongoDB operations with proper error handling

## Technical Implementation
- **Architecture**: Service layer with clear separation of concerns
- **Validation**: Multi-stage validation (cart, products, inventory, pricing)
- **Integration**: Cart model, Product model, Order model coordination
- **Transactions**: Atomic operations for order creation
- **Error Handling**: Detailed error messages and proper status codes

## Order Processing Workflow

### 1. Order Creation Flow
```python
def create_order(cart_session_id, customer_info, phone_verification_session_id):
    # 1. Validate SMS verification session
    # 2. Retrieve and validate cart
    # 3. Validate products and inventory
    # 4. Calculate totals and pricing
    # 5. Create order with order number
    # 6. Clear cart session
    # 7. Return order confirmation
```

### 2. Validation Stages
1. **Phone Verification**: Verify SMS verification session is valid
2. **Cart Validation**: Ensure cart exists and has items
3. **Product Validation**: Verify all products exist and are active
4. **Inventory Validation**: Check product availability 
5. **Pricing Validation**: Recalculate prices to prevent tampering
6. **Customer Validation**: Validate customer information completeness

### 3. Order Data Structure
```python
{
    "order_number": "ORD-20250113-001234",
    "customer": {
        "phone_number": "+1234567890",
        "name": "John Doe",
        "email": "john@example.com",
        "address": {...}
    },
    "items": [
        {
            "product_id": "product_123",
            "name": "Organic Apples",
            "category": "Fruits",
            "quantity": 2,
            "unit_price": 4.99,
            "total_price": 9.98
        }
    ],
    "totals": {
        "subtotal": 9.98,
        "tax": 0.80,
        "delivery_fee": 5.00,
        "total": 15.78
    },
    "status": "pending",
    "verification_session_id": "session_123",
    "created_at": "2025-01-13T15:00:00Z"
}
```

## Service Implementation

### 1. Core Order Service Class
```python
class OrderService:
    def __init__(self):
        self.db = get_database()
        self.orders_collection = self.db.orders
        self.products_collection = self.db.products
        self.verification_sessions_collection = self.db.verification_sessions
        
    def create_order(self, cart_session_id, customer_info, phone_verification_session_id):
        # Main order creation logic
        pass
```

### 2. Validation Methods
```python
def _validate_verification_session(self, session_id, phone_number):
    # Verify SMS verification session is valid and matches phone
    pass

def _validate_cart(self, cart_session_id):
    # Retrieve and validate cart exists with items
    pass

def _validate_products_and_inventory(self, cart_items):
    # Verify products exist, are active, and have sufficient inventory
    pass

def _calculate_pricing(self, cart_items):
    # Recalculate all pricing to prevent client-side tampering
    pass
```

### 3. Order Creation Methods
```python
def _generate_order_number(self):
    # Generate unique order number: ORD-YYYYMMDD-NNNNNN
    pass

def _create_order_document(self, cart, customer_info, totals, order_number):
    # Create complete order document for MongoDB
    pass

def _clear_cart_session(self, cart_session_id):
    # Clear cart after successful order creation
    pass
```

## Business Logic Requirements

### 1. Phone Verification Integration
- **Session Validation**: Verify SMS verification session exists and is valid
- **Phone Matching**: Ensure verification session phone matches customer phone
- **Session Expiry**: Check verification session hasn't expired (2 hours)
- **Single Use**: Mark verification session as used after order creation

### 2. Cart Processing
- **Cart Retrieval**: Get cart by session ID with all items
- **Item Validation**: Ensure cart has at least one item
- **Session Validation**: Check cart session hasn't expired
- **Quantity Limits**: Validate reasonable quantities for each item

### 3. Product and Inventory Management
- **Product Existence**: Verify all cart products exist in database
- **Product Status**: Ensure products are active and available
- **Inventory Checking**: Verify sufficient stock for ordered quantities
- **Price Verification**: Recalculate prices from database (security)

### 4. Pricing and Totals Calculation
```python
def calculate_order_totals(items):
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_rate = 0.08  # 8% tax
    tax = subtotal * tax_rate
    delivery_fee = 5.00 if subtotal < 50.00 else 0.00  # Free delivery over $50
    total = subtotal + tax + delivery_fee
    
    return {
        'subtotal': round(subtotal, 2),
        'tax': round(tax, 2),
        'delivery_fee': delivery_fee,
        'total': round(total, 2)
    }
```

### 5. Order Number Generation
```python
def generate_order_number():
    # Format: ORD-YYYYMMDD-NNNNNN
    date_part = datetime.utcnow().strftime('%Y%m%d')
    
    # Get next sequence number for the day
    sequence = get_next_order_sequence(date_part)
    
    return f"ORD-{date_part}-{sequence:06d}"
```

## Error Handling Strategy

### 1. Validation Errors
```python
class OrderValidationError(Exception):
    def __init__(self, message, error_code, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
```

### 2. Error Scenarios
- **Invalid Verification**: Phone verification session invalid/expired
- **Empty Cart**: Cart session not found or has no items
- **Product Unavailable**: Products no longer available or inactive
- **Insufficient Inventory**: Not enough stock for requested quantities
- **Pricing Mismatch**: Client-side prices don't match database prices
- **Customer Data Invalid**: Required customer information missing/invalid

### 3. Error Response Format
```python
{
    "success": false,
    "error": {
        "code": "ORDER_001",
        "message": "Cart session not found or expired",
        "details": {
            "cart_session_id": "cart_123",
            "suggestion": "Please add items to cart again"
        }
    }
}
```

## Integration Points

### 1. Cart Model Integration
```python
# Retrieve cart with all items
cart = Cart.get_by_session_id(cart_session_id)
if not cart or cart.is_expired():
    raise OrderValidationError("Cart session not found or expired", "ORDER_001")

# Get cart items with product details
cart_items = cart.get_items_with_products()
```

### 2. Product Model Integration
```python
# Validate products exist and are available
for item in cart_items:
    product = Product.get_by_id(item['product_id'])
    if not product or not product.is_active():
        raise OrderValidationError(f"Product {item['name']} is no longer available", "ORDER_002")
    
    if product.inventory < item['quantity']:
        raise OrderValidationError(f"Insufficient inventory for {item['name']}", "ORDER_003")
```

### 3. Order Model Integration
```python
# Create order using Order model
order_data = {
    'order_number': order_number,
    'customer': customer_info,
    'items': processed_items,
    'totals': calculated_totals,
    'status': 'pending',
    'verification_session_id': phone_verification_session_id,
    'cart_session_id': cart_session_id,
    'created_at': datetime.utcnow()
}

order = Order.create(order_data)
```

## Database Operations

### 1. Atomic Order Creation
```python
def create_order_atomic(self, order_data, cart_session_id):
    # Start database session for transaction
    with self.db.client.start_session() as session:
        with session.start_transaction():
            try:
                # Create order
                order_result = self.orders_collection.insert_one(order_data, session=session)
                
                # Update product inventory
                for item in order_data['items']:
                    self.products_collection.update_one(
                        {'_id': ObjectId(item['product_id'])},
                        {'$inc': {'inventory': -item['quantity']}},
                        session=session
                    )
                
                # Clear cart
                self.db.cart_sessions.delete_one(
                    {'session_id': cart_session_id},
                    session=session
                )
                
                # Mark verification session as used
                self.verification_sessions_collection.update_one(
                    {'session_id': order_data['verification_session_id']},
                    {'$set': {'used': True, 'used_at': datetime.utcnow()}},
                    session=session
                )
                
                session.commit_transaction()
                return order_result.inserted_id
                
            except Exception as e:
                session.abort_transaction()
                raise OrderCreationError(f"Failed to create order: {str(e)}")
```

### 2. Order Number Sequence Management
```python
def get_next_order_sequence(self, date_part):
    # Use MongoDB findAndModify for atomic sequence generation
    result = self.db.order_sequences.find_one_and_update(
        {'date': date_part},
        {'$inc': {'sequence': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result['sequence']
```

## Testing Considerations

### 1. Unit Tests
- **Order Creation**: Test successful order creation with valid data
- **Validation Logic**: Test each validation method independently
- **Error Scenarios**: Test all error conditions and messages
- **Pricing Calculations**: Test pricing logic with various scenarios
- **Order Number Generation**: Test uniqueness and format

### 2. Integration Tests
- **End-to-End Flow**: Test complete order creation workflow
- **Database Transactions**: Test atomic operations and rollbacks
- **Model Integration**: Test interaction with Cart, Product, Order models
- **SMS Integration**: Test verification session validation

### 3. Edge Cases
- **Concurrent Orders**: Test inventory management with concurrent requests
- **Large Carts**: Test performance with large numbers of items
- **Price Changes**: Test handling of price changes during order process
- **Session Expiry**: Test various session expiry scenarios

## Performance Considerations

### 1. Database Optimization
- **Efficient Queries**: Use projection to fetch only needed fields
- **Index Usage**: Leverage existing indexes on products and sessions
- **Batch Operations**: Minimize database round trips
- **Connection Pooling**: Reuse existing database connections

### 2. Memory Management
- **Lazy Loading**: Load product details only when needed
- **Data Transformation**: Minimize in-memory data processing
- **Garbage Collection**: Clean up temporary objects promptly
- **Error Handling**: Avoid memory leaks in error scenarios

## Success Criteria
- Complete order processing service with create_order function
- Comprehensive validation for all business rules
- Integration with Cart, Product, and Order models
- SMS verification session validation
- Atomic database operations with proper rollback
- Detailed error handling with clear error messages
- Order number generation with uniqueness guarantee
- Proper inventory management and updates