import React from 'react';

const ErrorMessage = ({ 
  message, 
  type = 'error', 
  dismissible = false,
  onDismiss,
  onRetry,
  className = '',
  icon = true,
  showRetry = false,
  retryText = 'Încercați din nou',
  children
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
      `.trim().replace(/\s+/g, ' ')}
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
        
        {/* Additional content */}
        {children && (
          <div className="mt-2">
            {children}
          </div>
        )}
        
        {/* Retry button */}
        {showRetry && onRetry && (
          <div className="mt-3">
            <button
              onClick={onRetry}
              className="text-sm font-medium underline hover:no-underline transition-all min-h-[44px] px-2 flex items-center"
              aria-label={retryText}
            >
              🔄 {retryText}
            </button>
          </div>
        )}
      </div>

      {dismissible && onDismiss && (
        <button
          type="button"
          className={`
            flex-shrink-0 ml-3 p-2 rounded-md min-w-[44px] min-h-[44px] flex items-center justify-center
            ${currentStyle.iconColor}
            hover:bg-opacity-20 hover:bg-current
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current
          `.trim().replace(/\s+/g, ' ')}
          onClick={onDismiss}
          aria-label="Închide mesajul"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
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

export const APIError = ({ error, onRetry, ...props }) => (
  <ErrorMessage 
    message={error} 
    type="error" 
    dismissible={true}
    showRetry={!!onRetry}
    onRetry={onRetry}
    className="mb-4"
    {...props}
  />
);

export const NetworkError = ({ onRetry, ...props }) => (
  <ErrorMessage 
    message="Problemă de conexiune. Verificați internetul și încercați din nou."
    type="error" 
    showRetry={!!onRetry}
    onRetry={onRetry}
    retryText="Verificați conexiunea"
    {...props}
  >
    <p className="text-xs mt-1 text-gray-600">
      Asigurați-vă că sunteți conectat la internet și că serverul este disponibil.
    </p>
  </ErrorMessage>
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

export const ServerError = ({ onRetry, ...props }) => (
  <ErrorMessage 
    message="Eroare la server. Încercați din nou în câteva minute."
    type="error" 
    showRetry={!!onRetry}
    onRetry={onRetry}
    retryText="Încercați din nou"
    {...props}
  >
    <p className="text-xs mt-1 text-gray-600">
      Dacă problema persistă, contactați suportul la 0700 123 456.
    </p>
  </ErrorMessage>
);

export default ErrorMessage;