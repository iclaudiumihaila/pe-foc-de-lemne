import { useState, useEffect, useRef, useCallback } from 'react';
import { performanceMonitor } from '../utils/performance';

// Hook for lazy loading images with performance monitoring
export const useImageLazyLoading = (options = {}) => {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    fallbackSrc = '/images/placeholder.jpg',
    retryAttempts = 3,
    retryDelay = 1000
  } = options;

  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentSrc, setCurrentSrc] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const imgRef = useRef(null);
  const observerRef = useRef(null);

  // Intersection Observer callback
  const handleIntersection = useCallback((entries) => {
    const [entry] = entries;
    
    if (entry.isIntersecting && !isLoaded && !isLoading) {
      setIsLoading(true);
      
      // Performance monitoring
      const measurement = performanceMonitor.measureFunction('Image Load', () => {});
      measurement.onRenderStart();
      
      // Start loading the image
      if (imgRef.current) {
        const img = new Image();
        
        img.onload = () => {
          setCurrentSrc(img.src);
          setIsLoaded(true);
          setIsLoading(false);
          setError(null);
          measurement.onRenderEnd();
          
          performanceMonitor.recordMetric('Image Load Success', performance.now(), {
            src: img.src,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight
          });
        };
        
        img.onerror = () => {
          setIsLoading(false);
          setError(new Error(`Nu s-a putut încărca imaginea: ${img.src}`));
          
          performanceMonitor.recordMetric('Image Load Error', performance.now(), {
            src: img.src,
            retryCount
          });
          
          // Retry logic
          if (retryCount < retryAttempts) {
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
              setError(null);
            }, retryDelay * (retryCount + 1)); // Exponential backoff
          } else {
            // Use fallback image
            setCurrentSrc(fallbackSrc);
            setIsLoaded(true);
          }
        };
        
        img.src = imgRef.current.dataset.src;
      }
    }
  }, [isLoaded, isLoading, retryCount, retryAttempts, retryDelay, fallbackSrc]);

  // Set up intersection observer
  useEffect(() => {
    if (!imgRef.current) return;

    // Create observer if not exists
    if (!observerRef.current) {
      observerRef.current = new IntersectionObserver(handleIntersection, {
        threshold,
        rootMargin
      });
    }

    // Start observing
    observerRef.current.observe(imgRef.current);

    // Cleanup
    return () => {
      if (observerRef.current && imgRef.current) {
        observerRef.current.unobserve(imgRef.current);
      }
    };
  }, [handleIntersection, threshold, rootMargin]);

  // Cleanup observer on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  return {
    imgRef,
    isLoaded,
    isLoading,
    error,
    currentSrc,
    retryCount
  };
};

// Hook for preloading critical images
export const useImagePreloader = (imageSources = []) => {
  const [preloadedImages, setPreloadedImages] = useState(new Set());
  const [preloadProgress, setPreloadProgress] = useState(0);
  const [isPreloading, setIsPreloading] = useState(false);

  const preloadImages = useCallback(async () => {
    if (imageSources.length === 0) return;
    
    setIsPreloading(true);
    setPreloadProgress(0);
    
    const promises = imageSources.map((src, index) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        
        img.onload = () => {
          setPreloadedImages(prev => new Set([...prev, src]));
          setPreloadProgress(((index + 1) / imageSources.length) * 100);
          
          performanceMonitor.recordMetric('Image Preload Success', performance.now(), {
            src,
            index,
            total: imageSources.length
          });
          
          resolve(src);
        };
        
        img.onerror = () => {
          performanceMonitor.recordMetric('Image Preload Error', performance.now(), {
            src,
            index
          });
          reject(new Error(`Preload failed for ${src}`));
        };
        
        img.src = src;
      });
    });

    try {
      await Promise.allSettled(promises);
    } catch (error) {
      console.warn('Eroare la preîncărcarea imaginilor:', error);
    } finally {
      setIsPreloading(false);
    }
  }, [imageSources]);

  useEffect(() => {
    preloadImages();
  }, [preloadImages]);

  return {
    preloadedImages,
    preloadProgress,
    isPreloading,
    preloadImages
  };
};

// Hook for responsive image loading
export const useResponsiveImage = (srcSet = {}, options = {}) => {
  const [currentSrc, setCurrentSrc] = useState(null);
  const [devicePixelRatio, setDevicePixelRatio] = useState(window.devicePixelRatio || 1);

  const selectOptimalSrc = useCallback(() => {
    const { small, medium, large, xlarge } = srcSet;
    const screenWidth = window.innerWidth;
    const dpr = devicePixelRatio;

    // Select source based on screen width and pixel ratio
    let selectedSrc;
    
    if (screenWidth < 640) {
      selectedSrc = small;
    } else if (screenWidth < 1024) {
      selectedSrc = medium;
    } else if (screenWidth < 1536) {
      selectedSrc = large;
    } else {
      selectedSrc = xlarge || large;
    }

    // Use high DPI version if available and needed
    if (dpr > 1 && selectedSrc) {
      const highDpiSrc = selectedSrc.replace(/(\.[^.]+)$/, '@2x$1');
      // In a real app, you'd check if the @2x version exists
      // For now, we'll use the regular version
    }

    setCurrentSrc(selectedSrc);
    
    performanceMonitor.recordMetric('Responsive Image Selection', performance.now(), {
      screenWidth,
      devicePixelRatio: dpr,
      selectedSrc
    });
  }, [srcSet, devicePixelRatio]);

  // Monitor screen size and pixel ratio changes
  useEffect(() => {
    const handleResize = performanceUtils.throttle(() => {
      selectOptimalSrc();
    }, 250);

    const handlePixelRatioChange = () => {
      setDevicePixelRatio(window.devicePixelRatio || 1);
    };

    selectOptimalSrc();

    window.addEventListener('resize', handleResize);
    
    // Monitor pixel ratio changes (for zoom)
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(resolution: 1dppx)');
      mediaQuery.addListener(handlePixelRatioChange);
      
      return () => {
        window.removeEventListener('resize', handleResize);
        mediaQuery.removeListener(handlePixelRatioChange);
      };
    }

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [selectOptimalSrc]);

  return {
    currentSrc,
    devicePixelRatio
  };
};

// Hook for image optimization
export const useImageOptimization = () => {
  // Convert image to WebP if supported
  const convertToWebP = useCallback((src) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    return new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        // Try to convert to WebP
        canvas.toBlob((blob) => {
          if (blob) {
            const webpUrl = URL.createObjectURL(blob);
            resolve(webpUrl);
          } else {
            resolve(src); // Fallback to original
          }
        }, 'image/webp', 0.8);
      };
      
      img.onerror = () => resolve(src);
      img.src = src;
    });
  }, []);

  // Check WebP support
  const isWebPSupported = useCallback(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }, []);

  // Compress image
  const compressImage = useCallback((file, quality = 0.8, maxWidth = 1920, maxHeight = 1080) => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        // Calculate new dimensions
        let { width, height } = img;
        
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }
        
        if (height > maxHeight) {
          width = (width * maxHeight) / height;
          height = maxHeight;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        // Draw and compress
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(resolve, file.type, quality);
      };
      
      img.src = URL.createObjectURL(file);
    });
  }, []);

  return {
    convertToWebP,
    isWebPSupported,
    compressImage
  };
};

export default useImageLazyLoading;