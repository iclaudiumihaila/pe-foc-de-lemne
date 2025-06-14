# Task 44: Create base API service configuration

## Task Details
- **ID**: 44_api_service_base_setup
- **Title**: Create base API service configuration
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: React app basic setup (Task 41)

## Objective
Setup axios configuration for backend API communication to enable the React frontend to communicate with the Flask backend API that was built in Tasks 5-40, providing error handling, request interceptors, and response formatting.

## Requirements
1. **Base API Configuration**: Axios instance with base URL and timeout
2. **Request Interceptors**: Add request headers and authentication handling
3. **Response Interceptors**: Handle success and error responses consistently
4. **Error Handling**: Centralized error handling for API requests
5. **Environment Configuration**: Support for different API base URLs
6. **Health Check**: Test endpoint to verify backend connectivity

## Technical Implementation

### 1. API Service Configuration (frontend/src/services/api.js)
```javascript
import axios from 'axios';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api';
const API_TIMEOUT = 10000; // 10 seconds

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now()
    };
    
    // Add any auth tokens here in the future
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    
    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      data: config.data
    });
    
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    
    return response;
  },
  (error) => {
    console.error('API Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data
    });
    
    // Handle common error cases
    if (error.response?.status === 401) {
      // Handle unauthorized - could redirect to login in the future
      console.warn('Unauthorized API request');
    } else if (error.response?.status === 403) {
      // Handle forbidden
      console.warn('Forbidden API request');
    } else if (error.response?.status === 404) {
      // Handle not found
      console.warn('API endpoint not found');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error occurred');
    } else if (error.code === 'ECONNABORTED') {
      // Handle timeout
      console.error('API request timeout');
    } else if (!error.response) {
      // Handle network errors
      console.error('Network error - backend may be down');
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 2. API Service Methods (frontend/src/services/apiService.js)
```javascript
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

export default new ApiService();
```

### 3. Product API Service (frontend/src/services/productService.js)
```javascript
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

export default new ProductService();
```

### 4. Order API Service (frontend/src/services/orderService.js)
```javascript
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

export default new OrderService();
```

### 5. SMS Verification Service (frontend/src/services/smsService.js)
```javascript
import apiService from './apiService';

class SmsService {
  // Send verification code
  async sendVerificationCode(phoneNumber) {
    return await apiService.post('/sms/send-verification', {
      phone_number: phoneNumber
    });
  }
  
  // Verify code
  async verifyCode(phoneNumber, code) {
    return await apiService.post('/sms/verify-code', {
      phone_number: phoneNumber,
      verification_code: code
    });
  }
  
  // Get verification status
  async getVerificationStatus(phoneNumber) {
    return await apiService.get('/sms/status', {
      phone_number: phoneNumber
    });
  }
}

export default new SmsService();
```

### 6. Environment Configuration (.env.example)
```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080/api

# Development settings
REACT_APP_ENV=development
REACT_APP_DEBUG=true

# Future authentication settings
# REACT_APP_AUTH_ENABLED=false
# REACT_APP_SESSION_TIMEOUT=3600000
```

### 7. API Hook for React Components (frontend/src/hooks/useApi.js)
```javascript
import { useState, useEffect } from 'react';

export const useApi = (apiCall, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const result = await apiCall();
        
        if (isMounted) {
          if (result.success) {
            setData(result.data);
          } else {
            setError(result.error || 'API request failed');
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'An error occurred');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMounted = false;
    };
  }, dependencies);
  
  return { data, loading, error };
};

export const useApiCall = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const execute = async (apiCall) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiCall();
      
      if (result.success) {
        return result.data;
      } else {
        setError(result.error || 'API request failed');
        throw new Error(result.error || 'API request failed');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { execute, loading, error };
};
```

### 8. API Testing Component (frontend/src/components/ApiTest.jsx)
```javascript
import React, { useState } from 'react';
import apiService from '../services/apiService';
import productService from '../services/productService';

function ApiTest() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [products, setProducts] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const testHealthCheck = async () => {
    setLoading(true);
    try {
      const result = await apiService.healthCheck();
      setHealthStatus(result);
    } catch (error) {
      setHealthStatus({ success: false, error: error.message });
    }
    setLoading(false);
  };
  
  const testProductsEndpoint = async () => {
    setLoading(true);
    try {
      const result = await productService.getProducts();
      setProducts(result);
    } catch (error) {
      setProducts({ success: false, error: error.message });
    }
    setLoading(false);
  };
  
  return (
    <div className="card max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-secondary-800 mb-6">API Connection Test</h2>
      
      <div className="space-y-4">
        <div>
          <button 
            onClick={testHealthCheck}
            disabled={loading}
            className="btn-primary mr-4"
          >
            {loading ? 'Testing...' : 'Test Health Check'}
          </button>
          
          <button 
            onClick={testProductsEndpoint}
            disabled={loading}
            className="btn-secondary"
          >
            {loading ? 'Testing...' : 'Test Products API'}
          </button>
        </div>
        
        {healthStatus && (
          <div className={`p-4 rounded-lg ${healthStatus.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            <h3 className="font-semibold">Health Check Result:</h3>
            <pre className="text-sm mt-2">{JSON.stringify(healthStatus, null, 2)}</pre>
          </div>
        )}
        
        {products && (
          <div className={`p-4 rounded-lg ${products.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            <h3 className="font-semibold">Products API Result:</h3>
            <pre className="text-sm mt-2">{JSON.stringify(products, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default ApiTest;
```

## Implementation Steps

### 1. Create API Service Directory Structure
- Create frontend/src/services/ directory
- Setup axios configuration with base URL and interceptors
- Implement error handling and logging
- Add environment variable support

### 2. Implement Base API Service
- Create api.js with axios configuration
- Add request and response interceptors
- Implement timeout and error handling
- Setup logging for debugging

### 3. Create Service Layer Classes
- ProductService for product-related API calls
- OrderService for order management
- SmsService for SMS verification
- ApiService as base class for common methods

### 4. Add React Hooks for API Integration
- useApi hook for data fetching
- useApiCall hook for imperative API calls
- Error handling and loading states
- Component lifecycle management

### 5. Test API Configuration
- Create ApiTest component for testing
- Test health check endpoint
- Verify error handling
- Test different API endpoints

## API Endpoints Integration

### 1. Backend API Structure (from Tasks 5-40)
```
Backend API Endpoints:
├── /api/health (GET) - Health check
├── /api/products (GET) - List products
├── /api/products/:id (GET) - Get product
├── /api/orders (POST) - Create order
├── /api/orders/:id (GET) - Get order
├── /api/sms/send-verification (POST) - Send SMS code
└── /api/sms/verify-code (POST) - Verify SMS code
```

### 2. Request/Response Format
```javascript
// Request format
{
  method: 'POST',
  url: '/api/orders',
  data: {
    customer_name: 'John Doe',
    phone_number: '+1234567890',
    items: [
      { product_id: 1, quantity: 2 },
      { product_id: 2, quantity: 1 }
    ]
  }
}

// Response format
{
  success: true,
  data: {
    order_id: '12345',
    status: 'pending',
    total_amount: 29.97
  },
  status: 201
}
```

### 3. Error Response Format
```javascript
// Error response
{
  success: false,
  error: 'Validation failed: phone_number is required',
  status: 400
}
```

## Features Implemented

### 1. Request Management
- **Base URL Configuration**: Environment-based API endpoint
- **Timeout Handling**: 10-second timeout for all requests
- **Content-Type Headers**: JSON request/response handling
- **Cache Prevention**: Timestamp parameter to prevent caching

### 2. Response Processing
- **Success Handling**: Consistent success response format
- **Error Handling**: Centralized error processing
- **Status Code Handling**: HTTP status code interpretation
- **Logging**: Request/response logging for debugging

### 3. Service Architecture
- **Service Classes**: Organized API calls by domain
- **Method Consistency**: Standardized method signatures
- **Error Propagation**: Consistent error handling across services
- **Response Formatting**: Uniform response structure

### 4. React Integration
- **Custom Hooks**: useApi and useApiCall for component integration
- **Loading States**: Built-in loading state management
- **Error States**: Error handling for components
- **Lifecycle Management**: Proper cleanup and cancellation

## Environment Configuration

### 1. Development Setup
```bash
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_ENV=development
REACT_APP_DEBUG=true
```

### 2. Production Configuration
```bash
REACT_APP_API_BASE_URL=https://api.localproducer.com/api
REACT_APP_ENV=production
REACT_APP_DEBUG=false
```

### 3. Environment Variables Usage
- API base URL from environment
- Debug logging control
- Development vs production configuration
- Future authentication settings

## Success Criteria
- API service can make HTTP requests to backend health endpoint
- Request and response interceptors work correctly
- Error handling manages different error scenarios
- Service classes provide clean API for components
- React hooks integrate seamlessly with components
- Environment configuration supports different deployments