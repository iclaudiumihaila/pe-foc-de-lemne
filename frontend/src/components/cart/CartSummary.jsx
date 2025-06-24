import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartContext } from '../../contexts/CartContext';

const CartSummary = ({ 
  showCheckoutButton = true,
  className = ''
}) => {
  const navigate = useNavigate();
  const { 
    cartItemCount, 
    cartSubtotal, 
    cartTax, 
    cartTotal,
    formatPrice,
    validateCart
  } = useCartContext();

  // Handle checkout button click
  const handleCheckout = async () => {
    // Validate cart before proceeding
    const isValid = await validateCart();
    if (!isValid) {
      return;
    }

    if (cartItemCount === 0) {
      return;
    }

    // Navigate to checkout
    navigate('/comanda');
  };

  // Don't render if cart is empty
  if (cartItemCount === 0) {
    return null;
  }

  // Clean version
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <h2 className="text-lg font-medium text-gray-900 mb-4">
        Rezumat comandă
      </h2>

      <div className="space-y-3">
        {/* Subtotal */}
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal ({cartItemCount} produse)</span>
          <span className="text-gray-900">{formatPrice(cartSubtotal)}</span>
        </div>

        {/* Delivery */}
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Livrare</span>
          <span className="text-green-600 font-medium">Gratuită</span>
        </div>

        {/* Total */}
        <div className="border-t pt-3">
          <div className="flex justify-between">
            <span className="font-medium text-gray-900">Total</span>
            <span className="text-xl font-semibold text-gray-900">
              {formatPrice(cartTotal)}
            </span>
          </div>
        </div>

        {/* Checkout Button */}
        {showCheckoutButton && (
          <button
            onClick={handleCheckout}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg transition-colors mt-4"
            disabled={cartItemCount === 0}
          >
            Finalizează comanda
          </button>
        )}
      </div>
    </div>
  );
};

// Empty cart summary component
export const EmptyCartSummary = ({ className = '' }) => (
  <div className={`text-center py-12 ${className}`}>
    <div className="text-6xl mb-4">🛒</div>
    <h3 className="text-xl font-medium text-gray-900 mb-2">
      Coșul este gol
    </h3>
    <p className="text-gray-500 mb-6">
      Adaugă produse pentru a continua
    </p>
    <button
      onClick={() => window.location.href = '/products'}
      className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors"
    >
      Vezi produsele
    </button>
  </div>
);

// Checkout summary for final confirmation
export const CheckoutSummary = ({ orderData, className = '' }) => {
  const { formatPrice } = useCartContext();
  
  if (!orderData) return null;

  return (
    <div className={`bg-green-50 border border-green-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-green-600 text-xl">✅</span>
        <h3 className="text-lg font-semibold text-green-800">
          Comanda confirmată
        </h3>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-700">Numărul comenzii:</span>
          <span className="font-medium">{orderData.orderNumber}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-700">Total plătit:</span>
          <span className="font-bold text-green-700">
            {formatPrice(orderData.total)}
          </span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-700">Metoda de plată:</span>
          <span className="font-medium">
            {orderData.paymentMethod || 'Ramburs'}
          </span>
        </div>

        <div className="border-t border-green-200 pt-3 mt-4">
          <p className="text-green-700 text-xs">
            📧 Vei primi un email de confirmare cu detaliile comenzii.
            <br />
            📞 Te vom contacta pentru confirmarea livrării.
          </p>
        </div>
      </div>
    </div>
  );
};

// Loading skeleton for cart summary
export const CartSummarySkeleton = () => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <div className="h-6 bg-gray-200 rounded animate-pulse mb-4 w-1/2" />
    
    <div className="space-y-3">
      <div className="flex justify-between">
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/4" />
      </div>
      
      <div className="flex justify-between">
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/4" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/5" />
      </div>
      
      <div className="border-t border-gray-200 pt-3">
        <div className="flex justify-between">
          <div className="h-5 bg-gray-200 rounded animate-pulse w-1/3" />
          <div className="h-5 bg-gray-200 rounded animate-pulse w-1/4" />
        </div>
      </div>
      
      <div className="pt-4">
        <div className="h-12 bg-gray-200 rounded animate-pulse w-full" />
      </div>
    </div>
  </div>
);

export default CartSummary;