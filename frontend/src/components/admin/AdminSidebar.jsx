import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAdminSidebar } from '../../context/AdminSidebarContext';
import { LayoutDashboard, Package, ShoppingBag, FolderTree, MessageSquare, ChevronLeft, ChevronRight } from 'lucide-react';

const AdminSidebar = () => {
  const { isCollapsed, toggleCollapse, setActiveItem } = useAdminSidebar();
  const location = useLocation();

  return (
    <nav className={`bg-white dark:bg-gray-800 shadow-lg h-full transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          className="w-full flex items-center justify-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          onClick={toggleCollapse}
          type="button"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </button>
      </div>
      
      <ul className="py-4">
        <li>
          <Link 
            to="/admin/dashboard" 
            className={`flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${location.pathname === '/admin/dashboard' ? 'bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-600' : ''}`}
            onClick={() => setActiveItem('dashboard')}
          >
            <LayoutDashboard className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            {!isCollapsed && <span className="ml-3">Tablou de bord</span>}
          </Link>
        </li>
        
        <li>
          <Link 
            to="/admin/products" 
            className={`flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${location.pathname === '/admin/products' ? 'bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-600' : ''}`}
            onClick={() => setActiveItem('products')}
          >
            <Package className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            {!isCollapsed && <span className="ml-3">Produse</span>}
          </Link>
        </li>
        
        <li>
          <Link 
            to="/admin/orders" 
            className={`flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${location.pathname === '/admin/orders' ? 'bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-600' : ''}`}
            onClick={() => setActiveItem('orders')}
          >
            <ShoppingBag className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            {!isCollapsed && <span className="ml-3">Comenzi</span>}
          </Link>
        </li>
        
        <li>
          <Link 
            to="/admin/categories" 
            className={`flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${location.pathname === '/admin/categories' ? 'bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-600' : ''}`}
            onClick={() => setActiveItem('categories')}
          >
            <FolderTree className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            {!isCollapsed && <span className="ml-3">Categorii</span>}
          </Link>
        </li>
        
        <li>
          <Link 
            to="/admin/sms-providers" 
            className={`flex items-center px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${location.pathname === '/admin/sms-providers' ? 'bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-600' : ''}`}
            onClick={() => setActiveItem('sms-providers')}
          >
            <MessageSquare className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            {!isCollapsed && <span className="ml-3">Furnizori SMS</span>}
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default AdminSidebar;