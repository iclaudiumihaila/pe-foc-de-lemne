import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import { Package, ShoppingBag, Clock, FolderTree, Plus, FileText, Archive } from 'lucide-react';

const AdminDashboard = () => {
  const { isLoading } = useAuth();

  // Dashboard state
  const [dashboardData, setDashboardData] = useState({
    totalProducts: 0,
    totalOrders: 0,
    pendingOrders: 0,
    totalCategories: 0,
    recentActivity: []
  });
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [error, setError] = useState(null);

  // Authentication is already handled by ProtectedRoute wrapper

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

    loadDashboardData();
  }, []);

  // Show loading while checking data
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loading size="large" message="Se încarcă panoul de administrare..." />
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Panoul de Administrare
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
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
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="rounded-md bg-orange-50 dark:bg-orange-900/20 p-3">
                      <Package className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Total Produse
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {dashboardData.totalProducts}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Total Orders */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-3">
                      <ShoppingBag className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Total Comenzi
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {dashboardData.totalOrders}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Pending Orders */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="rounded-md bg-yellow-50 dark:bg-yellow-900/20 p-3">
                      <Clock className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Comenzi în Așteptare
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {dashboardData.pendingOrders}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Total Categories */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="rounded-md bg-purple-50 dark:bg-purple-900/20 p-3">
                      <FolderTree className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Total Categorii
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {dashboardData.totalCategories}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions and Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Actions */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                  Acțiuni Rapide
                </h3>
              </div>
              <div className="px-6 py-4 space-y-4">
                <Link
                  to="/admin/products"
                  className="flex items-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
                >
                  <Plus className="h-5 w-5 text-orange-600 dark:text-orange-400 mr-3" />
                  <span className="text-orange-800 dark:text-orange-200 font-medium">Adaugă Produs Nou</span>
                </Link>

                <Link
                  to="/admin/orders"
                  className="flex items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                >
                  <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-3" />
                  <span className="text-blue-800 dark:text-blue-200 font-medium">Vezi Toate Comenzile</span>
                </Link>

                <Link
                  to="/admin/categories"
                  className="flex items-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
                >
                  <Archive className="h-5 w-5 text-purple-600 dark:text-purple-400 mr-3" />
                  <span className="text-purple-800 dark:text-purple-200 font-medium">Gestionează Categorii</span>
                </Link>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
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
                            <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700" aria-hidden="true" />
                          )}
                          <div className="relative flex space-x-3">
                            <div>
                              <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white dark:ring-gray-800 ${
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
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  {activity.message}
                                </p>
                              </div>
                              <div className="text-right text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
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
  );
};

export default AdminDashboard;