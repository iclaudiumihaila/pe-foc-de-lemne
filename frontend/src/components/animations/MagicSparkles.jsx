import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';

const Sparkle = ({ x, y, color, size, duration, delay }) => {
  const symbols = ['✨', '⭐', '🌟', '💫', '✦', '✧'];
  const symbol = symbols[Math.floor(Math.random() * symbols.length)];
  
  return (
    <div
      className="sparkle"
      style={{
        '--sparkle-x': `${x}px`,
        '--sparkle-y': `${y}px`,
        '--sparkle-color': color,
        '--sparkle-size': `${size}px`,
        '--sparkle-duration': `${duration}ms`,
        '--sparkle-delay': `${delay}ms`,
      }}
    >
      {symbol}
    </div>
  );
};

const MagicSparkles = ({ x, y, count = 12 }) => {
  const [sparkles, setSparkles] = useState([]);

  useEffect(() => {
    const newSparkles = Array.from({ length: count }, (_, i) => ({
      id: i,
      x: 0,
      y: 0,
      color: ['#FFD700', '#FFA500', '#FF69B4', '#00CED1', '#9370DB', '#32CD32', '#FF1493'][Math.floor(Math.random() * 7)],
      size: Math.random() * 12 + 8, // Smaller sparkles (8-20px)
      duration: Math.random() * 600 + 400, // Faster animation (400-1000ms)
      delay: Math.random() * 150, // Less delay spread
      angle: (i * 360) / count + Math.random() * 30 - 15,
      distance: Math.random() * 25 + 15, // Much smaller distance (15-40px)
    }));
    setSparkles(newSparkles);

    const timer = setTimeout(() => {
      setSparkles([]);
    }, 1000); // Cleanup faster

    return () => clearTimeout(timer);
  }, [count]);

  return (
    <div className="magic-sparkles-container" style={{ left: x, top: y }}>
      {sparkles.map((sparkle) => (
        <Sparkle
          key={sparkle.id}
          x={sparkle.distance * Math.cos((sparkle.angle * Math.PI) / 180)}
          y={sparkle.distance * Math.sin((sparkle.angle * Math.PI) / 180)}
          color={sparkle.color}
          size={sparkle.size}
          duration={sparkle.duration}
          delay={sparkle.delay}
        />
      ))}
    </div>
  );
};

export const showMagicSparkles = (element) => {
  if (!element) return;

  const rect = element.getBoundingClientRect();
  const x = rect.left + rect.width / 2;
  const y = rect.top + rect.height / 2;

  // Create container for sparkles
  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.pointerEvents = 'none';
  container.style.zIndex = '9999';
  container.style.left = '0';
  container.style.top = '0';
  document.body.appendChild(container);

  // Render sparkles
  const root = ReactDOM.createRoot(container);
  root.render(<MagicSparkles x={x} y={y} />);

  // Clean up after animation
  setTimeout(() => {
    root.unmount();
    document.body.removeChild(container);
  }, 2000);
};

export default MagicSparkles;