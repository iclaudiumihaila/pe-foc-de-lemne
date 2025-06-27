import { useState, useEffect } from 'react';
import { useToast } from '../components/common/Toast';

// Network status hook
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastOfflineTime, setLastOfflineTime] = useState(null);
  const [connectionType, setConnectionType] = useState('unknown');
  const toast = useToast();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      
      // Show reconnection message if we were offline
      if (lastOfflineTime) {
        const offlineDuration = Date.now() - lastOfflineTime;
        if (offlineDuration > 5000) { // Only show if offline for more than 5 seconds
          toast.showSuccess('Conexiunea la internet a fost restabilită.');
        }
        setLastOfflineTime(null);
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setLastOfflineTime(Date.now());
      toast.showWarning('Conexiunea la internet s-a pierdut. Unele funcții pot fi limitate.');
    };

    const handleConnectionChange = () => {
      if (navigator.connection) {
        setConnectionType(navigator.connection.effectiveType || 'unknown');
      }
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Listen for connection changes (if supported)
    if (navigator.connection) {
      navigator.connection.addEventListener('change', handleConnectionChange);
      setConnectionType(navigator.connection.effectiveType || 'unknown');
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if (navigator.connection) {
        navigator.connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, [lastOfflineTime, toast]);

  return {
    isOnline,
    connectionType,
    isSlowConnection: connectionType === 'slow-2g' || connectionType === '2g',
    lastOfflineTime
  };
};

// Enhanced network status hook with retry queue
export const useNetworkStatusWithQueue = () => {
  const networkStatus = useNetworkStatus();
  const [requestQueue, setRequestQueue] = useState([]);
  const [isProcessingQueue, setIsProcessingQueue] = useState(false);

  const addToQueue = (requestFunction, options = {}) => {
    const queueItem = {
      id: Date.now().toString(),
      requestFunction,
      options,
      timestamp: Date.now(),
      retryCount: 0
    };

    setRequestQueue(queue => [...queue, queueItem]);
    return queueItem.id;
  };

  const removeFromQueue = (id) => {
    setRequestQueue(queue => queue.filter(item => item.id !== id));
  };

  const processQueue = async () => {
    if (!networkStatus.isOnline || isProcessingQueue || requestQueue.length === 0) {
      return;
    }

    setIsProcessingQueue(true);

    const itemsToProcess = [...requestQueue];
    setRequestQueue([]);

    for (const item of itemsToProcess) {
      try {
        await item.requestFunction();
        console.log(`Successfully processed queued request ${item.id}`);
      } catch (error) {
        console.error(`Failed to process queued request ${item.id}:`, error);
        
        // Re-queue if retryable and under retry limit
        if (item.retryCount < (item.options.maxRetries || 3)) {
          setRequestQueue(queue => [...queue, {
            ...item,
            retryCount: item.retryCount + 1
          }]);
        }
      }
    }

    setIsProcessingQueue(false);
  };

  // Process queue when coming back online
  useEffect(() => {
    if (networkStatus.isOnline && requestQueue.length > 0) {
      const timer = setTimeout(processQueue, 1000); // Wait 1 second after coming online
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [networkStatus.isOnline, requestQueue.length]);

  return {
    ...networkStatus,
    requestQueue,
    addToQueue,
    removeFromQueue,
    processQueue,
    isProcessingQueue
  };
};

// Connection quality monitoring
export const useConnectionQuality = () => {
  const [quality, setQuality] = useState('good');
  const [latency, setLatency] = useState(null);

  useEffect(() => {
    let timeoutId;

    const measureLatency = async () => {
      const start = performance.now();
      
      try {
        // Use a simple image request to measure latency
        const img = new Image();
        img.onload = () => {
          const end = performance.now();
          const latencyMs = end - start;
          setLatency(latencyMs);

          // Determine connection quality based on latency
          if (latencyMs < 100) {
            setQuality('excellent');
          } else if (latencyMs < 300) {
            setQuality('good');
          } else if (latencyMs < 1000) {
            setQuality('fair');
          } else {
            setQuality('poor');
          }
        };
        
        img.onerror = () => {
          setQuality('poor');
          setLatency(null);
        };
        
        // Use a small image for testing
        img.src = `${process.env.REACT_APP_API_BASE_URL || ''}/favicon.ico?t=${Date.now()}`;
      } catch (error) {
        setQuality('poor');
        setLatency(null);
      }
    };

    const startMeasuring = () => {
      measureLatency();
      timeoutId = setTimeout(startMeasuring, 30000); // Measure every 30 seconds
    };

    if (navigator.onLine) {
      startMeasuring();
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

  return {
    quality,
    latency,
    isGoodConnection: quality === 'excellent' || quality === 'good'
  };
};

export default useNetworkStatus;