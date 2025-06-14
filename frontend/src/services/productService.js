import apiService from './apiService';

class ProductService {
  // Get all products
  async getProducts(filters = {}) {
    return await apiService.get('/products', filters);
  }
  
  // Get product by ID
  async getProduct(productId) {
    return await apiService.get(`/products/${productId}`);
  }
  
  // Get products by category
  async getProductsByCategory(category) {
    return await apiService.get('/products', { category });
  }
  
  // Search products
  async searchProducts(query) {
    return await apiService.get('/products/search', { q: query });
  }
}

const productServiceInstance = new ProductService();
export default productServiceInstance;