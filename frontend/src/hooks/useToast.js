// Re-export useToast from Toast component for convenience
export { useToast, useApiToast, TOAST_TYPES } from '../components/common/Toast';

// Additional helper for simplified toast calls
export const useSimpleToast = () => {
  const { showSuccess, showError, showWarning, showInfo } = useToast();
  
  return {
    showToast: (message, type = 'info') => {
      switch (type) {
        case 'success':
          showSuccess(message);
          break;
        case 'error':
          showError(message);
          break;
        case 'warning':
          showWarning(message);
          break;
        case 'info':
        default:
          showInfo(message);
          break;
      }
    }
  };
};