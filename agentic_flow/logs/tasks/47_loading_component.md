# Task 47: Create Loading component

## Task Details
- **ID**: 47_loading_component_creation
- **Title**: Create Loading component
- **Priority**: High
- **Estimate**: 10 minutes
- **Dependencies**: Tailwind CSS configuration (Task 43)

## Objective
Implement a reusable Loading component with spinner animation for async operations, providing visual feedback during API calls, form submissions, and other loading states throughout the application.

## Requirements
1. **Spinner Animation**: CSS/Tailwind-based rotating spinner
2. **Accessibility**: Proper ARIA labels and screen reader support
3. **Customizable**: Accept props for size, color variations
4. **Centered Layout**: Properly centered within its container
5. **Performance**: Lightweight implementation using CSS animations

## Technical Implementation

### 1. Loading Component (frontend/src/components/common/Loading.jsx)
```javascript
import React from 'react';

const Loading = ({ 
  size = 'medium', 
  color = 'primary', 
  message = 'Loading...', 
  fullScreen = false,
  className = '' 
}) => {
  // Size variations
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8', 
    large: 'w-12 h-12',
    extra: 'w-16 h-16'
  };

  // Color variations
  const colorClasses = {
    primary: 'border-primary-500',
    secondary: 'border-secondary-500', 
    white: 'border-white',
    gray: 'border-gray-500'
  };

  const spinnerClasses = `
    inline-block
    ${sizeClasses[size]}
    border-4
    border-solid
    ${colorClasses[color]}
    border-t-transparent
    rounded-full
    animate-spin
  `.trim().replace(/\s+/g, ' ');

  const containerClasses = fullScreen
    ? 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
    : 'flex items-center justify-center p-4';

  return (
    <div 
      className={`${containerClasses} ${className}`}
      role="status"
      aria-live="polite"
      aria-label={message}
    >
      <div className="flex flex-col items-center space-y-2">
        <div 
          className={spinnerClasses}
          aria-hidden="true"
        />
        {message && (
          <span className="text-sm text-gray-600 sr-only">
            {message}
          </span>
        )}
      </div>
    </div>
  );
};

// Export with default props
Loading.defaultProps = {
  size: 'medium',
  color: 'primary', 
  message: 'Loading...',
  fullScreen: false,
  className: ''
};

export default Loading;
```

### 2. Alternative Spinner Designs
```javascript
// Dots spinner variant
export const DotsLoading = ({ className = '' }) => (
  <div className={`flex space-x-1 ${className}`} role="status" aria-label="Loading">
    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
  </div>
);

// Pulse spinner variant  
export const PulseLoading = ({ className = '' }) => (
  <div className={`flex space-x-1 ${className}`} role="status" aria-label="Loading">
    <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse"></div>
    <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
    <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
  </div>
);
```

### 3. Usage Examples
```javascript
// Basic usage
<Loading />

// Large spinner with custom message
<Loading size="large" message="Processing your order..." />

// Full screen loading overlay
<Loading fullScreen={true} message="Please wait..." />

// Small inline loading
<Loading size="small" color="white" className="ml-2" />

// In a button
<button disabled>
  <Loading size="small" className="mr-2" />
  Submitting...
</button>

// In a card/container
<div className="bg-white p-6 rounded-lg">
  <Loading message="Loading products..." />
</div>
```

## Component Features

### 1. Size Variations
- **Small**: 16px (w-4 h-4) - for inline use, buttons
- **Medium**: 32px (w-8 h-8) - default size, cards
- **Large**: 48px (w-12 h-12) - page loading
- **Extra**: 64px (w-16 h-16) - full screen loading

### 2. Color Themes
- **Primary**: Brand color (primary-500)
- **Secondary**: Secondary color (secondary-500)  
- **White**: For dark backgrounds
- **Gray**: Neutral option

### 3. Accessibility Features
- **ARIA role**: `status` for screen readers
- **ARIA live**: `polite` for non-intrusive announcements
- **ARIA label**: Descriptive message for context
- **Screen reader text**: Hidden but readable message
- **Semantic structure**: Proper heading hierarchy

### 4. Animation Properties
- **CSS Transform**: Uses `transform: rotate()` for smooth animation
- **Hardware Acceleration**: GPU-accelerated animations
- **Performance**: 60fps animation with `will-change: transform`
- **Duration**: 1 second rotation cycle
- **Easing**: Linear timing for consistent speed

## Implementation Steps

### 1. Create Component File
- Create `/frontend/src/components/common/Loading.jsx`
- Implement base Loading component with spinner
- Add prop support for customization

### 2. Add Styling Classes
- Define size variations using Tailwind classes
- Implement color theme support
- Add animation keyframes

### 3. Accessibility Implementation
- Add ARIA attributes and roles
- Include screen reader support
- Test with keyboard navigation

### 4. Export and Integration
- Export component with proper defaults
- Add to main component index if needed
- Prepare for use in other components

## Testing Considerations

### 1. Visual Testing
- Verify spinner rotates smoothly
- Check all size variations render correctly
- Test color themes work properly
- Validate responsive behavior

### 2. Accessibility Testing  
- Screen reader announces loading state
- ARIA attributes are properly set
- Keyboard navigation doesn't break
- Focus management works correctly

### 3. Performance Testing
- Animation runs at 60fps
- No memory leaks during long loading
- CPU usage remains reasonable
- Works on mobile devices

## Integration Points

### 1. API Service Usage
```javascript
// In API service calls
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  setLoading(true);
  try {
    const data = await api.get('/products');
    setProducts(data);
  } finally {
    setLoading(false);
  }
};

return loading ? <Loading /> : <ProductList products={products} />;
```

### 2. Form Submission
```javascript
// In form components
const [submitting, setSubmitting] = useState(false);

const handleSubmit = async (formData) => {
  setSubmitting(true);
  try {
    await api.post('/orders', formData);
  } finally {
    setSubmitting(false);
  }
};

return (
  <button disabled={submitting}>
    {submitting ? <Loading size="small" /> : 'Submit Order'}
  </button>
);
```

### 3. Page Level Loading
```javascript
// In page components
const ProductsPage = () => {
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchProducts().finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Loading size="large" message="Loading products..." />;
  }

  return <ProductGrid products={products} />;
};
```

## Success Criteria
- Loading component renders with smooth spinning animation
- All size and color variations work correctly
- Component is accessible with proper ARIA attributes
- Can be used inline, in containers, and as full-screen overlay
- Performance is smooth on mobile and desktop devices
- Integration with forms and API calls works seamlessly