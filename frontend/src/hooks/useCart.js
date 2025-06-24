import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import api from '../services/api';

export const useCart = () => {
  // Initialize cart from localStorage or sessionStorage
  const getInitialCart = () => {
    try {
      // Try localStorage first
      const savedCart = localStorage.getItem('cart');
      if (savedCart) {
        const items = JSON.parse(savedCart);
        if (Array.isArray(items) && items.length > 0) {
          console.log('Initializing cart from localStorage:', items);
          return items;
        }
      }
      
      // Fallback to sessionStorage
      const sessionCart = sessionStorage.getItem('cart');
      if (sessionCart) {
        const items = JSON.parse(sessionCart);
        if (Array.isArray(items) && items.length > 0) {
          console.log('Initializing cart from sessionStorage:', items);
          // Also save to localStorage for persistence
          localStorage.setItem('cart', sessionCart);
          return items;
        }
      }
    } catch (error) {
      console.error('Error parsing saved cart:', error);
    }
    console.log('No saved cart found, starting with empty cart');
    return [];
  };

  const [cartItems, setCartItems] = useState(getInitialCart);
  const [cartItemCount, setCartItemCount] = useState(0);
  const [cartTotal, setCartTotal] = useState(0);
  const [cartSubtotal, setCartSubtotal] = useState(0);
  const [cartTax, setCartTax] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [cartId, setCartId] = useState(null);
  
  // Generate or retrieve cart session ID (MongoDB ObjectId format)
  useEffect(() => {
    let sessionCartId = localStorage.getItem('cartId');
    if (!sessionCartId || !sessionCartId.match(/^[0-9a-fA-F]{24}$/)) {
      // Generate a valid MongoDB ObjectId (24 hex characters)
      const timestamp = Math.floor(Date.now() / 1000).toString(16).padStart(8, '0');
      const randomHex = Array.from({length: 16}, () => Math.floor(Math.random() * 16).toString(16)).join('');
      sessionCartId = timestamp + randomHex;
      localStorage.setItem('cartId', sessionCartId);
    }
    setCartId(sessionCartId);
  }, []);
  
  
  // Update counts and totals when cart items change
  useEffect(() => {
    const itemCount = cartItems.reduce((sum, item) => sum + (item.quantity || 0), 0);
    const subtotal = cartItems.reduce((sum, item) => {
      const price = parseFloat(item.price) || 0;
      const quantity = parseInt(item.quantity) || 0;
      return sum + (price * quantity);
    }, 0);
    
    // Calculate tax (19% VAT for Romania)
    const tax = subtotal * 0.19;
    const total = subtotal + tax;
    
    setCartItemCount(itemCount);
    setCartSubtotal(subtotal);
    setCartTax(tax);
    setCartTotal(total);
    
    // Save to both localStorage and sessionStorage for redundancy
    try {
      const cartData = JSON.stringify(cartItems);
      console.log('Saving cart to storage:', cartItems);
      localStorage.setItem('cart', cartData);
      sessionStorage.setItem('cart', cartData);
    } catch (error) {
      console.error('Error saving cart to storage:', error);
      toast.error('Eroare la salvarea cosului');
    }
  }, [cartItems]);
  
  // Format price for display
  const formatPrice = useCallback((price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  }, []);
  
  // Sync cart item to backend
  const syncCartItemToBackend = useCallback(async (item, sessionId) => {
    try {
      await api.post('/cart/', {
        product_id: item.id || item._id,
        quantity: item.quantity,
        session_id: sessionId
      });
      return true;
    } catch (error) {
      console.error('Error syncing cart item to backend:', error);
      return false;
    }
  }, []);
  
  // Add item to cart
  const addToCart = useCallback((product, quantity = 1) => {
    if (!product || !product.id) {
      toast.error('Produs invalid');
      return;
    }
    
    if (!product.inStock) {
      toast.error('Produsul nu este in stoc');
      return;
    }
    
    if (quantity <= 0) {
      toast.error('Cantitatea trebuie sa fie pozitiva');
      return;
    }
    
    setIsLoading(true);
    
    try {
      console.log('Adding to cart:', product);
      
      // First update local state
      setCartItems(prevItems => {
        const existingItem = prevItems.find(item => item.id === product.id);
        
        if (existingItem) {
          const newQuantity = existingItem.quantity + quantity;
          toast.success(`${product.name} - cantitate actualizata la ${newQuantity}`);
          
          return prevItems.map(item =>
            item.id === product.id
              ? { ...item, quantity: newQuantity }
              : item
          );
        } else {
          toast.success(`${product.name} adaugat in cos`);
          
          return [...prevItems, { 
            ...product, 
            quantity,
            addedAt: new Date().toISOString()
          }];
        }
      });
      
      // Sync to backend after state update
      if (cartId) {
        setTimeout(async () => {
          await syncCartItemToBackend({
            id: product.id,
            _id: product._id,
            quantity: quantity
          }, cartId);
        }, 100);
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error('Eroare la adaugarea in cos');
    } finally {
      setIsLoading(false);
    }
  }, [cartId, syncCartItemToBackend]);
  
  // Remove item from cart
  const removeFromCart = useCallback((productId) => {
    if (!productId) return;
    
    setCartItems(prevItems => {
      const item = prevItems.find(item => item.id === productId);
      if (item) {
        toast.success(`${item.name} eliminat din cos`);
      }
      return prevItems.filter(item => item.id !== productId);
    });
  }, []);
  
  // Update item quantity
  const updateQuantity = useCallback((productId, quantity) => {
    if (!productId) return;
    
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    setCartItems(prevItems => {
      const item = prevItems.find(item => item.id === productId);
      if (item) {
        toast.success(`${item.name} - cantitate actualizata`);
      }
      
      return prevItems.map(item =>
        item.id === productId
          ? { ...item, quantity: parseInt(quantity) }
          : item
      );
    });
  }, [removeFromCart]);
  
  // Increment item quantity
  const incrementQuantity = useCallback((productId) => {
    setCartItems(prevItems =>
      prevItems.map(item =>
        item.id === productId
          ? { ...item, quantity: item.quantity + 1 }
          : item
      )
    );
  }, []);
  
  // Decrement item quantity
  const decrementQuantity = useCallback((productId) => {
    setCartItems(prevItems =>
      prevItems.map(item => {
        if (item.id === productId) {
          const newQuantity = item.quantity - 1;
          return newQuantity > 0 ? { ...item, quantity: newQuantity } : null;
        }
        return item;
      }).filter(Boolean)
    );
  }, []);
  
  // Clear entire cart
  const clearCart = useCallback(() => {
    setCartItems([]);
    toast.success('Cosul a fost golit');
  }, []);
  
  // Get cart item by product ID
  const getCartItem = useCallback((productId) => {
    return cartItems.find(item => item.id === productId);
  }, [cartItems]);
  
  // Check if product is in cart
  const isInCart = useCallback((productId) => {
    return cartItems.some(item => item.id === productId);
  }, [cartItems]);
  
  // Get cart summary for checkout
  const getCartSummary = useCallback(() => {
    return {
      items: cartItems,
      itemCount: cartItemCount,
      subtotal: cartSubtotal,
      tax: cartTax,
      total: cartTotal,
      cartId: cartId,
      formattedSubtotal: formatPrice(cartSubtotal),
      formattedTax: formatPrice(cartTax),
      formattedTotal: formatPrice(cartTotal)
    };
  }, [cartItems, cartItemCount, cartSubtotal, cartTax, cartTotal, cartId, formatPrice]);
  
  // Validate cart items (check stock, prices, etc.)
  const validateCart = useCallback(async () => {
    // This would typically make an API call to validate items
    // For now, we'll do basic validation
    const invalidItems = cartItems.filter(item => 
      !item.id || !item.name || !item.price || item.quantity <= 0
    );
    
    if (invalidItems.length > 0) {
      console.warn('Invalid cart items found:', invalidItems);
      // Remove invalid items
      setCartItems(prevItems => 
        prevItems.filter(item => 
          item.id && item.name && item.price && item.quantity > 0
        )
      );
      toast.error('Unele produse din cos au fost eliminate (produse invalide)');
    }
    
    return invalidItems.length === 0;
  }, [cartItems]);
  
  return {
    // State
    cartItems,
    cartItemCount,
    cartTotal,
    cartSubtotal,
    cartTax,
    isLoading,
    cartId,
    
    // Actions
    addToCart,
    removeFromCart,
    updateQuantity,
    incrementQuantity,
    decrementQuantity,
    clearCart,
    
    // Utilities
    getCartItem,
    isInCart,
    getCartSummary,
    validateCart,
    formatPrice
  };
};