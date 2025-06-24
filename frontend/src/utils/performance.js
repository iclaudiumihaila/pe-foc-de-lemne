// Performance utilities and monitoring
class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = new Map();
    this.isSupported = 'performance' in window;
    this.vitalsSupported = 'PerformanceObserver' in window;
    
    if (this.vitalsSupported) {
      this.initializeWebVitals();
    }
  }

  // Initialize Core Web Vitals monitoring
  initializeWebVitals() {
    try {
      // Largest Contentful Paint (LCP)
      this.observeMetric('largest-contentful-paint', (entry) => {
        this.recordMetric('LCP', entry.startTime, {
          target: entry.element?.tagName || 'unknown',
          size: entry.size
        });
      });

      // First Input Delay (FID)
      this.observeMetric('first-input', (entry) => {
        this.recordMetric('FID', entry.processingStart - entry.startTime, {
          eventType: entry.name
        });
      });

      // Cumulative Layout Shift (CLS)
      this.observeMetric('layout-shift', (entry) => {
        if (!entry.hadRecentInput) {
          this.recordMetric('CLS', entry.value, {
            sources: entry.sources?.length || 0
          });
        }
      });

    } catch (error) {
      console.warn('Eroare la inițializarea monitorizării performanței:', error);
    }
  }

  // Observe specific performance metrics
  observeMetric(type, callback) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          callback(entry);
        }
      });

      observer.observe({ entryTypes: [type] });
      this.observers.set(type, observer);
    } catch (error) {
      console.warn(`Nu s-a putut observa metrica ${type}:`, error);
    }
  }

  // Record a performance metric
  recordMetric(name, value, metadata = {}) {
    const timestamp = Date.now();
    const metric = {
      name,
      value,
      timestamp,
      metadata,
      url: window.location.href
    };

    // Store metric
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name).push(metric);

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`📊 Metrică performanță: ${name} = ${value.toFixed(2)}ms`, metadata);
    }

    // Send to analytics (if configured)
    this.sendToAnalytics(metric);
  }

  // Measure function execution time
  measureFunction(name, fn) {
    return async (...args) => {
      const startTime = performance.now();
      try {
        const result = await fn(...args);
        const duration = performance.now() - startTime;
        this.recordMetric(`Function: ${name}`, duration);
        return result;
      } catch (error) {
        const duration = performance.now() - startTime;
        this.recordMetric(`Function: ${name} (Error)`, duration, { error: error.message });
        throw error;
      }
    };
  }

  // Measure React component render time
  measureComponentRender(componentName) {
    return {
      onRenderStart: () => {
        this.startTime = performance.now();
      },
      onRenderEnd: () => {
        if (this.startTime) {
          const duration = performance.now() - this.startTime;
          this.recordMetric(`Component Render: ${componentName}`, duration);
          this.startTime = null;
        }
      }
    };
  }

  // Measure network requests
  measureNetworkRequest(url, method = 'GET') {
    const startTime = performance.now();
    
    return {
      onComplete: (response) => {
        const duration = performance.now() - startTime;
        this.recordMetric('Network Request', duration, {
          url,
          method,
          status: response?.status,
          success: response?.ok
        });
      },
      onError: (error) => {
        const duration = performance.now() - startTime;
        this.recordMetric('Network Request (Error)', duration, {
          url,
          method,
          error: error.message
        });
      }
    };
  }

  // Get performance metrics summary
  getMetricsSummary() {
    const summary = {};
    
    for (const [name, values] of this.metrics.entries()) {
      const recent = values.slice(-10); // Last 10 measurements
      const avg = recent.reduce((sum, m) => sum + m.value, 0) / recent.length;
      const min = Math.min(...recent.map(m => m.value));
      const max = Math.max(...recent.map(m => m.value));
      
      summary[name] = {
        average: avg,
        min,
        max,
        count: values.length,
        recent: recent.length
      };
    }
    
    return summary;
  }

  // Check if performance is good
  isPerformanceGood() {
    const summary = this.getMetricsSummary();
    
    const checks = {
      lcp: !summary.LCP || summary.LCP.average < 2500, // < 2.5s
      fid: !summary.FID || summary.FID.average < 100,  // < 100ms
      cls: !summary.CLS || summary.CLS.average < 0.1   // < 0.1
    };
    
    return Object.values(checks).every(check => check);
  }

  // Send metrics to analytics service
  sendToAnalytics(metric) {
    if (typeof window.gtag !== 'undefined') {
      window.gtag('event', 'performance_metric', {
        metric_name: metric.name,
        metric_value: Math.round(metric.value),
        custom_map: {
          metric_metadata: JSON.stringify(metric.metadata)
        }
      });
    }
  }

  // Clean up observers
  disconnect() {
    for (const observer of this.observers.values()) {
      observer.disconnect();
    }
    this.observers.clear();
  }
}

// Bundle size monitoring
export const bundleAnalyzer = {
  // Calculate approximate bundle size
  estimateBundleSize() {
    if (!performance.getEntriesByType) return null;
    
    const resources = performance.getEntriesByType('resource');
    const jsFiles = resources.filter(r => r.name.includes('.js'));
    const cssFiles = resources.filter(r => r.name.includes('.css'));
    
    const jsSize = jsFiles.reduce((total, file) => total + (file.transferSize || 0), 0);
    const cssSize = cssFiles.reduce((total, file) => total + (file.transferSize || 0), 0);
    
    return {
      javascript: jsSize,
      css: cssSize,
      total: jsSize + cssSize,
      files: {
        js: jsFiles.length,
        css: cssFiles.length
      }
    };
  },

  // Log bundle analysis
  logBundleAnalysis() {
    const analysis = this.estimateBundleSize();
    if (analysis && process.env.NODE_ENV === 'development') {
      console.group('📦 Analiză dimensiune bundle');
      console.log(`JavaScript: ${(analysis.javascript / 1024).toFixed(2)} KB`);
      console.log(`CSS: ${(analysis.css / 1024).toFixed(2)} KB`);
      console.log(`Total: ${(analysis.total / 1024).toFixed(2)} KB`);
      console.log(`Fișiere: ${analysis.files.js} JS, ${analysis.files.css} CSS`);
      console.groupEnd();
    }
    return analysis;
  }
};

// Memory usage monitoring
export const memoryMonitor = {
  // Get current memory usage
  getMemoryUsage() {
    if (!performance.memory) return null;
    
    return {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit,
      percentage: (performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize) * 100,
      percentageOfLimit: (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100
    };
  },

  // Check for memory leaks
  detectMemoryLeaks() {
    const usage = this.getMemoryUsage();
    if (!usage) return false;
    
    // Consider it a potential leak if using >90% of the heap LIMIT (not just allocated)
    // or if the allocated heap is >80% of limit and usage is >90% of allocated
    return usage.percentageOfLimit > 90 || 
           (usage.total / usage.limit > 0.8 && usage.percentage > 90);
  },

  // Log memory usage
  logMemoryUsage() {
    const usage = this.getMemoryUsage();
    if (usage && process.env.NODE_ENV === 'development') {
      const usedMB = (usage.used / 1048576).toFixed(2);
      const totalMB = (usage.total / 1048576).toFixed(2);
      const limitMB = (usage.limit / 1048576).toFixed(2);
      
      console.log(`🧠 Memorie: ${usedMB}MB/${totalMB}MB alocată (${usage.percentageOfLimit.toFixed(1)}% din limita de ${limitMB}MB)`);
      
      if (this.detectMemoryLeaks()) {
        console.warn('⚠️ Posibilă scurgere de memorie detectată!');
      }
    }
    return usage;
  }
};

// Performance optimization utilities
export const performanceUtils = {
  // Debounce function for performance
  debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        if (!immediate) func(...args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func(...args);
    };
  },

  // Throttle function for performance
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Request idle callback with fallback
  requestIdleCallback(callback, options = {}) {
    if ('requestIdleCallback' in window) {
      return window.requestIdleCallback(callback, options);
    } else {
      // Fallback for browsers without support
      return setTimeout(() => callback({ timeRemaining: () => 50 }), 1);
    }
  },

  // Cancel idle callback
  cancelIdleCallback(id) {
    if ('cancelIdleCallback' in window) {
      window.cancelIdleCallback(id);
    } else {
      clearTimeout(id);
    }
  },

  // Optimize heavy computations
  optimizeComputation(computation, chunkSize = 1000) {
    return new Promise((resolve) => {
      const chunks = [];
      let index = 0;
      
      const processChunk = () => {
        const endIndex = Math.min(index + chunkSize, computation.length);
        const chunk = computation.slice(index, endIndex);
        chunks.push(chunk);
        index = endIndex;
        
        if (index < computation.length) {
          this.requestIdleCallback(processChunk);
        } else {
          resolve(chunks.flat());
        }
      };
      
      processChunk();
    });
  }
};

// Create global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Initialize monitoring when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    performanceMonitor.recordMetric('DOM Ready', performance.now());
  });
} else {
  performanceMonitor.recordMetric('DOM Ready', performance.now());
}

// Monitor page load
window.addEventListener('load', () => {
  performanceMonitor.recordMetric('Page Load', performance.now());
  
  // Log initial bundle and memory analysis
  setTimeout(() => {
    bundleAnalyzer.logBundleAnalysis();
    memoryMonitor.logMemoryUsage();
  }, 1000);
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
  performanceMonitor.disconnect();
});

export default performanceMonitor;