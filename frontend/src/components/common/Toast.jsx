import React, { useState, useEffect, createContext, useContext } from 'react';

// Toast Context
const ToastContext = createContext();

// Toast types
const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Toast configuration
const TOAST_CONFIG = {
  duration: 5000, // 5 seconds
  maxToasts: 5,
  position: 'top-right' // top-right, top-left, bottom-right, bottom-left
};

// Individual Toast Component
const Toast = ({ id, type, message, duration, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  useEffect(() => {
    // Fade in animation
    const fadeInTimer = setTimeout(() => setIsVisible(true), 10);
    
    // Auto dismiss
    const dismissTimer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => {
      clearTimeout(fadeInTimer);
      clearTimeout(dismissTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [duration]);

  const handleClose = () => {
    setIsRemoving(true);
    setTimeout(() => {
      onClose(id);
    }, 300); // Match animation duration
  };

  const getToastStyles = () => {
    const baseStyles = "flex items-start p-4 rounded-lg shadow-lg transition-all duration-300 transform";
    const visibilityStyles = isVisible && !isRemoving 
      ? "translate-x-0 opacity-100" 
      : "translate-x-full opacity-0";

    const typeStyles = {
      [TOAST_TYPES.SUCCESS]: "bg-green-50 border border-green-200",
      [TOAST_TYPES.ERROR]: "bg-red-50 border border-red-200",
      [TOAST_TYPES.WARNING]: "bg-yellow-50 border border-yellow-200",
      [TOAST_TYPES.INFO]: "bg-blue-50 border border-blue-200"
    };

    return `${baseStyles} ${visibilityStyles} ${typeStyles[type]}`;
  };

  const getIconAndColors = () => {
    switch (type) {
      case TOAST_TYPES.SUCCESS:
        return {
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          ),
          iconColor: "text-green-600",
          textColor: "text-green-800",
          buttonColor: "text-green-600 hover:text-green-800"
        };
      case TOAST_TYPES.ERROR:
        return {
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
          iconColor: "text-red-600",
          textColor: "text-red-800",
          buttonColor: "text-red-600 hover:text-red-800"
        };
      case TOAST_TYPES.WARNING:
        return {
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.18 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          ),
          iconColor: "text-yellow-600",
          textColor: "text-yellow-800",
          buttonColor: "text-yellow-600 hover:text-yellow-800"
        };
      case TOAST_TYPES.INFO:
        return {
          icon: (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          iconColor: "text-blue-600",
          textColor: "text-blue-800",
          buttonColor: "text-blue-600 hover:text-blue-800"
        };
      default:
        return {
          icon: null,
          iconColor: "text-gray-600",
          textColor: "text-gray-800",
          buttonColor: "text-gray-600 hover:text-gray-800"
        };
    }
  };

  const { icon, iconColor, textColor, buttonColor } = getIconAndColors();

  return (
    <div className={getToastStyles()} role="alert" aria-live="polite">
      {/* Icon */}
      <div className={`flex-shrink-0 ${iconColor}`}>
        {icon}
      </div>

      {/* Message */}
      <div className={`ml-3 flex-1 ${textColor}`}>
        <p className="text-sm font-medium">{message}</p>
      </div>

      {/* Close Button */}
      <button
        onClick={handleClose}
        className={`ml-3 flex-shrink-0 ${buttonColor} transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center`}
        aria-label="Închide notificarea"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

// Toast Container Component
const ToastContainer = ({ toasts, onRemoveToast, position }) => {
  const getContainerStyles = () => {
    const baseStyles = "fixed z-50 p-4 space-y-3 pointer-events-none";
    
    const positionStyles = {
      'top-right': "top-0 right-0",
      'top-left': "top-0 left-0",
      'bottom-right': "bottom-0 right-0",
      'bottom-left': "bottom-0 left-0"
    };

    return `${baseStyles} ${positionStyles[position]}`;
  };

  if (toasts.length === 0) return null;

  return (
    <div className={getContainerStyles()}>
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto w-full max-w-sm">
          <Toast
            id={toast.id}
            type={toast.type}
            message={toast.message}
            duration={toast.duration}
            onClose={onRemoveToast}
          />
        </div>
      ))}
    </div>
  );
};

// Toast Provider Component
export const ToastProvider = ({ children, position = TOAST_CONFIG.position }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (type, message, duration = TOAST_CONFIG.duration) => {
    const id = Date.now().toString();
    const newToast = { id, type, message, duration };

    setToasts(currentToasts => {
      const updatedToasts = [...currentToasts, newToast];
      // Limit the number of toasts
      return updatedToasts.slice(-TOAST_CONFIG.maxToasts);
    });

    return id;
  };

  const removeToast = (id) => {
    setToasts(currentToasts => currentToasts.filter(toast => toast.id !== id));
  };

  const clearAllToasts = () => {
    setToasts([]);
  };

  const showSuccess = (message, duration) => addToast(TOAST_TYPES.SUCCESS, message, duration);
  const showError = (message, duration) => addToast(TOAST_TYPES.ERROR, message, duration);
  const showWarning = (message, duration) => addToast(TOAST_TYPES.WARNING, message, duration);
  const showInfo = (message, duration) => addToast(TOAST_TYPES.INFO, message, duration);

  const contextValue = {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearAllToasts
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer
        toasts={toasts}
        onRemoveToast={removeToast}
        position={position}
      />
    </ToastContext.Provider>
  );
};

// Hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

// Convenience hook for common toast patterns
export const useApiToast = () => {
  const toast = useToast();

  const handleApiError = (error, customMessage = null) => {
    if (customMessage) {
      toast.showError(customMessage);
    } else if (error.message) {
      toast.showError(error.message);
    } else {
      toast.showError('A apărut o eroare neașteptată.');
    }
  };

  const handleApiSuccess = (message = 'Operația s-a finalizat cu succes.') => {
    toast.showSuccess(message);
  };

  const handleNetworkError = () => {
    toast.showError('Problemă de conexiune. Verificați internetul și încercați din nou.');
  };

  return {
    ...toast,
    handleApiError,
    handleApiSuccess,
    handleNetworkError
  };
};

export { TOAST_TYPES };
export default Toast;