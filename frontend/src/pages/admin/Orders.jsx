import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, Search, Filter } from 'lucide-react';
import adminOrderService from '../../services/adminOrderService';
import AdminTable from '../../components/admin/common/AdminTable';
import AdminPagination from '../../components/admin/common/AdminPagination';

const AdminOrders = () => {
  const navigate = useNavigate();
  
  // State
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchPhone, setSearchPhone] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;
  
  // Sort
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Order statuses with colors (matching backend STATUS_ constants)
  const orderStatuses = {
    pending: { label: 'În așteptare', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200' },
    confirmed: { label: 'Confirmat', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200' },
    preparing: { label: 'În preparare', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-200' },
    ready: { label: 'Pregătit', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-200' },
    delivered: { label: 'Livrat', color: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200' },
    cancelled: { label: 'Anulat', color: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-200' }
  };

  // Fetch orders
  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page: currentPage,
        limit: itemsPerPage,
        sort_by: sortBy,
        sort_order: sortOrder
      };
      
      // Add filters if set
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (searchPhone) {
        params.phone = searchPhone;
      }
      if (dateFrom) {
        params.date_from = dateFrom;
      }
      if (dateTo) {
        params.date_to = dateTo;
      }
      
      const response = await adminOrderService.getOrders(params);
      
      setOrders(response.orders || []);
      setTotalPages(response.total_pages || 1);
      setTotalItems(response.total || 0);
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError('Eroare la încărcarea comenzilor');
    } finally {
      setLoading(false);
    }
  }, [currentPage, sortBy, sortOrder, statusFilter, searchPhone, dateFrom, dateTo]);

  // Load orders on mount and when filters change
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, searchPhone, dateFrom, dateTo]);

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ro-RO', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON',
      minimumFractionDigits: 2
    }).format(amount);
  };

  // Handle sort
  const handleSort = (column) => {
    if (column === sortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  // Handle row click
  const handleRowClick = (order) => {
    navigate(`/admin/orders/${order.id}`);
  };

  // Table columns
  const columns = [
    {
      key: 'order_number',
      label: 'Nr. Comandă',
      sortable: true,
      render: (value) => (
        <span className="font-medium text-gray-900 dark:text-white">
          #{value}
        </span>
      )
    },
    {
      key: 'created_at',
      label: 'Data',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'customer_name',
      label: 'Client',
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">{row.customer_phone}</div>
        </div>
      )
    },
    {
      key: 'items_count',
      label: 'Produse',
      render: (value) => `${value} produse`
    },
    {
      key: 'total',
      label: 'Total',
      sortable: true,
      render: (value) => (
        <span className="font-medium">{formatCurrency(value)}</span>
      )
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => {
        const status = orderStatuses[value] || { label: value, color: 'bg-gray-100 text-gray-800' };
        return (
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.color}`}>
            {status.label}
          </span>
        );
      }
    },
    {
      key: 'delivery_city',
      label: 'Oraș',
      render: (value) => value || '-'
    }
  ];

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ShoppingBag className="h-8 w-8 text-orange-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gestionare Comenzi
            </h1>
          </div>
        </div>
        
        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Phone Search */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Căutare după telefon
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={searchPhone}
                  onChange={(e) => setSearchPhone(e.target.value)}
                  placeholder="ex: 0722123456"
                  className="pl-10 w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white"
                />
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status comandă
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Toate</option>
                {Object.entries(orderStatuses).map(([value, status]) => (
                  <option key={value} value={value}>{status.label}</option>
                ))}
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                De la data
              </label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Până la data
              </label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Clear Filters */}
          {(searchPhone || statusFilter !== 'all' || dateFrom || dateTo) && (
            <div className="mt-4">
              <button
                onClick={() => {
                  setSearchPhone('');
                  setStatusFilter('all');
                  setDateFrom('');
                  setDateTo('');
                }}
                className="flex items-center space-x-2 text-sm text-orange-600 hover:text-orange-700"
              >
                <Filter className="h-4 w-4" />
                <span>Resetează filtrele</span>
              </button>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Orders Table */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <AdminTable
            columns={columns}
            data={orders}
            onSort={handleSort}
            onRowClick={handleRowClick}
            loading={loading}
            emptyMessage={
              searchPhone || statusFilter !== 'all' || dateFrom || dateTo
                ? 'Nu s-au găsit comenzi conform filtrelor selectate'
                : 'Nu există comenzi încă'
            }
          />

          {/* Pagination */}
          {!loading && orders.length > 0 && (
            <div className="px-6 py-3 border-t border-gray-200 dark:border-gray-700">
              <AdminPagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminOrders;