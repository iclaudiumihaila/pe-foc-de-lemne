import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import api from '../services/api';
import { useApiToast } from '../components/common/Toast';
import { SectionLoading } from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import { ChevronLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import ProductCardStack from '../components/swipe/ProductCardStack';
// Removed SwipeActions - using gesture-only interface
import { showFloatingIndicator } from '../components/animations/FloatingIndicator';
import { getImageUrl } from '../utils/imageUrl';
import '../styles/swipe-animations.css';

// Device detection utilities
const isTouchDevice = () => {
  return ('ontouchstart' in window) || 
    (navigator.maxTouchPoints > 0) ||
    (navigator.msMaxTouchPoints > 0);
};

const isMobile = () => {
  return isTouchDevice() && window.innerWidth <= 768;
};

const SwipeProducts = () => {
  const { addToCart, removeFromCart } = useCartContext();
  const toast = useApiToast();
  
  // State management
  const [products, setProducts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [swipeHistory, setSwipeHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // Track session for analytics
  const [sessionStart] = useState(Date.now());
  const [swipeCount, setSwipeCount] = useState(0);
  const [rightSwipes, setRightSwipes] = useState(0);
  const [hideInstructions, setHideInstructions] = useState(false);
  
  const fetchProducts = async (page = 1) => {
    try {
      if (page === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      
      const response = await api.get('/products', {
        params: {
          page: page,
          limit: 20,
          is_available: true
        }
      });
      
      console.log('Products API response:', response.data);
      
      // The API returns products in response.data.data.products
      const productsData = response.data?.data?.products || [];
      
      if (Array.isArray(productsData)) {
        if (page === 1) {
          setProducts(productsData);
        } else {
          // Append new products
          setProducts(prev => [...prev, ...productsData]);
        }
        setHasMore(productsData.length === 20);
        setCurrentPage(page);
      } else {
        console.error('Invalid products data:', productsData);
        setProducts([]);
        setHasMore(false);
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      if (page === 1) {
        setError('Nu s-au putut încărca produsele');
        toast.showError('Eroare la încărcarea produselor');
      } else {
        toast.showError('Eroare la încărcarea mai multor produse');
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };
  
  // Transform product for cart compatibility
  const transformProduct = (product) => {
    return {
      id: product.id,
      name: product.name,
      price: product.price,
      image: getImageUrl(product.images && product.images.length > 0 ? product.images[0] : null, 'pinterest'),
      description: product.description,
      category: product.category?.name || 'General',
      unit: product.unit || 'bucată',
      inStock: product.is_available !== false && product.stock_quantity > 0,
      stock_quantity: product.stock_quantity,
      quantity: 1
    };
  };
  
  // Handle add to cart from modal
  const handleAddToCart = async (product, quantity = 1) => {
    try {
      const transformedProduct = transformProduct(product);
      await addToCart(transformedProduct, quantity);
      // No toast - visual feedback only
    } catch (err) {
      console.error('Error adding to cart:', err);
      // Silent error - button will show normal state
    }
  };

  // Handle swipe actions
  const handleSwipe = async (direction) => {
    if (!products || products.length === 0) return;
    
    const product = products[currentIndex % products.length];
    setSwipeCount(prev => prev + 1);
    
    // Add to swipe history (limit to 20)
    setSwipeHistory(prev => [...prev.slice(-19), { product, direction, index: currentIndex }]);
    
    if (direction === 'up') {
      // Add to cart on upward swipe
      try {
        const transformedProduct = transformProduct(product);
        await addToCart(transformedProduct, 1);
        setRightSwipes(prev => prev + 1);
        setHideInstructions(true); // Hide instructions after first cart addition
        
        // Enhanced success animation
        const mainContainer = document.querySelector('.swipe-products-container');
        if (mainContainer) {
          // Add success pulse effect
          mainContainer.style.boxShadow = '0 0 40px rgba(34, 197, 94, 0.5)';
          setTimeout(() => {
            mainContainer.style.boxShadow = '';
          }, 400);
        }
        
        // Create flying product animation to cart
        const cardElement = document.querySelector('.swipeable-card-top');
        const cartIcon = document.querySelector('.cart-icon-container');
        if (cardElement && cartIcon) {
          const rect = cardElement.getBoundingClientRect();
          const cartRect = cartIcon.getBoundingClientRect();
          
          // Create flying product element
          const flyingProduct = document.createElement('div');
          flyingProduct.className = 'flying-product';
          flyingProduct.innerHTML = `
            <div class="bg-green-600 rounded-full p-3 shadow-lg">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
                <path d="M9 2L12 1L15 2L19 5.5L21 12L18 21L6 21L3 12L5 5.5L9 2Z" stroke-linejoin="round"/>
              </svg>
            </div>
          `;
          flyingProduct.style.cssText = `
            position: fixed;
            top: ${rect.top + rect.height / 2}px;
            left: ${rect.left + rect.width / 2}px;
            transform: translate(-50%, -50%);
            z-index: 9999;
            pointer-events: none;
          `;
          document.body.appendChild(flyingProduct);
          
          // Animate to cart
          requestAnimationFrame(() => {
            flyingProduct.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            flyingProduct.style.top = `${cartRect.top + cartRect.height / 2}px`;
            flyingProduct.style.left = `${cartRect.left + cartRect.width / 2}px`;
            flyingProduct.style.transform = 'translate(-50%, -50%) scale(0.3)';
            flyingProduct.style.opacity = '0';
          });
          
          // Animate cart icon when product arrives
          setTimeout(() => {
            cartIcon.classList.add('cart-receive-item');
            setTimeout(() => cartIcon.classList.remove('cart-receive-item'), 600);
          }, 700);
          
          setTimeout(() => flyingProduct.remove(), 900);
        }
        
        // Show success message with animation
        const successMessage = document.createElement('div');
        successMessage.className = 'swipe-success-message';
        successMessage.textContent = 'Adăugat în coș!';
        successMessage.style.cssText = `
          position: fixed;
          bottom: 100px;
          left: 50%;
          transform: translateX(-50%) translateY(20px);
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          padding: 12px 24px;
          border-radius: 30px;
          font-weight: 600;
          box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
          opacity: 0;
          transition: all 0.3s ease-out;
          z-index: 9999;
        `;
        document.body.appendChild(successMessage);
        
        requestAnimationFrame(() => {
          successMessage.style.opacity = '1';
          successMessage.style.transform = 'translateX(-50%) translateY(0)';
        });
        
        setTimeout(() => {
          successMessage.style.opacity = '0';
          successMessage.style.transform = 'translateX(-50%) translateY(-20px)';
          setTimeout(() => successMessage.remove(), 300);
        }, 2000);
        
      } catch (err) {
        toast.showError('Nu s-a putut adăuga în coș');
      }
    }
    
    // Move to next product with looping
    setCurrentIndex(prev => {
      const nextIndex = prev + 1;
      // Loop back to beginning when reaching the end
      return nextIndex >= products.length ? 0 : nextIndex;
    });
  };
  
  // Handle undo
  const handleUndo = async () => {
    if (swipeHistory.length === 0) return;
    
    const lastSwipe = swipeHistory[swipeHistory.length - 1];
    setSwipeHistory(prev => prev.slice(0, -1));
    setCurrentIndex(lastSwipe.index);
    
    // Update statistics
    setSwipeCount(prev => Math.max(0, prev - 1));
    
    // If it was an upward swipe, remove from cart
    if (lastSwipe.direction === 'up') {
      try {
        // Remove from cart context silently (without toast)
        const transformedProduct = transformProduct(lastSwipe.product);
        // Call removeFromCart directly without triggering its toast
        const cartItems = JSON.parse(localStorage.getItem('cartItems') || '[]');
        const updatedItems = cartItems.filter(item => item.id !== transformedProduct.id);
        localStorage.setItem('cartItems', JSON.stringify(updatedItems));
        window.dispatchEvent(new Event('storage'));
        
        setRightSwipes(prev => Math.max(0, prev - 1));
      } catch (err) {
        console.error('Error removing from cart:', err);
      }
    }
  };
  
  // Check if this is a mobile device first
  const [isMobileDevice, setIsMobileDevice] = useState(() => isMobile());
  
  // Check if mobile on mount and window resize
  useEffect(() => {
    const checkDevice = () => {
      setIsMobileDevice(isMobile());
    };
    
    checkDevice();
    window.addEventListener('resize', checkDevice);
    
    return () => window.removeEventListener('resize', checkDevice);
  }, []);
  
  // Fetch products only on mobile devices
  useEffect(() => {
    if (isMobileDevice) {
      fetchProducts(1);
    }
  }, [isMobileDevice]);
  
  // Since we're looping, we don't need to preload more products
  // This can be removed or kept for initial load optimization
  
  // Redirect desktop users
  if (!isMobileDevice) {
    return <Navigate to="/products" replace />;
  }
  
  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <SectionLoading message="Se încarcă produsele..." />
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <ErrorMessage 
          message={error}
          onRetry={fetchProducts}
        />
      </div>
    );
  }
  
  // Empty state
  if (!loading && (!products || products.length === 0)) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        {/* Empty content - no header */}
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-white rounded-lg shadow-md p-8 max-w-sm w-full">
            <div className="text-6xl mb-4">📦</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Nu sunt produse disponibile
            </h2>
            <p className="text-gray-600 mb-6">
              Pentru a folosi modul swipe, trebuie să existe produse în magazin.
            </p>
            <div className="space-y-3">
              <Link 
                to="/products" 
                className="block w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Vezi magazinul
              </Link>
              {isMobileDevice && (
                <p className="text-sm text-gray-500">
                  Swipe mode este disponibil doar pe dispozitive mobile
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main content area - no header on mobile */}
      <div className="flex-1 flex items-start justify-center pt-8 px-4 pb-4 swipe-products-container" style={{ touchAction: 'none' }}>
        <div className="w-full max-w-sm relative" style={{ touchAction: 'none' }}>
          {/* Center point for floating indicator */}
          <div className="swipe-center-point absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
          
          {/* Product card stack */}
          <ProductCardStack
            products={products}
            currentIndex={currentIndex}
            onSwipe={handleSwipe}
            onCardTap={(product) => {
              setSelectedProduct(product);
              setShowDetailModal(true);
            }}
            onAddToCart={handleAddToCart}
            swipeHistory={swipeHistory}
            hideInstructions={hideInstructions}
          />
        </div>
      </div>
      
      {/* Previous button - Tinder-style rounded icon */}
      <div className={`fixed bottom-1 left-1/2 transform -translate-x-1/2 z-40 transition-all duration-500 ${
        swipeHistory.length > 0 ? 'opacity-100 scale-100' : 'opacity-0 scale-0 pointer-events-none'
      }`}>
        <button
          onClick={handleUndo}
          className="group relative bg-yellow-400 text-white shadow-lg rounded-full w-14 h-14 hover:shadow-xl transition-all duration-300 transform hover:scale-110 flex items-center justify-center"
          disabled={swipeHistory.length === 0}
        >
          {/* Hover effect */}
          <div className="absolute inset-0 bg-yellow-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          {/* Undo/Return arrow icon */}
          <svg className="w-7 h-7 relative z-10 transform group-hover:rotate-[-15deg] transition-transform duration-300" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 10a7 7 0 0 1 7-7h4a7 7 0 0 1 7 7v4a7 7 0 0 1-7 7h-4a7 7 0 0 1-7-7v-4z" opacity="0"/>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 14l-4-4m0 0l4-4m-4 4h12a4 4 0 0 1 0 8h-4" />
          </svg>
        </button>
      </div>
      
      {/* Stats footer */}
      <div className="swipe-stats-footer bg-white border-t px-4 py-2 text-center text-sm text-gray-600 relative">
        <div className="flex items-center justify-center gap-4">
          <span>Adăugate în coș: {rightSwipes} | Total: {swipeCount}</span>
          {loadingMore && (
            <div className="flex items-center gap-2 text-xs">
              <div className="animate-spin h-3 w-3 border-2 border-gray-400 border-t-transparent rounded-full"></div>
              <span>Se încarcă mai multe...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SwipeProducts;