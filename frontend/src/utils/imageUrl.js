/**
 * Utility function to get the full URL for product images
 */

// Get the base URL for the backend server (without /api)
const getBackendBaseUrl = () => {
  const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
  // Remove the /api part to get the base server URL
  return apiUrl.replace(/\/api$/, '');
};

/**
 * Get the full URL for an image
 * @param {string} imagePath - The image path (can be relative or full URL)
 * @param {string} size - The image size variant (thumb, medium, large, pinterest)
 * @returns {string} The full URL for the image
 */
export const getImageUrl = (imagePath, size = null) => {
  if (!imagePath) {
    return '/images/placeholder-product.jpg';
  }

  // If it's already a full URL, return as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  // If size is specified and it's an uploaded image, modify path for size variant
  if (size && imagePath.startsWith('/uploads')) {
    const pathParts = imagePath.split('/');
    const filename = pathParts[pathParts.length - 1];
    
    // Remove any existing size suffix (_thumb, _medium, _large, _pinterest)
    const sizePattern = /_(thumb|medium|large|pinterest)\./;
    const cleanFilename = filename.replace(sizePattern, '.');
    
    // Add the new size suffix
    const [name, ext] = cleanFilename.split(/\.(?=[^.]+$)/);
    pathParts[pathParts.length - 1] = `${name}_${size}.${ext}`;
    imagePath = pathParts.join('/');
  }

  // If it's an uploaded image path, prepend the backend URL
  if (imagePath.startsWith('/uploads')) {
    return `${getBackendBaseUrl()}${imagePath}`;
  }

  // Otherwise, assume it's a local static image
  return imagePath;
};

export default getImageUrl;