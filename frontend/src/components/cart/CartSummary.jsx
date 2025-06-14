import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartContext } from '../../contexts/CartContext';

const CartSummary = ({ 
  showCheckoutButton = true, 
  showTitle = true,
  compact = false,
  className = '',
  onCheckout 
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

    // Custom checkout handler if provided
    if (onCheckout) {
      onCheckout();
      return;
    }

    // Default navigation to checkout
    navigate('/checkout');
  };

  // Don't render if cart is empty
  if (cartItemCount === 0) {
    return null;
  }

  // Compact version for mobile or sidebar
  if (compact) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-medium text-gray-700">
            Total ({cartItemCount} {cartItemCount === 1 ? 'produs' : 'produse'})
          </span>
          <span className="text-lg font-bold text-gray-900">
            {formatPrice(cartTotal)}
          </span>
        </div>
        
        {showCheckoutButton && (
          <button
            onClick={handleCheckout}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 rounded-lg transition-colors min-h-[44px] text-sm sm:text-base"
          >
            Finalizează comanda
          </button>
        )}
      </div>
    );
  }

  // Full version with detailed breakdown
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      {showTitle && (
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Rezumatul comenzii
        </h2>
      )}

      {/* Cart Items Count */}
      <div className="flex items-center justify-between py-2 text-sm text-gray-600">
        <span>
          {cartItemCount} {cartItemCount === 1 ? 'produs' : 'produse'} în coș
        </span>
      </div>

      <div className="border-t border-gray-200 pt-4 space-y-3">
        {/* Subtotal */}
        <div className="flex items-center justify-between">
          <span className="text-gray-700">Subtotal</span>
          <span className="font-medium text-gray-900">
            {formatPrice(cartSubtotal)}
          </span>
        </div>

        {/* Tax (VAT) */}
        <div className="flex items-center justify-between">
          <span className="text-gray-700">
            TVA (19%)
            <span className="text-xs text-gray-500 ml-1">
              inclusă în preț
            </span>
          </span>
          <span className="font-medium text-gray-900">
            {formatPrice(cartTax)}
          </span>
        </div>

        {/* Delivery Info */}
        <div className="flex items-center justify-between">
          <span className="text-gray-700">
            Livrare
            <span className="text-xs text-green-600 ml-1">
              📍 Locală
            </span>
          </span>
          <span className="font-medium text-green-600">
            Gratuită
          </span>
        </div>

        {/* Total */}
        <div className="border-t border-gray-200 pt-3">
          <div className="flex items-center justify-between">
            <span className="text-lg font-semibold text-gray-900">
              Total de plată
            </span>
            <span className="text-xl font-bold text-primary-600">
              {formatPrice(cartTotal)}
            </span>
          </div>
        </div>

        {/* Tax Notice */}
        <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-md">
          💡 Prețurile includ TVA conform legislației românești. 
          Produsele locale susțin economia comunitară.
        </div>

        {/* Checkout Button */}
        {showCheckoutButton && (
          <div className="pt-4">
            <button
              onClick={handleCheckout}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2 min-h-[52px] text-sm sm:text-base"
              disabled={cartItemCount === 0}
            >
              <span>🛒</span>
              Finalizează comanda
              <span className="text-sm font-normal">
                ({formatPrice(cartTotal)})
              </span>
            </button>
          </div>
        )}

        {/* Security Notice */}
        <div className="text-xs text-gray-500 text-center mt-3">
          🔒 Plata securizată • 📞 Suport local • ✅ Produse verificate
        </div>
      </div>
    </div>
  );
};

// Empty cart summary component
export const EmptyCartSummary = ({ className = '' }) => (
  <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 text-center ${className}`}>
    <div className="text-4xl mb-3">🛒</div>
    <h3 className="text-lg font-medium text-gray-700 mb-2">
      Coșul este gol
    </h3>
    <p className="text-gray-500 text-sm mb-4">
      Adaugă produse pentru a vedea rezumatul comenzii
    </p>
    <button
      onClick={() => window.location.href = '/products'}
      className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-colors min-h-[44px] text-sm sm:text-base"
    >
      Explorează produsele
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