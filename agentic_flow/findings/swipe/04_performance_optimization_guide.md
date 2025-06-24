# Swipe Performance Optimization Guide

## Table of Contents
1. [Current Performance Analysis](#current-performance-analysis)
2. [CSS Optimization Techniques](#css-optimization-techniques)
3. [JavaScript Performance Best Practices](#javascript-performance-best-practices)
4. [GPU Acceleration Techniques](#gpu-acceleration-techniques)
5. [Memory Management](#memory-management)
6. [Mobile-Specific Optimizations](#mobile-specific-optimizations)
7. [Image Optimization](#image-optimization)
8. [Performance Metrics & Monitoring](#performance-metrics--monitoring)
9. [Implementation Checklist](#implementation-checklist)

## Current Performance Analysis

### Identified Performance Issues

1. **Frequent Re-renders**
   - State updates on every swipe movement causing unnecessary re-renders
   - All cards re-rendering when only the top card is moving

2. **DOM Manipulation**
   - Direct style manipulation during swipe (lines 45-47 in SwipeableCard)
   - Creating/removing DOM elements for success indicators

3. **Memory Leaks**
   - Event listeners not properly cleaned up
   - Animations continuing after component unmount

4. **Image Loading**
   - All images loaded eagerly, including hidden cards
   - No progressive loading or optimization

### Performance Bottlenecks

```javascript
// Current issues in SwipeableCard.jsx:
// 1. State updates on every pixel of movement
onSwiping: (eventData) => {
  setSwiping(true);        // Re-render
  setDeltaX(eventData.deltaX);  // Re-render
  setDeltaY(eventData.deltaY);  // Re-render
  setSwipeDirection(...);       // Re-render
}

// 2. Direct DOM manipulation
cardRef.current.style.transition = 'all 0.5s ease-out';
cardRef.current.style.transform = `translateX(${translateX}) rotate(${rotation})`;
```

## CSS Optimization Techniques

### 1. GPU Acceleration

```css
/* Enable GPU acceleration for smooth animations */
.swipeable-card {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force GPU layer */
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Use transform3d for better performance */
.swipeable-card.swiping {
  transform: translate3d(var(--x), var(--y), 0) rotate(var(--rotation));
}
```

### 2. Reduce Repaints and Reflows

```css
/* Isolate layout changes */
.card-stack-container {
  contain: layout style paint;
  position: relative;
  isolation: isolate;
}

/* Use CSS variables for dynamic values */
.swipeable-card {
  --x: 0;
  --y: 0;
  --rotation: 0deg;
  transform: translate3d(var(--x), var(--y), 0) rotate(var(--rotation));
}
```

### 3. Optimize Animations

```css
/* Use optimal timing functions */
.swipe-transition {
  transition: transform 0.3s cubic-bezier(0.4, 0.0, 0.2, 1),
              opacity 0.3s ease-out;
}

/* Disable animations on low-end devices */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* Use CSS-only animations where possible */
@keyframes swipeOut {
  from {
    transform: translate3d(0, 0, 0) rotate(0);
    opacity: 1;
  }
  to {
    transform: translate3d(var(--exit-x), var(--exit-y), 0) rotate(var(--exit-rotation));
    opacity: 0;
  }
}
```

## JavaScript Performance Best Practices

### 1. Optimize Event Handling

```javascript
// Use RAF for smooth updates
const updateCardPosition = useCallback((deltaX, deltaY) => {
  if (animationFrameId.current) {
    cancelAnimationFrame(animationFrameId.current);
  }
  
  animationFrameId.current = requestAnimationFrame(() => {
    if (cardRef.current) {
      cardRef.current.style.setProperty('--x', `${deltaX}px`);
      cardRef.current.style.setProperty('--y', `${deltaY}px`);
      cardRef.current.style.setProperty('--rotation', `${deltaX * 0.1}deg`);
    }
  });
}, []);

// Batch state updates
const updateSwipeState = useCallback((eventData) => {
  // Use a single state object instead of multiple states
  setSwipeState(prev => ({
    ...prev,
    deltaX: eventData.deltaX,
    deltaY: eventData.deltaY,
    swiping: true,
    direction: Math.abs(eventData.deltaX) > 50 
      ? (eventData.deltaX > 0 ? 'right' : 'left') 
      : null
  }));
}, []);
```

### 2. Debounce and Throttle

```javascript
// Throttle swipe updates for better performance
const throttledSwipeUpdate = useMemo(
  () => throttle(updateSwipeState, 16), // ~60fps
  [updateSwipeState]
);

// Debounce expensive calculations
const debouncedOverlayOpacity = useMemo(
  () => debounce(calculateOverlayOpacity, 50),
  []
);
```

### 3. Memoization

```javascript
// Memoize expensive calculations
const overlayOpacity = useMemo(() => {
  if (!swiping || !swipeDirection) return 0;
  const threshold = 100;
  const progress = Math.abs(deltaX) / threshold;
  return Math.min(1, progress);
}, [swiping, swipeDirection, deltaX]);

// Memoize static components
const StaticProductInfo = React.memo(({ product }) => (
  <div className="product-info">
    <h3>{product.name}</h3>
    <p>{product.price}</p>
  </div>
));
```

## GPU Acceleration Techniques

### 1. Layer Creation

```javascript
// Force GPU layers for animated elements
const cardStyle = {
  willChange: isTop ? 'transform, opacity' : 'auto',
  transform: `translate3d(0, 0, ${position * -1}px)`, // Z-index with 3D
  contain: 'layout style paint'
};
```

### 2. Composite-Only Properties

```javascript
// Use only GPU-accelerated properties
const animateCard = (element, x, y, rotation) => {
  // Good: Only transform and opacity
  element.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rotation}deg)`;
  element.style.opacity = calculateOpacity(x);
  
  // Avoid: Properties that trigger reflow/repaint
  // element.style.left = x + 'px';
  // element.style.width = newWidth + 'px';
};
```

### 3. Transform Matrix

```javascript
// Use matrix transforms for complex animations
const getTransformMatrix = (x, y, rotation, scale) => {
  const rad = rotation * (Math.PI / 180);
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  
  return `matrix(${cos * scale}, ${sin * scale}, ${-sin * scale}, ${cos * scale}, ${x}, ${y})`;
};
```

## Memory Management

### 1. Cleanup Event Listeners

```javascript
useEffect(() => {
  const handleTouchMove = (e) => {
    if (isSwiping) e.preventDefault();
  };
  
  document.addEventListener('touchmove', handleTouchMove, { passive: false });
  
  return () => {
    document.removeEventListener('touchmove', handleTouchMove);
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
    }
  };
}, [isSwiping]);
```

### 2. Limit Card Stack Size

```javascript
// Only render visible cards + buffer
const getVisibleCards = (products, currentIndex) => {
  const VISIBLE_CARDS = 3;
  const BUFFER_CARDS = 2;
  
  return products.slice(
    currentIndex,
    currentIndex + VISIBLE_CARDS + BUFFER_CARDS
  );
};

// Remove old cards from memory
useEffect(() => {
  if (currentIndex > 10) {
    // Clear references to swiped cards
    setSwipeHistory(prev => prev.slice(-10));
  }
}, [currentIndex]);
```

### 3. Image Memory Management

```javascript
// Preload only next few images
const preloadImages = useCallback((products, startIndex) => {
  const PRELOAD_COUNT = 5;
  const imagesToPreload = products
    .slice(startIndex, startIndex + PRELOAD_COUNT)
    .map(p => p.images?.[0])
    .filter(Boolean);
  
  imagesToPreload.forEach(src => {
    const img = new Image();
    img.src = getImageUrl(src);
  });
}, []);

// Clean up loaded images
const cleanupImages = useCallback((products, beforeIndex) => {
  // Implementation to remove images from memory
  // This is browser-dependent
}, []);
```

## Mobile-Specific Optimizations

### 1. Touch Event Optimization

```javascript
// Use passive event listeners where possible
const touchHandlers = {
  onTouchStart: { passive: true },
  onTouchMove: { passive: false }, // Need preventDefault
  onTouchEnd: { passive: true }
};

// Optimize touch responsiveness
const handleTouchStart = useCallback((e) => {
  // Store initial touch position
  touchStartX.current = e.touches[0].clientX;
  touchStartY.current = e.touches[0].clientY;
  touchStartTime.current = Date.now();
}, []);
```

### 2. Reduce JavaScript Execution

```javascript
// Use CSS for animations when possible
const triggerSwipeAnimation = (direction) => {
  cardRef.current.classList.add(`swipe-out-${direction}`);
  // Let CSS handle the animation
};

// Minimize JS calculations during swipe
const calculateSwipeVelocity = useCallback((deltaX, deltaTime) => {
  // Simple velocity calculation
  return Math.abs(deltaX / deltaTime);
}, []);
```

### 3. Network-Aware Loading

```javascript
// Adjust quality based on connection
const getImageQuality = () => {
  const connection = navigator.connection;
  if (!connection) return 'high';
  
  switch (connection.effectiveType) {
    case 'slow-2g':
    case '2g':
      return 'low';
    case '3g':
      return 'medium';
    default:
      return 'high';
  }
};

// Implement progressive loading
const loadProductBatch = async (page, quality) => {
  const params = {
    page,
    limit: quality === 'low' ? 10 : 20,
    imageQuality: quality
  };
  
  return api.get('/products', { params });
};
```

## Image Optimization

### 1. Lazy Loading

```javascript
const LazyImage = ({ src, alt, className }) => {
  const [imageSrc, setImageSrc] = useState(null);
  const imageRef = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setImageSrc(src);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );
    
    if (imageRef.current) {
      observer.observe(imageRef.current);
    }
    
    return () => observer.disconnect();
  }, [src]);
  
  return (
    <img
      ref={imageRef}
      src={imageSrc || '/placeholder.jpg'}
      alt={alt}
      className={className}
      loading="lazy"
    />
  );
};
```

### 2. Progressive Image Loading

```javascript
const ProgressiveImage = ({ src, placeholder, alt }) => {
  const [currentSrc, setCurrentSrc] = useState(placeholder);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      setCurrentSrc(src);
      setLoading(false);
    };
  }, [src]);
  
  return (
    <div className="progressive-image-container">
      <img
        src={currentSrc}
        alt={alt}
        className={`progressive-image ${loading ? 'loading' : 'loaded'}`}
      />
    </div>
  );
};
```

### 3. Image Format Optimization

```javascript
// Use modern image formats with fallbacks
const OptimizedImage = ({ src, alt }) => {
  const filename = src.split('.')[0];
  
  return (
    <picture>
      <source srcSet={`${filename}.webp`} type="image/webp" />
      <source srcSet={`${filename}.jpg`} type="image/jpeg" />
      <img src={src} alt={alt} loading="lazy" />
    </picture>
  );
};
```

## Performance Metrics & Monitoring

### 1. Key Metrics to Track

```javascript
// Swipe performance metrics
const trackSwipePerformance = {
  // Frame rate during swipe
  measureFrameRate: () => {
    let lastTime = performance.now();
    let frames = 0;
    
    const measureFrame = () => {
      frames++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        console.log(`FPS: ${frames}`);
        frames = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFrame);
    };
    
    measureFrame();
  },
  
  // Swipe responsiveness
  measureSwipeLatency: (startTime) => {
    const latency = performance.now() - startTime;
    performanceMonitor.recordMetric('Swipe Latency', latency);
  },
  
  // Animation smoothness
  measureAnimationJank: () => {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 16.67) { // Longer than 1 frame at 60fps
          console.warn('Long frame detected:', entry.duration);
        }
      }
    });
    
    observer.observe({ entryTypes: ['measure'] });
  }
};
```

### 2. Performance Budgets

```javascript
const performanceBudgets = {
  // JavaScript execution time
  swipeHandler: 8, // ms
  renderCycle: 16, // ms (60fps)
  
  // Memory usage
  maxMemoryUsage: 50, // MB
  maxDOMNodes: 1000,
  
  // Network
  imageLoadTime: 1000, // ms
  apiResponseTime: 500, // ms
  
  // User-centric metrics
  timeToInteractive: 3000, // ms
  firstContentfulPaint: 1500 // ms
};
```

### 3. Testing Methodology

```javascript
// Performance testing utilities
const performanceTests = {
  // Test swipe smoothness
  async testSwipePerformance() {
    const results = [];
    
    for (let i = 0; i < 100; i++) {
      const startTime = performance.now();
      
      // Simulate swipe
      await simulateSwipe({
        startX: 150,
        startY: 300,
        endX: 350,
        endY: 300,
        duration: 300
      });
      
      const duration = performance.now() - startTime;
      results.push(duration);
    }
    
    return {
      average: results.reduce((a, b) => a + b) / results.length,
      min: Math.min(...results),
      max: Math.max(...results),
      p95: results.sort((a, b) => a - b)[Math.floor(results.length * 0.95)]
    };
  },
  
  // Test memory usage
  async testMemoryUsage() {
    const initial = performance.memory.usedJSHeapSize;
    
    // Perform actions
    for (let i = 0; i < 50; i++) {
      await simulateSwipe({ direction: i % 2 === 0 ? 'left' : 'right' });
    }
    
    const final = performance.memory.usedJSHeapSize;
    const increase = (final - initial) / 1048576; // Convert to MB
    
    return {
      initial: initial / 1048576,
      final: final / 1048576,
      increase,
      leaked: increase > 10 // More than 10MB increase might indicate a leak
    };
  }
};
```

## Implementation Checklist

### Immediate Optimizations (High Impact)
- [ ] Implement RAF-based position updates
- [ ] Batch state updates into single object
- [ ] Add `will-change` and `transform3d` to cards
- [ ] Implement lazy loading for images
- [ ] Limit rendered cards to visible + buffer
- [ ] Use CSS variables for dynamic styles
- [ ] Add cleanup for event listeners

### Medium-Term Optimizations
- [ ] Implement virtual scrolling for card stack
- [ ] Add progressive image loading
- [ ] Optimize touch event handling
- [ ] Implement network-aware loading
- [ ] Add performance monitoring
- [ ] Memoize expensive calculations
- [ ] Use Web Workers for heavy computations

### Long-Term Optimizations
- [ ] Implement service worker for caching
- [ ] Add WebP/AVIF image support
- [ ] Implement predictive preloading
- [ ] Add performance budgets to CI/CD
- [ ] Implement A/B testing for optimizations
- [ ] Create performance dashboard
- [ ] Add automated performance regression tests

## Code Examples

### Optimized SwipeableCard Component

```javascript
const SwipeableCard = React.memo(({ product, onSwipe, isTop }) => {
  const cardRef = useRef(null);
  const animationFrameId = useRef(null);
  
  // Single state object for better performance
  const [swipeState, setSwipeState] = useState({
    deltaX: 0,
    deltaY: 0,
    swiping: false,
    direction: null
  });
  
  // RAF-based position update
  const updatePosition = useCallback((x, y) => {
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
    }
    
    animationFrameId.current = requestAnimationFrame(() => {
      if (cardRef.current) {
        cardRef.current.style.setProperty('--x', `${x}px`);
        cardRef.current.style.setProperty('--y', `${y}px`);
        cardRef.current.style.setProperty('--rotation', `${x * 0.1}deg`);
      }
    });
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, []);
  
  const handlers = useSwipeable({
    onSwiping: throttle((eventData) => {
      setSwipeState(prev => ({
        deltaX: eventData.deltaX,
        deltaY: eventData.deltaY,
        swiping: true,
        direction: Math.abs(eventData.deltaX) > 50
          ? (eventData.deltaX > 0 ? 'right' : 'left')
          : null
      }));
      
      updatePosition(eventData.deltaX, eventData.deltaY);
    }, 16),
    
    onSwipedLeft: () => handleSwipeComplete('left'),
    onSwipedRight: () => handleSwipeComplete('right'),
    
    preventScrollOnSwipe: true,
    trackMouse: false,
    trackTouch: true
  });
  
  // Only re-render when necessary
  return (
    <div
      ref={cardRef}
      {...handlers}
      className="swipeable-card"
      style={{
        '--x': 0,
        '--y': 0,
        '--rotation': '0deg'
      }}
    >
      {/* Card content */}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for memo
  return prevProps.product.id === nextProps.product.id &&
         prevProps.isTop === nextProps.isTop;
});
```

### Performance Monitoring Hook

```javascript
const useSwipePerformance = () => {
  const metricsRef = useRef({
    swipes: 0,
    totalLatency: 0,
    frameDrops: 0
  });
  
  const trackSwipe = useCallback((startTime) => {
    const latency = performance.now() - startTime;
    metricsRef.current.swipes++;
    metricsRef.current.totalLatency += latency;
    
    if (latency > 16.67) {
      metricsRef.current.frameDrops++;
    }
    
    // Log every 10 swipes
    if (metricsRef.current.swipes % 10 === 0) {
      const avgLatency = metricsRef.current.totalLatency / metricsRef.current.swipes;
      console.log('Swipe Performance:', {
        averageLatency: avgLatency.toFixed(2),
        frameDropRate: (metricsRef.current.frameDrops / metricsRef.current.swipes * 100).toFixed(1) + '%'
      });
    }
  }, []);
  
  return { trackSwipe };
};
```

## Conclusion

Performance optimization for swipe interactions requires a multi-faceted approach combining CSS optimizations, JavaScript best practices, and careful memory management. The key is to:

1. **Minimize DOM manipulations** - Use CSS transforms and variables
2. **Batch updates** - Reduce re-renders and use RAF
3. **Optimize for mobile** - Consider limited resources and touch events
4. **Monitor continuously** - Track metrics and set budgets
5. **Test thoroughly** - Use real devices and network conditions

By implementing these optimizations, you can achieve smooth 60fps swipe interactions even on low-end mobile devices while maintaining a responsive and engaging user experience.