import api from './api';

const adminOrderService = {
  // Get orders with filters and pagination
  getOrders: async (params = {}) => {
    try {
      // Transform frontend params to match backend expectations
      const transformedParams = { ...params };
      
      // Transform date filters
      if (params.date_from) {
        transformedParams.start_date = params.date_from;
        delete transformedParams.date_from;
      }
      if (params.date_to) {
        transformedParams.end_date = params.date_to;
        delete transformedParams.date_to;
      }
      
      // Transform phone parameter
      if (params.phone) {
        transformedParams.customer_phone = params.phone;
        delete transformedParams.phone;
      }
      
      const response = await api.get('/admin/orders', { params: transformedParams });
      
      // The backend returns data directly, not wrapped
      return response.data;
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  },

  // Get single order details
  getOrder: async (orderId) => {
    try {
      const response = await api.get(`/admin/orders/${orderId}`);
      
      // The backend returns data directly, not wrapped
      return response.data;
    } catch (error) {
      console.error('Error fetching order:', error);
      throw error;
    }
  },

  // Update order status
  updateOrderStatus: async (orderId, status, note = '') => {
    try {
      const response = await api.put(`/admin/orders/${orderId}/status`, {
        status,
        note
      });
      return response.data;
    } catch (error) {
      console.error('Error updating order status:', error);
      throw error;
    }
  },

  // Get order statistics
  getOrderStats: async (params = {}) => {
    try {
      const response = await api.get('/admin/orders/stats', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching order stats:', error);
      throw error;
    }
  }
};

export default adminOrderService;