# Task 29: Create GET /api/cart/:session endpoint

## Task Details
- **ID**: 29_cart_get_contents_endpoint
- **Title**: Create GET /api/cart/:session endpoint
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Cart add item endpoint

## Objective
Implement a GET endpoint at `/api/cart/:session` that retrieves cart contents by session ID with proper validation and error handling.

## Requirements
1. **Endpoint Path**: `/api/cart/:session`
2. **HTTP Method**: GET
3. **Path Parameter**: `session` (cart session ID)
4. **Response Format**: Standard API response with cart contents
5. **Session Validation**: Validate session ID format and existence
6. **Expiry Check**: Handle expired cart sessions
7. **Error Handling**: Proper error responses for invalid sessions
8. **Status Codes**: 200 for success, 400 for invalid format, 404 for not found, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/cart.py`
- **Function**: `get_cart_contents(session_id)`
- **Session Lookup**: Find cart by session ID in database
- **Validation**: Session ID format and expiry checking
- **Response**: Use standardized API response format

## Expected Response Structure
```json
{
    "success": true,
    "data": {
        "session_id": "507f1f77bcf86cd799439011",
        "items": [
            {
                "product_id": "507f1f77bcf86cd799439012",
                "product_name": "Product Name",
                "quantity": 2,
                "price": 29.99,
                "subtotal": 59.98
            }
        ],
        "total_items": 2,
        "total_amount": 59.98,
        "created_at": "2025-01-13T12:00:00Z",
        "updated_at": "2025-01-13T13:00:00Z",
        "expires_at": "2025-01-14T13:00:00Z"
    },
    "message": "Cart contents retrieved successfully"
}
```

## Error Scenarios
- **400**: Invalid session ID format
- **404**: Cart session not found or expired
- **500**: Database connection error

## Testing Criteria
1. Endpoint responds with 200 status code for valid session
2. Returns complete cart information with all items
3. Validates session ID format (24-character hex string)
4. Handles non-existent session IDs with 404
5. Handles expired sessions appropriately
6. Returns proper error responses for invalid data
7. Handles database connection errors properly
8. Response follows standard API format

## Success Criteria
- GET /api/cart/:session endpoint is accessible
- Returns cart contents for valid sessions
- Proper session validation and expiry handling
- Comprehensive error handling
- Test harness validates endpoint functionality
- Integration with existing cart system