import React, { useState, useRef, useEffect } from 'react';
import { X, ShoppingCart } from 'lucide-react';
import { getImageUrl } from '../../utils/imageUrl';
import ProductDetailsModal from '../product/ProductDetailsModal';

const SwipeableCard = ({ product, onSwipe, onTap, isTop, onAddToCart }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [velocity, setVelocity] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const [touchStartTime, setTouchStartTime] = useState(0);
  const [totalMovement, setTotalMovement] = useState(0);
  const cardRef = useRef(null);
  const startTimeRef = useRef(null);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isExpanded) {
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
    } else {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    }
    
    return () => {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
    };
  }, [isExpanded]);

  useEffect(() => {
    const card = cardRef.current;
    if (!card || !isTop) return;

    const handleTouchStart = (e) => {
      const touch = e.touches[0];
      setStartPos({ x: touch.clientX, y: touch.clientY });
      setTouchStartTime(Date.now());
      setTotalMovement(0);
      startTimeRef.current = Date.now();
      // Don't preventDefault here - only on actual drag
      // Don't set isDragging yet - wait for movement
    };

    const handleTouchMove = (e) => {
      const touch = e.touches[0];
      const deltaX = touch.clientX - startPos.x;
      const deltaY = touch.clientY - startPos.y;
      const movement = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      
      setTotalMovement(movement);
      
      // Only start dragging after 10px of movement
      if (movement > 10 && !isDragging) {
        setIsDragging(true);
      }
      
      if (isDragging) {
        setPosition({ x: deltaX, y: deltaY });
        
        // Calculate velocity
        const timeDiff = Date.now() - startTimeRef.current;
        if (timeDiff > 0) {
          const currentVelocity = Math.abs(deltaX) / timeDiff;
          setVelocity(currentVelocity);
        }
        
        e.preventDefault();
      }
    };

    const handleTouchEnd = (e) => {
      const touchDuration = Date.now() - touchStartTime;
      
      // Check for tap first (short duration and minimal movement)
      if (touchDuration < 200 && totalMovement < 10) {
        // It's a tap! Open the modal
        setIsExpanded(true);
        setPosition({ x: 0, y: 0 });
        setIsDragging(false);
        return;
      }
      
      // Not a tap, check for swipes
      const horizontalThreshold = velocity > 0.5 ? 50 : 100; // Lower threshold for fast swipes
      const verticalThreshold = 100; // Threshold for vertical swipe
      
      // Check for upward swipe first (add to cart)
      if (position.y < -verticalThreshold && Math.abs(position.x) < horizontalThreshold) {
        // Upward swipe detected - add to cart
        cardRef.current.style.transition = 'all 0.5s ease-out';
        cardRef.current.style.transform = `translateY(-150%) scale(0.8)`;
        cardRef.current.style.opacity = '0';
        
        setTimeout(() => {
          onSwipe('up');
        }, 300);
      } else if (Math.abs(position.x) > horizontalThreshold) {
        // Horizontal swipe detected - skip product
        const direction = position.x > 0 ? 'right' : 'left';
        
        // Animate card flying out
        cardRef.current.style.transition = 'all 0.5s ease-out';
        cardRef.current.style.transform = `translateX(${direction === 'right' ? '150%' : '-150%'}) rotate(${direction === 'right' ? '30deg' : '-30deg'})`;
        cardRef.current.style.opacity = '0';
        
        setTimeout(() => {
          onSwipe(direction);
        }, 300);
      } else {
        // Spring back
        setPosition({ x: 0, y: 0 });
      }
      setIsDragging(false);
      setVelocity(0);
    };

    card.addEventListener('touchstart', handleTouchStart, { passive: false });
    card.addEventListener('touchmove', handleTouchMove, { passive: false });
    card.addEventListener('touchend', handleTouchEnd, { passive: false });

    return () => {
      card.removeEventListener('touchstart', handleTouchStart);
      card.removeEventListener('touchmove', handleTouchMove);
      card.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isDragging, startPos, position, onSwipe, isTop, totalMovement, touchStartTime, velocity]);

  if (!product) return null;

  const cardStyle = {
    transform: `translate(${position.x}px, ${position.y}px) rotate(${position.x * 0.1}deg)`,
    transition: isDragging ? 'none' : 'all 0.3s ease-out',
    touchAction: 'none',
    userSelect: 'none',
    WebkitUserSelect: 'none',
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  return (
    <div
      ref={cardRef}
      className="w-full h-full bg-white rounded-2xl shadow-xl overflow-hidden relative"
      style={cardStyle}
      onClick={() => {
        if (!isDragging) {
          setIsExpanded(true);
        }
      }}
    >
      {/* Product Image */}
      <div style={{ height: '65%' }} className="relative overflow-hidden">
        {product?.images?.[0] ? (
          <img 
            src={getImageUrl(product.images[0], 'pinterest')}
            alt={product?.name || 'Produs'}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-20 h-20 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        
        {/* Stock warning badge */}
        {product?.stock_quantity && product.stock_quantity < 10 && product.stock_quantity > 0 && (
          <div className="absolute top-4 right-4 bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            Doar {product.stock_quantity} în stoc
          </div>
        )}
      </div>

      {/* Product Info */}
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
        {product?.unit && product.unit !== 'bucată' && (
          <span className="text-sm text-gray-500 mt-2">per {product.unit}</span>
        )}
      </div>

      {/* Visual feedback overlays */}
      {/* SKIP LEFT overlay */}
      <div 
        className="absolute inset-0 bg-gradient-to-br from-gray-400/20 to-gray-500/20 flex items-center justify-center pointer-events-none"
        style={{ 
          opacity: isDragging && position.x < -50 ? Math.min(1, Math.abs(position.x) / 200) : 0,
          transition: 'opacity 0.2s ease-out'
        }}
      >
        <div className="bg-gray-500 text-white p-4 rounded-full transform -rotate-12">
          <X className="w-16 h-16" strokeWidth={3} />
        </div>
        <span className="absolute top-16 left-16 text-gray-500 text-6xl font-black transform -rotate-12 select-none"
              style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.1)' }}>
          SKIP
        </span>
      </div>

      {/* SKIP RIGHT overlay */}
      <div 
        className="absolute inset-0 bg-gradient-to-bl from-gray-400/20 to-gray-500/20 flex items-center justify-center pointer-events-none"
        style={{ 
          opacity: isDragging && position.x > 50 ? Math.min(1, Math.abs(position.x) / 200) : 0,
          transition: 'opacity 0.2s ease-out'
        }}
      >
        <div className="bg-gray-500 text-white p-4 rounded-full transform rotate-12">
          <X className="w-16 h-16" strokeWidth={3} />
        </div>
        <span className="absolute top-16 right-16 text-gray-500 text-6xl font-black transform rotate-12 select-none"
              style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.1)' }}>
          SKIP
        </span>
      </div>

      {/* ADD TO CART upward swipe overlay */}
      <div 
        className="absolute inset-0 pointer-events-none rounded-2xl overflow-hidden"
        style={{ 
          opacity: isDragging && position.y < -50 && Math.abs(position.x) < 50 ? Math.min(1, Math.abs(position.y) / 100) : 0,
          transition: 'opacity 0.2s ease-out'
        }}
      >
        {/* Solid green background */}
        <div 
          className="absolute inset-0 bg-green-600"
          style={{
            opacity: isDragging && position.y < -50 && Math.abs(position.x) < 50 ? 0.9 : 0,
            transition: 'opacity 0.2s ease-out'
          }}
        />
        
        {/* Content on top of green background */}
        <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative" style={{
          transform: `translateY(${Math.max(0, position.y / 2)}px)`,
          transition: isDragging ? 'none' : 'transform 0.3s ease-out'
        }}>
          <div className="bg-white shadow-2xl p-6 rounded-full">
            <ShoppingCart 
              className="w-20 h-20 text-green-600" 
              strokeWidth={2.5}
              fill={position.y < -100 ? 'currentColor' : 'none'}
            />
            <div 
              className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-xl shadow-lg"
              style={{
                transform: `scale(${position.y < -100 ? 1 : 0})`,
                transition: 'transform 0.2s ease-out'
              }}
            >
              +
            </div>
          </div>
          <div 
            className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
            style={{
              opacity: position.y < -100 ? 1 : 0,
              transform: `translateX(-50%) translateY(${position.y < -100 ? 0 : 10}px)`,
              transition: 'all 0.2s ease-out'
            }}
          >
            <span className="text-white font-bold text-lg drop-shadow-lg">Adaugă în coș</span>
          </div>
        </div>
        </div>
      </div>

      {/* Product Details Modal */}
      <ProductDetailsModal 
        isOpen={isExpanded}
        onClose={() => {
          setIsExpanded(false);
        }}
        product={product}
        onAddToCart={onAddToCart}
      />
    </div>
  );
};

export default SwipeableCard;