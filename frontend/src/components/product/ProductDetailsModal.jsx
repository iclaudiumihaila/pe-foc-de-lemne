import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { X } from 'lucide-react';
import AddToCartButton from '../common/AddToCartButton';

const ProductDetailsModal = ({ isOpen, onClose, product, onAddToCart }) => {
  const [modalDragY, setModalDragY] = useState(0);
  const [modalStartY, setModalStartY] = useState(0);
  const [quantity, setQuantity] = useState(1);

  // Reset quantity when modal opens
  useEffect(() => {
    if (isOpen) {
      setQuantity(1);
    }
  }, [isOpen]);

  // Prevent body scroll when modal is open and preserve scroll position
  useEffect(() => {
    if (isOpen) {
      // Store current scroll position
      const scrollY = window.scrollY;
      
      // Lock body scroll and maintain position - enhanced for iOS
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.overflow = 'hidden';
      document.body.style.width = '100%';
      document.body.style.height = '100%';
      document.body.style.touchAction = 'none';
      document.body.style.webkitOverflowScrolling = 'touch';
      
      // Also lock html element for iOS Safari
      document.documentElement.style.overflow = 'hidden';
      document.documentElement.style.position = 'relative';
      document.documentElement.style.height = '100%';
    } else {
      // Get the scroll position from the body's top style
      const scrollY = document.body.style.top;
      
      // Reset body styles
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.overflow = '';
      document.body.style.width = '';
      document.body.style.height = '';
      document.body.style.touchAction = '';
      document.body.style.webkitOverflowScrolling = '';
      
      // Reset html styles
      document.documentElement.style.overflow = '';
      document.documentElement.style.position = '';
      document.documentElement.style.height = '';
      
      // Restore scroll position
      if (scrollY) {
        window.scrollTo(0, parseInt(scrollY.replace('px', '')) * -1);
      }
    }
    
    return () => {
      // Cleanup on unmount
      const scrollY = document.body.style.top;
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.overflow = '';
      document.body.style.width = '';
      document.body.style.height = '';
      document.body.style.touchAction = '';
      document.body.style.webkitOverflowScrolling = '';
      document.documentElement.style.overflow = '';
      document.documentElement.style.position = '';
      document.documentElement.style.height = '';
      if (scrollY) {
        window.scrollTo(0, parseInt(scrollY.replace('px', '')) * -1);
      }
    };
  }, [isOpen]);

  if (!isOpen || !product) return null;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price || 0);
  };

  return ReactDOM.createPortal(
    <div 
      className={`fixed inset-0 z-[100] bg-white transform transition-transform duration-300 ease-out ${
        isOpen ? 'translate-y-0' : 'translate-y-full'
      }`}
      style={{ 
        pointerEvents: isOpen ? 'auto' : 'none',
        transform: isOpen ? `translateY(${modalDragY > 0 ? modalDragY : 0}px)` : 'translateY(100%)'
      }}
      onTouchStart={(e) => {
        // Only allow swipe down from the header area or when scrolled to top
        const scrollableContent = e.currentTarget.querySelector('.overflow-y-auto');
        if (!scrollableContent || scrollableContent.scrollTop === 0) {
          setModalStartY(e.touches[0].clientY);
          setModalDragY(0);
        }
      }}
      onTouchMove={(e) => {
        if (modalStartY > 0) {
          const deltaY = e.touches[0].clientY - modalStartY;
          if (deltaY > 0) { // Only track downward swipes
            setModalDragY(deltaY);
          }
        }
      }}
      onTouchEnd={(e) => {
        const threshold = 100;
        if (modalDragY > threshold) {
          // Close modal
          onClose();
        }
        setModalDragY(0);
        setModalStartY(0);
      }}
      onWheel={(e) => {
        // Prevent wheel events from bubbling to body
        const scrollableContent = e.currentTarget.querySelector('.overflow-y-auto');
        if (scrollableContent && !scrollableContent.contains(e.target)) {
          e.preventDefault();
        }
      }}
    >
      <div className="h-full flex flex-col max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative h-full flex flex-col">
          {/* Swipe handle */}
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 z-20">
            <div className="w-12 h-1 bg-gray-300 rounded-full" />
          </div>
          
          {/* Header with close button */}
          <div className="absolute top-0 right-0 z-10 p-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="bg-white bg-opacity-90 backdrop-blur-sm rounded-full p-3 shadow-lg hover:bg-opacity-100 transition-all"
            >
              <X className="w-6 h-6 text-gray-700" />
            </button>
          </div>

          {/* Scrollable Product Details */}
          <div className="flex-1 overflow-y-auto pb-6 pt-16">
            <div className="py-6">
            {/* Name and Price */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-3">
                {product?.name || 'Produs'}
              </h1>
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold text-green-600">
                  {formatPrice(product?.price)}
                </span>
                {product?.unit && product.unit !== 'bucată' && (
                  <span className="text-lg text-gray-500">/ {product.unit}</span>
                )}
              </div>
            </div>

            {/* Quantity Controls and Add to Cart */}
            <div className="pb-6 mb-6 border-b">
              <div className="flex items-center justify-center gap-4 mb-6">
                <button 
                  onClick={() => setQuantity(q => Math.max(1, q - 1))}
                  disabled={quantity <= 1}
                  className="w-12 h-12 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-110 active:scale-95 flex items-center justify-center"
                >
                  <span className="text-2xl font-medium text-gray-700">−</span>
                </button>
                <span className="w-16 text-center font-semibold text-2xl text-gray-900">{quantity}</span>
                <button 
                  onClick={() => setQuantity(q => Math.min(product?.stock_quantity || 999, q + 1))}
                  disabled={quantity >= (product?.stock_quantity || 999)}
                  className="w-12 h-12 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-110 active:scale-95 flex items-center justify-center"
                >
                  <span className="text-2xl font-medium text-gray-700">+</span>
                </button>
              </div>
              
              <AddToCartButton
                onClick={async () => {
                  if (onAddToCart) {
                    await onAddToCart(product, quantity);
                    // Close modal after showing success animation
                    setTimeout(() => {
                      onClose();
                    }, 800);
                  }
                }}
                disabled={product?.inStock === false || product?.stock_quantity === 0}
                className="w-full"
                quantity={quantity}
              >
                {product?.inStock === false || product?.stock_quantity === 0
                  ? 'Stoc epuizat' 
                  : 'Adaugă în coș'
                }
              </AddToCartButton>
            </div>

            {/* Stock Badge */}
            {product?.stock_quantity && product.stock_quantity < 10 && product.stock_quantity > 0 && (
              <div className="bg-orange-50 text-orange-800 px-4 py-3 rounded-lg text-sm font-medium mb-6 inline-flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Doar {product.stock_quantity} bucăți în stoc
              </div>
            )}

            {/* Description */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Descriere</h2>
              <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                {product?.description || 'Produs disponibil în stoc'}
              </p>
            </div>

            {/* Additional Info */}
            {product?.category && (
              <div className="border-t pt-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Informații suplimentare</h3>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Categorie:</dt>
                    <dd className="font-medium">{typeof product.category === 'string' ? product.category : product.category?.name}</dd>
                  </div>
                  {product?.unit && (
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Unitate de măsură:</dt>
                      <dd className="font-medium">{product.unit}</dd>
                    </div>
                  )}
                </dl>
              </div>
            )}
            
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ProductDetailsModal;