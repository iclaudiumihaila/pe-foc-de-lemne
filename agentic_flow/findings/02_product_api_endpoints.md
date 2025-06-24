# Product API Endpoints Analysis

## Overview
The application has two sets of product-related endpoints:
1. Public endpoints in `/backend/app/routes/products.py` (accessed via `/api/products`)
2. Admin endpoints in `/backend/app/routes/admin/products.py` (accessed via `/api/admin/products`)

## Key Findings

### Field Name Inconsistencies
There are significant field name differences between the public and admin endpoints:

1. **Product ID Field**:
   - Public endpoints: `id`
   - Admin endpoints: `id`
   - Product model: `_id` (MongoDB native)

2. **Category Field**:
   - Public endpoints: `category_id` (for input), `category` (object in response)
   - Admin endpoints: `category` (ObjectId string)
   - Product model: `category_id`

3. **Availability Field**:
   - Public endpoints: `is_available`
   - Admin endpoints: `active`
   - Product model: `is_available`

4. **Stock Field**:
   - Public endpoints: `stock_quantity`
   - Admin endpoints: `stock`
   - Product model: `stock_quantity`

5. **Image Field**:
   - Public endpoints: `images` (array)
   - Admin endpoints: `image` (single string)
   - Product model: `images` (array)

6. **Timestamps**:
   - Public endpoints: `created_at`, `updated_at`
   - Admin endpoints: `createdAt` (camelCase)
   - Product model: `created_at`, `updated_at`

## Endpoint Details

### Public Product Endpoints

#### 1. GET /api/products/
**Purpose**: List products with pagination, filtering, sorting, and search
**Query Parameters**:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `category_id` (str): Filter by category ObjectId
- `available_only` (bool): Only show available products (default: true)
- `sort_by` (str): Sort field (name, price, created_at, stock_quantity)
- `sort_order` (str): Sort order (asc, desc)
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `q` (str): Search query for product name and description

**Response Format**:
```json
{
  "status": "success",
  "data": {
    "products": [
      {
        "id": "string",
        "name": "string",
        "slug": "string",
        "description": "string",
        "price": 0.00,
        "images": ["string"],
        "stock_quantity": 0,
        "is_available": true,
        "preparation_time_hours": 24,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "category_id": "string",
        "category": {
          "id": "string",
          "name": "string",
          "slug": "string"
        },
        "search_score": 0.0
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 0,
      "total_pages": 0,
      "has_next": false,
      "has_prev": false
    },
    "filters": {},
    "search": {}
  },
  "message": "string"
}
```

#### 2. GET /api/products/search
**Purpose**: Search products by name and description
**Query Parameters**: Similar to list endpoint but requires `q` parameter

#### 3. GET /api/products/{product_id}
**Purpose**: Get individual product details by ID or slug
**Response Format**: Single product with category information

#### 4. POST /api/products/admin/products
**Purpose**: Create new product (admin only)
**Request Body**:
```json
{
  "name": "string",
  "description": "string",
  "price": 0.00,
  "category_id": "string",
  "images": ["string"],
  "stock_quantity": 0,
  "weight_grams": 0,
  "preparation_time_hours": 24
}
```

#### 5. PUT /api/products/admin/products/{product_id}
**Purpose**: Update existing product (admin only)
**Request Body**: Partial update with any of the creation fields

#### 6. DELETE /api/products/admin/products/{product_id}
**Purpose**: Soft delete product (sets is_available=false and stock_quantity=0)

### Admin Product Endpoints

#### 1. GET /api/admin/products
**Purpose**: Get all products with pagination, search, and filters
**Query Parameters**:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 10)
- `search` (str): Search in name and description
- `category` (str): Filter by category ObjectId
- `status` (str): Filter by status ('active' or other)

**Response Format**:
```json
{
  "products": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "price": 0.00,
      "category": "string",
      "categoryName": "string",
      "active": true,
      "stock": 0,
      "image": "string",
      "createdAt": "2024-01-01T00:00:00.000000"
    }
  ],
  "total": 0,
  "page": 1,
  "totalPages": 0
}
```

#### 2. GET /api/admin/products/{product_id}
**Purpose**: Get single product details
**Response Format**: Same as list but single product

#### 3. POST /api/admin/products
**Purpose**: Create new product
**Request Body**:
```json
{
  "name": "string",
  "description": "string",
  "price": 0.00,
  "category": "string",
  "active": true,
  "stock": 0,
  "image": "string"
}
```

#### 4. PUT /api/admin/products/{product_id}
**Purpose**: Update product
**Request Body**: Partial update with any of the creation fields

#### 5. DELETE /api/admin/products/{product_id}
**Purpose**: Soft delete by setting active=false

## Key Differences Summary

1. **Database Access Pattern**:
   - Public endpoints use the Product model class with proper validation
   - Admin endpoints directly access MongoDB without using the model

2. **Field Naming Convention**:
   - Public endpoints use snake_case (is_available, stock_quantity)
   - Admin endpoints mix camelCase (createdAt) and snake_case

3. **Response Structure**:
   - Public endpoints use standardized success_response wrapper
   - Admin endpoints return raw JSON without wrapper

4. **Error Handling**:
   - Public endpoints have comprehensive error handling with Romanian messages
   - Admin endpoints have basic error handling with English messages

5. **Validation**:
   - Public endpoints use JSON schema validation and model validation
   - Admin endpoints have minimal validation

6. **Images**:
   - Public endpoints support multiple images (array)
   - Admin endpoints support only single image (string)

## Recommendations

1. **Standardize Field Names**: Use consistent field names across all endpoints
2. **Use Model Classes**: Admin endpoints should use the Product model for consistency
3. **Unified Response Format**: Both endpoint sets should use the same response wrapper
4. **Consistent Validation**: Apply the same validation rules to both endpoint sets
5. **Image Handling**: Admin endpoints should support multiple images like public endpoints