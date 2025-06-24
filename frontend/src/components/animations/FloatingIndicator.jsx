import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';

const FloatingIndicator = ({ quantity = 1, position, onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Remove the indicator after animation completes
    const timer = setTimeout(() => {
      setIsVisible(false);
      if (onComplete) {
        onComplete();
      }
    }, 1000); // Match animation duration

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!isVisible || !position) return null;

  const indicator = (
    <div
      className="fixed pointer-events-none z-50"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <div className="animate-float-up text-2xl font-bold text-orange-600">
        +{quantity}
      </div>
    </div>
  );

  // Render to document body using portal
  return ReactDOM.createPortal(indicator, document.body);
};

// Manager component to handle multiple floating indicators
export const FloatingIndicatorManager = () => {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    // Listen for custom events to show indicators
    const handleShowIndicator = (event) => {
      const { quantity, position } = event.detail;
      const id = Date.now() + Math.random(); // Unique ID for each indicator

      setIndicators(prev => [...prev, { id, quantity, position }]);
    };

    window.addEventListener('showFloatingIndicator', handleShowIndicator);

    return () => {
      window.removeEventListener('showFloatingIndicator', handleShowIndicator);
    };
  }, []);

  const handleComplete = (id) => {
    setIndicators(prev => prev.filter(indicator => indicator.id !== id));
  };

  return (
    <>
      {indicators.map(indicator => (
        <FloatingIndicator
          key={indicator.id}
          quantity={indicator.quantity}
          position={indicator.position}
          onComplete={() => handleComplete(indicator.id)}
        />
      ))}
    </>
  );
};

// Helper function to trigger floating indicator
export const showFloatingIndicator = (quantity, buttonElement) => {
  if (!buttonElement) return;

  const rect = buttonElement.getBoundingClientRect();
  const position = {
    x: rect.left + rect.width / 2 - 20, // Center horizontally
    y: rect.top - 10, // Start slightly above button
  };

  // Dispatch custom event
  window.dispatchEvent(new CustomEvent('showFloatingIndicator', {
    detail: { quantity, position }
  }));
};

export default FloatingIndicator;