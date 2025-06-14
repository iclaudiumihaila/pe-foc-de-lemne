import axios from 'axios';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api';
const API_TIMEOUT = 10000; // 10 seconds

// Romanian error messages
const romanianErrors = {
  // HTTP status errors
  400: 'Cererea nu este validă. Verificați datele introduse.',
  401: 'Nu sunteți autorizat. Reconectați-vă.',
  403: 'Acces interzis. Nu aveți permisiunea necesară.',
  404: 'Resursa solicitată nu a fost găsită.',
  408: 'Cererea a expirat. Încercați din nou.',
  429: 'Prea multe cereri. Încercați din nou mai târziu.',
  500: 'Eroare internă a serverului. Încercați din nou.',
  502: 'Serviciul este temporar indisponibil.',
  503: 'Serviciul este în mentenanță. Încercați mai târziu.',
  504: 'Timeout la server. Verificați conexiunea.',
  
  // Network and general errors
  'NETWORK_ERROR': 'Problemă de conexiune. Verificați internetul.',
  'TIMEOUT_ERROR': 'Cererea a expirat. Încercați din nou.',
  'UNKNOWN_ERROR': 'A apărut o eroare neașteptată.',
  'PARSE_ERROR': 'Eroare la procesarea răspunsului de la server.'
};

// Retry configuration
const retryConfig = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryableStatusCodes: [408, 429, 502, 503, 504],
  retryableNetworkErrors: ['ECONNABORTED', 'ENOTFOUND', 'ECONNRESET']
};

// Enhanced error class
class ApiError extends Error {
  constructor(message, status, code, isNetworkError = false, isRetryable = false, originalError = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.isNetworkError = isNetworkError;
    this.isRetryable = isRetryable;
    this.originalError = originalError;
    this.timestamp = new Date().toISOString();
  }
}

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

// Error handling functions
const createApiError = (error) => {
  let message, status, code, isNetworkError = false, isRetryable = false;
  
  if (error.response) {
    // Server responded with error status
    status = error.response.status;
    message = romanianErrors[status] || romanianErrors['UNKNOWN_ERROR'];
    code = status.toString();
    isRetryable = retryConfig.retryableStatusCodes.includes(status);
    
    // Try to get Romanian message from server response
    if (error.response.data?.message) {
      message = error.response.data.message;
    }
  } else if (error.code === 'ECONNABORTED') {
    // Request timeout
    message = romanianErrors['TIMEOUT_ERROR'];
    code = 'TIMEOUT_ERROR';
    isRetryable = true;
  } else if (error.request) {
    // Network error
    message = romanianErrors['NETWORK_ERROR'];
    code = 'NETWORK_ERROR';
    isNetworkError = true;
    isRetryable = retryConfig.retryableNetworkErrors.includes(error.code);
  } else {
    // Something else happened
    message = romanianErrors['UNKNOWN_ERROR'];
    code = 'UNKNOWN_ERROR';
  }
  
  return new ApiError(message, status, code, isNetworkError, isRetryable, error);
};

// Retry function with exponential backoff
const retryRequest = async (config, retryCount = 0) => {
  try {
    return await api.request(config);
  } catch (error) {
    const apiError = createApiError(error);
    
    if (retryCount < retryConfig.maxRetries && apiError.isRetryable) {
      const delay = retryConfig.retryDelay * Math.pow(2, retryCount); // Exponential backoff
      console.log(`Retrying request after ${delay}ms (attempt ${retryCount + 1}/${retryConfig.maxRetries})`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return retryRequest(config, retryCount + 1);
    }
    
    throw apiError;
  }
};

// Response interceptor with enhanced error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    
    return response;
  },
  async (error) => {
    console.error('API Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data
    });
    
    const apiError = createApiError(error);
    
    // Log error for monitoring
    console.error('Enhanced API Error:', {
      message: apiError.message,
      status: apiError.status,
      code: apiError.code,
      isNetworkError: apiError.isNetworkError,
      isRetryable: apiError.isRetryable,
      timestamp: apiError.timestamp,
      url: error.config?.url
    });
    
    return Promise.reject(apiError);
  }
);

// Enhanced API methods with retry logic
const enhancedApi = {
  async get(url, config = {}) {
    return retryRequest({ ...config, method: 'get', url });
  },
  
  async post(url, data, config = {}) {
    return retryRequest({ ...config, method: 'post', url, data });
  },
  
  async put(url, data, config = {}) {
    return retryRequest({ ...config, method: 'put', url, data });
  },
  
  async delete(url, config = {}) {
    return retryRequest({ ...config, method: 'delete', url });
  },
  
  async patch(url, data, config = {}) {
    return retryRequest({ ...config, method: 'patch', url, data });
  }
};

// Export both the original axios instance and enhanced API
export default enhancedApi;
export { api as axiosInstance, ApiError, romanianErrors };