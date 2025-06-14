# Task 28: Create POST /api/cart endpoint

## Task Details
- **ID**: 28_cart_add_item_endpoint
- **Title**: Create POST /api/cart endpoint
- **Priority**: High
- **Estimate**: 25 minutes
- **Dependencies**: Cart model creation, Basic API blueprint

## Objective
Implement a POST endpoint at `/api/cart` that allows adding items to a shopping cart session with proper validation, inventory checking, and session management.

## Requirements
1. **Endpoint Path**: `/api/cart`
2. **HTTP Method**: POST
3. **Request Body**: JSON with product_id, quantity, and optional session_id
4. **Response Format**: Standard API response with updated cart contents
5. **Session Management**: Create or update cart session
6. **Inventory Validation**: Check product availability and stock
7. **Error Handling**: Proper error responses for invalid data
8. **Status Codes**: 200 for success, 400 for validation errors, 404 for not found, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/cart.py`
- **Function**: `add_to_cart()`
- **Session Storage**: Use session-based cart storage or temporary database storage
- **Validation**: Product existence, stock availability, quantity limits
- **Response**: Use standardized API response format

## Expected Request Format
```json
{
    "product_id": "507f1f77bcf86cd799439011",
    "quantity": 2,
    "session_id": "optional_session_id"
}
```

## Expected Response Structure
```json
{
    "success": true,
    "data": {
        "session_id": "generated_or_provided_session_id",
        "cart": {
            "items": [
                {
                    "product_id": "507f1f77bcf86cd799439011",
                    "product_name": "Product Name",
                    "price": 29.99,
                    "quantity": 2,
                    "subtotal": 59.98
                }
            ],
            "total_items": 2,
            "total_amount": 59.98,
            "updated_at": "2025-01-13T12:00:00Z"
        }
    },
    "message": "Item added to cart successfully"
}
```

## Validation Requirements
1. **Product ID**: Valid ObjectId format and product exists
2. **Quantity**: Positive integer within reasonable limits (1-100)
3. **Stock Check**: Ensure sufficient inventory available
4. **Session Management**: Generate session ID if not provided
5. **Cart Limits**: Maximum items per cart (e.g., 50 items)

## Error Scenarios
- **400**: Invalid product ID format, invalid quantity, insufficient stock
- **404**: Product not found or not available
- **500**: Database connection error, session storage error

## Testing Criteria
1. Endpoint responds with 200 status code for valid requests
2. Creates new cart session if session_id not provided
3. Updates existing cart session if session_id provided
4. Validates product existence and availability
5. Enforces quantity limits and stock availability
6. Returns proper error responses for invalid data
7. Handles database connection errors properly
8. Session management works correctly

## Success Criteria
- POST /api/cart endpoint is accessible
- Adds items to cart with proper validation
- Session management and persistence
- Comprehensive error handling
- Test harness validates cart functionality
- Integration with existing Flask application structure