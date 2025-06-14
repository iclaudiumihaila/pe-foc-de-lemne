import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, isLoading, logout, isAdmin } = useAuth();

  // Dashboard state
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    totalProducts: 0,
    totalOrders: 0,
    pendingOrders: 0,
    totalCategories: 0,
    recentActivity: []
  });
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [error, setError] = useState(null);

  // Authentication protection
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isAdmin())) {
      navigate('/admin/login', { replace: true });
    }
  }, [isAuthenticated, isAdmin, isLoading, navigate]);

  // Load dashboard data (placeholder for now)
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoadingData(true);
      setError(null);

      try {
        // Simulate API call - replace with real API calls in future tasks
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data for dashboard
        setDashboardData({
          totalProducts: 24,
          totalOrders: 156,
          pendingOrders: 8,
          totalCategories: 6,
          recentActivity: [
            {
              id: 1,
              type: 'order',
              message: 'Comandă nouă #1234 de la Maria Popescu',
              time: '2 min'
            },
            {
              id: 2,
              type: 'product',
              message: 'Produs nou adăugat: Brânză de capră',
              time: '1 oră'
            },
            {
              id: 3,
              type: 'order',
              message: 'Comandă #1233 livrată cu succes',
              time: '3 ore'
            }
          ]
        });
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        setError('Eroare la încărcarea datelor dashboard-ului');
      } finally {
        setIsLoadingData(false);
      }
    };

    if (isAuthenticated && isAdmin()) {
      loadDashboardData();
    }
  }, [isAuthenticated, isAdmin]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/admin/login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="large" message="Se încarcă panoul de administrare..." />
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated || !isAdmin()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 fixed w-full z-30 top-0">
        <div className="px-3 py-3 lg:px-5 lg:pl-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-start">
              {/* Mobile menu button */}
              <button
                onClick={toggleMobileMenu}
                type="button"
                className="inline-flex items-center p-2 text-sm text-gray-500 rounded-lg lg:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
                aria-controls="sidebar-menu"
                aria-expanded={isMobileMenuOpen}
              >
                <span className="sr-only">Deschide meniul principal</span>
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"></path>
                </svg>
              </button>
              
              {/* Logo */}
              <Link to="/" className="flex ml-2 md:mr-24">
                <span className="self-center text-xl font-semibold sm:text-2xl whitespace-nowrap text-green-800">
                  Pe Foc de Lemne
                </span>
              </Link>
            </div>

            {/* User menu */}
            <div className="flex items-center">
              <div className="flex items-center ml-3">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700">
                    Bună ziua, <span className="font-medium">{user?.name}</span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-red-600 hover:text-red-800 focus:outline-none focus:underline"
                  >
                    Deconectare
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Sidebar */}
      <aside 
        id="sidebar-menu"
        className={`fixed top-0 left-0 z-40 w-64 h-screen pt-20 transition-transform bg-white border-r border-gray-200 ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
        aria-label="Sidebar"
      >
        <div className="h-full px-3 pb-4 overflow-y-auto bg-white">
          <ul className="space-y-2 font-medium">
            {/* Dashboard */}
            <li>
              <Link
                to="/admin/dashboard"
                className="flex items-center p-2 text-gray-900 rounded-lg bg-gray-100 group"
              >
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
                </svg>
                <span className="ml-3">Tablou de bord</span>
              </Link>
            </li>

            {/* Products */}
            <li>
              <Link
                to="/admin/products"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg className="w-5 h-5 text-gray-500 group-hover:text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2L3 7v11a1 1 0 001 1h12a1 1 0 001-1V7l-7-5zM8 15a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clipRule="evenodd"></path>
                </svg>
                <span className="ml-3">Produse</span>
              </Link>
            </li>

            {/* Orders */}
            <li>
              <Link
                to="/admin/orders"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg className="w-5 h-5 text-gray-500 group-hover:text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd"></path>
                </svg>
                <span className="ml-3">Comenzi</span>
              </Link>
            </li>

            {/* Categories */}
            <li>
              <Link
                to="/admin/categories"
                className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg className="w-5 h-5 text-gray-500 group-hover:text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"></path>
                </svg>
                <span className="ml-3">Categorii</span>
              </Link>
            </li>
          </ul>

          {/* Store link */}
          <div className="pt-8 mt-8 border-t border-gray-200">
            <Link
              to="/"
              className="flex items-center p-2 text-gray-500 rounded-lg hover:bg-gray-100 group"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd"></path>
              </svg>
              <span className="ml-3">Înapoi la magazin</span>
            </Link>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="p-4 lg:ml-64">
        <div className="p-4 mt-14">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Panoul de Administrare
            </h1>
            <p className="text-gray-600">
              Bine ați venit în panoul de control pentru Pe Foc de Lemne
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <ErrorMessage 
              message={error}
              type="error"
              dismissible={true}
              onDismiss={() => setError(null)}
              className="mb-6"
            />
          )}

          {/* Loading State */}
          {isLoadingData ? (
            <div className="flex justify-center py-12">
              <Loading size="large" message="Se încarcă datele..." />
            </div>
          ) : (
            <>
              {/* Statistics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Total Products */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Produse
                          </dt>
                          <dd className="text-lg font-medium text-gray-900">
                            {dashboardData.totalProducts}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Total Orders */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Comenzi
                          </dt>
                          <dd className="text-lg font-medium text-gray-900">
                            {dashboardData.totalOrders}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Pending Orders */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Comenzi în Așteptare
                          </dt>
                          <dd className="text-lg font-medium text-gray-900">
                            {dashboardData.pendingOrders}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Total Categories */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Categorii
                          </dt>
                          <dd className="text-lg font-medium text-gray-900">
                            {dashboardData.totalCategories}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Actions */}
                <div className="bg-white shadow rounded-lg">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Acțiuni Rapide
                    </h3>
                  </div>
                  <div className="px-6 py-4 space-y-4">
                    <Link
                      to="/admin/products/new"
                      className="flex items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                    >
                      <svg className="h-5 w-5 text-green-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span className="text-green-800 font-medium">Adaugă Produs Nou</span>
                    </Link>

                    <Link
                      to="/admin/orders"
                      className="flex items-center p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      <svg className="h-5 w-5 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <span className="text-blue-800 font-medium">Vezi Toate Comenzile</span>
                    </Link>

                    <Link
                      to="/admin/categories"
                      className="flex items-center p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
                    >
                      <svg className="h-5 w-5 text-purple-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      <span className="text-purple-800 font-medium">Gestionează Categorii</span>
                    </Link>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white shadow rounded-lg">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Activitate Recentă
                    </h3>
                  </div>
                  <div className="px-6 py-4">
                    <div className="flow-root">
                      <ul className="-mb-8">
                        {dashboardData.recentActivity.map((activity, index) => (
                          <li key={activity.id}>
                            <div className="relative pb-8">
                              {index !== dashboardData.recentActivity.length - 1 && (
                                <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                              )}
                              <div className="relative flex space-x-3">
                                <div>
                                  <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                                    activity.type === 'order' ? 'bg-blue-500' : 'bg-green-500'
                                  }`}>
                                    {activity.type === 'order' ? (
                                      <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd" />
                                      </svg>
                                    ) : (
                                      <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 2L3 7v11a1 1 0 001 1h12a1 1 0 001-1V7l-7-5z" clipRule="evenodd" />
                                      </svg>
                                    )}
                                  </span>
                                </div>
                                <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                                  <div>
                                    <p className="text-sm text-gray-500">
                                      {activity.message}
                                    </p>
                                  </div>
                                  <div className="text-right text-sm whitespace-nowrap text-gray-500">
                                    {activity.time}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
          onClick={toggleMobileMenu}
        />
      )}
    </div>
  );
};

export default AdminDashboard;