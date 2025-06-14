# Task 14: Create Product Data Model with MongoDB Schema

**Task ID**: 14_product_data_model  
**Title**: Create Product data model with MongoDB schema  
**Phase**: Backend Data Models  
**Developer Role**: Active  

## Task Description
Create Product model class with MongoDB operations and validation

## Deliverable
backend/app/models/product.py with Product class and database operations

## Dependencies
- 09_database_indexes_setup
- 10_input_validation_middleware
- 13_user_data_model

## Acceptance Criteria
- Product model matches architecture MongoDB schema
- Image URL validation and handling
- Price and stock management with validation
- MongoDB CRUD operations (create, find, update, delete)
- Category relationship management
- Inventory tracking with stock updates
- Proper indexing utilization
- Input validation integration
- Slug generation for SEO-friendly URLs

## Implementation Plan
1. Create backend/app/models/product.py file
2. Import required dependencies (pymongo, datetime, decimal)
3. Implement Product class with schema-compliant structure
4. Add image URL validation and handling
5. Add price validation with decimal precision
6. Implement stock management and tracking
7. Implement CRUD operations (create, find, update, delete)
8. Add category relationship management
9. Add slug generation for URLs
10. Integrate with validation middleware
11. Add proper error handling and logging

## Product Schema Requirements
Based on architecture.md MongoDB schema:

```json
{
  "_id": "ObjectId",
  "name": "string (2-100 chars, indexed)",
  "slug": "string (URL-friendly, unique indexed)",
  "description": "string (10-1000 chars)",
  "price": "decimal (2 decimal places, > 0)",
  "category_id": "ObjectId (reference to categories)",
  "images": "array of strings (URLs)",
  "stock_quantity": "integer (>= 0)",
  "is_available": "boolean (default: true)",
  "weight_grams": "integer (optional, > 0)",
  "preparation_time_hours": "integer (default: 24)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "created_by": "ObjectId (reference to users)"
}
```

## Required Methods
- `Product.__init__()` - Initialize Product object
- `Product.create()` - Create new product in database
- `Product.find_by_id()` - Find product by ObjectId
- `Product.find_by_slug()` - Find product by URL slug
- `Product.find_by_category()` - Find products in category
- `Product.find_available()` - Find available products with stock
- `Product.update()` - Update product data
- `Product.update_stock()` - Update stock quantity
- `Product.delete()` - Soft delete product (set unavailable)
- `Product.to_dict()` - Convert to dictionary representation
- `Product.generate_slug()` - Generate URL-friendly slug from name

## Stock Management
- Stock tracking with quantity validation
- Automatic availability based on stock levels
- Stock update operations with audit logging
- Inventory validation before order processing

## Image Management
- Multiple image URL support
- URL format validation
- Image array management
- Optional image handling

## Category Integration
- Category ObjectId reference validation
- Category-based product queries
- Category relationship integrity

## SEO Features
- URL slug generation from product name
- Unique slug validation and conflict resolution
- SEO-friendly URL patterns

## Testing
Verify Product model CRUD operations and business logic work correctly.

## Estimated Time
30 minutes

## Notes
This creates the core Product model for catalog management. Includes inventory tracking, category relationships, and SEO-friendly URLs following MongoDB schema from architecture.