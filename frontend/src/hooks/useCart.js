import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

export const useCart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [cartItemCount, setCartItemCount] = useState(0);
  const [cartTotal, setCartTotal] = useState(0);
  const [cartSubtotal, setCartSubtotal] = useState(0);
  const [cartTax, setCartTax] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [cartId, setCartId] = useState(null);
  
  // Generate or retrieve cart session ID
  useEffect(() => {
    let sessionCartId = localStorage.getItem('cartId');
    if (!sessionCartId) {
      sessionCartId = `cart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('cartId', sessionCartId);
    }
    setCartId(sessionCartId);
  }, []);
  
  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const items = JSON.parse(savedCart);
        if (Array.isArray(items)) {
          setCartItems(items);
        }
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
        setCartItems([]);
        localStorage.removeItem('cart');
      }
    }
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
    
    // Save to localStorage with error handling
    try {
      localStorage.setItem('cart', JSON.stringify(cartItems));
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
      toast.error('Eroare la salvarea coșului');
    }
  }, [cartItems]);
  
  // Format price for display
  const formatPrice = useCallback((price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  }, []);
  
  // Add item to cart
  const addToCart = useCallback((product, quantity = 1) => {
    if (!product || !product.id) {
      toast.error('Produs invalid');
      return;
    }
    
    if (!product.inStock) {
      toast.error('Produsul nu este în stoc');
      return;
    }
    
    if (quantity <= 0) {
      toast.error('Cantitatea trebuie să fie pozitivă');
      return;
    }
    
    setIsLoading(true);
    
    try {
      setCartItems(prevItems => {
        const existingItem = prevItems.find(item => item.id === product.id);
        
        if (existingItem) {
          const newQuantity = existingItem.quantity + quantity;
          toast.success(`${product.name} - cantitate actualizată la ${newQuantity}`);
          
          return prevItems.map(item =>
            item.id === product.id
              ? { ...item, quantity: newQuantity }
              : item
          );
        } else {
          toast.success(`${product.name} adăugat în coș`);
          
          return [...prevItems, { 
            ...product, 
            quantity,
            addedAt: new Date().toISOString()
          }];
        }
      });
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error('Eroare la adăugarea în coș');
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // Remove item from cart
  const removeFromCart = useCallback((productId) => {
    if (!productId) return;
    
    setCartItems(prevItems => {
      const item = prevItems.find(item => item.id === productId);
      if (item) {
        toast.success(`${item.name} eliminat din coș`);
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
        toast.success(`${item.name} - cantitate actualizată`);
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
    toast.success('Coșul a fost golit');
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
      toast.error('Unele produse din coș au fost eliminate (produse invalide)');
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