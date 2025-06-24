import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import AdminNavBar from '../components/admin/AdminNavBar';
import AdminSidebar from '../components/admin/AdminSidebar';
import { AdminSidebarProvider, useAdminSidebar } from '../context/AdminSidebarContext';
import { useAuth } from '../context/AuthContext';

const AdminLayoutContent = () => {
  const { isCollapsed } = useAdminSidebar();
  const { isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();
  
  // Check if we're on the login page
  const isLoginPage = location.pathname === '/admin/login';
  
  // Only show navigation for authenticated admin users
  const showNavigation = isAuthenticated && isAdmin() && !isLoginPage;
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {showNavigation && (
        <>
          <div className="fixed top-0 left-0 right-0 z-50">
            <AdminNavBar />
          </div>
          <div className="fixed left-0 top-16 h-full z-40">
            <AdminSidebar />
          </div>
        </>
      )}
      <div className={showNavigation ? `pt-16 transition-all duration-300 ${isCollapsed ? 'pl-16' : 'pl-64'}` : ''}>
        <Outlet />
      </div>
    </div>
  );
};

const AdminLayout = () => {
  return (
    <AdminSidebarProvider>
      <AdminLayoutContent />
    </AdminSidebarProvider>
  );
};

export default AdminLayout;