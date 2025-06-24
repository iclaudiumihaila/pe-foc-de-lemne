import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminNavBar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login');
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-md h-16 border-b border-gray-200 dark:border-gray-700">
      <div className="h-full px-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Pe Foc de Lemne - Admin</h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <span className="text-gray-700 dark:text-gray-300 text-sm">
            Admin: {user?.name || 'Administrator'}
          </span>
          <button 
            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm font-medium transition-colors"
            type="button"
            onClick={handleLogout}
          >
            Deconectare
          </button>
        </div>
      </div>
    </nav>
  );
};

export default AdminNavBar;