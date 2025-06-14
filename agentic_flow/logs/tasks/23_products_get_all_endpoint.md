# Task 23: Create GET /api/products endpoint

## Task Details
- **ID**: 23_products_get_all_endpoint
- **Title**: Create GET /api/products endpoint
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Product model creation, Basic API blueprint

## Objective
Implement a GET endpoint at `/api/products` that retrieves all active products from the database and returns them in a standardized API response format.

## Requirements
1. **Endpoint Path**: `/api/products`
2. **HTTP Method**: GET
3. **Response Format**: Standard API response with products array
4. **Product Filtering**: Only return active products (status: 'active')
5. **Product Fields**: Include all relevant product information
6. **Error Handling**: Proper error responses for database issues
7. **Status Codes**: 200 for success, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/products.py`
- **Function**: `get_all_products()`
- **Database Query**: Find all products where status is 'active'
- **Response**: Use standardized API response format from error handlers

## Expected Response Structure
```json
{
    "success": true,
    "data": [
        {
            "_id": "product_id",
            "name": "Product Name",
            "description": "Product Description",
            "price": 29.99,
            "category_id": "category_id",
            "category_name": "Category Name",
            "images": ["image1.jpg"],
            "stock_quantity": 10,
            "status": "active",
            "created_at": "2025-01-13T10:00:00Z",
            "updated_at": "2025-01-13T10:00:00Z"
        }
    ],
    "message": "Products retrieved successfully"
}
```

## Testing Criteria
1. Endpoint responds with 200 status code
2. Returns JSON response with correct structure
3. Only includes active products
4. Handles empty product list gracefully
5. Handles database connection errors properly
6. Response includes all required product fields

## Success Criteria
- GET /api/products endpoint is accessible
- Returns all active products in standardized format
- Proper error handling for database issues
- Test harness validates endpoint functionality
- Integration with existing Flask application structure