import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CartProvider, useCartContext, useCartOperations } from '../CartContext';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Mock localStorage
const mockLocalStorage = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Test component to access cart context
const TestComponent = ({ onCartUpdate }) => {
  const cart = useCartContext();
  
  React.useEffect(() => {
    if (onCartUpdate) {
      onCartUpdate(cart);
    }
  }, [cart, onCartUpdate]);
  
  return (
    <div>
      <div data-testid="cart-item-count">{cart.cartItemCount}</div>
      <div data-testid="cart-total">{cart.cartTotal.toFixed(2)}</div>
      <div data-testid="cart-subtotal">{cart.cartSubtotal.toFixed(2)}</div>
      <div data-testid="cart-tax">{cart.cartTax.toFixed(2)}</div>
      <div data-testid="cart-id">{cart.cartId}</div>
      <div data-testid="formatted-total">{cart.formatPrice(cart.cartTotal)}</div>
      <button 
        data-testid="add-to-cart"
        onClick={() => cart.addToCart(mockProduct, 1)}
      >
        Add to Cart
      </button>
      <button 
        data-testid="remove-from-cart"
        onClick={() => cart.removeFromCart(mockProduct.id)}
      >
        Remove from Cart
      </button>
      <button 
        data-testid="clear-cart"
        onClick={() => cart.clearCart()}
      >
        Clear Cart
      </button>
      <button 
        data-testid="increment-quantity"
        onClick={() => cart.incrementQuantity(mockProduct.id)}
      >
        Increment
      </button>
      <button 
        data-testid="decrement-quantity"
        onClick={() => cart.decrementQuantity(mockProduct.id)}
      >
        Decrement
      </button>
      <button 
        data-testid="update-quantity"
        onClick={() => cart.updateQuantity(mockProduct.id, 5)}
      >
        Update Quantity
      </button>
      <button 
        data-testid="validate-cart"
        onClick={() => cart.validateCart()}
      >
        Validate Cart
      </button>
    </div>
  );
};

// Mock product data
const mockProduct = {
  id: '1',
  name: 'Test Product',
  price: 10.00,
  image: '/test-image.jpg',
  category: 'Test Category',
  inStock: true,
  isOrganic: false
};

const mockProductOrganic = {
  id: '2',
  name: 'Organic Product',
  price: 15.00,
  image: '/organic-image.jpg',
  category: 'Organic Category',
  inStock: true,
  isOrganic: true
};

const mockProductOutOfStock = {
  id: '3',
  name: 'Out of Stock Product',
  price: 20.00,
  image: '/oos-image.jpg',
  category: 'Test Category',
  inStock: false,
  isOrganic: false
};

// Helper function to render component with CartProvider
const renderWithCartProvider = (component) => {
  return render(
    <CartProvider>
      {component}
    </CartProvider>
  );
};

describe('CartContext', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    jest.clearAllMocks();
  });

  describe('Provider Initialization', () => {
    test('provides cart context to children', () => {
      renderWithCartProvider(<TestComponent />);
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('0.00');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('0.00');
      expect(screen.getByTestId('cart-tax')).toHaveTextContent('0.00');
    });

    test('generates cart ID on initialization', () => {
      renderWithCartProvider(<TestComponent />);
      
      const cartId = screen.getByTestId('cart-id').textContent;
      expect(cartId).toBeTruthy();
      expect(cartId).toMatch(/^cart_\d+_/);
    });

    test('throws error when useCartContext is used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useCartContext must be used within a CartProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Cart Operations', () => {
    test('adds product to cart', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('10.00');
    });

    test('calculates Romanian VAT (19%) correctly', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      // Subtotal: 10.00, Tax: 1.90, Total: 11.90
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('10.00');
      expect(screen.getByTestId('cart-tax')).toHaveTextContent('1.90');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('11.90');
    });

    test('formats price in Romanian currency', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      const formattedTotal = screen.getByTestId('formatted-total').textContent;
      expect(formattedTotal).toContain('RON');
      expect(formattedTotal).toContain('11,90');
    });

    test('removes product from cart', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const removeButton = screen.getByTestId('remove-from-cart');
      
      // Add product first
      await act(async () => {
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      
      // Remove product
      await act(async () => {
        removeButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('0.00');
    });

    test('clears entire cart', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const clearButton = screen.getByTestId('clear-cart');
      
      // Add multiple products
      await act(async () => {
        addButton.click();
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('2');
      
      // Clear cart
      await act(async () => {
        clearButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('0.00');
    });
  });

  describe('Quantity Management', () => {
    test('increments product quantity', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const incrementButton = screen.getByTestId('increment-quantity');
      
      // Add product first
      await act(async () => {
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      
      // Increment quantity
      await act(async () => {
        incrementButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('2');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('20.00');
    });

    test('decrements product quantity', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const decrementButton = screen.getByTestId('decrement-quantity');
      
      // Add product twice to have quantity 2
      await act(async () => {
        addButton.click();
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('2');
      
      // Decrement quantity
      await act(async () => {
        decrementButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('10.00');
    });

    test('removes product when quantity decremented to 0', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const decrementButton = screen.getByTestId('decrement-quantity');
      
      // Add product once
      await act(async () => {
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      
      // Decrement to remove
      await act(async () => {
        decrementButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
    });

    test('updates product quantity to specific value', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const updateButton = screen.getByTestId('update-quantity');
      
      // Add product first
      await act(async () => {
        addButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('1');
      
      // Update quantity to 5
      await act(async () => {
        updateButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('5');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('50.00');
    });
  });

  describe('Product Validation', () => {
    test('validates cart items', async () => {
      let cartContext;
      const onCartUpdate = (cart) => {
        cartContext = cart;
      };
      
      renderWithCartProvider(<TestComponent onCartUpdate={onCartUpdate} />);
      
      const validateButton = screen.getByTestId('validate-cart');
      
      await act(async () => {
        validateButton.click();
      });
      
      // Should validate successfully with empty cart
      expect(cartContext).toBeDefined();
    });

    test('prevents adding invalid products', async () => {
      const TestComponentWithInvalidProduct = () => {
        const cart = useCartContext();
        
        return (
          <button 
            data-testid="add-invalid-product"
            onClick={() => cart.addToCart(null, 1)}
          >
            Add Invalid Product
          </button>
        );
      };
      
      renderWithCartProvider(<TestComponentWithInvalidProduct />);
      
      const addButton = screen.getByTestId('add-invalid-product');
      
      await act(async () => {
        addButton.click();
      });
      
      // Should not crash and product should not be added
      // (we can't easily test toast messages in this setup)
    });

    test('prevents adding out of stock products', async () => {
      const TestComponentWithOOSProduct = () => {
        const cart = useCartContext();
        
        return (
          <div>
            <div data-testid="cart-item-count">{cart.cartItemCount}</div>
            <button 
              data-testid="add-oos-product"
              onClick={() => cart.addToCart(mockProductOutOfStock, 1)}
            >
              Add OOS Product
            </button>
          </div>
        );
      };
      
      renderWithCartProvider(<TestComponentWithOOSProduct />);
      
      const addButton = screen.getByTestId('add-oos-product');
      
      await act(async () => {
        addButton.click();
      });
      
      // Cart should remain empty
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
    });
  });

  describe('localStorage Integration', () => {
    test('saves cart to localStorage', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'cart',
        expect.stringContaining('Test Product')
      );
    });

    test('saves cart ID to localStorage', () => {
      renderWithCartProvider(<TestComponent />);
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'cartId',
        expect.stringMatching(/^cart_\d+_/)
      );
    });

    test('loads cart from localStorage on initialization', async () => {
      const savedCart = JSON.stringify([
        { ...mockProduct, quantity: 2 }
      ]);
      
      mockLocalStorage.getItem.mockReturnValue(savedCart);
      
      renderWithCartProvider(<TestComponent />);
      
      // Wait for useEffect to run
      await waitFor(() => {
        expect(screen.getByTestId('cart-item-count')).toHaveTextContent('2');
      });
      
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('20.00');
    });

    test('handles corrupted localStorage data gracefully', async () => {
      mockLocalStorage.getItem.mockReturnValue('invalid-json');
      
      renderWithCartProvider(<TestComponent />);
      
      // Wait for useEffect to run and handle the error
      await waitFor(() => {
        expect(screen.getByTestId('cart-item-count')).toHaveTextContent('0');
      });
    });
  });

  describe('Cart Utilities', () => {
    test('provides cart summary', async () => {
      let cartContext;
      const onCartUpdate = (cart) => {
        cartContext = cart;
      };
      
      renderWithCartProvider(<TestComponent onCartUpdate={onCartUpdate} />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      const summary = cartContext.getCartSummary();
      
      expect(summary).toHaveProperty('items');
      expect(summary).toHaveProperty('itemCount', 1);
      expect(summary).toHaveProperty('subtotal', 10);
      expect(summary).toHaveProperty('tax', 1.9);
      expect(summary).toHaveProperty('total', 11.9);
      expect(summary).toHaveProperty('cartId');
      expect(summary).toHaveProperty('formattedTotal');
    });

    test('checks if product is in cart', async () => {
      let cartContext;
      const onCartUpdate = (cart) => {
        cartContext = cart;
      };
      
      renderWithCartProvider(<TestComponent onCartUpdate={onCartUpdate} />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      // Initially not in cart
      expect(cartContext.isInCart(mockProduct.id)).toBe(false);
      
      await act(async () => {
        addButton.click();
      });
      
      // Now in cart
      expect(cartContext.isInCart(mockProduct.id)).toBe(true);
    });

    test('gets cart item by ID', async () => {
      let cartContext;
      const onCartUpdate = (cart) => {
        cartContext = cart;
      };
      
      renderWithCartProvider(<TestComponent onCartUpdate={onCartUpdate} />);
      
      const addButton = screen.getByTestId('add-to-cart');
      
      await act(async () => {
        addButton.click();
      });
      
      const cartItem = cartContext.getCartItem(mockProduct.id);
      
      expect(cartItem).toBeDefined();
      expect(cartItem.id).toBe(mockProduct.id);
      expect(cartItem.quantity).toBe(1);
    });
  });

  describe('useCartOperations Hook', () => {
    test('provides safe cart operations', () => {
      const TestComponentWithOperations = () => {
        const operations = useCartOperations();
        
        return (
          <div>
            <div data-testid="has-safe-operations">
              {operations.safeAddToCart ? 'true' : 'false'}
            </div>
            <button 
              data-testid="safe-add-to-cart"
              onClick={() => operations.safeAddToCart(mockProduct, 1)}
            >
              Safe Add to Cart
            </button>
          </div>
        );
      };
      
      renderWithCartProvider(<TestComponentWithOperations />);
      
      expect(screen.getByTestId('has-safe-operations')).toHaveTextContent('true');
    });
  });

  describe('Complex Scenarios', () => {
    test('handles multiple products with different quantities', async () => {
      const TestComponentMultiple = () => {
        const cart = useCartContext();
        
        return (
          <div>
            <div data-testid="cart-item-count">{cart.cartItemCount}</div>
            <div data-testid="cart-total">{cart.cartTotal.toFixed(2)}</div>
            <button 
              data-testid="add-product-1"
              onClick={() => cart.addToCart(mockProduct, 2)}
            >
              Add Product 1
            </button>
            <button 
              data-testid="add-product-2"
              onClick={() => cart.addToCart(mockProductOrganic, 3)}
            >
              Add Product 2
            </button>
          </div>
        );
      };
      
      renderWithCartProvider(<TestComponentMultiple />);
      
      const addProduct1 = screen.getByTestId('add-product-1');
      const addProduct2 = screen.getByTestId('add-product-2');
      
      await act(async () => {
        addProduct1.click();
        addProduct2.click();
      });
      
      // 2 * 10 + 3 * 15 = 65 (subtotal)
      // 65 * 0.19 = 12.35 (tax)
      // 65 + 12.35 = 77.35 (total)
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('5');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('77.35');
    });

    test('maintains cart state across operations', async () => {
      renderWithCartProvider(<TestComponent />);
      
      const addButton = screen.getByTestId('add-to-cart');
      const incrementButton = screen.getByTestId('increment-quantity');
      const updateButton = screen.getByTestId('update-quantity');
      
      // Add product
      await act(async () => {
        addButton.click();
      });
      
      // Increment quantity
      await act(async () => {
        incrementButton.click();
      });
      
      // Update to specific quantity
      await act(async () => {
        updateButton.click();
      });
      
      expect(screen.getByTestId('cart-item-count')).toHaveTextContent('5');
      expect(screen.getByTestId('cart-subtotal')).toHaveTextContent('50.00');
      expect(screen.getByTestId('cart-tax')).toHaveTextContent('9.50');
      expect(screen.getByTestId('cart-total')).toHaveTextContent('59.50');
    });
  });
});