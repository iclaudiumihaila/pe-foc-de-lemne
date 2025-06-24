import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import { clearAllCartData } from '../utils/clearCart';

const ClearCart = () => {
  const navigate = useNavigate();
  const { clearCart } = useCartContext();
  
  useEffect(() => {
    // Clear all cart data
    clearAllCartData();
    clearCart();
    
    // Redirect to home page
    setTimeout(() => {
      navigate('/');
    }, 1000);
  }, [clearCart, navigate]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Coșul a fost golit</h2>
        <p className="text-gray-600">Redirectare către pagina principală...</p>
      </div>
    </div>
  );
};

export default ClearCart;