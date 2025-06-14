import React from 'react';
import { useCartContext } from '../../contexts/CartContext';

const ProductCard = ({ product, onAddToCart, className = '' }) => {
  const { addToCart } = useCartContext();
  
  if (!product) return null;

  const {
    name,
    price,
    image,
    description,
    category,
    unit,
    inStock = true,
    isOrganic = false,
    quantity = 1
  } = product;

  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    } else {
      addToCart(product, quantity);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  };

  return (
    <div className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 max-w-sm w-full ${className}`}>
      {/* Product Image */}
      <div className="relative">
        <img
          src={image || '/images/placeholder-product.jpg'}
          alt={name}
          className="w-full h-48 object-cover rounded-t-lg"
          onError={(e) => {
            e.target.src = '/images/placeholder-product.jpg';
          }}
        />
        
        {/* Organic Badge */}
        {isOrganic && (
          <span className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
            🌱 Organic
          </span>
        )}
        
        {/* Stock Status */}
        {!inStock && (
          <span className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            Stoc epuizat
          </span>
        )}
      </div>

      {/* Product Information */}
      <div className="p-4">
        {/* Category */}
        {category && (
          <span className="inline-block bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full mb-2">
            {category}
          </span>
        )}
        
        {/* Product Name */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {name}
        </h3>
        
        {/* Description */}
        {description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {description}
          </p>
        )}
        
        {/* Price and Unit */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-xl font-bold text-primary-600">
              {formatPrice(price)}
            </span>
            {unit && (
              <span className="text-sm text-gray-500 ml-1">
                / {unit}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Add to Cart Button */}
      <div className="px-4 pb-4">
        <button
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base ${
            inStock 
              ? 'bg-primary-600 hover:bg-primary-700 text-white' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          disabled={!inStock}
          onClick={handleAddToCart}
        >
          <span>🛒</span>
          {inStock ? 'Adaugă în coș' : 'Stoc epuizat'}
        </button>
      </div>
    </div>
  );
};

// Skeleton loader for loading states
export const ProductCardSkeleton = () => (
  <div className="bg-white rounded-lg shadow-md max-w-sm">
    <div className="w-full h-48 bg-gray-200 animate-pulse rounded-t-lg" />
    <div className="p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3" />
      <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
      <div className="h-6 bg-gray-200 rounded animate-pulse w-1/2" />
    </div>
    <div className="px-4 pb-4">
      <div className="h-10 bg-gray-200 rounded animate-pulse w-full" />
    </div>
  </div>
);

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
          src={product.image || '/images/placeholder-product.jpg'}
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
            <button
              className={`p-2 rounded-lg text-sm min-h-[44px] min-w-[44px] flex items-center justify-center ${
                product.inStock
                  ? 'text-primary-600 hover:bg-primary-50'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
              onClick={handleAddToCart}
              disabled={!product.inStock}
              aria-label={`Adaugă ${product.name} în coș`}
            >
              🛒
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;