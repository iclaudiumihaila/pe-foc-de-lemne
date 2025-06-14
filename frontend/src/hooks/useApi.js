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