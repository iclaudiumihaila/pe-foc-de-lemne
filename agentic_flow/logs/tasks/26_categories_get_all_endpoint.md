# Task 26: Create GET /api/categories endpoint

## Task Details
- **ID**: 26_categories_get_all_endpoint
- **Title**: Create GET /api/categories endpoint
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: Product endpoints completed

## Objective
Implement a GET endpoint at `/api/categories` that retrieves all active categories from the database and returns them in a standardized API response format.

## Requirements
1. **Endpoint Path**: `/api/categories`
2. **HTTP Method**: GET
3. **Response Format**: Standard API response with categories array
4. **Category Filtering**: Only return active categories (status: 'active')
5. **Category Fields**: Include all relevant category information
6. **Product Counts**: Include product count for each category
7. **Error Handling**: Proper error responses for database issues
8. **Status Codes**: 200 for success, 500 for server errors

## Technical Implementation
- **File**: `backend/app/routes/categories.py`
- **Function**: `list_categories()`
- **Database Query**: Find all categories where status is 'active'
- **Response**: Use standardized API response format from error handlers

## Expected Response Structure
```json
{
    "success": true,
    "data": [
        {
            "_id": "category_id",
            "name": "Category Name",
            "slug": "category-slug",
            "description": "Category Description",
            "image_url": "category-image.jpg",
            "product_count": 15,
            "status": "active",
            "created_at": "2025-01-13T10:00:00Z",
            "updated_at": "2025-01-13T10:00:00Z"
        }
    ],
    "message": "Categories retrieved successfully"
}
```

## Testing Criteria
1. Endpoint responds with 200 status code
2. Returns JSON response with correct structure
3. Only includes active categories
4. Handles empty category list gracefully
5. Handles database connection errors properly
6. Response includes all required category fields
7. Product counts are accurate and up-to-date

## Success Criteria
- GET /api/categories endpoint is accessible
- Returns all active categories in standardized format
- Proper error handling for database issues
- Test harness validates endpoint functionality
- Integration with existing Flask application structure