import { useEffect, useRef, useCallback } from 'react';
import { performanceMonitor, memoryMonitor } from '../utils/performance';

// Hook for memory management and cleanup
export const useMemoryCleanup = (options = {}) => {
  const {
    cleanupInterval = 30000, // 30 seconds
    memoryThreshold = 80, // 80% memory usage
    enableLogging = process.env.NODE_ENV === 'development'
  } = options;

  const cleanupTasks = useRef(new Set());
  const intervalRef = useRef(null);
  const isCleaningUp = useRef(false);

  // Add cleanup task
  const addCleanupTask = useCallback((task, identifier) => {
    cleanupTasks.current.add({ task, identifier, timestamp: Date.now() });
    
    if (enableLogging) {
      console.log(`🧹 Adăugat task de curățare: ${identifier}`);
    }
  }, [enableLogging]);

  // Remove cleanup task
  const removeCleanupTask = useCallback((identifier) => {
    const task = Array.from(cleanupTasks.current).find(t => t.identifier === identifier);
    if (task) {
      cleanupTasks.current.delete(task);
      
      if (enableLogging) {
        console.log(`🧹 Eliminat task de curățare: ${identifier}`);
      }
    }
  }, [enableLogging]);

  // Execute cleanup tasks
  const executeCleanup = useCallback(async () => {
    if (isCleaningUp.current || cleanupTasks.current.size === 0) {
      return;
    }

    isCleaningUp.current = true;
    const startTime = performance.now();

    try {
      const tasksToExecute = Array.from(cleanupTasks.current);
      
      if (enableLogging) {
        console.group(`🧹 Executare curățare memorie (${tasksToExecute.length} task-uri)`);
      }

      for (const { task, identifier } of tasksToExecute) {
        try {
          await task();
          cleanupTasks.current.delete({ task, identifier });
          
          if (enableLogging) {
            console.log(`✅ Curățare completă: ${identifier}`);
          }
        } catch (error) {
          console.error(`❌ Eroare la curățare ${identifier}:`, error);
        }
      }

      // Force garbage collection if available (development only)
      if (enableLogging && window.gc) {
        window.gc();
        console.log('🗑️ Garbage collection forțat');
      }

      const duration = performance.now() - startTime;
      performanceMonitor.recordMetric('Memory Cleanup', duration, {
        tasksExecuted: tasksToExecute.length
      });

      if (enableLogging) {
        console.log(`⏱️ Curățare completă în ${duration.toFixed(2)}ms`);
        console.groupEnd();
      }

    } finally {
      isCleaningUp.current = false;
    }
  }, [enableLogging]);

  // Check memory usage and trigger cleanup if needed
  const checkMemoryUsage = useCallback(() => {
    const memoryUsage = memoryMonitor.getMemoryUsage();
    
    if (memoryUsage && memoryUsage.percentage > memoryThreshold) {
      if (enableLogging) {
        console.warn(`⚠️ Utilizare memorie ridicată: ${memoryUsage.percentage.toFixed(1)}%`);
      }
      
      executeCleanup();
    }
  }, [memoryThreshold, executeCleanup, enableLogging]);

  // Set up cleanup interval
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      checkMemoryUsage();
    }, cleanupInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [checkMemoryUsage, cleanupInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      executeCleanup();
    };
  }, [executeCleanup]);

  return {
    addCleanupTask,
    removeCleanupTask,
    executeCleanup,
    checkMemoryUsage,
    isCleaningUp: isCleaningUp.current,
    activeTasks: cleanupTasks.current.size
  };
};

// Hook for component-specific memory cleanup
export const useComponentCleanup = (componentName) => {
  const { addCleanupTask, removeCleanupTask } = useMemoryCleanup();
  const cleanupRefs = useRef(new Map());

  // Add event listener with automatic cleanup
  const addEventListenerWithCleanup = useCallback((element, event, handler, options) => {
    const identifier = `${componentName}-event-${event}-${Date.now()}`;
    
    element.addEventListener(event, handler, options);
    
    const cleanup = () => {
      element.removeEventListener(event, handler, options);
    };
    
    cleanupRefs.current.set(identifier, cleanup);
    addCleanupTask(cleanup, identifier);
    
    return () => {
      cleanup();
      cleanupRefs.current.delete(identifier);
      removeCleanupTask(identifier);
    };
  }, [componentName, addCleanupTask, removeCleanupTask]);

  // Add timeout with automatic cleanup
  const addTimeoutWithCleanup = useCallback((callback, delay) => {
    const identifier = `${componentName}-timeout-${Date.now()}`;
    
    const timeoutId = setTimeout(callback, delay);
    
    const cleanup = () => {
      clearTimeout(timeoutId);
    };
    
    cleanupRefs.current.set(identifier, cleanup);
    addCleanupTask(cleanup, identifier);
    
    return () => {
      cleanup();
      cleanupRefs.current.delete(identifier);
      removeCleanupTask(identifier);
    };
  }, [componentName, addCleanupTask, removeCleanupTask]);

  // Add interval with automatic cleanup
  const addIntervalWithCleanup = useCallback((callback, interval) => {
    const identifier = `${componentName}-interval-${Date.now()}`;
    
    const intervalId = setInterval(callback, interval);
    
    const cleanup = () => {
      clearInterval(intervalId);
    };
    
    cleanupRefs.current.set(identifier, cleanup);
    addCleanupTask(cleanup, identifier);
    
    return () => {
      cleanup();
      cleanupRefs.current.delete(identifier);
      removeCleanupTask(identifier);
    };
  }, [componentName, addCleanupTask, removeCleanupTask]);

  // Add observer with automatic cleanup
  const addObserverWithCleanup = useCallback((observer, identifier) => {
    const cleanupId = `${componentName}-observer-${identifier}-${Date.now()}`;
    
    const cleanup = () => {
      if (observer && observer.disconnect) {
        observer.disconnect();
      }
    };
    
    cleanupRefs.current.set(cleanupId, cleanup);
    addCleanupTask(cleanup, cleanupId);
    
    return () => {
      cleanup();
      cleanupRefs.current.delete(cleanupId);
      removeCleanupTask(cleanupId);
    };
  }, [componentName, addCleanupTask, removeCleanupTask]);

  // Cleanup all component references
  const cleanupAll = useCallback(() => {
    for (const [identifier, cleanup] of cleanupRefs.current.entries()) {
      try {
        cleanup();
        removeCleanupTask(identifier);
      } catch (error) {
        console.error(`Eroare la curățarea ${identifier}:`, error);
      }
    }
    cleanupRefs.current.clear();
  }, [removeCleanupTask]);

  // Auto cleanup on unmount
  useEffect(() => {
    return cleanupAll;
  }, [cleanupAll]);

  return {
    addEventListenerWithCleanup,
    addTimeoutWithCleanup,
    addIntervalWithCleanup,
    addObserverWithCleanup,
    cleanupAll,
    activeRefs: cleanupRefs.current.size
  };
};

// Hook for cache management
export const useCacheManagement = (options = {}) => {
  const {
    maxCacheSize = 50, // Maximum number of cache entries
    maxCacheAge = 300000, // 5 minutes
    enableLogging = process.env.NODE_ENV === 'development'
  } = options;

  const cache = useRef(new Map());
  const { addCleanupTask } = useMemoryCleanup();

  // Add to cache
  const setCache = useCallback((key, value, customAge) => {
    const entry = {
      value,
      timestamp: Date.now(),
      maxAge: customAge || maxCacheAge
    };

    cache.current.set(key, entry);

    // Remove oldest entries if cache is too large
    if (cache.current.size > maxCacheSize) {
      const entries = Array.from(cache.current.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      const toRemove = entries.slice(0, cache.current.size - maxCacheSize);
      toRemove.forEach(([key]) => cache.current.delete(key));
      
      if (enableLogging) {
        console.log(`🗑️ Eliminat ${toRemove.length} intrări vechi din cache`);
      }
    }
  }, [maxCacheSize, maxCacheAge, enableLogging]);

  // Get from cache
  const getCache = useCallback((key) => {
    const entry = cache.current.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if entry is expired
    if (Date.now() - entry.timestamp > entry.maxAge) {
      cache.current.delete(key);
      
      if (enableLogging) {
        console.log(`⏰ Cache expirat pentru: ${key}`);
      }
      
      return null;
    }

    return entry.value;
  }, [enableLogging]);

  // Clear expired entries
  const clearExpired = useCallback(() => {
    const now = Date.now();
    let removedCount = 0;

    for (const [key, entry] of cache.current.entries()) {
      if (now - entry.timestamp > entry.maxAge) {
        cache.current.delete(key);
        removedCount++;
      }
    }

    if (enableLogging && removedCount > 0) {
      console.log(`🧹 Eliminat ${removedCount} intrări expirate din cache`);
    }

    return removedCount;
  }, [enableLogging]);

  // Clear all cache
  const clearCache = useCallback(() => {
    const size = cache.current.size;
    cache.current.clear();
    
    if (enableLogging) {
      console.log(`🗑️ Cache complet curățat (${size} intrări)`);
    }
  }, [enableLogging]);

  // Set up automatic cleanup
  useEffect(() => {
    const cleanupTask = () => clearExpired();
    addCleanupTask(cleanupTask, 'cache-cleanup');
  }, [clearExpired, addCleanupTask]);

  return {
    setCache,
    getCache,
    clearExpired,
    clearCache,
    cacheSize: cache.current.size
  };
};

export default useMemoryCleanup;