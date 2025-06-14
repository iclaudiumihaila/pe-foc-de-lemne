import React, { createContext, useContext, useEffect } from 'react';
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
  
  // Initialize cart validation on mount
  useEffect(() => {
    const initializeCart = async () => {
      try {
        await cartData.validateCart();
      } catch (error) {
        console.error('Error initializing cart:', error);
      }
    };
    
    initializeCart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Listen for storage changes to sync across tabs
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'cart' && e.newValue !== e.oldValue) {
        // Cart was updated in another tab - reload the page to sync
        window.location.reload();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);
  
  return (
    <CartContext.Provider value={cartData}>
      {children}
    </CartContext.Provider>
  );
};

// Higher-order component for cart integration
export const withCart = (Component) => {
  return function CartWrappedComponent(props) {
    const cartContext = useCartContext();
    return <Component {...props} cart={cartContext} />;
  };
};

// Custom hook for cart operations with error handling
export const useCartOperations = () => {
  const cart = useCartContext();
  
  const safeAddToCart = async (product, quantity = 1) => {
    try {
      cart.addToCart(product, quantity);
      return { success: true };
    } catch (error) {
      console.error('Error adding to cart:', error);
      return { success: false, error: error.message };
    }
  };
  
  const safeClearCart = async () => {
    try {
      cart.clearCart();
      return { success: true };
    } catch (error) {
      console.error('Error clearing cart:', error);
      return { success: false, error: error.message };
    }
  };
  
  return {
    ...cart,
    safeAddToCart,
    safeClearCart
  };
};