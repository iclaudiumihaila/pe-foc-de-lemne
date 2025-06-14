# Task 25: Create products search endpoint

## Task Details
- **ID**: 25_products_search_endpoint
- **Title**: Create products search endpoint
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Products GET endpoints

## Objective
Implement a search endpoint for products that allows text-based searching across product names, descriptions, and other relevant fields with proper filtering and pagination.

## Requirements
1. **Endpoint Path**: `/api/products/search`
2. **HTTP Method**: GET
3. **Query Parameters**: 
   - `q` (string): Search query text
   - `page` (int): Page number for pagination
   - `limit` (int): Items per page
   - `category_id` (string): Filter by category
   - Additional filters as needed
4. **Search Fields**: Product name, description, and other searchable fields
5. **Response Format**: Standard API response with search results and metadata
6. **Error Handling**: Proper error responses for invalid queries
7. **Status Codes**: 200 for success, 400 for invalid parameters, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/products.py`
- **Function**: `search_products()`
- **Search Method**: MongoDB text search or regex-based search
- **Database Query**: Full-text search across product fields
- **Response**: Use standardized API response format

## Expected Response Structure
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "_id": "product_id",
                "name": "Product Name",
                "description": "Product Description",
                "price": 29.99,
                "category": {
                    "id": "category_id",
                    "name": "Category Name",
                    "slug": "category-slug"
                },
                "images": ["image1.jpg"],
                "stock_quantity": 10,
                "is_available": true,
                "relevance_score": 0.95
            }
        ],
        "search_metadata": {
            "query": "search term",
            "total_results": 25,
            "search_time_ms": 45
        },
        "pagination": {
            "page": 1,
            "limit": 20,
            "total_pages": 2,
            "has_next": true,
            "has_prev": false
        }
    },
    "message": "Search completed successfully"
}
```

## Testing Criteria
1. Endpoint responds with 200 status code for valid search queries
2. Returns relevant products based on search terms
3. Supports pagination for search results
4. Handles empty search queries gracefully
5. Validates and filters by category if specified
6. Returns proper error responses for invalid parameters
7. Includes search metadata in response
8. Handles database connection errors properly

## Success Criteria
- GET /api/products/search endpoint is accessible
- Returns filtered products based on search query
- Proper pagination and filtering support
- Comprehensive error handling
- Test harness validates search functionality
- Integration with existing Flask application structure