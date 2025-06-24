import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import CartItem from '../components/cart/CartItem';
import CartSummary, { EmptyCartSummary } from '../components/cart/CartSummary';
import { PageLoading } from '../components/common/Loading';
import ErrorMessage, { NetworkError, ServerError } from '../components/common/ErrorMessage';
import { SectionErrorBoundary } from '../components/common/ErrorBoundary';
import { useApiToast } from '../components/common/Toast';
import { ArrowLeft, ShoppingBag, Trash2 } from 'lucide-react';

const Cart = () => {
  const { 
    cartItems, 
    cartItemCount, 
    loading, 
    clearCart,
    error: cartError 
  } = useCartContext();
  
  const toast = useApiToast();
  const [clearingCart, setClearingCart] = useState(false);
  
  // Detect mobile device - must be before any conditional returns
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Handle cart clearing with error handling
  const handleClearCart = async () => {
    if (!window.confirm('Sigur vrei să golești coșul complet?')) {
      return;
    }
    
    try {
      setClearingCart(true);
      await clearCart();
      toast.showSuccess('Coșul a fost golit cu succes.');
    } catch (err) {
      console.error('Error clearing cart:', err);
      
      if (err.isNetworkError) {
        toast.handleNetworkError();
      } else {
        toast.handleApiError(err, 'Eroare la golirea coșului. Încercați din nou.');
      }
    } finally {
      setClearingCart(false);
    }
  };

  if (loading) {
    return (
      <PageLoading message="Se încarcă coșul de cumpărături..." />
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Modern Mobile Header */}
      <header className="sticky top-0 z-40 bg-white shadow-sm">
        <div className="flex items-center px-4 py-3">
          <Link to="/products" className="p-2 -m-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </Link>
          <h1 className="flex-1 text-center text-xl font-semibold text-gray-900">
            Coșul tău
          </h1>
          {cartItemCount > 0 && (
            <button
              onClick={handleClearCart}
              disabled={clearingCart}
              className="p-2 -m-2 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
              aria-label="Golește coșul"
            >
              <Trash2 className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </div>
      </header>

      {/* Cart Error Display */}
      {cartError && (
        <div className="m-4">
          <SectionErrorBoundary>
            {cartError.isNetworkError ? (
              <NetworkError 
                onRetry={() => window.location.reload()}
              />
            ) : cartError.status >= 500 ? (
              <ServerError 
                onRetry={() => window.location.reload()}
              />
            ) : (
              <ErrorMessage 
                message={cartError.message || 'Eroare la încărcarea coșului de cumpărături'}
                showRetry={true}
                onRetry={() => window.location.reload()}
              />
            )}
          </SectionErrorBoundary>
        </div>
      )}

      {cartItemCount === 0 ? (
        /* Empty Cart State */
        <div className="flex-1 flex items-center justify-center p-4 min-h-[calc(100vh-200px)]">
          <div className="text-center max-w-sm">
            <div className="mb-6">
              <div className="w-24 h-24 bg-gray-100 rounded-full mx-auto flex items-center justify-center">
                <ShoppingBag className="w-12 h-12 text-gray-400" />
              </div>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Coșul tău este gol
            </h2>
            <p className="text-gray-600 mb-6">
              Adaugă produse pentru a continua cumpărăturile
            </p>
            <Link
              to="/products"
              className="inline-flex items-center justify-center w-full px-6 py-3 bg-green-600 text-white font-medium rounded-full hover:bg-green-700 transition-colors"
            >
              Explorează produsele
            </Link>
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-[calc(100vh-64px)]">
          {/* Cart Items - Scrollable Area */}
          <div className="flex-1 overflow-y-auto">
            <div className="px-4 py-2">
              {cartItems.map((item, index) => (
                <div key={item.id}>
                  <CartItem 
                    item={item}
                    isMobile={true}
                  />
                  {index < cartItems.length - 1 && (
                    <div className="h-px bg-gray-200 mx-4" />
                  )}
                </div>
              ))}
            </div>
            
            {/* Add some padding at the bottom for better scrolling */}
            <div className="h-32" />
          </div>

          {/* Fixed Bottom Summary */}
          <div className="fixed bottom-0 left-0 right-0 bg-white shadow-[0_-4px_12px_rgba(0,0,0,0.08)] z-30">
            <div className="px-4 py-3">
              {/* Summary Row */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm text-gray-600">Total ({cartItemCount} produse)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {new Intl.NumberFormat('ro-RO', {
                      style: 'currency',
                      currency: 'RON'
                    }).format(cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0))}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Livrare</p>
                  <p className="text-sm font-medium text-green-600">Gratuită</p>
                </div>
              </div>
              
              {/* Checkout Button */}
              <Link
                to="/comanda"
                className="block w-full bg-green-600 text-white text-center py-3 rounded-lg font-medium text-base hover:bg-green-700 transition-colors shadow-sm"
              >
                Finalizează comanda
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;