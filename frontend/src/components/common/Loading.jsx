import React from 'react';

const Loading = ({ 
  size = 'medium', 
  color = 'primary', 
  message = 'Se încarcă...', 
  fullScreen = false,
  className = '',
  variant = 'spinner',
  showMessage = false
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

  const renderLoadingIndicator = () => {
    switch (variant) {
      case 'dots':
        return <DotsLoading className="" />;
      case 'pulse':
        return <PulseLoading className="" />;
      case 'bars':
        return <BarsLoading className="" />;
      case 'spinner':
      default:
        return (
          <div 
            className={spinnerClasses}
            aria-hidden="true"
          />
        );
    }
  };

  return (
    <div 
      className={`${containerClasses} ${className}`}
      role="status"
      aria-live="polite"
      aria-label={message}
    >
      <div className="flex flex-col items-center space-y-2">
        {renderLoadingIndicator()}
        {(showMessage && message) && (
          <span className={`text-sm text-gray-600 ${fullScreen ? 'text-white' : ''}`}>
            {message}
          </span>
        )}
        {/* Hidden message for screen readers */}
        <span className="sr-only">
          {message}
        </span>
      </div>
    </div>
  );
};

// Alternative spinner designs for variety
export const DotsLoading = ({ className = '', color = 'green' }) => {
  const colorClass = color === 'green' ? 'bg-green-600' : 'bg-primary-500';
  return (
    <div className={`flex space-x-1 ${className}`} role="status" aria-label="Se încarcă">
      <div className={`w-2 h-2 ${colorClass} rounded-full animate-bounce`}></div>
      <div className={`w-2 h-2 ${colorClass} rounded-full animate-bounce`} style={{ animationDelay: '0.1s' }}></div>
      <div className={`w-2 h-2 ${colorClass} rounded-full animate-bounce`} style={{ animationDelay: '0.2s' }}></div>
    </div>
  );
};

export const PulseLoading = ({ className = '', color = 'green' }) => {
  const colorClass = color === 'green' ? 'bg-green-600' : 'bg-primary-500';
  return (
    <div className={`flex space-x-1 ${className}`} role="status" aria-label="Se încarcă">
      <div className={`w-3 h-3 ${colorClass} rounded-full animate-pulse`}></div>
      <div className={`w-3 h-3 ${colorClass} rounded-full animate-pulse`} style={{ animationDelay: '0.2s' }}></div>
      <div className={`w-3 h-3 ${colorClass} rounded-full animate-pulse`} style={{ animationDelay: '0.4s' }}></div>
    </div>
  );
};

export const BarsLoading = ({ className = '', color = 'green' }) => {
  const colorClass = color === 'green' ? 'bg-green-600' : 'bg-primary-500';
  return (
    <div className={`flex space-x-1 items-end ${className}`} role="status" aria-label="Se încarcă">
      <div className={`w-1 h-4 ${colorClass} animate-pulse`} style={{ animationDelay: '0s' }}></div>
      <div className={`w-1 h-6 ${colorClass} animate-pulse`} style={{ animationDelay: '0.2s' }}></div>
      <div className={`w-1 h-3 ${colorClass} animate-pulse`} style={{ animationDelay: '0.4s' }}></div>
      <div className={`w-1 h-5 ${colorClass} animate-pulse`} style={{ animationDelay: '0.6s' }}></div>
    </div>
  );
};

// Page-level loading component
export const PageLoading = ({ 
  message = 'Se încarcă pagina...', 
  className = '' 
}) => (
  <div className={`min-h-screen bg-gray-50 flex items-center justify-center ${className}`}>
    <div className="text-center">
      <Loading 
        size="large" 
        showMessage={true} 
        message={message}
        color="primary"
      />
    </div>
  </div>
);

// Component section loading
export const SectionLoading = ({ 
  message = 'Se încarcă...', 
  className = '',
  height = 'h-32'
}) => (
  <div className={`${height} bg-white rounded-lg border border-gray-200 flex items-center justify-center ${className}`}>
    <Loading 
      size="medium" 
      showMessage={true} 
      message={message}
      variant="dots"
    />
  </div>
);

// Inline loading for buttons and small components
export const InlineLoading = ({ 
  message = 'Se procesează...', 
  size = 'small',
  className = '' 
}) => (
  <div className={`inline-flex items-center space-x-2 ${className}`}>
    <Loading 
      size={size} 
      variant="spinner"
      color="primary"
      className="p-0"
    />
    <span className="text-sm text-gray-600">{message}</span>
  </div>
);

export default Loading;