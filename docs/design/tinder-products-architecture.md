# Tinder-Style Products Feed Architecture

## Overview
Create a mobile-only swipeable products feed inspired by Tinder's card UI for product discovery and engagement.

## User Experience

### Mobile-Only Feature
- Route: `/products/swipe` (redirects to regular products page on desktop)
- Device detection: Show only on mobile devices (max-width: 768px)
- Fallback: Desktop users see regular grid view

### Swipe Interactions
- **Swipe Right**: Add product to cart (green overlay + cart icon)
- **Swipe Left**: Skip product (red overlay + X icon)  
- **Tap Card**: Show product details modal
- **Swipe Up**: Show more product info (optional)
- **Undo Button**: Restore last swiped product

### Visual Design
```
┌─────────────────┐
│   Header Nav    │
├─────────────────┤
│                 │
│  Product Stack  │
│   [3 cards]     │
│                 │
│ ❌    ❤️    ↩️  │ <- Action buttons
└─────────────────┘
```

## Technical Architecture

### 1. Component Structure
```
SwipeProducts/
├── SwipeProductsPage.jsx     // Main page with mobile detection
├── ProductCardStack.jsx      // Stack of 3 visible cards
├── SwipeableCard.jsx        // Individual swipeable card
├── SwipeActions.jsx         // Action buttons below cards
└── SwipeProductDetail.jsx   // Modal for product details
```

### 2. State Management
```javascript
{
  products: [],           // All products to swipe through
  currentIndex: 0,        // Current card index
  swipeHistory: [],       // For undo functionality (max 20 items)
  cartAdditions: [],      // Products added via swipe
  loading: false,
  hasMore: true,
  showDetailModal: false, // Product detail modal state
  selectedProduct: null,  // Product being viewed in detail
  offlineQueue: []        // Cart additions while offline
}
```

### 3. Library Choice
**Recommended**: `react-swipeable` (actively maintained)
- Pros: Lightweight, well-maintained, 645+ projects using it
- Handles touch gestures without heavy dependencies
- Better than HammerJS (unmaintained for 8 years)

Alternative: Custom implementation (~50 lines) for full control

### 4. Key Features

#### Product Loading Strategy
- Initial load: 20 products
- Preload next batch when 5 cards remaining
- Infinite scroll pattern

#### Animation Requirements
- Smooth card rotation on drag
- Spring physics for snap-back
- Opacity fade on swipe out
- Stack reordering animation

#### Cart Integration
```javascript
const handleSwipeRight = async (product) => {
  // Add to cart with visual feedback
  await addToCart(product, 1);
  showFloatingIndicator('+1', cardRef);
  // Move to next card
  setCurrentIndex(prev => prev + 1);
};
```

## Implementation Details

### 1. Mobile & Touch Detection
```javascript
const isTouchDevice = () => {
  return ('ontouchstart' in window) || 
    (navigator.maxTouchPoints > 0) ||
    (navigator.msMaxTouchPoints > 0);
};

const isMobile = () => {
  return isTouchDevice() && window.innerWidth <= 768;
};

// In SwipeProductsPage
if (!isMobile()) {
  return <Navigate to="/products" />;
}
```

### 2. Swipeable Card Component
```javascript
<Swipeable
  onSwipedLeft={() => handleSwipe('left')}
  onSwipedRight={() => handleSwipe('right')}
  onSwiping={handleSwiping}
  trackMouse={false} // Mobile only
  preventDefaultTouchmoveEvent={true}
>
  <ProductCard style={getCardStyle(index)} />
</Swipeable>
```

### 3. Stack Visualization
- Show 3 cards: current + 2 behind
- Scale and translate for depth effect
- Blur background cards slightly

### 4. Performance Optimizations
- Lazy load product images with Intersection Observer
- Virtualize card stack (only render visible)
- Debounce swipe actions
- Preload next images during idle
- Limit swipe history to last 20 items

### 5. Product Detail Modal
```javascript
const handleCardTap = (product) => {
  setSelectedProduct(product);
  setShowDetailModal(true);
  // Track analytics event
  trackEvent('product_detail_view', { productId: product.id });
};
```

### 6. Loading States
- **Initial Load**: Skeleton cards stack
- **Image Loading**: Blur placeholder with fade-in
- **Data Fetching**: Subtle loader at bottom of stack
- **Error State**: Retry card with error message

### 7. Accessibility Features
```javascript
// Keyboard navigation for accessibility mode
const handleKeyPress = (e) => {
  if (!accessibilityMode) return;
  
  switch(e.key) {
    case 'ArrowRight': handleSwipe('right'); break;
    case 'ArrowLeft': handleSwipe('left'); break;
    case 'Enter': handleCardTap(currentProduct); break;
    case 'u': handleUndo(); break;
  }
};
```

### 8. Error Handling
```javascript
// Error boundary wrapper
<ErrorBoundary fallback={<SwipeErrorFallback />}>
  <ProductCardStack />
</ErrorBoundary>

// Offline queue for cart additions
const handleOfflineCart = async (product) => {
  if (!navigator.onLine) {
    addToOfflineQueue(product);
    showToast('Produs salvat. Va fi adăugat când reveniți online.');
  }
};
```

### 9. Progressive Image Loading
```javascript
// Use native loading="lazy" with intersection observer fallback
<img 
  src={lowResUrl}
  data-src={highResUrl}
  loading="lazy"
  className="progressive-image"
  onLoad={handleImageLoad}
/>

## Data Flow

1. **Initial Load**: Fetch first batch of products
2. **User Swipes**: Update currentIndex, trigger animations
3. **Cart Action**: On right swipe, add to cart context
4. **Preload**: When approaching end, fetch more products
5. **Analytics**: Track swipe patterns for insights

## Edge Cases

1. **Network Issues**: Cache swiped products locally
2. **Empty State**: "No more products" card
3. **Cart Failures**: Queue additions, retry with notification
4. **Rapid Swiping**: Throttle to prevent UI glitches
5. **Device Rotation**: Lock to portrait or adapt layout

## Analytics Integration

### Events to Track
```javascript
// Using existing analyticsService
import { trackEvent } from '../services/analyticsService';

// Swipe events
trackEvent('product_swipe', {
  productId: product.id,
  direction: 'right' | 'left',
  timeOnCard: Date.now() - cardShowTime,
  cardIndex: currentIndex
});

// Detail view
trackEvent('product_detail_view', {
  productId: product.id,
  source: 'swipe_tap'
});

// Session metrics
trackEvent('swipe_session_end', {
  totalSwipes: swipeCount,
  rightSwipes: cartAdditions.length,
  leftSwipes: skippedCount,
  sessionDuration: Date.now() - sessionStart
});
```

### Metrics Dashboard
- Swipe right rate (cart additions)
- Swipe left rate (rejections)  
- Average time per card
- Most/least swiped products
- Conversion rate vs grid view

## Benefits

1. **Engagement**: Gamified shopping experience
2. **Discovery**: Users see more products per session
3. **Mobile-First**: Optimized for touch devices
4. **Data Collection**: Learn user preferences
5. **Social Potential**: Share liked products

## Future Enhancements

1. **Filters**: Pre-filter stack by category/price
2. **AI Recommendations**: Personalize product order
3. **Social Features**: See what friends liked
4. **Gamification**: Streaks, rewards for swiping
5. **Voice Commands**: "Add to cart" via voice