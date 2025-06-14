import React, { useState, useEffect } from 'react';
import { useImageLazyLoading, useResponsiveImage } from '../../hooks/useImageLazyLoading';
import { DotsLoading } from './Loading';

// Optimized lazy loading image component
const LazyImage = ({
  src,
  srcSet,
  alt,
  className = '',
  width,
  height,
  placeholder = '/images/placeholder.jpg',
  fallback = '/images/image-not-found.jpg',
  loadingComponent,
  errorComponent,
  onLoad,
  onError,
  priority = false,
  blur = true,
  quality = 85,
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState(priority ? src : placeholder);
  const [imageError, setImageError] = useState(false);

  // Use responsive image if srcSet is provided
  const { currentSrc: responsiveSrc } = useResponsiveImage(
    typeof srcSet === 'object' ? srcSet : {}
  );

  // Use lazy loading for non-priority images
  const {
    imgRef,
    isLoaded,
    isLoading,
    error,
    currentSrc
  } = useImageLazyLoading({
    fallbackSrc: fallback,
    retryAttempts: 2,
    retryDelay: 1000
  });

  // Determine final image source
  const finalSrc = responsiveSrc || src;

  useEffect(() => {
    if (priority) {
      // For priority images, load immediately
      const img = new Image();
      img.onload = () => {
        setImageSrc(finalSrc);
        onLoad?.(img);
      };
      img.onerror = () => {
        setImageError(true);
        setImageSrc(fallback);
        onError?.(new Error(`Failed to load priority image: ${finalSrc}`));
      };
      img.src = finalSrc;
    } else {
      // For lazy loaded images, use the hook
      if (currentSrc) {
        setImageSrc(currentSrc);
        if (!error) {
          onLoad?.();
        }
      }
      if (error) {
        setImageError(true);
        onError?.(error);
      }
    }
  }, [priority, finalSrc, currentSrc, error, fallback, onLoad, onError]);

  // Loading state component
  const renderLoading = () => {
    if (loadingComponent) {
      return loadingComponent;
    }

    return (
      <div className="flex items-center justify-center bg-gray-100 animate-pulse">
        <DotsLoading color="gray" />
        <span className="ml-2 text-sm text-gray-500">Se încarcă imaginea...</span>
      </div>
    );
  };

  // Error state component
  const renderError = () => {
    if (errorComponent) {
      return errorComponent;
    }

    return (
      <div className="flex flex-col items-center justify-center bg-gray-100 p-4 text-center">
        <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span className="text-sm text-gray-500">Imaginea nu poate fi încărcată</span>
      </div>
    );
  };

  // Image styles
  const imageStyles = {
    width: width || '100%',
    height: height || 'auto',
    transition: 'opacity 0.3s ease-in-out',
    opacity: (priority || isLoaded) && !imageError ? 1 : 0.7,
    filter: blur && !isLoaded ? 'blur(4px)' : 'none'
  };

  // Container styles
  const containerStyles = {
    position: 'relative',
    overflow: 'hidden',
    backgroundColor: '#f3f4f6',
    width: width || '100%',
    height: height || 'auto'
  };

  return (
    <div style={containerStyles} className={className}>
      {/* Main image */}
      <img
        ref={priority ? null : imgRef}
        data-src={priority ? undefined : finalSrc}
        src={imageSrc}
        alt={alt}
        style={imageStyles}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        {...props}
      />

      {/* Loading overlay */}
      {!priority && isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          {renderLoading()}
        </div>
      )}

      {/* Error overlay */}
      {imageError && (
        <div className="absolute inset-0 flex items-center justify-center">
          {renderError()}
        </div>
      )}

      {/* Progressive enhancement: show low quality placeholder */}
      {!priority && !isLoaded && placeholder && (
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat filter blur-sm"
          style={{ backgroundImage: `url(${placeholder})` }}
        />
      )}
    </div>
  );
};

// Specialized image components
export const ProductImage = ({ 
  product, 
  size = 'medium',
  className = '',
  ...props 
}) => {
  const sizeConfig = {
    small: { width: 200, height: 200 },
    medium: { width: 400, height: 400 },
    large: { width: 800, height: 600 }
  };

  const { width, height } = sizeConfig[size] || sizeConfig.medium;

  // Generate responsive srcSet if product has multiple image sizes
  const srcSet = product.images?.length > 1 ? {
    small: product.images[0],
    medium: product.images[1] || product.images[0],
    large: product.images[2] || product.images[1] || product.images[0]
  } : null;

  return (
    <LazyImage
      src={product.images?.[0] || '/images/placeholder-product.jpg'}
      srcSet={srcSet}
      alt={`Imagine produs: ${product.name}`}
      width={width}
      height={height}
      placeholder="/images/placeholder-product.jpg"
      fallback="/images/product-not-found.jpg"
      className={`rounded-lg ${className}`}
      {...props}
    />
  );
};

export const CategoryImage = ({
  category,
  size = 'medium',
  className = '',
  ...props
}) => {
  const sizeConfig = {
    small: { width: 150, height: 100 },
    medium: { width: 300, height: 200 },
    large: { width: 600, height: 400 }
  };

  const { width, height } = sizeConfig[size] || sizeConfig.medium;

  return (
    <LazyImage
      src={category.image || '/images/placeholder-category.jpg'}
      alt={`Imagine categorie: ${category.name}`}
      width={width}
      height={height}
      placeholder="/images/placeholder-category.jpg"
      fallback="/images/category-not-found.jpg"
      className={`rounded-lg ${className}`}
      {...props}
    />
  );
};

export const HeroImage = ({ 
  src, 
  alt, 
  className = '',
  ...props 
}) => (
  <LazyImage
    src={src}
    alt={alt}
    priority={true} // Hero images should load immediately
    className={`w-full ${className}`}
    width="100%"
    height="auto"
    blur={false} // No blur for hero images
    {...props}
  />
);

export const ThumbnailImage = ({ 
  src, 
  alt, 
  className = '',
  ...props 
}) => (
  <LazyImage
    src={src}
    alt={alt}
    width={80}
    height={80}
    className={`rounded-md ${className}`}
    placeholder="/images/placeholder-thumbnail.jpg"
    fallback="/images/thumbnail-not-found.jpg"
    {...props}
  />
);

// Gallery component with optimized loading
export const ImageGallery = ({ 
  images = [], 
  className = '',
  onImageClick 
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleImageClick = (index) => {
    setSelectedIndex(index);
    onImageClick?.(images[index], index);
  };

  if (images.length === 0) {
    return (
      <div className={`bg-gray-100 rounded-lg p-8 text-center ${className}`}>
        <span className="text-gray-500">Nu există imagini disponibile</span>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Main image */}
      <div className="aspect-w-4 aspect-h-3">
        <LazyImage
          src={images[selectedIndex]}
          alt={`Imagine ${selectedIndex + 1} din ${images.length}`}
          priority={selectedIndex === 0}
          className="w-full h-full object-cover rounded-lg"
        />
      </div>

      {/* Thumbnail navigation */}
      {images.length > 1 && (
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {images.map((image, index) => (
            <button
              key={index}
              onClick={() => handleImageClick(index)}
              className={`flex-shrink-0 rounded-md overflow-hidden border-2 transition-colors ${
                index === selectedIndex 
                  ? 'border-green-600' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <ThumbnailImage
                src={image}
                alt={`Miniatură ${index + 1}`}
                className="cursor-pointer"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LazyImage;