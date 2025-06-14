# Task 83: Create admin category delete endpoint

**ID**: 83_admin_category_delete_endpoint  
**Title**: Create admin category delete endpoint  
**Description**: Implement admin endpoint for deleting categories  
**Dependencies**: Admin category update endpoint (Task 82)  
**Estimate**: 15 minutes  
**Deliverable**: DELETE /api/admin/categories/:id route with admin auth

## Context

The admin category management system is complete with comprehensive CRUD operations:
- Admin category create endpoint with Romanian localization and validation
- Admin category update endpoint with partial updates, change tracking, and audit logging
- Admin authentication middleware with JWT validation and role verification
- Complete audit logging system for admin actions
- Romanian localization patterns established throughout all interfaces
- Comprehensive error handling and validation patterns

This task implements the final category management endpoint, allowing administrators to delete categories while maintaining data integrity through business rule validation.

## Requirements

### Core Functionality

1. **Category Delete Endpoint**
   - DELETE /api/admin/categories/:id endpoint
   - Admin authentication required via middleware
   - Soft delete implementation (is_active=False)
   - Category existence validation
   - Business rule enforcement

2. **Soft Delete Implementation**
   - Set is_active=False instead of physical deletion
   - Preserve category data for audit and recovery
   - Maintain referential integrity with existing products
   - Allow future reactivation if needed

3. **Business Rule Validation**
   - Prevent deletion of categories with associated products
   - Check product count before allowing deletion
   - Provide clear guidance on resolving conflicts
   - Romanian error messages for business rule violations

### Business Logic & Data Integrity

1. **Product Relationship Checking**
   - Count active products in category before deletion
   - Prevent deletion if products exist
   - Suggest moving products to other categories
   - Provide product count in error messages

2. **Safe Deletion Process**
   - Validate category exists before deletion attempt
   - Check if category is already inactive
   - Atomic operation to prevent partial states
   - Complete audit trail for all deletion attempts

3. **Category State Management**
   - Handle already deleted categories gracefully
   - Prevent double deletion attempts
   - Maintain category visibility rules
   - Preserve data integrity across the system

### API Response Format

1. **Success Response (200 OK)**
   ```json
   {
     "success": true,
     "message": "Categoria 'Diverse' a fost dezactivată cu succes",
     "data": {
       "category_id": "ObjectId",
       "category_name": "Diverse", 
       "deleted": true,
       "was_active": true,
       "product_count": 0,
       "deleted_at": "2025-01-15T00:00:00Z"
     }
   }
   ```

2. **Already Deleted Response (200 OK)**
   ```json
   {
     "success": true,
     "message": "Categoria este deja dezactivată",
     "data": {
       "category_id": "ObjectId",
       "deleted": true,
       "was_active": false
     }
   }
   ```

3. **Error Responses**
   - 400 Bad Request: Business rule violations
   - 401 Unauthorized: Missing or invalid authentication
   - 403 Forbidden: Non-admin user access attempt
   - 404 Not Found: Category does not exist
   - 409 Conflict: Category has associated products
   - 500 Internal Server Error: Database or server errors

### Validation Rules

1. **Category Existence**
   - Validate category ID format (ObjectId)
   - Check category exists in database
   - Handle invalid ObjectId format gracefully
   - Romanian error messages for not found scenarios

2. **Product Relationship Validation**
   - Count active products in category
   - Calculate total product count for reporting
   - Check both available and unavailable products
   - Provide accurate count in error messages

3. **Business Rule Enforcement**
   - Prevent deletion if products exist
   - Allow deletion only for empty categories
   - Suggest alternatives for categories with products
   - Maintain data consistency across operations

### Romanian Localization

1. **Success Messages**
   - "Categoria '{name}' a fost dezactivată cu succes"
   - "Categoria este deja dezactivată"
   - "Categoria a fost marcată ca inactivă"

2. **Error Messages**
   - "Categoria nu a fost găsită"
   - "Nu se poate șterge categoria care conține {count} produse"
   - "Pentru a șterge categoria, mutați sau ștergeți mai întâi produsele"
   - "Categoria este deja dezactivată"
   - "Eroare la dezactivarea categoriei în baza de date"
   - "ID-ul categoriei nu este valid"

3. **Business Rule Messages**
   - "Categoria nu poate fi ștearsă deoarece conține produse active"
   - "Mutați produsele în alte categorii înainte de ștergere"
   - "Contactați administratorul pentru suport cu ștergerea categoriei"

4. **Audit Log Messages**
   - "Categorie dezactivată"
   - "Tentativă de ștergere categorie cu produse"
   - "Categorie deja dezactivată - nici o acțiune"

### Security and Admin Features

1. **Authentication and Authorization**
   - Admin authentication middleware required
   - JWT token validation
   - Admin role verification
   - Request logging for audit purposes

2. **Audit Logging**
   - Log all category deletion attempts (successful and failed)
   - Include admin user ID, timestamp, and category details
   - Track product count at time of deletion attempt
   - Romanian action descriptions for compliance

3. **Data Protection**
   - Soft delete to preserve data integrity
   - No physical deletion of category records
   - Maintain foreign key relationships
   - Enable recovery of accidentally deleted categories

### Error Handling

1. **Validation Errors**
   - Invalid ObjectId format handling
   - Category not found scenarios
   - Romanian error message localization
   - Clear guidance for resolution

2. **Business Logic Errors**
   - Product relationship conflicts
   - Already deleted category handling
   - Detailed product count reporting
   - Actionable error messages

3. **Database Errors**
   - Connection error handling
   - Update failure scenarios
   - Transaction rollback on failures
   - Romanian error messages

### Product Relationship Management

1. **Product Count Calculation**
   - Count active products in category
   - Include both available and unavailable products
   - Real-time count calculation before deletion
   - Accurate reporting in error messages

2. **Conflict Resolution Guidance**
   - Suggest moving products to other categories
   - Provide product count for planning
   - Offer alternative workflows
   - Romanian guidance messages

3. **Data Integrity Protection**
   - Prevent orphaned products
   - Maintain referential integrity
   - Preserve product-category relationships
   - Enable data recovery if needed

## Success Criteria

1. ✅ Endpoint created at DELETE /api/admin/categories/:id
2. ✅ Admin authentication middleware integration
3. ✅ Soft delete implementation with is_active=False
4. ✅ Category existence validation with 404 handling
5. ✅ Product relationship checking and conflict prevention
6. ✅ Romanian error and success message localization
7. ✅ Audit logging for admin category deletion actions
8. ✅ Business rule enforcement for data integrity
9. ✅ Comprehensive error handling for all scenarios
10. ✅ Product count reporting in error messages
11. ✅ Already deleted category handling
12. ✅ Proper HTTP status codes and response format

## Implementation Details

The endpoint will be implemented by enhancing:
- Route handler: backend/app/routes/categories.py (update existing DELETE endpoint)
- Admin authentication via existing auth_middleware.py
- Category model integration for soft delete operations
- Product count calculation and validation
- Romanian message constants for localization
- Audit logging integration for admin actions
- Business rule validation for data integrity protection