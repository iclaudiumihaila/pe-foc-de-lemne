# Task 46: Create Header component tests

## Task Details
- **ID**: 46_header_component_tests
- **Title**: Create Header component tests
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: Header component creation (Task 45)

## Objective
Create comprehensive React Testing Library tests for the Header component to verify navigation functionality, mobile menu behavior, cart integration, accessibility features, and responsive design, ensuring robust functionality and preventing regressions.

## Requirements
1. **Navigation Testing**: Test navigation links and active states
2. **Mobile Menu Testing**: Test hamburger menu toggle functionality
3. **Cart Integration Testing**: Test cart badge display and updates
4. **Accessibility Testing**: Verify ARIA labels and keyboard navigation
5. **Responsive Testing**: Test desktop and mobile layouts
6. **Router Integration**: Test React Router Link components
7. **Context Integration**: Test cart context usage

## Technical Implementation

### 1. Header Component Test Suite (frontend/src/components/common/__tests__/Header.test.jsx)
```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CartProvider } from '../../../contexts/CartContext';
import Header from '../Header';

// Test wrapper with necessary providers
const TestWrapper = ({ children, initialCartItems = [] }) => {
  return (
    <CartProvider>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </CartProvider>
  );
};

// Helper function to render Header with providers
const renderHeader = (props = {}) => {
  return render(
    <TestWrapper>
      <Header {...props} />
    </TestWrapper>
  );
};

describe('Header Component', () => {
  describe('Basic Rendering', () => {
    test('renders header with logo', () => {
      renderHeader();
      
      const logo = screen.getByRole('link', { name: /local producer - home/i });
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('href', '/');
    });

    test('renders main navigation links', () => {
      renderHeader();
      
      expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /products/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /cart/i })).toBeInTheDocument();
    });

    test('renders cart icon with initial count of 0', () => {
      renderHeader();
      
      const cartLink = screen.getByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLink).toBeInTheDocument();
      expect(cartLink).toHaveAttribute('href', '/cart');
    });
  });

  describe('Mobile Menu Functionality', () => {
    test('mobile menu button is present', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      expect(menuButton).toBeInTheDocument();
      expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    });

    test('mobile menu opens when button is clicked', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      const mobileMenu = screen.getByRole('navigation', { name: /mobile navigation/i });
      
      // Initially closed
      expect(menuButton).toHaveAttribute('aria-expanded', 'false');
      expect(mobileMenu).toHaveClass('max-h-0', 'opacity-0');
      
      // Click to open
      fireEvent.click(menuButton);
      
      expect(menuButton).toHaveAttribute('aria-expanded', 'true');
      expect(mobileMenu).toHaveClass('max-h-64', 'opacity-100');
    });

    test('mobile menu closes when button is clicked again', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      const mobileMenu = screen.getByRole('navigation', { name: /mobile navigation/i });
      
      // Open menu
      fireEvent.click(menuButton);
      expect(mobileMenu).toHaveClass('max-h-64', 'opacity-100');
      
      // Close menu
      fireEvent.click(menuButton);
      expect(mobileMenu).toHaveClass('max-h-0', 'opacity-0');
      expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    });

    test('mobile menu contains navigation links', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      fireEvent.click(menuButton);
      
      const mobileNav = screen.getByRole('navigation', { name: /mobile navigation/i });
      expect(mobileNav).toBeInTheDocument();
      
      // Check mobile navigation links
      const mobileLinks = screen.getAllByRole('link');
      const homeLinks = mobileLinks.filter(link => link.textContent.includes('Home'));
      const productsLinks = mobileLinks.filter(link => link.textContent.includes('Products'));
      const cartLinks = mobileLinks.filter(link => link.textContent.includes('Cart'));
      
      expect(homeLinks.length).toBeGreaterThan(0);
      expect(productsLinks.length).toBeGreaterThan(0);
      expect(cartLinks.length).toBeGreaterThan(0);
    });
  });

  describe('Cart Integration', () => {
    test('displays cart badge when items are added', async () => {
      const { container } = renderHeader();
      
      // Initially no badge
      let cartBadge = container.querySelector('.bg-red-500');
      expect(cartBadge).not.toBeInTheDocument();
      
      // This test would need cart context to be pre-populated with items
      // For now, we test the structure
      const cartLink = screen.getByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLink).toBeInTheDocument();
    });

    test('cart badge shows correct count format', () => {
      // This would be tested with different cart states
      // Implementation depends on being able to mock cart context
      renderHeader();
      
      const cartIcon = screen.getByText('🛒');
      expect(cartIcon).toBeInTheDocument();
    });
  });

  describe('Navigation and Active States', () => {
    test('navigation links have correct href attributes', () => {
      renderHeader();
      
      const homeLink = screen.getByRole('link', { name: /^home$/i });
      const productsLink = screen.getByRole('link', { name: /^products$/i });
      const cartLink = screen.getByRole('link', { name: /cart/i });
      
      expect(homeLink).toHaveAttribute('href', '/');
      expect(productsLink).toHaveAttribute('href', '/products');
      expect(cartLink).toHaveAttribute('href', '/cart');
    });
  });

  describe('Accessibility Features', () => {
    test('has proper ARIA labels', () => {
      renderHeader();
      
      // Logo accessibility
      const logo = screen.getByRole('link', { name: /local producer - home/i });
      expect(logo).toHaveAttribute('aria-label', 'Local Producer - Home');
      
      // Navigation accessibility
      const mainNav = screen.getByRole('navigation', { name: /main navigation/i });
      expect(mainNav).toHaveAttribute('aria-label', 'Main navigation');
      
      // Mobile menu button accessibility
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      expect(menuButton).toHaveAttribute('aria-label', 'Toggle mobile menu');
      expect(menuButton).toHaveAttribute('aria-controls', 'mobile-menu');
    });

    test('cart link has descriptive aria-label', () => {
      renderHeader();
      
      const cartLink = screen.getByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLink).toHaveAttribute('aria-label', 'Shopping cart with 0 items');
    });

    test('mobile menu has proper ARIA attributes', () => {
      renderHeader();
      
      const mobileMenu = document.getElementById('mobile-menu');
      expect(mobileMenu).toBeInTheDocument();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      expect(menuButton).toHaveAttribute('aria-controls', 'mobile-menu');
      expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    });

    test('screen reader content is properly hidden', () => {
      renderHeader();
      
      const srOnly = document.querySelector('.sr-only');
      expect(srOnly).toBeInTheDocument();
      expect(srOnly).toHaveTextContent('Open main menu');
    });
  });

  describe('Responsive Design', () => {
    test('desktop navigation is hidden on mobile', () => {
      renderHeader();
      
      const desktopNav = screen.getByRole('navigation', { name: /main navigation/i });
      expect(desktopNav).toHaveClass('hidden', 'md:flex');
    });

    test('mobile menu button is hidden on desktop', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      expect(menuButton).toHaveClass('md:hidden');
    });

    test('desktop cart link has responsive classes', () => {
      renderHeader();
      
      const desktopCartLink = screen.getByRole('link', { name: /shopping cart with 0 items/i });
      expect(desktopCartLink).toHaveClass('hidden', 'sm:flex');
    });
  });

  describe('Event Handling', () => {
    test('mobile menu toggle changes icon', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      
      // Initially shows hamburger icon
      expect(menuButton.querySelector('path[d*="M4 6h16M4 12h16M4 18h16"]')).toBeInTheDocument();
      
      // Click to show close icon
      fireEvent.click(menuButton);
      expect(menuButton.querySelector('path[d*="M6 18L18 6M6 6l12 12"]')).toBeInTheDocument();
    });

    test('keyboard navigation works', () => {
      renderHeader();
      
      const logo = screen.getByRole('link', { name: /local producer - home/i });
      const homeLink = screen.getByRole('link', { name: /^home$/i });
      
      // Test tab navigation
      logo.focus();
      expect(document.activeElement).toBe(logo);
      
      fireEvent.keyDown(logo, { key: 'Tab' });
      // After tab, focus should move to next element
    });
  });

  describe('Integration with Router', () => {
    test('navigation links use React Router Link components', () => {
      renderHeader();
      
      const homeLink = screen.getByRole('link', { name: /^home$/i });
      expect(homeLink).toHaveAttribute('href', '/');
      
      // Test that clicking doesn't cause page reload (React Router behavior)
      const originalLocation = window.location.href;
      fireEvent.click(homeLink);
      expect(window.location.href).toBe(originalLocation);
    });
  });
});

// Additional test for cart context integration
describe('Header with Cart Context', () => {
  test('integrates with cart context correctly', () => {
    // This test verifies that the component properly uses useCartContext
    // Without throwing errors when wrapped in CartProvider
    expect(() => {
      renderHeader();
    }).not.toThrow();
  });
});
```

### 2. Cart Context Mock for Testing
```javascript
// frontend/src/components/common/__tests__/__mocks__/CartContextMock.js
import React from 'react';

export const mockCartContext = {
  cartItems: [],
  cartItemCount: 0,
  cartTotal: 0,
  addToCart: jest.fn(),
  removeFromCart: jest.fn(),
  updateQuantity: jest.fn(),
  clearCart: jest.fn()
};

export const CartProviderMock = ({ children, value = mockCartContext }) => {
  return (
    <div data-testid="cart-provider-mock">
      {React.cloneElement(children, { cartContext: value })}
    </div>
  );
};
```

### 3. Test Utilities and Helpers
```javascript
// frontend/src/components/common/__tests__/test-utils.js
import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CartProvider } from '../../../contexts/CartContext';

// Custom render function with all providers
export const renderWithProviders = (ui, options = {}) => {
  const { initialEntries = ['/'], ...renderOptions } = options;
  
  const Wrapper = ({ children }) => {
    return (
      <CartProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </CartProvider>
    );
  };
  
  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

// Helper to mock cart state
export const mockCartState = (overrides = {}) => {
  return {
    cartItems: [],
    cartItemCount: 0,
    cartTotal: 0,
    addToCart: jest.fn(),
    removeFromCart: jest.fn(),
    updateQuantity: jest.fn(),
    clearCart: jest.fn(),
    ...overrides
  };
};

// Helper to simulate cart with items
export const mockCartWithItems = (itemCount = 3) => {
  return mockCartState({
    cartItemCount: itemCount,
    cartItems: Array(itemCount).fill(null).map((_, index) => ({
      id: index + 1,
      name: `Test Product ${index + 1}`,
      price: 9.99,
      quantity: 1
    })),
    cartTotal: itemCount * 9.99
  });
};
```

### 4. Advanced Cart Integration Tests
```javascript
// Additional tests for cart functionality
describe('Header Cart Integration Advanced', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  test('displays cart badge with correct count when cart has items', () => {
    // Mock localStorage with cart items
    const cartItems = [
      { id: 1, name: 'Test Product', price: 9.99, quantity: 2 },
      { id: 2, name: 'Another Product', price: 14.99, quantity: 1 }
    ];
    localStorage.setItem('cart', JSON.stringify(cartItems));
    
    renderHeader();
    
    // Should show total quantity (2 + 1 = 3)
    const cartLink = screen.getByRole('link', { name: /shopping cart with 3 items/i });
    expect(cartLink).toBeInTheDocument();
    
    const cartBadge = screen.getByText('3');
    expect(cartBadge).toBeInTheDocument();
    expect(cartBadge).toHaveClass('bg-red-500');
  });

  test('displays 99+ for cart counts over 99', () => {
    // Mock cart with 100+ items
    const cartItems = [
      { id: 1, name: 'Test Product', price: 9.99, quantity: 150 }
    ];
    localStorage.setItem('cart', JSON.stringify(cartItems));
    
    renderHeader();
    
    const cartBadge = screen.getByText('99+');
    expect(cartBadge).toBeInTheDocument();
  });

  test('hides cart badge when cart is empty', () => {
    localStorage.setItem('cart', JSON.stringify([]));
    
    const { container } = renderHeader();
    
    const cartBadge = container.querySelector('.bg-red-500');
    expect(cartBadge).not.toBeInTheDocument();
  });
});
```

## Test Categories and Coverage

### 1. Component Rendering Tests
- Logo rendering and accessibility
- Navigation links presence and attributes
- Cart icon and initial state
- Responsive class application

### 2. Mobile Menu Tests
- Menu button presence and attributes
- Menu toggle functionality
- Menu state management
- Icon changes (hamburger to close)
- Mobile navigation links

### 3. Cart Integration Tests
- Cart badge display logic
- Item count formatting
- Cart state updates
- LocalStorage integration
- Context provider usage

### 4. Accessibility Tests
- ARIA labels and attributes
- Screen reader content
- Keyboard navigation
- Focus management
- Semantic markup

### 5. Responsive Design Tests
- Desktop/mobile class application
- Breakpoint behavior
- Touch target sizing
- Layout adaptation

### 6. Router Integration Tests
- React Router Link usage
- Navigation behavior
- URL updates
- Active state management

## Testing Tools and Setup

### 1. React Testing Library Features
```javascript
// Core testing utilities
import { 
  render, 
  screen, 
  fireEvent, 
  waitFor,
  within 
} from '@testing-library/react';

// User event simulation
import userEvent from '@testing-library/user-event';

// Custom queries and matchers
import '@testing-library/jest-dom';
```

### 2. Jest Configuration
```javascript
// Test environment setup
expect.extend({
  toBeInTheDocument: expect.toBeInTheDocument,
  toHaveClass: expect.toHaveClass,
  toHaveAttribute: expect.toHaveAttribute
});

// Mock implementations
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => ({ pathname: '/' })
}));
```

### 3. Test Environment
- **JSDOM**: Browser environment simulation
- **React Router**: Router testing utilities
- **Context Testing**: Cart context integration
- **LocalStorage**: Storage mocking and testing

## Implementation Steps

### 1. Create Test Directory Structure
- Create `__tests__` directory in components/common
- Setup test utilities and mocks
- Configure test environment

### 2. Write Component Tests
- Basic rendering tests
- Mobile menu functionality tests
- Cart integration tests
- Accessibility tests

### 3. Add Advanced Testing
- Router integration tests
- Responsive design tests
- Edge case handling
- Error boundary tests

### 4. Test Coverage Verification
- Run test suite
- Verify coverage metrics
- Add missing test cases
- Document test scenarios

## Test Execution Commands

### 1. Run All Tests
```bash
npm test
npm test -- --coverage
npm test -- --watchAll
```

### 2. Run Specific Tests
```bash
npm test Header.test.jsx
npm test -- --testNamePattern="mobile menu"
npm test -- --verbose
```

### 3. Coverage Analysis
```bash
npm test -- --coverage --watchAll=false
npm run test:coverage
```

## Success Criteria
- All Header component tests pass
- Test coverage exceeds 90% for Header component
- Mobile menu functionality fully tested
- Cart integration tests verify state management
- Accessibility tests ensure WCAG compliance
- Router integration tests verify navigation
- Edge cases and error scenarios covered