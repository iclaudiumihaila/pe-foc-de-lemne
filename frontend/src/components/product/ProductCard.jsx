import React, { useState } from 'react';
import { useCartContext } from '../../contexts/CartContext';
import AddToCartButton from '../common/AddToCartButton';
import { getImageUrl } from '../../utils/imageUrl';
import ProductDetailsModal from './ProductDetailsModal';

const ProductCard = ({ product, onAddToCart, className = '' }) => {
  const { addToCart } = useCartContext();
  const [showModal, setShowModal] = useState(false);
  
  if (!product) return null;

  const {
    name,
    image,
    inStock = true,
    quantity = 1
  } = product;

  const handleAddToCart = (e, quantityToAdd) => {
    // Handle both event objects and direct calls
    if (e && e.stopPropagation) {
      e.stopPropagation(); // Prevent modal from opening when clicking cart button
    }
    if (onAddToCart) {
      onAddToCart(product, quantityToAdd || quantity || 1);
    } else {
      addToCart(product, quantityToAdd || quantity || 1);
    }
  };

  return (
    <>
      <div 
        className={`relative group cursor-pointer overflow-hidden rounded-lg bg-gray-50 min-h-[200px] sm:min-h-[250px] ${className}`}
        onClick={() => setShowModal(true)}
      >
        {/* Product Image - fixed height with cover */}
      <img
        src={getImageUrl(image, 'pinterest')}
        alt={name}
        className="w-full h-full object-cover"
        loading="lazy"
        onError={(e) => {
          // Fallback to medium size if pinterest not available
          if (!e.target.src.includes('_medium')) {
            e.target.src = getImageUrl(image, 'medium');
          } else {
            e.target.src = '/images/placeholder-product.jpg';
          }
        }}
      />
      
      {/* Product name overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 via-black/30 to-transparent p-3 pb-2">
        <h3 className="text-white text-xs font-medium leading-tight line-clamp-2 mb-1">
          {name}
        </h3>
      </div>
      
      {/* Cart button */}
      <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
        <AddToCartButton
          onClick={handleAddToCart}
          disabled={!inStock}
          className="!w-8 !h-8 !p-0 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm !text-white shadow-sm"
          quantity={1}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </AddToCartButton>
      </div>
      
      {/* Stock badge */}
      {!inStock && (
        <div className="absolute top-2 left-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
          Stoc epuizat
        </div>
      )}
      </div>

      {/* Product Details Modal */}
      <ProductDetailsModal 
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        product={product}
        onAddToCart={(prod, qty) => handleAddToCart(null, qty)}
      />
    </>
  );
};

// Skeleton loader for loading states
export const ProductCardSkeleton = () => {
  // Random heights for skeleton to mimic Pinterest variety
  const heights = ['h-48', 'h-56', 'h-64', 'h-72', 'h-80'];
  const randomHeight = heights[Math.floor(Math.random() * heights.length)];
  
  return (
    <div className="bg-gray-200 rounded-2xl animate-pulse">
      <div className={`w-full ${randomHeight}`} />
    </div>
  );
};

// Compact variant for list views
export const CompactProductCard = ({ product, onAddToCart, className = '' }) => {
  const { addToCart } = useCartContext();
  
  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    } else {
      addToCart(product, 1);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm p-3 w-full ${className}`}>
      <div className="flex gap-3">
        {/* Small Product Image */}
        <img
          src={getImageUrl(product.image)}
          alt={product.name}
          className="w-16 h-16 object-cover rounded-md flex-shrink-0"
          onError={(e) => {
            e.target.src = '/images/placeholder-product.jpg';
          }}
        />
        
        {/* Product Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 truncate">
            {product.name}
          </h4>
          <p className="text-sm text-gray-500 truncate">
            {product.category}
          </p>
          <div className="flex items-center justify-between mt-2">
            <span className="font-semibold text-primary-600">
              {formatPrice(product.price)}
            </span>
            <AddToCartButton
              onClick={handleAddToCart}
              disabled={!product.inStock}
              quantity={1}
              className="!p-2 !min-h-[44px] !min-w-[44px]"
            >
              <span className="text-xl">🛒</span>
            </AddToCartButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;