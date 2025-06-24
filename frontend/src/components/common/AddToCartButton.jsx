import React, { useState, useCallback, useRef } from 'react';
import { ShoppingCart } from 'lucide-react';
import { showFloatingIndicator } from '../animations/FloatingIndicator';
import { showMagicSparkles } from '../animations/MagicSparkles';

const AddToCartButton = ({ 
  onClick, 
  disabled = false, 
  className = '',
  children = 'Adaugă în coș',
  quantity = 1
}) => {
  const [buttonState, setButtonState] = useState('normal'); // normal, loading, success
  const buttonRef = useRef(null);

  const handleClick = useCallback(async (e) => {
    if (buttonState !== 'normal' || disabled) return;

    // Add magic effects immediately
    buttonRef.current?.classList.add('magic-wobble');
    showMagicSparkles(buttonRef.current);
    
    setButtonState('loading');
    
    try {
      // Call the parent's onClick handler
      if (onClick) {
        await onClick(e);
      }
      
      // Show success state
      setButtonState('success');
      
      // Add pulse effect on success
      buttonRef.current?.classList.add('magic-pulse');
      
      // Show floating indicator
      showFloatingIndicator(quantity, buttonRef.current);
      
      // Return to normal state after 1 second
      setTimeout(() => {
        setButtonState('normal');
        buttonRef.current?.classList.remove('magic-wobble', 'magic-pulse');
      }, 1000);
    } catch (error) {
      // If there's an error, return to normal state immediately
      setButtonState('normal');
      buttonRef.current?.classList.remove('magic-wobble', 'magic-pulse');
      console.error('Error adding to cart:', error);
    }
  }, [onClick, buttonState, disabled, quantity]);

  const getButtonContent = () => {
    // Check if children is a React element (icon-only mode)
    const isIconOnly = React.isValidElement(children);
    
    switch (buttonState) {
      case 'loading':
        return (
          <div className="relative flex items-center justify-center">
            <div className="relative w-5 h-5">
              <ShoppingCart className="absolute inset-0 animate-icon-morph" strokeWidth={2} />
            </div>
            {!isIconOnly && (
              <span className="absolute opacity-0">{children}</span>
            )}
          </div>
        );
      case 'success':
        return (
          <div className="relative flex items-center justify-center">
            <div className="relative w-5 h-5">
              <svg 
                className="absolute inset-0 animate-icon-success" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            {!isIconOnly && (
              <span className="absolute opacity-0">{children}</span>
            )}
          </div>
        );
      default:
        return isIconOnly ? (
          children
        ) : (
          <>
            <ShoppingCart className="w-4 h-4" strokeWidth={2} />
            <span>{children}</span>
          </>
        );
    }
  };

  const getButtonClasses = () => {
    const baseClasses = 'relative flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 overflow-hidden';
    
    const stateClasses = {
      normal: 'bg-green-600 hover:bg-green-700 text-white',
      loading: 'bg-green-600 text-white cursor-wait',
      success: 'bg-green-600 text-white'
    };

    const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : '';

    return `${baseClasses} ${stateClasses[buttonState]} ${disabledClasses} ${className}`;
  };

  return (
    <button
      ref={buttonRef}
      type="button"
      onClick={handleClick}
      disabled={disabled || buttonState !== 'normal'}
      className={getButtonClasses()}
      aria-live="polite"
      aria-busy={buttonState === 'loading'}
    >
      {getButtonContent()}
    </button>
  );
};

export default AddToCartButton;