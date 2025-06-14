# Task 48: Create ErrorMessage component

## Task Details
- **ID**: 48_error_message_component_creation
- **Title**: Create ErrorMessage component
- **Priority**: High
- **Estimate**: 10 minutes
- **Dependencies**: Tailwind CSS configuration (Task 43)

## Objective
Implement a consistent ErrorMessage component to display error messages with standard styling, accessibility features, and dismissible functionality for use throughout the application in forms, API responses, and validation scenarios.

## Requirements
1. **Error Display**: Clear error message presentation with error styling
2. **Dismissible**: Optional close button to dismiss errors
3. **Accessibility**: Proper ARIA attributes and screen reader support
4. **Customizable**: Different error types (error, warning, info)
5. **Responsive**: Works on mobile and desktop layouts

## Technical Implementation

### 1. ErrorMessage Component (frontend/src/components/common/ErrorMessage.jsx)
```javascript
import React from 'react';

const ErrorMessage = ({ 
  message, 
  type = 'error', 
  dismissible = false,
  onDismiss,
  className = '',
  icon = true 
}) => {
  if (!message) return null;

  // Type-based styling
  const typeStyles = {
    error: {
      container: 'bg-red-50 border-red-200 text-red-800',
      icon: '❌',
      iconColor: 'text-red-500'
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      icon: '⚠️',
      iconColor: 'text-yellow-500'
    },
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: 'ℹ️',
      iconColor: 'text-blue-500'
    },
    success: {
      container: 'bg-green-50 border-green-200 text-green-800',
      icon: '✅',
      iconColor: 'text-green-500'
    }
  };

  const currentStyle = typeStyles[type] || typeStyles.error;

  return (
    <div 
      className={`
        flex items-start p-4 mb-4 border rounded-lg
        ${currentStyle.container}
        ${className}
      `}
      role="alert"
      aria-live="polite"
    >
      {icon && (
        <div className={`flex-shrink-0 mr-3 ${currentStyle.iconColor}`}>
          <span className="text-lg" aria-hidden="true">
            {currentStyle.icon}
          </span>
        </div>
      )}
      
      <div className="flex-1">
        <p className="text-sm font-medium">
          {message}
        </p>
      </div>

      {dismissible && onDismiss && (
        <button
          type="button"
          className={`
            flex-shrink-0 ml-3 p-1 rounded-md
            ${currentStyle.iconColor}
            hover:bg-opacity-20 hover:bg-current
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current
          `}
          onClick={onDismiss}
          aria-label="Dismiss error message"
        >
          <span className="text-lg" aria-hidden="true">×</span>
        </button>
      )}
    </div>
  );
};

// Specialized error components for common use cases
export const FormError = ({ error, ...props }) => (
  <ErrorMessage 
    message={error} 
    type="error" 
    className="mt-2"
    {...props} 
  />
);

export const APIError = ({ error, retry, ...props }) => (
  <ErrorMessage 
    message={error} 
    type="error" 
    dismissible={true}
    className="mb-4"
    {...props}
  />
);

export const ValidationError = ({ errors, ...props }) => {
  if (!errors || errors.length === 0) return null;
  
  return (
    <div className="space-y-2">
      {errors.map((error, index) => (
        <ErrorMessage 
          key={index}
          message={error} 
          type="error"
          icon={false}
          className="py-2 text-sm"
          {...props}
        />
      ))}
    </div>
  );
};

export default ErrorMessage;
```

### 2. Usage Examples
```javascript
// Basic error message
<ErrorMessage message="Something went wrong. Please try again." />

// Warning message
<ErrorMessage 
  message="Your session will expire in 5 minutes." 
  type="warning" 
/>

// Dismissible error
<ErrorMessage 
  message="Failed to load data." 
  type="error"
  dismissible={true}
  onDismiss={() => setError(null)}
/>

// Form validation error
<FormError error={formErrors.email} />

// API error with retry
<APIError 
  error="Network error occurred"
  onDismiss={() => setApiError(null)}
/>

// Multiple validation errors
<ValidationError errors={validationErrors} />
```

## Component Features

### 1. Message Types
- **Error**: Red styling for critical errors
- **Warning**: Yellow styling for warnings
- **Info**: Blue styling for informational messages
- **Success**: Green styling for success confirmations

### 2. Visual Design
- **Border and Background**: Subtle colored backgrounds with matching borders
- **Icons**: Emoji-based icons for visual identification
- **Typography**: Clear, readable text with appropriate contrast
- **Spacing**: Consistent padding and margins

### 3. Accessibility Features
- **ARIA role="alert"**: Announces errors to screen readers
- **aria-live="polite"**: Non-intrusive announcements
- **Keyboard navigation**: Focusable dismiss button
- **Color contrast**: WCAG compliant color combinations
- **Screen reader labels**: Descriptive button labels

### 4. Interactive Features
- **Dismissible**: Optional close button functionality
- **Auto-dismiss**: Can be configured with timeouts
- **Callback support**: onDismiss handler for state management

## Implementation Steps

### 1. Create Component File
- Create `/frontend/src/components/common/ErrorMessage.jsx`
- Implement base ErrorMessage component
- Add type-based styling system

### 2. Add Specialized Variants
- FormError for form validation
- APIError for API response errors
- ValidationError for multiple error lists

### 3. Styling Implementation
- Define color schemes for each message type
- Implement responsive design
- Add hover and focus states

### 4. Accessibility Enhancement
- Add ARIA attributes and roles
- Implement keyboard navigation
- Test with screen readers

## Styling System

### 1. Color Schemes
```javascript
const typeStyles = {
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: '❌',
    iconColor: 'text-red-500'
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: '⚠️', 
    iconColor: 'text-yellow-500'
  },
  // ... additional types
};
```

### 2. Layout Structure
- **Flexbox Layout**: Icon, message, and dismiss button alignment
- **Responsive Padding**: Consistent spacing across devices
- **Border Radius**: Rounded corners for modern appearance
- **Typography**: Appropriate font weights and sizes

## Integration Points

### 1. Form Validation
```javascript
// In form components
const [errors, setErrors] = useState({});

const validateForm = (data) => {
  const newErrors = {};
  if (!data.email) newErrors.email = 'Email is required';
  setErrors(newErrors);
};

return (
  <form>
    <input type="email" />
    <FormError error={errors.email} />
  </form>
);
```

### 2. API Error Handling
```javascript
// In API service components
const [apiError, setApiError] = useState(null);

const fetchData = async () => {
  try {
    const data = await api.get('/products');
    setProducts(data);
  } catch (error) {
    setApiError('Failed to load products. Please try again.');
  }
};

return (
  <>
    {apiError && (
      <APIError 
        error={apiError} 
        onDismiss={() => setApiError(null)}
      />
    )}
    <ProductList products={products} />
  </>
);
```

### 3. Global Error Handling
```javascript
// In app-level error boundary
const ErrorBoundary = ({ children }) => {
  const [error, setError] = useState(null);

  if (error) {
    return (
      <ErrorMessage 
        message="Something went wrong. Please refresh the page."
        type="error"
        dismissible={true}
        onDismiss={() => setError(null)}
      />
    );
  }

  return children;
};
```

## Testing Considerations

### 1. Visual Testing
- Verify all message types render correctly
- Check responsive behavior on mobile
- Test color contrast for accessibility
- Validate icon and text alignment

### 2. Interaction Testing
- Dismiss button functionality
- Keyboard navigation support
- Focus management
- Callback execution

### 3. Accessibility Testing
- Screen reader announcements
- ARIA attribute validation
- Color-only information alternatives
- Focus indicator visibility

## Success Criteria
- ErrorMessage component displays different message types correctly
- Dismissible functionality works with proper callbacks
- Component is fully accessible with ARIA attributes
- Specialized variants (FormError, APIError) work as expected
- Component integrates seamlessly with forms and API calls
- Styling is consistent with application design system