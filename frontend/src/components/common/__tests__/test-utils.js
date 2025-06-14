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