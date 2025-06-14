# Task 15: Create Category Data Model with MongoDB Schema

**Task ID**: 15_category_data_model  
**Title**: Create Category data model with MongoDB schema  
**Phase**: Backend Data Models  
**Developer Role**: Active  

## Task Description
Create Category model class with MongoDB operations and hierarchy management

## Deliverable
backend/app/models/category.py with Category class and database operations

## Dependencies
- 09_database_indexes_setup
- 10_input_validation_middleware
- 13_user_data_model

## Acceptance Criteria
- Category model matches architecture MongoDB schema
- Category hierarchy and ordering management
- MongoDB CRUD operations (create, find, update, delete)
- Product count tracking and statistics
- Slug generation for SEO-friendly URLs
- Proper indexing utilization
- Input validation integration
- Category-product relationship integrity

## Implementation Plan
1. Create backend/app/models/category.py file
2. Import required dependencies (pymongo, datetime)
3. Implement Category class with schema-compliant structure
4. Add category hierarchy management
5. Add display order validation and management
6. Implement CRUD operations (create, find, update, delete)
7. Add product count tracking
8. Add slug generation for URLs
9. Integrate with validation middleware
10. Add proper error handling and logging

## Category Schema Requirements
Based on architecture.md MongoDB schema:

```json
{
  "_id": "ObjectId",
  "name": "string (2-50 chars, unique indexed)",
  "slug": "string (URL-friendly, unique indexed)",
  "description": "string (optional, max 500 chars)",
  "display_order": "integer (for sorting, default: 0)",
  "is_active": "boolean (default: true)",
  "product_count": "integer (cached count, default: 0)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "created_by": "ObjectId (reference to users)"
}
```

## Required Methods
- `Category.__init__()` - Initialize Category object
- `Category.create()` - Create new category in database
- `Category.find_by_id()` - Find category by ObjectId
- `Category.find_by_slug()` - Find category by URL slug
- `Category.find_all()` - Find all categories with ordering
- `Category.find_active()` - Find active categories only
- `Category.update()` - Update category data
- `Category.update_product_count()` - Update cached product count
- `Category.delete()` - Soft delete category (set inactive)
- `Category.to_dict()` - Convert to dictionary representation
- `Category.generate_slug()` - Generate URL-friendly slug from name

## Display Order Management
- Integer-based ordering for category display
- Automatic ordering assignment for new categories
- Order validation and conflict resolution
- Sorting support for category listings

## Product Count Tracking
- Cached product count for performance
- Automatic count updates on product changes
- Count validation and recalculation
- Statistical reporting support

## SEO Features
- URL slug generation from category name
- Unique slug validation and conflict resolution
- SEO-friendly URL patterns
- Slug updates when name changes

## Category-Product Relationship
- Product count tracking and updates
- Category reference validation
- Relationship integrity maintenance
- Cascade handling for category deletion

## Testing
Verify Category model CRUD operations and business logic work correctly.

## Estimated Time
20 minutes

## Notes
This creates the Category model for product organization. Includes hierarchy management, product counting, and SEO-friendly URLs following MongoDB schema from architecture.