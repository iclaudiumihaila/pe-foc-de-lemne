import api from './api';

const API_PREFIX = '/admin/products';

/**
 * Admin Product Service
 * Handles all admin product-related API calls
 */
const adminProductService = {
  /**
   * Get products with pagination, search, and filters
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   * @param {string} params.q - Search query
   * @param {string} params.category_id - Filter by category
   * @param {string} params.sort_by - Sort field
   * @param {string} params.sort_order - Sort order (asc/desc)
   * @param {boolean} params.available_only - Filter by availability
   * @returns {Promise<Object>} Products data with pagination
   */
  async getProducts(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      // Add pagination
      if (params.page) queryParams.append('page', params.page);
      if (params.limit) queryParams.append('limit', params.limit);
      
      // Add search - backend expects 'search' parameter
      if (params.q) queryParams.append('search', params.q);
      
      // Add filters
      if (params.category_id) queryParams.append('category_id', params.category_id);
      if (params.sort_by) queryParams.append('sort_by', params.sort_by);
      if (params.sort_order) queryParams.append('sort_order', params.sort_order);
      if (params.available_only !== undefined) {
        queryParams.append('available_only', params.available_only);
      }
      
      const response = await api.get(`${API_PREFIX}?${queryParams.toString()}`);
      // Handle the response structure properly
      let result = response.data.success && response.data.data ? response.data.data : response.data;
      
      // Transform fields for frontend compatibility
      if (result.products && Array.isArray(result.products)) {
        result.products = result.products.map(product => {
          const transformed = { ...product };
          
          // Transform stock to stock_quantity
          if (product.stock !== undefined) {
            transformed.stock_quantity = product.stock;
          }
          
          // Transform category to category_id and create category object for display
          if (product.category !== undefined) {
            // Keep category_id as string
            transformed.category_id = product.category;
            // Create category object with name for table display
            if (product.categoryName) {
              transformed.category = {
                id: product.category,
                name: product.categoryName
              };
            }
          }
          
          // Transform active to is_available
          if (product.active !== undefined) {
            transformed.is_available = product.active;
          }
          
          // Transform single image to images array
          if (product.image && !product.images) {
            transformed.images = [product.image];
          }
          
          return transformed;
        });
      }
      
      // Transform pagination structure to match frontend expectations
      if (result.total !== undefined && result.page !== undefined && result.totalPages !== undefined) {
        result.pagination = {
          page: result.page,
          limit: params.limit || 10,
          total_items: result.total,
          total_pages: result.totalPages
        };
      }
      
      return result;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  /**
   * Get single product by ID
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Product data
   */
  async getProduct(productId) {
    try {
      const response = await api.get(`${API_PREFIX}/${productId}`);
      let product = response.data;
      console.log('RAW PRODUCT FROM API:', JSON.stringify(product, null, 2));
      
      // Transform fields for frontend compatibility
      if (product) {
        // Transform stock to stock_quantity
        if (product.stock !== undefined) {
          product.stock_quantity = product.stock;
        }
        
        // Transform category to category_id and create category object for display
        if (product.category !== undefined) {
          // Store the original category ID
          const categoryId = product.category;
          console.log('BEFORE TRANSFORM - category:', categoryId, 'type:', typeof categoryId);
          console.log('BEFORE TRANSFORM - category_id:', product.category_id, 'type:', typeof product.category_id);
          
          // Create category object with name for table display
          if (product.categoryName) {
            product.category = {
              id: categoryId,
              name: product.categoryName
            };
          }
          
          // Set category_id as string, not object
          product.category_id = categoryId;
          console.log('AFTER TRANSFORM - category:', product.category);
          console.log('AFTER TRANSFORM - category_id:', product.category_id, 'type:', typeof product.category_id);
        }
        
        // Transform active to is_available
        if (product.active !== undefined) {
          product.is_available = product.active;
        }
        
        // Transform single image to images array
        if (product.image && !product.images) {
          product.images = [product.image];
        }
      }
      
      console.log('FINAL PRODUCT RETURNED:', JSON.stringify(product, null, 2));
      return product;
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  },

  /**
   * Create new product
   * @param {Object} productData - Product data
   * @returns {Promise<Object>} Created product
   */
  async createProduct(productData) {
    try {
      // Send data as-is since backend now accepts the correct field names
      const response = await api.post(API_PREFIX, productData);
      // Handle the response structure properly
      if (response.data.success && response.data.data) {
        return response.data.data;
      }
      return response.data;
    } catch (error) {
      console.error('Error creating product:', error);
      throw error;
    }
  },

  /**
   * Update existing product
   * @param {string} productId - Product ID
   * @param {Object} productData - Updated product data
   * @returns {Promise<Object>} Updated product
   */
  async updateProduct(productId, productData) {
    try {
      // Send data as-is since backend now accepts the correct field names
      const response = await api.put(`${API_PREFIX}/${productId}`, productData);
      return response.data;
    } catch (error) {
      console.error('Error updating product:', error);
      throw error;
    }
  },

  /**
   * Delete product (soft delete)
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteProduct(productId) {
    try {
      const response = await api.delete(`${API_PREFIX}/${productId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting product:', error);
      throw error;
    }
  },

  /**
   * Get all categories for product form
   * @returns {Promise<Array>} Categories list
   */
  async getCategories() {
    try {
      const response = await api.get('/admin/categories');
      // Handle the response structure properly
      if (response.data.success && response.data.data) {
        return response.data.data.categories || [];
      }
      return response.data.categories || [];
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }
};

export default adminProductService;