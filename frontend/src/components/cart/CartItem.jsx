import React, { useState } from 'react';
import { useCartContext } from '../../contexts/CartContext';

const CartItem = ({ item, className = '', showActions = true, compact = false }) => {
  const { 
    updateQuantity, 
    removeFromCart, 
    incrementQuantity, 
    decrementQuantity,
    formatPrice 
  } = useCartContext();
  
  const [isUpdating, setIsUpdating] = useState(false);
  const [quantityInput, setQuantityInput] = useState(item.quantity.toString());

  if (!item) return null;

  const {
    id,
    name,
    price,
    image,
    quantity,
    category,
    unit,
    isOrganic = false
  } = item;

  // Calculate item total
  const itemTotal = price * quantity;

  // Handle quantity input change
  const handleQuantityChange = (e) => {
    const value = e.target.value;
    setQuantityInput(value);
  };

  // Handle quantity input blur (apply changes)
  const handleQuantityBlur = () => {
    const newQuantity = parseInt(quantityInput);
    if (isNaN(newQuantity) || newQuantity < 0) {
      setQuantityInput(quantity.toString());
      return;
    }
    
    if (newQuantity === 0) {
      handleRemove();
      return;
    }
    
    if (newQuantity !== quantity) {
      setIsUpdating(true);
      updateQuantity(id, newQuantity);
      setTimeout(() => setIsUpdating(false), 300);
    }
  };

  // Handle quantity input key press
  const handleQuantityKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.target.blur();
    }
  };

  // Handle increment
  const handleIncrement = () => {
    setIsUpdating(true);
    incrementQuantity(id);
    setQuantityInput((quantity + 1).toString());
    setTimeout(() => setIsUpdating(false), 300);
  };

  // Handle decrement
  const handleDecrement = () => {
    if (quantity <= 1) {
      handleRemove();
      return;
    }
    
    setIsUpdating(true);
    decrementQuantity(id);
    setQuantityInput((quantity - 1).toString());
    setTimeout(() => setIsUpdating(false), 300);
  };

  // Handle remove item
  const handleRemove = () => {
    if (window.confirm(`Sigur vrei să elimini "${name}" din coș?`)) {
      removeFromCart(id);
    }
  };

  // Compact version for mobile or summary views
  if (compact) {
    return (
      <div className={`flex items-center gap-3 py-2 ${className}`}>
        {/* Product Image */}
        <img
          src={image || '/images/placeholder-product.jpg'}
          alt={name}
          className="w-12 h-12 object-cover rounded-md flex-shrink-0"
          onError={(e) => {
            e.target.src = '/images/placeholder-product.jpg';
          }}
        />
        
        {/* Product Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 text-sm truncate">
            {name}
          </h4>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{quantity}x</span>
            <span>{formatPrice(price)}</span>
            {unit && <span>/ {unit}</span>}
          </div>
        </div>
        
        {/* Total Price */}
        <div className="text-sm font-semibold text-gray-900">
          {formatPrice(itemTotal)}
        </div>
      </div>
    );
  }

  // Full version for cart page
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <div className="flex gap-4">
        {/* Product Image */}
        <div className="relative flex-shrink-0">
          <img
            src={image || '/images/placeholder-product.jpg'}
            alt={name}
            className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-lg"
            onError={(e) => {
              e.target.src = '/images/placeholder-product.jpg';
            }}
          />
          
          {/* Organic Badge */}
          {isOrganic && (
            <span className="absolute -top-1 -right-1 bg-green-500 text-white text-xs px-1 py-0.5 rounded-full">
              🌱
            </span>
          )}
        </div>

        {/* Product Details */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
            {/* Product Info */}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {name}
              </h3>
              
              {/* Category */}
              {category && (
                <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full mb-2">
                  {category}
                </span>
              )}
              
              {/* Price per unit */}
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                <span className="font-medium">{formatPrice(price)}</span>
                {unit && <span>/ {unit}</span>}
              </div>
            </div>

            {/* Actions */}
            {showActions && (
              <div className="flex flex-col sm:items-end gap-3">
                {/* Quantity Controls */}
                <div className="flex items-center gap-2">
                  <label htmlFor={`quantity-${id}`} className="sr-only">
                    Cantitate pentru {name}
                  </label>
                  
                  {/* Decrement Button */}
                  <button
                    type="button"
                    onClick={handleDecrement}
                    disabled={isUpdating}
                    className="w-10 h-10 sm:w-8 sm:h-8 flex items-center justify-center bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors text-lg sm:text-base"
                    aria-label={`Scade cantitatea pentru ${name}`}
                  >
                    −
                  </button>
                  
                  {/* Quantity Input */}
                  <input
                    id={`quantity-${id}`}
                    type="number"
                    min="0"
                    value={quantityInput}
                    onChange={handleQuantityChange}
                    onBlur={handleQuantityBlur}
                    onKeyPress={handleQuantityKeyPress}
                    disabled={isUpdating}
                    className={`w-16 h-10 sm:h-8 text-center border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base ${
                      isUpdating ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  />
                  
                  {/* Increment Button */}
                  <button
                    type="button"
                    onClick={handleIncrement}
                    disabled={isUpdating}
                    className="w-10 h-10 sm:w-8 sm:h-8 flex items-center justify-center bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors text-lg sm:text-base"
                    aria-label={`Crește cantitatea pentru ${name}`}
                  >
                    +
                  </button>
                </div>

                {/* Item Total */}
                <div className="text-lg font-bold text-gray-900">
                  {formatPrice(itemTotal)}
                </div>

                {/* Remove Button */}
                <button
                  type="button"
                  onClick={handleRemove}
                  className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors min-h-[44px] px-2 flex items-center justify-center"
                  aria-label={`Elimină ${name} din coș`}
                >
                  🗑️ Elimină
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Layout Adjustments */}
      <div className="block sm:hidden mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Total produs:</span>
          <span className="text-lg font-bold text-gray-900">
            {formatPrice(itemTotal)}
          </span>
        </div>
      </div>
    </div>
  );
};

// CartItem for readonly display (order confirmation, etc.)
export const ReadOnlyCartItem = ({ item, className = '' }) => (
  <CartItem 
    item={item} 
    className={className}
    showActions={false}
  />
);

// CartItem for summary/checkout display
export const SummaryCartItem = ({ item, className = '' }) => (
  <CartItem 
    item={item} 
    className={className}
    compact={true}
  />
);

// Loading skeleton for CartItem
export const CartItemSkeleton = () => (
  <div className="bg-white rounded-lg border border-gray-200 p-4">
    <div className="flex gap-4">
      {/* Image Skeleton */}
      <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gray-200 rounded-lg animate-pulse flex-shrink-0" />
      
      {/* Content Skeleton */}
      <div className="flex-1 space-y-3">
        <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/4" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3" />
      </div>
      
      {/* Actions Skeleton */}
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
          <div className="w-16 h-8 bg-gray-200 rounded animate-pulse" />
          <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="h-6 bg-gray-200 rounded animate-pulse w-20" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-16" />
      </div>
    </div>
  </div>
);

export default CartItem;