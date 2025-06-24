import React from 'react';
import SwipeableCard from './SwipeableCard';
import { getImageUrl } from '../../utils/imageUrl';

const ProductCardStack = ({ 
  products, 
  currentIndex, 
  onSwipe, 
  onCardTap,
  onAddToCart,
  swipeHistory,
  hideInstructions 
}) => {
  // Get the next 3 products to display with looping
  const visibleCards = [];
  for (let i = 0; i < 3; i++) {
    const index = (currentIndex + i) % products.length;
    visibleCards.push({
      product: products[index],
      index: index,
      position: i
    });
  }

  // Calculate card styles based on position
  const getCardStyle = (position) => {
    const baseStyle = {
      position: 'absolute',
      width: '100%',
      height: '100%',
      transition: 'all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1)',
      cursor: position === 0 ? 'grab' : 'default'
    };

    switch (position) {
      case 0: // Top card - interactive
        return {
          ...baseStyle,
          zIndex: 30,
          transform: 'scale(1) translateY(0)',
          opacity: 1,
          filter: 'none'
        };
      case 1: // Middle card
        return {
          ...baseStyle,
          zIndex: 20,
          transform: 'scale(0.95) translateY(-20px)',
          opacity: 0.9,
          filter: 'blur(0.5px) brightness(0.95)',
          pointerEvents: 'none'
        };
      case 2: // Bottom card
        return {
          ...baseStyle,
          zIndex: 10,
          transform: 'scale(0.9) translateY(-40px)',
          opacity: 0.8,
          filter: 'blur(1px) brightness(0.9)',
          pointerEvents: 'none'
        };
      default:
        return baseStyle;
    }
  };


  return (
    <div className="relative w-full" style={{ paddingBottom: '140%', touchAction: 'none' }}>
      {/* Shadow effect for depth */}
      <div 
        className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-gray-200/20 to-transparent rounded-b-2xl pointer-events-none"
        style={{ transform: 'translateY(10px)' }}
      />
      
      {/* Render cards in reverse order so top card is last in DOM */}
      {visibleCards.reverse().map(({ product, index, position }) => (
        <div
          key={`${product.id}-${index}`}
          style={getCardStyle(position)}
        >
          {position === 0 ? (
            // Only the top card is swipeable
            <SwipeableCard
              product={product}
              onSwipe={onSwipe}
              onTap={() => onCardTap(product)}
              onAddToCart={onAddToCart}
              isTop={true}
            />
          ) : (
            // Background cards are static
            <div className="w-full h-full bg-white rounded-2xl shadow-lg overflow-hidden">
              <div style={{ height: '65%' }} className="relative overflow-hidden">
                {product?.images?.[0] ? (
                  <img
                    src={getImageUrl(product?.images?.[0], 'pinterest')}
                    alt={product?.name || 'Produs'}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
              </div>
              <div className="p-4 flex flex-col" style={{ height: '35%' }}>
                <h3 className="font-bold text-lg text-gray-900 line-clamp-1 mb-2">
                  {product?.name || 'Produs'}
                </h3>
                <p className="text-sm text-gray-600 line-clamp-3 mb-3 flex-1">
                  {product?.description || 'Produs disponibil în stoc'}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xl font-bold text-green-600">
                    {new Intl.NumberFormat('ro-RO', {
                      style: 'currency',
                      currency: 'RON'
                    }).format(product?.price || 0)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Swipe instruction */}
      {!hideInstructions && (
        <div className="absolute -top-12 left-0 right-0 text-center" style={{ 
          opacity: hideInstructions ? 0 : 0.4,
          transition: 'opacity 0.5s ease-out'
        }}>
          <span className="text-xs text-gray-400">swipe up to add to cart</span>
        </div>
      )}
    </div>
  );
};

export default ProductCardStack;