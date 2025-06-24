import api from './api';

const API_PREFIX = '/admin/categories';

/**
 * Admin Category Service
 * Handles all admin category-related API calls
 */
const adminCategoryService = {
  /**
   * Get all categories (flat list)
   * @returns {Promise<Array>} Categories list
   */
  async getCategories() {
    try {
      const response = await api.get(API_PREFIX);
      return response.data.categories || [];
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  /**
   * Get categories as tree structure
   * @returns {Promise<Array>} Categories tree
   */
  async getCategoriesTree() {
    try {
      const response = await api.get(`${API_PREFIX}/tree`);
      return response.data.categories || [];
    } catch (error) {
      console.error('Error fetching categories tree:', error);
      throw error;
    }
  },

  /**
   * Get single category by ID
   * @param {string} categoryId - Category ID
   * @returns {Promise<Object>} Category data
   */
  async getCategoryById(categoryId) {
    try {
      const response = await api.get(`${API_PREFIX}/${categoryId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching category:', error);
      throw error;
    }
  },

  /**
   * Create new category
   * @param {Object} categoryData - Category data
   * @returns {Promise<Object>} Created category
   */
  async createCategory(categoryData) {
    try {
      // Transform data for backend (already uses correct field names from form)
      const response = await api.post(API_PREFIX, categoryData);
      return response.data;
    } catch (error) {
      console.error('Error creating category:', error);
      throw error;
    }
  },

  /**
   * Update existing category
   * @param {string} categoryId - Category ID
   * @param {Object} categoryData - Updated category data
   * @returns {Promise<Object>} Updated category
   */
  async updateCategory(categoryId, categoryData) {
    try {
      // Transform data for backend (already uses correct field names from form)
      const response = await api.put(`${API_PREFIX}/${categoryId}`, categoryData);
      return response.data;
    } catch (error) {
      console.error('Error updating category:', error);
      throw error;
    }
  },

  /**
   * Delete category
   * @param {string} categoryId - Category ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteCategory(categoryId) {
    try {
      const response = await api.delete(`${API_PREFIX}/${categoryId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting category:', error);
      throw error;
    }
  },

  /**
   * Check if category has products
   * @param {string} categoryId - Category ID
   * @returns {Promise<boolean>} Whether category has products
   */
  async checkCategoryProducts(categoryId) {
    try {
      const response = await api.get(`/categories/${categoryId}/product-count`);
      return response.data.count > 0;
    } catch (error) {
      console.error('Error checking category products:', error);
      return false;
    }
  }
};

export default adminCategoryService;