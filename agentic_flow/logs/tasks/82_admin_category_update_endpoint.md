# Task 82: Create admin category update endpoint

**ID**: 82_admin_category_update_endpoint  
**Title**: Create admin category update endpoint  
**Description**: Implement admin endpoint for updating categories  
**Dependencies**: Admin category create endpoint (Task 81)  
**Estimate**: 15 minutes  
**Deliverable**: PUT /api/admin/categories/:id route with admin auth

## Context

The admin category management system is established with:
- Admin category create endpoint with comprehensive Romanian localization and validation
- Admin authentication middleware with JWT validation and role verification
- Complete audit logging system for admin actions
- Romanian localization patterns established
- Comprehensive error handling and validation patterns

This task implements the category update endpoint, allowing administrators to modify existing product categories while maintaining data integrity and business rules.

## Requirements

### Core Functionality

1. **Category Update Endpoint**
   - PUT /api/admin/categories/:id endpoint
   - Admin authentication required via middleware
   - Partial update support for category fields
   - Category existence validation
   - Business rule enforcement

2. **Updatable Fields**
   - Category name: validated, unique checking (excluding current)
   - Description: optional, maximum 500 characters
   - Display order: optional integer, range validation
   - is_active: boolean for category activation/deactivation
   - Automatic slug regeneration when name changes

3. **Input Validation**
   - Same validation rules as create endpoint
   - Name uniqueness excluding current category ID
   - Romanian validation error messages
   - Partial update support (only provided fields updated)

### Business Logic

1. **Category Identification**
   - Support ObjectId format for category_id parameter
   - Validate category exists and return 404 if not found
   - Load current category data for comparison

2. **Update Logic**
   - Only update fields provided in request body
   - Maintain existing values for omitted fields
   - Regenerate slug if name changes
   - Update timestamp automatically

3. **Name Uniqueness**
   - Check for duplicate names among active categories
   - Exclude current category from uniqueness check
   - Case-insensitive comparison
   - Romanian error messages for conflicts

### API Response Format

1. **Success Response (200 OK)**
   ```json
   {
     "success": true,
     "message": "Categoria 'Brânzeturi' a fost actualizată cu succes!",
     "data": {
       "category": {
         "id": "ObjectId",
         "name": "Brânzeturi",
         "description": "Brânzeturi artizanale actualizată",
         "slug": "branzeturi",
         "display_order": 2,
         "is_active": true,
         "product_count": 5,
         "created_at": "2025-01-14T23:00:00Z",
         "updated_at": "2025-01-14T23:55:00Z"
       },
       "changes": {
         "description": {
           "old": "Brânzeturi artizanale",
           "new": "Brânzeturi artizanale actualizată"
         },
         "display_order": {
           "old": 1,
           "new": 2
         }
       }
     }
   }
   ```

2. **Error Responses**
   - 400 Bad Request: Validation errors with Romanian messages
   - 401 Unauthorized: Missing or invalid authentication
   - 403 Forbidden: Non-admin user access attempt
   - 404 Not Found: Category does not exist
   - 409 Conflict: Duplicate category name
   - 500 Internal Server Error: Database or server errors

### Validation Rules

1. **Category Name (if provided)**
   - Minimum 2 characters, maximum 50 characters
   - Must be unique among active categories (excluding current)
   - Supports Romanian characters
   - Automatically trimmed and sanitized

2. **Description (if provided)**
   - Maximum 500 characters
   - HTML tags stripped for security
   - Automatically trimmed
   - Can be set to null to clear

3. **Display Order (if provided)**
   - Integer between 0 and 10000
   - Used for category sorting in frontend

4. **Is Active (if provided)**
   - Boolean value for category activation
   - Affects category visibility and product assignments

### Romanian Localization

1. **Success Messages**
   - "Categoria '{name}' a fost actualizată cu succes!"
   - "Categoria a fost dezactivată cu succes"
   - "Categoria a fost reactivată cu succes"

2. **Error Messages**
   - "Categoria nu a fost găsită"
   - "Numele categoriei trebuie să aibă între 2 și 50 de caractere"
   - "O categorie cu acest nume există deja"
   - "Descrierea nu poate depăși 500 de caractere"
   - "Ordinea de afișare trebuie să fie între 0 și 10000"
   - "Nu au fost furnizate date pentru actualizare"
   - "Eroare la actualizarea categoriei în baza de date"

3. **Audit Log Messages**
   - "Categorie actualizată"
   - "Categorie dezactivată"  
   - "Categorie reactivată"

### Security and Admin Features

1. **Authentication and Authorization**
   - Admin authentication middleware required
   - JWT token validation
   - Admin role verification
   - Request logging for audit purposes

2. **Audit Logging**
   - Log admin category update actions
   - Include admin user ID, timestamp, and change details
   - Track what fields were changed and their values
   - Romanian action descriptions

3. **Input Sanitization**
   - XSS prevention through input sanitization
   - HTML tag stripping in description fields
   - SQL injection prevention through MongoDB ODM

### Error Handling

1. **Validation Errors**
   - Comprehensive input validation with specific error messages
   - Field-level error reporting for frontend integration
   - Romanian error message localization

2. **Database Errors**
   - Connection error handling
   - Update failure handling
   - Transaction rollback on failures

3. **Business Logic Errors**
   - Category not found scenarios
   - Duplicate name conflicts
   - Invalid state transitions

### Change Tracking

1. **Change Detection**
   - Compare old and new values for each field
   - Track only fields that actually changed
   - Include change summary in response

2. **Change Logging**
   - Log specific changes made to category
   - Include old and new values in audit log
   - Track admin user who made changes

## Success Criteria

1. ✅ Endpoint created at PUT /api/admin/categories/:id
2. ✅ Admin authentication middleware integration
3. ✅ Partial update support for all category fields
4. ✅ Category existence validation with 404 handling
5. ✅ Name uniqueness validation excluding current category
6. ✅ Romanian error and success message localization
7. ✅ Audit logging for admin category update actions
8. ✅ Change tracking and reporting in response
9. ✅ Comprehensive error handling for all scenarios
10. ✅ Database integration with Category model
11. ✅ Security measures and input sanitization
12. ✅ Proper HTTP status codes and response format

## Implementation Details

The endpoint will be implemented in:
- Route handler: backend/app/routes/categories.py (update existing PUT endpoint)
- Admin authentication via existing auth_middleware.py
- Category model integration for database operations
- Romanian message constants for localization
- Audit logging integration for admin actions
- Change tracking for detailed update reporting