# Task 24: Create GET /api/products/:id endpoint

## Task Details
- **ID**: 24_products_get_one_endpoint
- **Title**: Create GET /api/products/:id endpoint
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: Products GET all endpoint

## Objective
Implement a GET endpoint at `/api/products/:id` that retrieves a single product by its ObjectId and returns it in a standardized API response format.

## Requirements
1. **Endpoint Path**: `/api/products/:id`
2. **HTTP Method**: GET
3. **Path Parameter**: `id` (MongoDB ObjectId string)
4. **Response Format**: Standard API response with single product object
5. **Product Status**: Only return active products
6. **Error Handling**: 404 for not found, 400 for invalid ID format
7. **Status Codes**: 200 for success, 400 for invalid ID, 404 for not found, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/products.py`
- **Function**: `get_product_by_id(product_id)`
- **Parameter Validation**: Validate ObjectId format
- **Database Query**: Find product by _id where status is 'active'
- **Response**: Use standardized API response format from error handlers

## Expected Response Structure

### Success (200)
```json
{
    "success": true,
    "data": {
        "_id": "product_id",
        "name": "Product Name",
        "description": "Product Description",
        "price": 29.99,
        "category_id": "category_id",
        "category": {
            "id": "category_id",
            "name": "Category Name",
            "slug": "category-slug"
        },
        "images": ["image1.jpg"],
        "stock_quantity": 10,
        "is_available": true,
        "status": "active",
        "created_at": "2025-01-13T10:00:00Z",
        "updated_at": "2025-01-13T10:00:00Z"
    },
    "message": "Product retrieved successfully"
}
```

### Error Responses
- **400**: Invalid product ID format
- **404**: Product not found or inactive
- **500**: Database connection error

## Testing Criteria
1. Endpoint responds with 200 status code for valid product ID
2. Returns 404 for non-existent product ID
3. Returns 400 for invalid ObjectId format
4. Returns JSON response with correct structure
5. Only returns active products
6. Includes category information if available
7. Handles database connection errors properly
8. Response includes all required product fields

## Success Criteria
- GET /api/products/:id endpoint is accessible
- Returns single product in standardized format
- Proper error handling for invalid IDs and not found cases
- Test harness validates endpoint functionality
- Integration with existing Flask application structure