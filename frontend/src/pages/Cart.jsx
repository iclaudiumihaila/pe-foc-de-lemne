import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import CartItem from '../components/cart/CartItem';
import CartSummary, { EmptyCartSummary } from '../components/cart/CartSummary';
import Loading, { PageLoading, SectionLoading } from '../components/common/Loading';
import { CartItemSkeleton, CartSummarySkeleton } from '../components/common/LoadingSkeleton';
import ErrorMessage, { NetworkError, ServerError } from '../components/common/ErrorMessage';
import { SectionErrorBoundary } from '../components/common/ErrorBoundary';
import { useApiToast } from '../components/common/Toast';

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
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumb Navigation */}
        <nav className="mb-6 text-sm text-gray-600">
          <Link to="/" className="hover:text-green-600 transition-colors">
            Acasă
          </Link>
          <span className="mx-2">›</span>
          <span className="text-gray-900">Coșul de cumpărături</span>
        </nav>

        {/* Page Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Coșul tău de cumpărături
          </h1>
          {cartItemCount > 0 ? (
            <p className="text-lg text-gray-600">
              Ai {cartItemCount} {cartItemCount === 1 ? 'produs' : 'produse'} în coș. 
              Verifică-le înainte de a plasa comanda.
            </p>
          ) : (
            <p className="text-lg text-gray-600">
              Coșul tău este gol. Descoperă produsele noastre locale și naturale.
            </p>
          )}
        </div>

        {/* Cart Error Display */}
        {cartError && (
          <div className="mb-6">
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
          <div className="max-w-2xl mx-auto">
            <EmptyCartSummary />
            
            {/* Additional empty cart messaging */}
            <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold text-green-800 mb-3">
                🌱 Descoperă produsele noastre locale
              </h3>
              <p className="text-green-700 mb-4">
                Avem o gamă variată de produse proaspete și naturale de la producătorii din zona ta. 
                Toate sunt verificate pentru calitate și prospețime.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-green-600">
                <div>🍎 Fructe și legume de sezon</div>
                <div>🍯 Miere și produse apicole</div>
                <div>🧀 Lactate tradiționale</div>
                <div>🥚 Ouă proaspete de țară</div>
              </div>
            </div>
          </div>
        ) : (
          /* Cart Items and Summary */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
            {/* Cart Items Section */}
            <section className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Produsele tale ({cartItemCount})
                  </h2>
                  {cartItemCount > 0 && (
                    <button
                      onClick={handleClearCart}
                      disabled={clearingCart}
                      className="text-sm text-red-600 hover:text-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                      {clearingCart ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Se golește...
                        </>
                      ) : (
                        'Golește coșul'
                      )}
                    </button>
                  )}
                </div>

                {/* Cart Items List */}
                <div className="space-y-4">
                  {cartItems.map((item) => (
                    <SectionErrorBoundary key={item.id}>
                      <CartItem 
                        key={item.id} 
                        item={item}
                      />
                    </SectionErrorBoundary>
                  ))}
                </div>
              </div>

              {/* Continue Shopping Section */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Continuă cumpărăturile
                </h3>
                <p className="text-gray-600 mb-4">
                  Explorează mai multe produse locale și naturale din catalogul nostru.
                </p>
                <Link
                  to="/products"
                  className="inline-flex items-center px-4 py-3 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors min-h-[44px] justify-center"
                >
                  <span className="mr-2">🛒</span>
                  Vezi toate produsele
                </Link>
              </div>
            </section>

            {/* Cart Summary Sidebar */}
            <aside className="lg:col-span-1">
              <div className="sticky top-4">
                <SectionErrorBoundary>
                  <CartSummary />
                </SectionErrorBoundary>
              </div>
            </aside>
          </div>
        )}

        {/* Local Producer Information */}
        {cartItemCount > 0 && (
          <div className="mt-12 bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-800 mb-4">
              💡 Beneficiile comenzii tale locale
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-green-700">
              <div className="text-center">
                <div className="text-2xl mb-2">🌱</div>
                <h4 className="font-medium mb-1">Produse naturale</h4>
                <p>Fără pesticide și chimicale dăunătoare</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">🚚</div>
                <h4 className="font-medium mb-1">Livrare gratuită</h4>
                <p>Transport local rapid și ecologic</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">🤝</div>
                <h4 className="font-medium mb-1">Susții comunitatea</h4>
                <p>Ajuți familiile de fermieri locali</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">✅</div>
                <h4 className="font-medium mb-1">Calitate garantată</h4>
                <p>Produse verificate și certificate</p>
              </div>
            </div>
          </div>
        )}

        {/* Help and Support Section */}
        <div className="mt-8 text-center">
          <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Ai nevoie de ajutor?
            </h3>
            <p className="text-gray-600 mb-4">
              Echipa noastră este aici să te ajute cu orice întrebări despre produse sau comenzi.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center text-sm">
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>📧</span>
                <span>contact@pefocdelemne.ro</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>📞</span>
                <span>0700 123 456</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>⏰</span>
                <span>Luni - Vineri, 9:00 - 18:00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;