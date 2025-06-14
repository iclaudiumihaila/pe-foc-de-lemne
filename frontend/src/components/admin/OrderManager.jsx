import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import Loading from '../common/Loading';
import ErrorMessage from '../common/ErrorMessage';

const OrderManager = () => {
  const { isAuthenticated, isAdmin, tokens } = useAuth();
  
  // State management
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Pagination and filtering
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalOrders, setTotalOrders] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFilter, setDateFilter] = useState({
    start_date: '',
    end_date: ''
  });
  const [amountFilter, setAmountFilter] = useState({
    min_total: '',
    max_total: ''
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Modal and form states
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);
  const [expandedOrder, setExpandedOrder] = useState(null);

  // Statistics
  const [statistics, setStatistics] = useState({
    total_revenue: 0,
    avg_order_value: 0,
    status_counts: {}
  });

  // Romanian status translations
  const statusTranslations = {
    'pending': 'în așteptare',
    'confirmed': 'confirmată',
    'completed': 'finalizată',
    'cancelled': 'anulată'
  };

  const statusOptions = [
    { value: 'pending', label: 'În așteptare', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'confirmed', label: 'Confirmată', color: 'bg-blue-100 text-blue-800' },
    { value: 'completed', label: 'Finalizată', color: 'bg-green-100 text-green-800' },
    { value: 'cancelled', label: 'Anulată', color: 'bg-red-100 text-red-800' }
  ];

  // Fetch orders
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      // Add filters
      if (statusFilter) params.set('status', statusFilter);
      if (searchTerm.trim()) params.set('customer', searchTerm.trim());
      if (dateFilter.start_date) params.set('start_date', dateFilter.start_date);
      if (dateFilter.end_date) params.set('end_date', dateFilter.end_date);
      if (amountFilter.min_total) params.set('min_total', amountFilter.min_total);
      if (amountFilter.max_total) params.set('max_total', amountFilter.max_total);
      
      const response = await api.get(`/admin/orders?${params}`, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });

      if (response.data.success) {
        setOrders(response.data.data.orders);
        setTotalPages(response.data.data.pagination.total_pages);
        setTotalOrders(response.data.data.pagination.total_items);
        setStatistics(response.data.data.statistics || {
          total_revenue: 0,
          avg_order_value: 0,
          status_counts: {}
        });
      }
    } catch (err) {
      console.error('Error fetching orders:', err);
      const errorMessage = err.response?.data?.error?.message || 'Eroare la încărcarea comenzilor. Încercați din nou.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter, dateFilter, amountFilter, sortBy, sortOrder, tokens]);

  // Initialize data
  useEffect(() => {
    if (isAuthenticated && isAdmin()) {
      fetchOrders();
    }
  }, [isAuthenticated, isAdmin, fetchOrders]);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchOrders();
  };

  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    setCurrentPage(1);
    if (filterType === 'status') {
      setStatusFilter(value);
    } else if (filterType === 'sort') {
      const [field, order] = value.split('_');
      setSortBy(field);
      setSortOrder(order);
    } else if (filterType === 'dateStart') {
      setDateFilter(prev => ({ ...prev, start_date: value }));
    } else if (filterType === 'dateEnd') {
      setDateFilter(prev => ({ ...prev, end_date: value }));
    } else if (filterType === 'minAmount') {
      setAmountFilter(prev => ({ ...prev, min_total: value }));
    } else if (filterType === 'maxAmount') {
      setAmountFilter(prev => ({ ...prev, max_total: value }));
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setDateFilter({ start_date: '', end_date: '' });
    setAmountFilter({ min_total: '', max_total: '' });
    setCurrentPage(1);
  };

  // Handle status update
  const handleStatusUpdate = async () => {
    if (!selectedOrder || !newStatus) return;

    try {
      setStatusLoading(true);
      setError(null);

      const response = await api.put(
        `/admin/orders/${selectedOrder._id}/status`,
        { status: newStatus },
        {
          headers: {
            'Authorization': `Bearer ${tokens?.access_token}`
          }
        }
      );

      if (response.data.success) {
        setSuccess('Statusul comenzii a fost actualizat cu succes!');
        setShowStatusModal(false);
        setSelectedOrder(null);
        setNewStatus('');
        fetchOrders();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error updating order status:', err);
      const errorMessage = err.response?.data?.error?.message || 'Eroare la actualizarea statusului. Încercați din nou.';
      setError(errorMessage);
    } finally {
      setStatusLoading(false);
    }
  };

  // Open status modal
  const openStatusModal = (order) => {
    setSelectedOrder(order);
    setNewStatus(order.status);
    setShowStatusModal(true);
  };

  // Close modal
  const closeModal = () => {
    setShowStatusModal(false);
    setSelectedOrder(null);
    setNewStatus('');
    setError(null);
  };

  // Toggle order details
  const toggleOrderDetails = (orderId) => {
    setExpandedOrder(expandedOrder === orderId ? null : orderId);
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ro-RO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(amount);
  };

  // Get status badge color
  const getStatusBadgeColor = (status) => {
    const statusOption = statusOptions.find(opt => opt.value === status);
    return statusOption ? statusOption.color : 'bg-gray-100 text-gray-800';
  };

  // Check admin access
  if (!isAuthenticated || !isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message="Acces neautorizat. Trebuie să fiți autentificat ca administrator." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestionare Comenzi</h1>
          <p className="text-gray-600 mt-1">Total: {totalOrders} comenzi</p>
        </div>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          {success}
        </div>
      )}
      
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} />
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Total venituri</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatCurrency(statistics.total_revenue || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Valoarea medie</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatCurrency(statistics.avg_order_value || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">În așteptare</p>
              <p className="text-2xl font-semibold text-gray-900">
                {statistics.status_counts?.pending || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="md:col-span-2">
            <div className="flex">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Căutați după client (nume/telefon)..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 transition-colors"
              >
                Căutare
              </button>
            </div>
          </form>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Toate statusurile</option>
            {statusOptions.map(status => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={`${sortBy}_${sortOrder}`}
            onChange={(e) => handleFilterChange('sort', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at_desc">Cele mai recente</option>
            <option value="created_at_asc">Cele mai vechi</option>
            <option value="total_desc">Valoare (descrescător)</option>
            <option value="total_asc">Valoare (crescător)</option>
            <option value="customer_name_asc">Client (A-Z)</option>
            <option value="customer_name_desc">Client (Z-A)</option>
          </select>
        </div>

        {/* Advanced Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date Filters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data început
            </label>
            <input
              type="date"
              value={dateFilter.start_date}
              onChange={(e) => handleFilterChange('dateStart', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Data sfârșit
            </label>
            <input
              type="date"
              value={dateFilter.end_date}
              onChange={(e) => handleFilterChange('dateEnd', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Amount Filters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Suma minimă (RON)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={amountFilter.min_total}
              onChange={(e) => handleFilterChange('minAmount', e.target.value)}
              placeholder="0.00"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Suma maximă (RON)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={amountFilter.max_total}
              onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
              placeholder="999.99"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Clear Filters */}
        <div className="mt-4 flex justify-end">
          <button
            onClick={clearFilters}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Șterge filtrele
          </button>
        </div>
      </div>

      {/* Orders Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loading size="large" message="Se încarcă comenzile..." />
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Nu au fost găsite comenzi.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Comandă
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acțiuni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {orders.map((order) => (
                  <React.Fragment key={order._id}>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <button
                            onClick={() => toggleOrderDetails(order._id)}
                            className="text-blue-600 hover:text-blue-800 mr-2"
                          >
                            <svg 
                              className={`h-4 w-4 transform transition-transform ${
                                expandedOrder === order._id ? 'rotate-90' : ''
                              }`} 
                              fill="currentColor" 
                              viewBox="0 0 20 20"
                            >
                              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                            </svg>
                          </button>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              #{order.order_number}
                            </div>
                            <div className="text-xs text-gray-500">
                              ID: {order._id.slice(-8)}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {order.customer_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {order.customer_phone}
                          </div>
                          {order.customer_email && (
                            <div className="text-xs text-gray-400">
                              {order.customer_email}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(order.total)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeColor(order.status)}`}>
                          {statusTranslations[order.status] || order.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => openStatusModal(order)}
                          className="text-blue-600 hover:text-blue-900 transition-colors"
                        >
                          Schimbă status
                        </button>
                      </td>
                    </tr>
                    
                    {/* Expanded Order Details */}
                    {expandedOrder === order._id && (
                      <tr>
                        <td colSpan="6" className="px-6 py-4 bg-gray-50">
                          <div className="space-y-4">
                            {/* Items */}
                            <div>
                              <h4 className="text-sm font-medium text-gray-900 mb-2">Produse comandate:</h4>
                              <div className="space-y-2">
                                {order.items && order.items.map((item, index) => (
                                  <div key={index} className="flex justify-between items-center bg-white p-3 rounded border">
                                    <div>
                                      <span className="text-sm font-medium text-gray-900">{item.name}</span>
                                      <span className="text-sm text-gray-500 ml-2">× {item.quantity}</span>
                                    </div>
                                    <span className="text-sm text-gray-900">
                                      {formatCurrency(item.price * item.quantity)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Special Instructions */}
                            {order.special_instructions && (
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Instrucțiuni speciale:</h4>
                                <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                                  {order.special_instructions}
                                </p>
                              </div>
                            )}

                            {/* Order Details */}
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="font-medium text-gray-900">Data creării:</span>
                                <span className="text-gray-600 ml-2">{formatDate(order.created_at)}</span>
                              </div>
                              <div>
                                <span className="font-medium text-gray-900">Ultima actualizare:</span>
                                <span className="text-gray-600 ml-2">{formatDate(order.updated_at)}</span>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Următor
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Pagina <span className="font-medium">{currentPage}</span> din{' '}
                    <span className="font-medium">{totalPages}</span> ({totalOrders} comenzi)
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Următor
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Status Update Modal */}
      {showStatusModal && selectedOrder && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Actualizează Status
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Comandă: <strong>#{selectedOrder.order_number}</strong>
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  Client: <strong>{selectedOrder.customer_name}</strong>
                </p>

                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status curent: <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ml-2 ${getStatusBadgeColor(selectedOrder.status)}`}>
                    {statusTranslations[selectedOrder.status] || selectedOrder.status}
                  </span>
                </label>

                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selectează noul status:
                </label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {statusOptions.map(status => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Anulează
                </button>
                <button
                  onClick={handleStatusUpdate}
                  disabled={statusLoading || newStatus === selectedOrder.status}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {statusLoading ? 'Se actualizează...' : 'Actualizează Status'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderManager;