# Task 75: Create ProductManager component

**ID**: 75_product_manager_component_creation  
**Title**: Create ProductManager component  
**Description**: Implement admin interface for product CRUD operations  
**Dependencies**: AdminDashboard page (Task 70), Loading component (Task 47)  
**Estimate**: 35 minutes  
**Deliverable**: frontend/src/components/admin/ProductManager.jsx

## Context

The admin product management backend is fully implemented with:
- Admin authentication middleware and JWT validation
- Product CRUD endpoints (create, update, delete) with Romanian localization
- Comprehensive validation and error handling
- Integration tests verifying all functionality
- Audit logging for admin actions

This task implements the frontend ProductManager component that provides the admin interface for managing products through the API endpoints.

## Requirements

### Component Features

1. **Product Listing**
   - Display products in a table/grid format
   - Pagination for large product lists
   - Search and filtering capabilities
   - Sort by name, price, category, stock, availability

2. **Product Creation**
   - Modal or form for adding new products
   - All required fields (name, description, price, category)
   - Optional fields (images, stock, weight, prep time)
   - Romanian validation messages
   - Category selection dropdown

3. **Product Editing**
   - Inline editing or edit modal
   - Pre-populated form with current values
   - Validation for all fields
   - Category change capability
   - Save/cancel functionality

4. **Product Deletion**
   - Delete button with confirmation dialog
   - Soft delete confirmation message
   - Romanian confirmation text
   - Success/error feedback

5. **Authentication Integration**
   - Use AuthContext for admin authentication
   - Handle token expiration
   - Redirect to login if not authenticated
   - Admin role verification

6. **API Integration**
   - Fetch products from GET /api/products
   - Create products via POST /api/admin/products
   - Update products via PUT /api/admin/products/:id
   - Delete products via DELETE /api/admin/products/:id
   - Handle API errors with Romanian messages

7. **User Experience**
   - Loading states during API calls
   - Success/error notifications
   - Romanian localization throughout
   - Responsive design with Tailwind CSS
   - Accessibility considerations

## Success Criteria

1. ✅ Component file created at frontend/src/components/admin/ProductManager.jsx
2. ✅ Product listing displays all products with pagination
3. ✅ Product creation form with all required and optional fields
4. ✅ Product editing functionality (inline or modal)
5. ✅ Product deletion with confirmation dialog
6. ✅ Romanian localization for all text and messages
7. ✅ Authentication integration with AuthContext
8. ✅ API integration with proper error handling
9. ✅ Loading states and user feedback
10. ✅ Responsive design with Tailwind CSS
11. ✅ Component integrates with AdminDashboard
12. ✅ Uses Loading component for loading states

## Implementation Details

The ProductManager component will be a comprehensive admin interface that:
- Manages product lifecycle from creation to deletion
- Provides smooth user experience with loading states
- Handles all error scenarios with Romanian messages
- Integrates seamlessly with existing admin authentication
- Uses modern React patterns (hooks, context, functional components)