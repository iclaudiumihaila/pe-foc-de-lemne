import React, { createContext, useContext, useState } from 'react';

// Create the context
const AdminSidebarContext = createContext({
  isCollapsed: false,
  toggleCollapse: () => {},
  activeItem: 'dashboard',
  setActiveItem: () => {}
});

// Provider component
export const AdminSidebarProvider = ({ children }) => {
  // Initialize from localStorage or default to false
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('adminSidebarCollapsed');
    return saved === 'true';
  });
  const [activeItem, setActiveItem] = useState('dashboard');

  const toggleCollapse = () => {
    setIsCollapsed(prev => {
      const newState = !prev;
      // Save to localStorage
      localStorage.setItem('adminSidebarCollapsed', newState.toString());
      return newState;
    });
  };

  const value = {
    isCollapsed,
    toggleCollapse,
    activeItem,
    setActiveItem
  };

  return (
    <AdminSidebarContext.Provider value={value}>
      {children}
    </AdminSidebarContext.Provider>
  );
};

// Custom hook for using the context
export const useAdminSidebar = () => {
  const context = useContext(AdminSidebarContext);
  if (!context) {
    throw new Error('useAdminSidebar must be used within AdminSidebarProvider');
  }
  return context;
};

export default AdminSidebarContext;