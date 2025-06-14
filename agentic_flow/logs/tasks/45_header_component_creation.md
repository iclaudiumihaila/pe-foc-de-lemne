# Task 45: Create Header component

## Task Details
- **ID**: 45_header_component_creation
- **Title**: Create Header component
- **Priority**: High
- **Estimate**: 25 minutes
- **Dependencies**: Tailwind CSS configuration (Task 43)

## Objective
Enhance the existing Header component with responsive design, improved navigation, cart functionality with item count display, mobile menu toggle, and integration with API services for dynamic cart state management.

## Requirements
1. **Responsive Design**: Mobile-first header with collapsible navigation
2. **Cart Integration**: Cart icon with dynamic item count from API
3. **Navigation**: Active state management and smooth transitions
4. **Mobile Menu**: Hamburger menu toggle for mobile devices
5. **Brand Identity**: Logo/brand name with proper styling
6. **Accessibility**: Keyboard navigation and screen reader support
7. **Performance**: Efficient re-rendering and state management

## Technical Implementation

### 1. Enhanced Header Component Structure
```javascript
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import orderService from '../../services/orderService';

function Header() {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [cartItemCount, setCartItemCount] = useState(0);
  
  // Mobile menu toggle
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);
  
  // Active navigation helper
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  // Cart count simulation (will be replaced with real cart state)
  useEffect(() => {
    // Simulate cart item count - replace with actual cart state
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const cartItems = JSON.parse(savedCart);
        const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
        setCartItemCount(totalItems);
      } catch (error) {
        console.error('Error parsing cart data:', error);
        setCartItemCount(0);
      }
    }
  }, []);
  
  return (
    <header className="bg-gradient-primary text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Brand */}
          <Link 
            to="/" 
            className="text-xl font-bold hover:opacity-90 transition-opacity duration-200"
            aria-label="Local Producer - Home"
          >
            🌱 Local Producer
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-1" aria-label="Main navigation">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/') ? 'page' : undefined}
            >
              Home
            </Link>
            <Link 
              to="/products" 
              className={`nav-link ${isActive('/products') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/products') ? 'page' : undefined}
            >
              Products
            </Link>
            <Link 
              to="/cart" 
              className={`nav-link ${isActive('/cart') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/cart') ? 'page' : undefined}
            >
              Cart
            </Link>
          </nav>
          
          {/* Desktop Cart & Mobile Menu Button */}
          <div className="flex items-center space-x-4">
            {/* Desktop Cart Icon */}
            <Link 
              to="/cart" 
              className="hidden sm:flex nav-link items-center space-x-2 relative"
              aria-label={`Shopping cart with ${cartItemCount} items`}
            >
              <div className="relative">
                <span className="text-xl">🛒</span>
                {cartItemCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                    {cartItemCount > 99 ? '99+' : cartItemCount}
                  </span>
                )}
              </div>
              <span className="hidden lg:inline">Cart</span>
            </Link>
            
            {/* Mobile Menu Button */}
            <button
              type="button"
              onClick={toggleMobileMenu}
              className="md:hidden nav-link p-2"
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-menu"
              aria-label="Toggle mobile menu"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
        
        {/* Mobile Navigation Menu */}
        <div 
          id="mobile-menu"
          className={`md:hidden transition-all duration-300 ease-in-out ${
            isMobileMenuOpen 
              ? 'max-h-64 opacity-100 border-t border-white border-opacity-20 pt-4 pb-2' 
              : 'max-h-0 opacity-0 overflow-hidden'
          }`}
        >
          <nav className="flex flex-col space-y-2" aria-label="Mobile navigation">
            <Link 
              to="/" 
              className={`nav-link text-center py-3 ${isActive('/') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/') ? 'page' : undefined}
            >
              🏠 Home
            </Link>
            <Link 
              to="/products" 
              className={`nav-link text-center py-3 ${isActive('/products') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/products') ? 'page' : undefined}
            >
              🛍️ Products
            </Link>
            <Link 
              to="/cart" 
              className={`nav-link text-center py-3 relative ${isActive('/cart') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/cart') ? 'page' : undefined}
              aria-label={`Shopping cart with ${cartItemCount} items`}
            >
              <div className="flex items-center justify-center space-x-2">
                <div className="relative">
                  <span>🛒</span>
                  {cartItemCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center font-bold">
                      {cartItemCount > 99 ? '99+' : cartItemCount}
                    </span>
                  )}
                </div>
                <span>Cart</span>
              </div>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;
```

### 2. Cart State Management Hook
```javascript
// frontend/src/hooks/useCart.js
import { useState, useEffect } from 'react';

export const useCart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [cartItemCount, setCartItemCount] = useState(0);
  const [cartTotal, setCartTotal] = useState(0);
  
  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const items = JSON.parse(savedCart);
        setCartItems(items);
      } catch (error) {
        console.error('Error loading cart:', error);
        setCartItems([]);
      }
    }
  }, []);
  
  // Update counts and totals when cart items change
  useEffect(() => {
    const itemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    setCartItemCount(itemCount);
    setCartTotal(total);
    
    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(cartItems));
  }, [cartItems]);
  
  const addToCart = (product, quantity = 1) => {
    setCartItems(prevItems => {
      const existingItem = prevItems.find(item => item.id === product.id);
      
      if (existingItem) {
        return prevItems.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        return [...prevItems, { ...product, quantity }];
      }
    });
  };
  
  const removeFromCart = (productId) => {
    setCartItems(prevItems => prevItems.filter(item => item.id !== productId));
  };
  
  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    setCartItems(prevItems =>
      prevItems.map(item =>
        item.id === productId
          ? { ...item, quantity }
          : item
      )
    );
  };
  
  const clearCart = () => {
    setCartItems([]);
  };
  
  return {
    cartItems,
    cartItemCount,
    cartTotal,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart
  };
};
```

### 3. Cart Context Provider
```javascript
// frontend/src/contexts/CartContext.js
import React, { createContext, useContext } from 'react';
import { useCart } from '../hooks/useCart';

const CartContext = createContext();

export const useCartContext = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCartContext must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const cartData = useCart();
  
  return (
    <CartContext.Provider value={cartData}>
      {children}
    </CartContext.Provider>
  );
};
```

### 4. Enhanced Tailwind CSS for Header
```css
/* Additional Tailwind component classes for Header */
@layer components {
  .header-nav-transition {
    @apply transition-all duration-300 ease-in-out;
  }
  
  .mobile-menu-slide {
    @apply transform transition-transform duration-300 ease-in-out;
  }
  
  .cart-badge {
    @apply absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold;
  }
  
  .nav-link-enhanced {
    @apply nav-link relative overflow-hidden;
  }
  
  .nav-link-enhanced::after {
    content: '';
    @apply absolute bottom-0 left-0 w-full h-0.5 bg-white transform scale-x-0 transition-transform duration-300 ease-in-out;
  }
  
  .nav-link-enhanced:hover::after,
  .nav-link-enhanced.active::after {
    @apply scale-x-100;
  }
}
```

## Implementation Steps

### 1. Enhance Existing Header Component
- Add mobile menu toggle functionality
- Implement cart item count display
- Add accessibility attributes
- Improve responsive design
- Add smooth animations

### 2. Create Cart State Management
- Implement useCart hook for cart state
- Add localStorage persistence
- Create cart context provider
- Add cart manipulation methods

### 3. Integrate with App Structure
- Wrap App with CartProvider
- Update Header to use cart context
- Add cart state to navigation
- Test cart functionality

### 4. Mobile Responsiveness
- Implement hamburger menu
- Add mobile-specific navigation
- Test touch interactions
- Verify accessibility on mobile

### 5. Testing and Verification
- Test desktop navigation
- Test mobile menu toggle
- Verify cart count updates
- Check accessibility compliance

## Features to Implement

### 1. Responsive Navigation
- **Desktop**: Horizontal navigation with active states
- **Mobile**: Collapsible hamburger menu
- **Tablet**: Hybrid approach with responsive breakpoints
- **Touch**: Touch-friendly navigation elements

### 2. Cart Functionality
- **Item Count**: Dynamic cart item count display
- **Badge**: Red notification badge for cart items
- **Persistence**: localStorage cart state persistence
- **Updates**: Real-time cart count updates

### 3. Accessibility Features
- **ARIA Labels**: Proper labeling for screen readers
- **Keyboard Navigation**: Tab-friendly navigation
- **Focus Management**: Visible focus indicators
- **Screen Reader**: Semantic markup for assistive technology

### 4. Animation and Transitions
- **Menu Toggle**: Smooth mobile menu transitions
- **Hover Effects**: Subtle hover animations
- **Active States**: Clear active page indicators
- **Loading States**: Smooth state transitions

## Integration Points

### 1. Router Integration
- React Router Link components
- Active route detection
- Navigation state management
- Route-based cart updates

### 2. API Integration
- Cart data from API services
- Order status integration
- User authentication preparation
- Real-time updates capability

### 3. State Management
- Cart context provider
- Local storage integration
- State persistence
- Cross-component state sharing

## Success Criteria
- Header component renders correctly on mobile and desktop
- Mobile menu toggle works smoothly
- Cart icon displays accurate item count
- Navigation active states work properly
- Accessibility standards are met
- Component is performant and responsive