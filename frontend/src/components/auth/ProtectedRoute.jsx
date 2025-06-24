import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageLoading } from '../common/Loading';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, isLoading: loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <PageLoading message="Verificare autentificare..." />;
  }

  if (!isAuthenticated) {
    // Redirect to login page but save the attempted location
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin()) {
    // User is authenticated but not an admin
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;