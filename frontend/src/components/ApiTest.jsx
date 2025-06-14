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
            <pre className="text-sm mt-2 whitespace-pre-wrap">{JSON.stringify(healthStatus, null, 2)}</pre>
          </div>
        )}
        
        {products && (
          <div className={`p-4 rounded-lg ${products.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            <h3 className="font-semibold">Products API Result:</h3>
            <pre className="text-sm mt-2 whitespace-pre-wrap">{JSON.stringify(products, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default ApiTest;