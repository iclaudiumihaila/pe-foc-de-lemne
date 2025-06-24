# Admin Functionality Architecture

**Created**: 2025-06-22T19:32:00Z  
**Version**: 2.0 (Updated based on Architect B feedback)

## Existing Components (Already Implemented)

### Authentication System ✓
- **AuthContext**: Handles admin authentication with JWT
- **AdminLogin**: Login page at `/admin/login`
- **Protected Routes**: Admin routes require authentication
- **Role Check**: `isAdmin()` function validates admin role

### Admin Layout System ✓
- **AdminLayout**: Layout wrapper with navbar and sidebar
- **AdminNavBar**: Top navigation with user info and logout
- **AdminSidebar**: Collapsible sidebar with navigation
- **AdminDashboard**: Dashboard page with statistics

## System Design for New Features

### Frontend Structure
```
frontend/src/
├── pages/admin/ (existing)
│   ├── AdminLogin.jsx        ✓ Exists
│   ├── AdminDashboard.jsx    ✓ Exists
│   ├── Products.jsx          ← To create
│   ├── ProductForm.jsx       ← To create
│   ├── Categories.jsx        ← To create
│   ├── Orders.jsx           ← To create
│   ├── OrderDetails.jsx     ← To create
│   └── SMSProviders.jsx     ← To create
├── components/admin/
│   ├── AdminNavBar.jsx       ✓ Exists
│   ├── AdminSidebar.jsx      ✓ Exists
│   ├── ProductManager.jsx    ✓ Exists (needs integration)
│   ├── CategoryManager.jsx   ✓ Exists (needs integration)
│   ├── OrderManager.jsx      ✓ Exists (needs integration)
│   └── common/               ← To create
│       ├── AdminTable.jsx    
│       ├── AdminModal.jsx    
│       ├── AdminForm.jsx     
│       └── AdminPagination.jsx
├── layouts/
│   ├── AdminLayout.jsx       ✓ Exists
│   └── PublicLayout.jsx      ✓ Exists
├── context/
│   ├── AuthContext.jsx       ✓ Exists
│   └── AdminSidebarContext.jsx ✓ Exists
└── services/
    ├── api.js                ✓ Exists
    ├── adminProductService.js    ← To create
    ├── adminCategoryService.js   ← To create
    ├── adminOrderService.js      ← To create
    └── smsProviderService.js     ← To create
```

### Backend Structure
```
backend/app/
├── routes/
│   ├── auth.py              ✓ Exists (admin login works)
│   ├── admin/               ← To create
│   │   ├── __init__.py
│   │   ├── products.py      
│   │   ├── categories.py    
│   │   ├── orders.py        
│   │   └── sms_providers.py 
├── services/
│   ├── auth_service.py      ✓ Exists
│   ├── admin/               ← To create
│   │   ├── __init__.py
│   │   ├── product_admin_service.py
│   │   ├── category_admin_service.py
│   │   └── order_admin_service.py
├── models/
│   ├── user.py              ✓ Exists (has admin role)
│   ├── product.py           ✓ Exists
│   ├── category.py          ✓ Exists
│   ├── order.py             ✓ Exists
│   └── sms_provider.py      ✓ Exists
└── utils/
    ├── auth_middleware.py   ✓ Exists (admin_required decorator)
    └── validators.py        ✓ Exists
```

### API Design

#### Authentication (Already Working)
- `POST /api/auth/login` - Admin login with phone/password
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user (includes role)

#### Product Admin Endpoints
- `GET /api/admin/products` - List with pagination, search, filters
- `GET /api/admin/products/:id` - Get single product details
- `POST /api/admin/products` - Create new product
- `PUT /api/admin/products/:id` - Update product
- `DELETE /api/admin/products/:id` - Soft delete product
- `PUT /api/admin/products/:id/status` - Toggle active/inactive
- `POST /api/admin/products/bulk-status` - Bulk status update

#### Category Admin Endpoints
- `GET /api/admin/categories` - List all categories
- `GET /api/admin/categories/tree` - Hierarchical tree view
- `POST /api/admin/categories` - Create category
- `PUT /api/admin/categories/:id` - Update category
- `DELETE /api/admin/categories/:id` - Delete (check for products)
- `PUT /api/admin/categories/reorder` - Update display order

#### Order Admin Endpoints
- `GET /api/admin/orders` - List with filters and pagination
- `GET /api/admin/orders/:id` - Get full order details
- `PUT /api/admin/orders/:id/status` - Update order status
- `POST /api/admin/orders/:id/note` - Add internal note
- `GET /api/admin/orders/:id/invoice` - Generate invoice PDF

#### SMS Provider Endpoints
- `GET /api/admin/sms-providers` - List all providers
- `POST /api/admin/sms-providers` - Add provider config
- `PUT /api/admin/sms-providers/:id` - Update config
- `DELETE /api/admin/sms-providers/:id` - Remove provider
- `POST /api/admin/sms-providers/:id/test` - Send test SMS
- `GET /api/admin/sms-logs` - View SMS send history

### Component Architecture

#### Reusable Admin Components

1. **AdminTable**
   ```jsx
   props: {
     columns: Array<{key, label, sortable, render}>
     data: Array<Object>
     onSort: Function
     onPageChange: Function
     totalPages: Number
     currentPage: Number
     onRowClick: Function
     bulkActions: Array<{label, action}>
     searchPlaceholder: String
   }
   ```

2. **AdminModal**
   ```jsx
   props: {
     isOpen: Boolean
     onClose: Function
     title: String
     size: 'sm' | 'md' | 'lg'
     footer: ReactNode
     loading: Boolean
   }
   ```

3. **AdminForm**
   ```jsx
   Utilities for:
   - Field validation
   - Error display
   - Submit handling
   - Loading states
   - Success messages
   ```

4. **AdminPagination**
   ```jsx
   props: {
     currentPage: Number
     totalPages: Number
     onPageChange: Function
     pageSize: Number
     totalItems: Number
   }
   ```

### State Management
- **React Query**: For API data fetching and caching
- **Local State**: For UI interactions
- **Context**: AdminSidebarContext (already exists)
- **Optimistic Updates**: For better UX on mutations

### Error Handling Architecture

1. **API Error Format**
   ```json
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Validation failed",
       "details": {
         "field": ["error message"]
       }
     }
   }
   ```

2. **Frontend Error Handling**
   - Toast notifications for user errors
   - Error boundaries for component crashes
   - Retry logic for network failures
   - Fallback UI for loading states

3. **Backend Error Handling**
   - Consistent error response format
   - Proper HTTP status codes
   - Detailed logging for debugging
   - Rate limiting with clear messages

### Security Considerations
- **Authentication**: JWT tokens with refresh mechanism ✓
- **Authorization**: Role-based checks on all admin endpoints
- **Input Validation**: Zod schemas for all inputs
- **XSS Protection**: Sanitize user-generated content
- **CSRF Protection**: Token validation for state changes
- **File Upload**: Type validation, size limits, virus scanning
- **Rate Limiting**: Stricter limits for admin endpoints

### Performance Optimizations
- **Code Splitting**: Lazy load admin routes ✓
- **Data Pagination**: All lists support pagination
- **Search Debouncing**: 300ms debounce on search inputs
- **Image Optimization**: Resize on upload, serve WebP
- **Caching Strategy**: 
  - Categories: 5 minute cache
  - Products: No cache (real-time)
  - Orders: No cache (real-time)
- **Database Indexes**: On frequently queried fields

### Monitoring & Analytics
- **Admin Activity Log**: Track all admin actions
- **Performance Monitoring**: Track slow queries
- **Error Tracking**: Sentry integration
- **Usage Analytics**: Track feature adoption