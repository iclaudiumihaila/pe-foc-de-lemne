import api from './api';

class ApiService {
  // Health check endpoint
  async healthCheck() {
    try {
      const response = await api.get('/health');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status
      };
    }
  }
  
  // Generic GET request
  async get(endpoint, params = {}) {
    try {
      const response = await api.get(endpoint, { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status
      };
    }
  }
  
  // Generic POST request
  async post(endpoint, data = {}) {
    try {
      const response = await api.post(endpoint, data);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status
      };
    }
  }
  
  // Generic PUT request
  async put(endpoint, data = {}) {
    try {
      const response = await api.put(endpoint, data);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status
      };
    }
  }
  
  // Generic DELETE request
  async delete(endpoint) {
    try {
      const response = await api.delete(endpoint);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
        status: error.response?.status
      };
    }
  }
}

const apiServiceInstance = new ApiService();
export default apiServiceInstance;