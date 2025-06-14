import { useState, useCallback, useRef, useEffect } from 'react';
import { useApiToast } from '../components/common/Toast';

// Hook for managing async operations with loading states
export const useAsyncOperation = (options = {}) => {
  const {
    onSuccess,
    onError,
    showSuccessToast = false,
    showErrorToast = true,
    successMessage = 'Operațiunea a fost finalizată cu succes.',
    errorMessage = 'A apărut o eroare. Încercați din nou.',
    autoReset = true,
    resetDelay = 2000
  } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);
  
  const toast = useApiToast();
  const timeoutRef = useRef(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const execute = useCallback(async (asyncFunction, ...args) => {
    try {
      setIsLoading(true);
      setError(null);
      setIsSuccess(false);
      setData(null);

      const result = await asyncFunction(...args);
      
      setData(result);
      setIsSuccess(true);
      
      if (showSuccessToast) {
        toast.showSuccess(successMessage);
      }
      
      if (onSuccess) {
        onSuccess(result);
      }

      // Auto reset success state
      if (autoReset) {
        timeoutRef.current = setTimeout(() => {
          setIsSuccess(false);
        }, resetDelay);
      }

      return result;
    } catch (err) {
      console.error('Async operation error:', err);
      
      setError(err);
      
      if (showErrorToast) {
        if (err.isNetworkError) {
          toast.handleNetworkError();
        } else {
          toast.handleApiError(err, errorMessage);
        }
      }
      
      if (onError) {
        onError(err);
      }

      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [onSuccess, onError, showSuccessToast, showErrorToast, successMessage, errorMessage, autoReset, resetDelay, toast]);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setData(null);
    setIsSuccess(false);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  return {
    execute,
    reset,
    isLoading,
    error,
    data,
    isSuccess,
    // Convenience status flags
    isIdle: !isLoading && !error && !isSuccess,
    isError: !!error,
    hasData: !!data
  };
};

// Hook for form submissions
export const useFormSubmission = (options = {}) => {
  const {
    onSuccess,
    onError,
    successMessage = 'Formularul a fost trimis cu succes.',
    errorMessage = 'Eroare la trimiterea formularului. Încercați din nou.',
    ...restOptions
  } = options;

  const asyncOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage,
    errorMessage,
    ...restOptions
  });

  const submitForm = useCallback(async (formData, submitFunction) => {
    return asyncOp.execute(submitFunction, formData);
  }, [asyncOp.execute]);

  return {
    ...asyncOp,
    submitForm,
    isSubmitting: asyncOp.isLoading,
    submissionError: asyncOp.error,
    isSubmitted: asyncOp.isSuccess
  };
};

// Hook for data fetching
export const useDataFetching = (options = {}) => {
  const {
    onSuccess,
    onError,
    errorMessage = 'Eroare la încărcarea datelor. Încercați din nou.',
    ...restOptions
  } = options;

  const asyncOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: false,
    showErrorToast: true,
    errorMessage,
    ...restOptions
  });

  const fetchData = useCallback(async (fetchFunction, ...args) => {
    return asyncOp.execute(fetchFunction, ...args);
  }, [asyncOp.execute]);

  const refetch = useCallback(async (fetchFunction, ...args) => {
    return fetchData(fetchFunction, ...args);
  }, [fetchData]);

  return {
    ...asyncOp,
    fetchData,
    refetch,
    isFetching: asyncOp.isLoading,
    fetchError: asyncOp.error,
    isFetched: asyncOp.isSuccess
  };
};

// Hook for delete operations
export const useDeleteOperation = (options = {}) => {
  const {
    onSuccess,
    onError,
    successMessage = 'Elementul a fost șters cu succes.',
    errorMessage = 'Eroare la ștergerea elementului. Încercați din nou.',
    confirmMessage = 'Sigur doriți să ștergeți acest element?',
    requireConfirmation = true,
    ...restOptions
  } = options;

  const asyncOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage,
    errorMessage,
    ...restOptions
  });

  const deleteItem = useCallback(async (deleteFunction, ...args) => {
    if (requireConfirmation) {
      const confirmed = window.confirm(confirmMessage);
      if (!confirmed) {
        return null;
      }
    }

    return asyncOp.execute(deleteFunction, ...args);
  }, [asyncOp.execute, requireConfirmation, confirmMessage]);

  return {
    ...asyncOp,
    deleteItem,
    isDeleting: asyncOp.isLoading,
    deleteError: asyncOp.error,
    isDeleted: asyncOp.isSuccess
  };
};

// Hook for update operations
export const useUpdateOperation = (options = {}) => {
  const {
    onSuccess,
    onError,
    successMessage = 'Elementul a fost actualizat cu succes.',
    errorMessage = 'Eroare la actualizarea elementului. Încercați din nou.',
    ...restOptions
  } = options;

  const asyncOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage,
    errorMessage,
    ...restOptions
  });

  const updateItem = useCallback(async (updateFunction, ...args) => {
    return asyncOp.execute(updateFunction, ...args);
  }, [asyncOp.execute]);

  return {
    ...asyncOp,
    updateItem,
    isUpdating: asyncOp.isLoading,
    updateError: asyncOp.error,
    isUpdated: asyncOp.isSuccess
  };
};

// Hook for cart operations
export const useCartOperation = (options = {}) => {
  const {
    onSuccess,
    onError,
    addSuccessMessage = 'Produs adăugat în coș.',
    removeSuccessMessage = 'Produs eliminat din coș.',
    updateSuccessMessage = 'Cantitatea a fost actualizată.',
    clearSuccessMessage = 'Coșul a fost golit.',
    errorMessage = 'Eroare la actualizarea coșului. Încercați din nou.',
    ...restOptions
  } = options;

  const addOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage: addSuccessMessage,
    errorMessage,
    ...restOptions
  });

  const removeOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage: removeSuccessMessage,
    errorMessage,
    ...restOptions
  });

  const updateOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage: updateSuccessMessage,
    errorMessage,
    ...restOptions
  });

  const clearOp = useAsyncOperation({
    onSuccess,
    onError,
    showSuccessToast: true,
    showErrorToast: true,
    successMessage: clearSuccessMessage,
    errorMessage,
    ...restOptions
  });

  const addToCart = useCallback(async (addFunction, ...args) => {
    return addOp.execute(addFunction, ...args);
  }, [addOp.execute]);

  const removeFromCart = useCallback(async (removeFunction, ...args) => {
    return removeOp.execute(removeFunction, ...args);
  }, [removeOp.execute]);

  const updateQuantity = useCallback(async (updateFunction, ...args) => {
    return updateOp.execute(updateFunction, ...args);
  }, [updateOp.execute]);

  const clearCart = useCallback(async (clearFunction, ...args) => {
    return clearOp.execute(clearFunction, ...args);
  }, [clearOp.execute]);

  return {
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    isAddingToCart: addOp.isLoading,
    isRemovingFromCart: removeOp.isLoading,
    isUpdatingQuantity: updateOp.isLoading,
    isClearingCart: clearOp.isLoading,
    cartError: addOp.error || removeOp.error || updateOp.error || clearOp.error,
    reset: () => {
      addOp.reset();
      removeOp.reset();
      updateOp.reset();
      clearOp.reset();
    }
  };
};

export default useAsyncOperation;