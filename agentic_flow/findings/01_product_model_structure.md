# Product Model Structure and Database Schema

## Overview
The Product model is defined in `/backend/app/models/product.py` and represents products in the MongoDB database. The model includes comprehensive validation, inventory management, and catalog functionality.

## Product Model Fields and Types

### Core Fields
- **_id** (ObjectId): MongoDB document ID
- **name** (str): Product name
  - Required
  - Length: 2-100 characters
  - Sanitized on save
- **slug** (str): URL-friendly slug
  - Auto-generated from name
  - Unique across products
  - Used for SEO-friendly URLs
- **description** (str): Product description
  - Required
  - Length: 10-1000 characters
  - Sanitized on save
- **price** (Decimal/float): Product price
  - Required
  - Range: 0.01 - 9999.99
  - Stored as float in MongoDB, converted to Decimal in Python
  - Exactly 2 decimal places
- **category_id** (ObjectId): Reference to category
  - Required
  - Must be valid ObjectId
- **images** (List[str]): List of image URLs/paths
  - Optional, defaults to empty list
  - Max 10 images
  - Supports both full URLs and relative paths
- **stock_quantity** (int): Available stock
  - Required, defaults to 0
  - Range: 0-10000
  - Automatically updates is_available
- **is_available** (bool): Product availability flag
  - Defaults to True
  - Auto-set based on stock_quantity > 0

### Optional Fields
- **weight_grams** (int): Product weight in grams
  - Optional
  - Range: 1-50000 (1g to 50kg)
- **preparation_time_hours** (int): Preparation time
  - Optional, defaults to 24
  - Range: 1-168 hours (1 hour to 1 week)

### Metadata Fields
- **created_at** (datetime): Creation timestamp
  - Auto-set on creation
- **updated_at** (datetime): Last update timestamp
  - Auto-updated on modifications
- **created_by** (ObjectId): User who created the product
  - Required on creation
  - Reference to user document

## Database Field Mappings

The Product model stores data in MongoDB with the following field mappings:

```python
{
    '_id': ObjectId,
    'name': str,
    'slug': str,
    'description': str,
    'price': float,  # Stored as float, converted to Decimal in Python
    'category_id': ObjectId,
    'images': [str],
    'stock_quantity': int,
    'is_available': bool,
    'weight_grams': int,  # Optional
    'preparation_time_hours': int,
    'created_at': datetime,
    'updated_at': datetime,
    'created_by': ObjectId
}
```

## Data Transformations

### During Creation (Product.create())
1. **Name**: Trimmed and sanitized
2. **Description**: Trimmed and sanitized
3. **Price**: Converted to Decimal, validated, then stored as float
4. **Slug**: Auto-generated from name, made unique
5. **is_available**: Auto-set based on stock_quantity > 0
6. **Timestamps**: created_at and updated_at set to current UTC time
7. **Images**: Validated as URLs or relative paths

### During Updates (product.update())
1. **Name changes**: Regenerate slug automatically
2. **Stock changes**: Update is_available automatically
3. **Price**: Converted to Decimal for validation, stored as float
4. **updated_at**: Always updated to current UTC time

### When Converting to Dict (product.to_dict())
1. **_id**: Converted to string as 'id'
2. **ObjectIds**: All converted to strings
3. **Dates**: Converted to ISO format with 'Z' suffix
4. **Price**: Kept as float
5. **Internal fields**: Excluded unless include_internal=True

## Database Indexes

Based on the database.py file, the products collection has these indexes:
- **category_id**: For filtering by category
- **active**: For filtering active products (legacy field)
- **featured**: For featured product queries (legacy field)
- **text search**: On name and description fields
- **price**: For sorting by price

Note: Some indexes reference legacy fields (active, featured) that are not in the current Product model.

## Legacy Field Migrations

The fix_products.py script shows historical field name changes:
- **active** → **is_available**
- **stock** → **stock_quantity**
- **image_url** → **images** (string to array)

## Required vs Optional Fields

### Required Fields (must be provided on creation)
- name
- description
- price
- category_id
- created_by

### Optional Fields with Defaults
- images (default: [])
- stock_quantity (default: 0)
- is_available (default: True, auto-managed)
- preparation_time_hours (default: 24)
- weight_grams (default: None)

### Auto-generated Fields
- _id (by MongoDB)
- slug (from name)
- created_at
- updated_at

## Validation Rules

### Name
- Required, non-empty
- 2-100 characters after trimming
- Sanitized for XSS

### Description
- Required, non-empty
- 10-1000 characters after trimming
- Sanitized for XSS

### Price
- Must be numeric (string, float, or Decimal)
- Range: 0.01 - 9999.99
- Rounded to 2 decimal places

### Stock Quantity
- Must be integer
- Range: 0-10000
- Negative values not allowed

### Weight (if provided)
- Must be integer
- Range: 1-50000 grams

### Preparation Time
- Must be integer
- Range: 1-168 hours

### Images
- Must be array of strings
- Each must be valid URL or relative path
- Supported formats: jpg, jpeg, png, gif, svg, webp
- Maximum 10 images