import React, { useState } from 'react';
import { useCartContext } from '../../contexts/CartContext';
import { getImageUrl } from '../../utils/imageUrl';

const CartItem = ({ item, isMobile = false }) => {
  const { 
    updateQuantity, 
    removeFromCart, 
    formatPrice 
  } = useCartContext();
  
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  if (!item) return null;

  const {
    id,
    name,
    price,
    image,
    quantity,
    unit
  } = item;

  const itemTotal = price * quantity;

  const handleQuantityChange = (newQuantity) => {
    if (newQuantity === 0) {
      handleRemove();
      return;
    }
    
    setIsUpdating(true);
    updateQuantity(id, newQuantity);
    setTimeout(() => setIsUpdating(false), 300);
  };

  const handleRemove = () => {
    setIsRemoving(true);
    setTimeout(() => {
      removeFromCart(id);
    }, 300);
  };

  if (isMobile) {
    return (
      <div 
        className={`bg-gray-50 rounded-lg overflow-hidden transition-all duration-300 ${
          isRemoving ? 'transform scale-95 opacity-0' : ''
        }`}
      >
        <div className="p-4">
          <div className="flex gap-3">
            {/* Product Image */}
            <div className="relative">
              <img
                src={getImageUrl(image)}
                alt={name}
                className="w-20 h-20 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = '/images/placeholder-product.jpg';
                }}
              />
            </div>

            {/* Product Details */}
            <div className="flex-1">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900 text-base leading-tight">{name}</h3>
                <button
                  onClick={handleRemove}
                  className="p-1 -m-1 text-gray-400 hover:text-red-600 transition-colors"
                  aria-label={`Elimină ${name}`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <p className="text-sm text-gray-600 mb-3">
                {formatPrice(price)}{unit && ` / ${unit}`}
              </p>

              {/* Mobile Quantity and Price */}
              <div className="flex items-center justify-between">
                {/* Quantity Controls */}
                <div className="flex items-center bg-gray-100 rounded-full">
                  <button
                    onClick={() => handleQuantityChange(quantity - 1)}
                    disabled={isUpdating}
                    className="w-10 h-10 flex items-center justify-center text-gray-600 hover:text-gray-800 disabled:opacity-50 transition-colors"
                    aria-label="Scade cantitatea"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
                    </svg>
                  </button>
                  
                  <span className="w-12 text-center font-semibold text-gray-900">{quantity}</span>
                  
                  <button
                    onClick={() => handleQuantityChange(quantity + 1)}
                    disabled={isUpdating}
                    className="w-10 h-10 flex items-center justify-center text-gray-600 hover:text-gray-800 disabled:opacity-50 transition-colors"
                    aria-label="Crește cantitatea"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>

                {/* Total Price */}
                <div className="text-right">
                  <p className="font-semibold text-lg text-gray-900">{formatPrice(itemTotal)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Desktop version (existing)
  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0">
      {/* Product Image */}
      <img
        src={getImageUrl(image)}
        alt={name}
        className="w-16 h-16 object-cover rounded"
        onError={(e) => {
          e.target.src = '/images/placeholder-product.jpg';
        }}
      />

      {/* Product Info */}
      <div className="flex-1">
        <h3 className="font-medium text-gray-900">{name}</h3>
        <p className="text-sm text-gray-500">
          {formatPrice(price)}{unit && ` / ${unit}`}
        </p>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleQuantityChange(quantity - 1)}
          disabled={isUpdating}
          className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 disabled:opacity-50"
          aria-label="Scade cantitatea"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
          </svg>
        </button>
        
        <span className="w-8 text-center font-medium">{quantity}</span>
        
        <button
          onClick={() => handleQuantityChange(quantity + 1)}
          disabled={isUpdating}
          className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 disabled:opacity-50"
          aria-label="Crește cantitatea"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Price */}
      <div className="text-right">
        <p className="font-medium text-gray-900">{formatPrice(itemTotal)}</p>
      </div>

      {/* Remove Button */}
      <button
        onClick={handleRemove}
        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
        aria-label={`Elimină ${name}`}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

export default CartItem;