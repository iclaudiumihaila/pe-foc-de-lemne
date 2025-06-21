import React, { createContext, useContext, useReducer, useEffect } from 'react';
import api from '../services/api';

// Initial state
const initialState = {
  isAuthenticated: false,
  user: null,
  isLoading: true,
  error: null,
  tokens: null
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REFRESH_TOKEN_SUCCESS: 'REFRESH_TOKEN_SUCCESS',
  REFRESH_TOKEN_FAILURE: 'REFRESH_TOKEN_FAILURE',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_AUTH_DATA: 'SET_AUTH_DATA'
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        tokens: null,
        isLoading: false,
        error: action.payload.error
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        tokens: null,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.REFRESH_TOKEN_SUCCESS:
      return {
        ...state,
        tokens: action.payload.tokens,
        error: null
      };
    
    case AUTH_ACTIONS.REFRESH_TOKEN_FAILURE:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        tokens: null,
        error: action.payload.error
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload.loading
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.SET_AUTH_DATA:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isLoading: false,
        error: null
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Storage keys
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  USER_DATA: 'auth_user_data'
};

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Token management utilities
  const setTokensInStorage = (tokens) => {
    if (tokens?.access_token) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
    }
    if (tokens?.refresh_token) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
    }
  };

  const clearTokensFromStorage = () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
  };

  const getTokenFromStorage = () => {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  };

  const getRefreshTokenFromStorage = () => {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  };

  const setUserDataInStorage = (userData) => {
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
  };

  const getUserDataFromStorage = () => {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    return userData ? JSON.parse(userData) : null;
  };

  // Create authenticated API instance
  const createAuthenticatedApi = (token) => {
    const authApi = api.create();
    authApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    return authApi;
  };

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await api.post('/auth/admin/login', {
        username: credentials.username,
        password: credentials.password
      });

      if (response.data.success) {
        const { user, tokens } = response.data.data;
        
        // Store tokens and user data
        setTokensInStorage(tokens);
        setUserDataInStorage(user);

        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user, tokens }
        });

        return { success: true, message: response.data.message };
      } else {
        const error = response.data.error?.message || 'Eroare la autentificare';
        dispatch({
          type: AUTH_ACTIONS.LOGIN_FAILURE,
          payload: { error }
        });
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 
                          error.response?.data?.message || 
                          'Eroare de rețea. Verificați conexiunea.';
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: { error: errorMessage }
      });
      
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    const token = getTokenFromStorage();
    
    try {
      if (token) {
        // Call logout endpoint to invalidate token on server
        const authApi = createAuthenticatedApi(token);
        await authApi.post('/auth/admin/logout');
      }
    } catch (error) {
      console.warn('Logout API call failed:', error.message);
      // Continue with client-side logout even if server call fails
    }

    // Clear client-side data
    clearTokensFromStorage();
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  // Refresh token function
  const refreshToken = async () => {
    const refresh_token = getRefreshTokenFromStorage();
    
    if (!refresh_token) {
      dispatch({
        type: AUTH_ACTIONS.REFRESH_TOKEN_FAILURE,
        payload: { error: 'Nu există token de reînnoire' }
      });
      return false;
    }

    try {
      const response = await api.post('/auth/admin/refresh', {
        refresh_token
      });

      if (response.data.success) {
        const tokens = response.data.data;
        setTokensInStorage(tokens);

        dispatch({
          type: AUTH_ACTIONS.REFRESH_TOKEN_SUCCESS,
          payload: { tokens }
        });

        return true;
      } else {
        clearTokensFromStorage();
        dispatch({
          type: AUTH_ACTIONS.REFRESH_TOKEN_FAILURE,
          payload: { error: response.data.error?.message || 'Token invalid' }
        });
        return false;
      }
    } catch (error) {
      clearTokensFromStorage();
      dispatch({
        type: AUTH_ACTIONS.REFRESH_TOKEN_FAILURE,
        payload: { error: 'Eroare la reînnoire token' }
      });
      return false;
    }
  };

  // Verify token function
  const verifyToken = async (token) => {
    try {
      const authApi = createAuthenticatedApi(token);
      const response = await authApi.post('/auth/admin/verify');
      
      return response.data.success && response.data.data.valid;
    } catch (error) {
      return false;
    }
  };

  // Check authentication status
  const checkAuthStatus = async () => {
    dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: { loading: true } });

    const token = getTokenFromStorage();
    const userData = getUserDataFromStorage();

    if (!token || !userData) {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: { loading: false } });
      return;
    }

    // Verify token is still valid
    const isValid = await verifyToken(token);
    
    if (isValid) {
      // Token is valid, restore authentication state
      dispatch({
        type: AUTH_ACTIONS.SET_AUTH_DATA,
        payload: {
          user: userData,
          tokens: { access_token: token, refresh_token: getRefreshTokenFromStorage() }
        }
      });
    } else {
      // Token is invalid, try to refresh
      const refreshed = await refreshToken();
      
      if (!refreshed) {
        // Refresh failed, clear everything
        clearTokensFromStorage();
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
      } else {
        // Refresh succeeded, restore state with updated tokens
        dispatch({
          type: AUTH_ACTIONS.SET_AUTH_DATA,
          payload: {
            user: userData,
            tokens: { 
              access_token: getTokenFromStorage(), 
              refresh_token: getRefreshTokenFromStorage() 
            }
          }
        });
      }
    }

    dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: { loading: false } });
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Get current access token
  const getToken = () => {
    return state.tokens?.access_token || getTokenFromStorage();
  };

  // Check if user has admin role
  const isAdmin = () => {
    return state.user?.role === 'admin';
  };

  // Protected route helper
  const requireAuth = () => {
    return state.isAuthenticated && isAdmin();
  };

  // Setup axios interceptor for automatic token attachment
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        const token = getToken();
        if (token && config.url?.includes('/admin/')) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors for admin routes
        if (error.response?.status === 401 && 
            originalRequest.url?.includes('/admin/') && 
            !originalRequest._retry) {
          
          originalRequest._retry = true;

          // Try to refresh token
          const refreshed = await refreshToken();
          
          if (refreshed) {
            // Retry original request with new token
            const newToken = getTokenFromStorage();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          } else {
            // Refresh failed, logout user
            logout();
          }
        }

        return Promise.reject(error);
      }
    );

    // Cleanup interceptors on unmount
    return () => {
      api.interceptors.request.eject(requestInterceptor);
      api.interceptors.response.eject(responseInterceptor);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.tokens]);

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const contextValue = {
    // State
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    isLoading: state.isLoading,
    error: state.error,
    tokens: state.tokens,

    // Actions
    login,
    logout,
    refreshToken,
    verifyToken,
    checkAuthStatus,
    clearError,

    // Utilities
    getToken,
    isAdmin,
    requireAuth
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;