import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { CartProvider } from '../../../contexts/CartContext';
import Header from '../Header';

// Test wrapper with necessary providers
const TestWrapper = ({ children }) => {
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
      
      expect(screen.getByRole('link', { name: /^home$/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /^products$/i })).toBeInTheDocument();
      // Cart link appears multiple times (desktop and mobile), so we check for at least one
      expect(screen.getAllByRole('link', { name: /cart/i }).length).toBeGreaterThan(0);
    });

    test('renders cart icon with initial count of 0', () => {
      renderHeader();
      
      const cartLinks = screen.getAllByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLinks.length).toBeGreaterThan(0);
      cartLinks.forEach(link => {
        expect(link).toHaveAttribute('href', '/cart');
      });
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
      const mobileMenu = document.getElementById('mobile-menu');
      
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
      const mobileMenu = document.getElementById('mobile-menu');
      
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
      
      // Check mobile navigation links within the mobile nav
      const mobileHomeLink = screen.getByRole('link', { name: /🏠 home/i });
      const mobileProductsLink = screen.getByRole('link', { name: /🛍️ products/i });
      
      expect(mobileHomeLink).toBeInTheDocument();
      expect(mobileProductsLink).toBeInTheDocument();
    });
  });

  describe('Cart Integration', () => {
    test('displays cart icon without badge initially', () => {
      const { container } = renderHeader();
      
      // Initially no badge
      const cartBadge = container.querySelector('.bg-red-500');
      expect(cartBadge).not.toBeInTheDocument();
      
      const cartLinks = screen.getAllByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLinks.length).toBeGreaterThan(0);
    });

    test('cart icon is present in header', () => {
      renderHeader();
      
      const cartIcons = screen.getAllByText('🛒');
      expect(cartIcons.length).toBeGreaterThan(0);
    });
  });

  describe('Navigation and Active States', () => {
    test('navigation links have correct href attributes', () => {
      renderHeader();
      
      const homeLink = screen.getByRole('link', { name: /^home$/i });
      const productsLink = screen.getByRole('link', { name: /^products$/i });
      const cartLinks = screen.getAllByRole('link', { name: /cart/i });
      
      expect(homeLink).toHaveAttribute('href', '/');
      expect(productsLink).toHaveAttribute('href', '/products');
      // All cart links should point to /cart
      cartLinks.forEach(link => {
        expect(link).toHaveAttribute('href', '/cart');
      });
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
      
      const cartLinks = screen.getAllByRole('link', { name: /shopping cart with 0 items/i });
      expect(cartLinks.length).toBeGreaterThan(0);
      cartLinks.forEach(link => {
        expect(link).toHaveAttribute('aria-label', 'Shopping cart with 0 items');
      });
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
      
      const cartLinks = screen.getAllByRole('link', { name: /shopping cart with 0 items/i });
      // Find the desktop cart link (has hidden sm:flex classes)
      const desktopCartLink = cartLinks.find(link => 
        link.className.includes('hidden') && link.className.includes('sm:flex')
      );
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

    test('menu button has proper type attribute', () => {
      renderHeader();
      
      const menuButton = screen.getByRole('button', { name: /toggle mobile menu/i });
      expect(menuButton).toHaveAttribute('type', 'button');
    });
  });

  describe('Integration with Router', () => {
    test('navigation links use React Router Link components', () => {
      renderHeader();
      
      const homeLink = screen.getByRole('link', { name: /^home$/i });
      expect(homeLink).toHaveAttribute('href', '/');
      
      // Test that links are properly rendered as anchor tags with href
      const productsLink = screen.getByRole('link', { name: /^products$/i });
      expect(productsLink).toHaveAttribute('href', '/products');
    });
  });

  describe('Header Structure', () => {
    test('header has proper semantic structure', () => {
      renderHeader();
      
      const header = document.querySelector('header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('bg-gradient-primary', 'text-white', 'sticky', 'top-0', 'z-50');
    });

    test('header contains brand emoji', () => {
      renderHeader();
      
      // The emoji is part of the logo text "🌱 Local Producer"
      const logoElement = screen.getByRole('link', { name: /local producer - home/i });
      expect(logoElement).toHaveTextContent('🌱 Local Producer');
    });

    test('header has shadow styling', () => {
      renderHeader();
      
      const header = document.querySelector('header');
      expect(header).toHaveClass('shadow-lg');
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

  test('renders without crashing when context is available', () => {
    renderHeader();
    
    const header = document.querySelector('header');
    expect(header).toBeInTheDocument();
  });
});