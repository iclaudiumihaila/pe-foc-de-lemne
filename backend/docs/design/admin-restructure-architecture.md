# Admin Area Restructuring Architecture

## 1. High-Level Architecture

### 1.1 Layout System Design
```
App.jsx
├── PublicLayout
│   ├── Header
│   ├── Routes (/, /products, /cart, etc.)
│   └── Footer
└── AdminLayout
    ├── AdminNavBar
    ├── AdminSidebar
    └── Routes (/admin/*, etc.)
```

### 1.2 Component Structure
```
src/
├── layouts/
│   ├── PublicLayout.jsx      # Wrapper for public pages
│   └── AdminLayout.jsx        # Wrapper for admin pages
├── components/
│   ├── admin/
│   │   ├── AdminNavBar.jsx   # Top navigation for admin
│   │   ├── AdminSidebar.jsx  # Side navigation for admin
│   │   └── [existing admin components]
│   └── common/
│       └── [existing common components]
└── pages/
    └── [existing pages]
```

## 2. Implementation Strategy

### 2.1 Layout Components

**PublicLayout.jsx**
- Wraps public routes
- Includes Header and Footer
- Maintains current site structure

**AdminLayout.jsx**
- Wraps admin routes
- Custom admin navigation
- No public site elements
- Persistent sidebar
- Clean workspace

### 2.2 Routing Architecture

```jsx
<Routes>
  {/* Public Routes */}
  <Route element={<PublicLayout />}>
    <Route path="/" element={<Home />} />
    <Route path="/products" element={<Products />} />
    <Route path="/cart" element={<Cart />} />
    {/* ... other public routes */}
  </Route>

  {/* Admin Routes */}
  <Route path="/admin" element={<AdminLayout />}>
    <Route path="login" element={<AdminLogin />} />
    <Route path="dashboard" element={<AdminDashboard />} />
    <Route path="products" element={<AdminProducts />} />
    <Route path="orders" element={<AdminOrders />} />
    <Route path="categories" element={<AdminCategories />} />
  </Route>
</Routes>
```

## 3. Component Specifications

### 3.1 AdminLayout Component
```jsx
// Features:
- Authentication check
- Admin navigation bar (top)
- Admin sidebar (left)
- Main content area (center)
- Responsive design
- Clean, professional styling
```

### 3.2 AdminNavBar Component
```jsx
// Features:
- Application title/logo
- User information display
- Logout button
- Optional notifications area
- Breadcrumb navigation
```

### 3.3 AdminSidebar Component
```jsx
// Features:
- Navigation menu items
- Active state indication
- Collapsible on mobile
- Icons for each menu item
- "Back to store" link
```

## 4. State Management

### 4.1 Authentication Context Integration
```jsx
// AdminLayout will consume AuthContext
const { isAuthenticated, user, isAdmin } = useAuth();

// Redirect if not authenticated or not admin
useEffect(() => {
  if (!isAuthenticated || !isAdmin()) {
    navigate('/admin/login');
  }
}, [isAuthenticated, isAdmin]);
```

### 4.2 Admin Sidebar Context
```jsx
// AdminSidebarContext.jsx
const AdminSidebarContext = createContext({
  isCollapsed: false,
  toggleCollapse: () => {},
  activeItem: 'dashboard'
});
```

### 4.3 Breadcrumb State Management
```jsx
// useBreadcrumbs hook
const breadcrumbs = useBreadcrumbs({
  '/admin/dashboard': 'Dashboard',
  '/admin/products': 'Products',
  '/admin/products/new': 'Add Product',
  '/admin/orders': 'Orders',
  '/admin/categories': 'Categories'
});
```

## 5. Styling Architecture

### 5.1 Admin Theme
```css
/* Admin-specific variables */
--admin-bg: #f5f5f5;
--admin-sidebar-bg: #2c3e50;
--admin-sidebar-text: #ecf0f1;
--admin-primary: #3498db;
--admin-border: #ddd;
```

### 5.2 Layout Classes
- `.admin-layout` - Main admin container
- `.admin-nav` - Top navigation
- `.admin-sidebar` - Side navigation
- `.admin-content` - Main content area

## 6. Migration Strategy

### 6.1 Phase 1: Create Layout Components
1. Build AdminLayout component
2. Build AdminNavBar component
3. Build AdminSidebar component

### 6.2 Phase 2: Implement Routing
1. Create PublicLayout wrapper
2. Update App.jsx routing structure
3. Test layout switching

### 6.3 Phase 3: Refactor Admin Pages
1. Remove embedded navigation from AdminDashboard
2. Ensure consistent styling
3. Update navigation links

## 7. Testing Requirements

### 7.1 Functional Tests
- Layout switching works correctly
- Authentication persists across layouts
- Navigation links function properly
- Mobile responsiveness

### 7.2 Visual Tests
- Admin layout renders correctly
- No public site elements in admin
- Consistent styling throughout
- Proper spacing and alignment

## 8. Error Handling

### 8.1 Layout Error Boundaries
```jsx
// AdminErrorBoundary.jsx
<ErrorBoundary fallback={<AdminErrorPage />}>
  <AdminLayout />
</ErrorBoundary>
```

### 8.2 Route Error Handling
- 404 Page for invalid admin routes
- Authentication failure redirects
- API error notifications
- Graceful fallbacks for failed components

### 8.3 Authentication Failures
```jsx
// Handle auth failures in AdminLayout
const handleAuthError = (error) => {
  if (error.code === 'AUTH_EXPIRED') {
    // Attempt token refresh
  } else {
    // Redirect to login
    navigate('/admin/login', { 
      state: { from: location.pathname } 
    });
  }
};
```

## 9. Performance Optimization

### 9.1 Code Splitting Strategy
```jsx
// Lazy load admin components
const AdminLayout = lazy(() => import('./layouts/AdminLayout'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const AdminProducts = lazy(() => import('./pages/AdminProducts'));
```

### 9.2 Bundle Optimization
- Separate webpack chunks for admin/public
- Admin-specific vendor bundle
- CSS code splitting
- Image optimization for admin assets

### 9.3 Loading Performance
```jsx
// Progressive loading with suspense
<Suspense fallback={<AdminLoadingScreen />}>
  <AdminLayout />
</Suspense>
```

## 10. Testing Strategy

### 10.1 Unit Tests
- Individual component testing
- Context provider testing
- Hook testing (useBreadcrumbs, etc.)

### 10.2 Integration Tests
- Layout switching scenarios
- Authentication flow testing
- Navigation state persistence
- Error boundary testing

### 10.3 E2E Tests
- Complete admin workflows
- Login to dashboard flow
- CRUD operations
- Navigation patterns

### 10.4 Performance Tests
- Bundle size limits
- Load time benchmarks
- Memory usage monitoring
- Layout transition performance