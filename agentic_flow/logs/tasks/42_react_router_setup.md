# Task 42: Setup React Router

## Task Details
- **ID**: 42_react_router_setup
- **Title**: Setup React Router
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: React app basic setup (Task 41)

## Objective
Configure React Router v6 with basic route structure to enable navigation between different pages of the local producer web application, establishing the foundation for multi-page user experience.

## Requirements
1. **Router Configuration**: React Router v6 configuration in App.jsx
2. **Basic Routes**: Placeholder routes for core application pages
3. **Navigation**: Basic navigation structure with routing links
4. **Route Structure**: Home, Products, Cart, Checkout, and other essential pages
5. **Layout**: Consistent layout structure across all routes
6. **Functionality**: React Router navigation works between placeholder pages

## Technical Implementation

### 1. Router Structure Overview
```
Routes Structure:
├── / (Home)
├── /products (Products listing)
├── /cart (Shopping cart)
├── /checkout (Order checkout)
├── /orders (Order confirmation/status)
└── /admin (Admin dashboard - for future)
```

### 2. App.jsx Router Configuration
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/common/Header';
import Home from './pages/Home';
import Products from './pages/Products';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import OrderConfirmation from './pages/OrderConfirmation';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/orders/:orderNumber" element={<OrderConfirmation />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```

### 3. Placeholder Page Components

#### Home Page (pages/Home.jsx)
```javascript
import React from 'react';

function Home() {
  return (
    <div className="home-page">
      <section className="hero-section">
        <h1>Local Producer Web Application</h1>
        <p>Welcome to our local produce marketplace</p>
        <h2>Fresh, Local, Sustainable</h2>
        <p>
          Discover the best local produce from farmers in your area. 
          Order fresh fruits, vegetables, and artisanal goods for pickup or delivery.
        </p>
      </section>
      
      <section className="features-section">
        <h3>What we offer</h3>
        <div className="features-grid">
          <div className="feature-card">
            <h4>🍎 Fresh Produce</h4>
            <p>Browse local products by category from verified local farmers</p>
          </div>
          <div className="feature-card">
            <h4>🛒 Easy Shopping</h4>
            <p>Add items to your cart and manage your order with ease</p>
          </div>
          <div className="feature-card">
            <h4>📱 Secure Verification</h4>
            <p>Phone verification ensures secure and authentic orders</p>
          </div>
          <div className="feature-card">
            <h4>📦 Order Management</h4>
            <p>Track your orders from preparation to pickup or delivery</p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <h3>Ready to get started?</h3>
        <p>Join our community of local food enthusiasts</p>
        <Link to="/products" className="cta-button">Browse Products</Link>
      </section>
    </div>
  );
}

export default Home;
```

#### Products Page (pages/Products.jsx)
```javascript
import React from 'react';

function Products() {
  return (
    <div className="products-page">
      <h1>Local Products</h1>
      <p>Browse our selection of fresh, local produce</p>
      
      <div className="products-content">
        <aside className="filters-sidebar">
          <h3>Filter Products</h3>
          <p>Category filters will go here</p>
        </aside>
        
        <section className="products-grid">
          <h3>Product Grid</h3>
          <p>Product listings will be displayed here</p>
          <div className="placeholder-products">
            <div className="product-placeholder">Product 1</div>
            <div className="product-placeholder">Product 2</div>
            <div className="product-placeholder">Product 3</div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Products;
```

#### Cart Page (pages/Cart.jsx)
```javascript
import React from 'react';

function Cart() {
  return (
    <div className="cart-page">
      <h1>Your Cart</h1>
      <p>Review your selected items before checkout</p>
      
      <div className="cart-content">
        <section className="cart-items">
          <h3>Cart Items</h3>
          <p>Cart items will be displayed here</p>
          <div className="placeholder-cart">
            <div className="cart-item-placeholder">Cart Item 1</div>
            <div className="cart-item-placeholder">Cart Item 2</div>
          </div>
        </section>
        
        <aside className="cart-summary">
          <h3>Order Summary</h3>
          <p>Order totals and checkout button will go here</p>
          <Link to="/checkout" className="checkout-button">
            Proceed to Checkout
          </Link>
        </aside>
      </div>
    </div>
  );
}

export default Cart;
```

#### Checkout Page (pages/Checkout.jsx)
```javascript
import React from 'react';

function Checkout() {
  return (
    <div className="checkout-page">
      <h1>Checkout</h1>
      <p>Complete your order with phone verification</p>
      
      <div className="checkout-content">
        <section className="customer-form">
          <h3>Customer Information</h3>
          <p>Customer form will go here</p>
        </section>
        
        <section className="sms-verification">
          <h3>Phone Verification</h3>
          <p>SMS verification component will go here</p>
        </section>
        
        <section className="order-summary">
          <h3>Order Summary</h3>
          <p>Final order review before submission</p>
        </section>
      </div>
    </div>
  );
}

export default Checkout;
```

#### Order Confirmation Page (pages/OrderConfirmation.jsx)
```javascript
import React from 'react';
import { useParams } from 'react-router-dom';

function OrderConfirmation() {
  const { orderNumber } = useParams();
  
  return (
    <div className="order-confirmation-page">
      <h1>Order Confirmed!</h1>
      <p>Thank you for your order</p>
      
      <div className="order-details">
        <h3>Order #{orderNumber}</h3>
        <p>Your order has been successfully placed</p>
        <p>You will receive SMS updates about your order status</p>
      </div>
      
      <div className="next-steps">
        <h3>What's Next?</h3>
        <ul>
          <li>You'll receive SMS confirmation shortly</li>
          <li>We'll notify you when your order is ready</li>
          <li>Pickup or delivery details will be sent via SMS</li>
        </ul>
      </div>
      
      <Link to="/" className="continue-shopping">
        Continue Shopping
      </Link>
    </div>
  );
}

export default OrderConfirmation;
```

#### Not Found Page (pages/NotFound.jsx)
```javascript
import React from 'react';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="not-found-page">
      <h1>Page Not Found</h1>
      <p>Sorry, the page you're looking for doesn't exist.</p>
      <Link to="/" className="home-link">
        Return to Home
      </Link>
    </div>
  );
}

export default NotFound;
```

### 4. Header Component with Navigation
```javascript
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };
  
  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="logo">
          <h1>Local Producer</h1>
        </Link>
        
        <nav className="main-navigation">
          <Link to="/" className={isActive('/')}>
            Home
          </Link>
          <Link to="/products" className={isActive('/products')}>
            Products
          </Link>
          <Link to="/cart" className={isActive('/cart')}>
            Cart
          </Link>
        </nav>
        
        <div className="header-actions">
          <Link to="/cart" className="cart-icon">
            🛒 Cart
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Header;
```

### 5. Updated CSS for Router Layout
```css
/* Router layout styles */
.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Header navigation styles */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
  text-decoration: none;
}

.main-navigation {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
}

.header-actions {
  display: flex;
  align-items: center;
}

.cart-icon {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.cart-icon:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Page layouts */
.home-page,
.products-page,
.cart-page,
.checkout-page,
.order-confirmation-page,
.not-found-page {
  min-height: 60vh;
  padding: 2rem 0;
}

.products-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.filters-sidebar {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  height: fit-content;
}

.products-grid {
  min-height: 400px;
}

.placeholder-products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.product-placeholder {
  background: #f0f0f0;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  border: 2px dashed #ccc;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  margin-top: 2rem;
}

.cart-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  height: fit-content;
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .main-navigation {
    gap: 1rem;
  }
  
  .products-content,
  .cart-content,
  .checkout-content {
    grid-template-columns: 1fr;
  }
  
  .main-content {
    padding: 0.5rem;
  }
}

/* Buttons and links */
.cta-button,
.checkout-button,
.continue-shopping,
.home-link {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.cta-button:hover,
.checkout-button:hover,
.continue-shopping:hover,
.home-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}
```

## Implementation Steps

### 1. Update App.jsx with Router Configuration
- Replace current App.jsx content with router-based structure
- Import necessary React Router components
- Configure route definitions for all main pages
- Wrap application in BrowserRouter

### 2. Create Page Components Directory Structure
- Create `src/pages/` directory
- Create placeholder page components (Home, Products, Cart, Checkout, OrderConfirmation, NotFound)
- Implement basic structure and content for each page
- Add proper imports and exports

### 3. Create Header Component with Navigation
- Create `src/components/common/` directory if not exists
- Implement Header component with navigation links
- Add active link highlighting
- Integrate cart icon and branding

### 4. Update CSS for Router Layout
- Add styles for header navigation
- Create responsive grid layouts for different pages
- Style navigation links and active states
- Ensure mobile responsiveness

### 5. Test Router Functionality
- Verify navigation between pages works
- Check that URLs update correctly
- Test back/forward browser buttons
- Validate responsive design on mobile

## Router Features

### 1. React Router v6 Features Used
- **BrowserRouter**: Clean URLs without hash
- **Routes & Route**: Declarative route configuration
- **Link**: Navigation with router awareness
- **useLocation**: Active link detection
- **useParams**: URL parameter extraction
- **Navigate**: Programmatic navigation (for future use)

### 2. Navigation Patterns
- **Header Navigation**: Persistent navigation across all pages
- **Active Link Highlighting**: Visual feedback for current page
- **Breadcrumb Ready**: Structure supports breadcrumb implementation
- **Mobile Navigation**: Responsive navigation for mobile devices

### 3. Route Organization
- **Logical Structure**: Routes mirror user workflow
- **Parameter Support**: Dynamic routes for order confirmation
- **404 Handling**: Catch-all route for non-existent pages
- **Future Extensibility**: Easy to add new routes

## Testing Strategy

### 1. Manual Navigation Testing
- Click through all navigation links
- Verify URL changes correspond to page content
- Test browser back/forward buttons
- Check direct URL access

### 2. Responsive Testing
- Test navigation on mobile devices
- Verify hamburger menu (if implemented)
- Check touch-friendly link sizes
- Validate responsive layouts

### 3. Accessibility Testing
- Verify keyboard navigation
- Check screen reader compatibility
- Test focus management
- Validate ARIA labels

## Future Integration Points

### 1. State Management Integration
- Router state integration with React Context
- Navigation state persistence
- Cart state across route changes
- User authentication state

### 2. API Integration
- Route-based data fetching
- Protected routes for authenticated pages
- Dynamic route generation from API data
- Error boundary integration

### 3. Performance Optimization
- Code splitting by route
- Lazy loading of page components
- Preloading of critical routes
- Bundle size optimization

## Success Criteria
- React Router navigation works between placeholder pages
- URLs update correctly when navigating
- Active link highlighting functions properly
- Mobile responsive navigation works
- All placeholder pages render without errors
- Header navigation is consistent across all routes
- 404 page displays for invalid routes
- Browser back/forward buttons work correctly