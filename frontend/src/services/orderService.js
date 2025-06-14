import apiService from './apiService';

class OrderService {
  // Create new order
  async createOrder(orderData) {
    return await apiService.post('/orders', orderData);
  }
  
  // Get order by ID
  async getOrder(orderId) {
    return await apiService.get(`/orders/${orderId}`);
  }
  
  // Get order status
  async getOrderStatus(orderId) {
    return await apiService.get(`/orders/${orderId}/status`);
  }
  
  // Update order
  async updateOrder(orderId, updates) {
    return await apiService.put(`/orders/${orderId}`, updates);
  }
}

const orderServiceInstance = new OrderService();
export default orderServiceInstance;