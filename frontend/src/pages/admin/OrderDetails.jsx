import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FileText, 
  ArrowLeft, 
  User, 
  Phone, 
  MapPin, 
  Calendar,
  Package,
  CreditCard,
  MessageSquare,
  Truck
} from 'lucide-react';
import adminOrderService from '../../services/adminOrderService';

const AdminOrderDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // State
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [statusNote, setStatusNote] = useState('');

  // Order statuses with colors
  const orderStatuses = {
    pending: { label: 'În așteptare', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
    confirmed: { label: 'Confirmat', color: 'bg-blue-100 text-blue-800 border-blue-300' },
    processing: { label: 'În procesare', color: 'bg-indigo-100 text-indigo-800 border-indigo-300' },
    shipped: { label: 'Expediat', color: 'bg-purple-100 text-purple-800 border-purple-300' },
    delivered: { label: 'Livrat', color: 'bg-green-100 text-green-800 border-green-300' },
    cancelled: { label: 'Anulat', color: 'bg-red-100 text-red-800 border-red-300' }
  };

  // Fetch order details
  useEffect(() => {
    const fetchOrder = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await adminOrderService.getOrder(id);
        setOrder(response);
      } catch (err) {
        console.error('Error fetching order:', err);
        setError('Eroare la încărcarea detaliilor comenzii');
      } finally {
        setLoading(false);
      }
    };
    
    fetchOrder();
  }, [id]);

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

  // Update order status
  const handleStatusUpdate = async (newStatus) => {
    if (updating || !order) return;
    
    setUpdating(true);
    setError(null);
    
    try {
      await adminOrderService.updateOrderStatus(order.id, newStatus, statusNote);
      setOrder({ ...order, status: newStatus });
      setStatusNote('');
      
      // Show success message
      alert('Status actualizat cu succes!');
    } catch (err) {
      console.error('Error updating order status:', err);
      setError('Eroare la actualizarea statusului');
    } finally {
      setUpdating(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  // Error state
  if (error && !order) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300 px-4 py-3 rounded-md">
          {error}
        </div>
        <button
          onClick={() => navigate('/admin/orders')}
          className="mt-4 flex items-center space-x-2 text-orange-600 hover:text-orange-700"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Înapoi la comenzi</span>
        </button>
      </div>
    );
  }

  if (!order) return null;

  const currentStatus = orderStatuses[order.status] || { label: order.status, color: 'bg-gray-100 text-gray-800' };

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/admin/orders')}
              className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <ArrowLeft className="h-6 w-6" />
            </button>
            <FileText className="h-8 w-8 text-orange-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Comandă #{order.order_number}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {formatDate(order.created_at)}
              </p>
            </div>
          </div>
          
          {/* Current Status */}
          <div className={`px-4 py-2 rounded-full border-2 font-medium ${currentStatus.color}`}>
            {currentStatus.label}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-300 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Customer Information */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <User className="h-5 w-5 mr-2 text-orange-600" />
                Informații Client
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Nume</p>
                  <p className="font-medium text-gray-900 dark:text-white">{order.customer_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Telefon</p>
                  <p className="font-medium text-gray-900 dark:text-white flex items-center">
                    <Phone className="h-4 w-4 mr-1" />
                    {order.customer_phone}
                  </p>
                </div>
                {order.customer_email && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                    <p className="font-medium text-gray-900 dark:text-white">{order.customer_email}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Delivery Information */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Truck className="h-5 w-5 mr-2 text-orange-600" />
                Informații Livrare
              </h2>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Adresă</p>
                  <p className="font-medium text-gray-900 dark:text-white flex items-start">
                    <MapPin className="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" />
                    <span>
                      {order.delivery_address}<br />
                      {order.delivery_city}, {order.delivery_county} {order.delivery_zip}
                    </span>
                  </p>
                </div>
                
                {order.delivery_notes && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Note livrare</p>
                    <p className="font-medium text-gray-900 dark:text-white flex items-start">
                      <MessageSquare className="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" />
                      {order.delivery_notes}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Order Items */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Package className="h-5 w-5 mr-2 text-orange-600" />
                Produse Comandate
              </h2>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Produs
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cantitate
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Preț unitar
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {order.items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-4 py-4">
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {item.product_name}
                            </p>
                            {item.variant && (
                              <p className="text-sm text-gray-500">{item.variant}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-center text-sm text-gray-900 dark:text-white">
                          {item.quantity}
                        </td>
                        <td className="px-4 py-4 text-right text-sm text-gray-900 dark:text-white">
                          {formatCurrency(item.price)}
                        </td>
                        <td className="px-4 py-4 text-right text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(item.quantity * item.price)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <td colSpan="3" className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-white">
                        Subtotal:
                      </td>
                      <td className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-white">
                        {formatCurrency(order.subtotal)}
                      </td>
                    </tr>
                    {order.shipping_cost > 0 && (
                      <tr>
                        <td colSpan="3" className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-white">
                          Transport:
                        </td>
                        <td className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(order.shipping_cost)}
                        </td>
                      </tr>
                    )}
                    <tr>
                      <td colSpan="3" className="px-4 py-3 text-right text-lg font-bold text-gray-900 dark:text-white">
                        Total:
                      </td>
                      <td className="px-4 py-3 text-right text-lg font-bold text-orange-600">
                        {formatCurrency(order.total)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Update Status */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Actualizare Status
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status nou
                  </label>
                  <select
                    value={order.status}
                    onChange={(e) => handleStatusUpdate(e.target.value)}
                    disabled={updating}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
                  >
                    {Object.entries(orderStatuses).map(([value, status]) => (
                      <option key={value} value={value}>{status.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notă (opțional)
                  </label>
                  <textarea
                    value={statusNote}
                    onChange={(e) => setStatusNote(e.target.value)}
                    rows={3}
                    disabled={updating}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
                    placeholder="Adaugă o notă despre schimbarea statusului..."
                  />
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <CreditCard className="h-5 w-5 mr-2 text-orange-600" />
                Sumar Comandă
              </h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Metodă plată:</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {order.payment_method === 'cash' ? 'Numerar la livrare' : order.payment_method}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Status plată:</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {order.payment_status === 'pending' ? 'În așteptare' : 
                     order.payment_status === 'paid' ? 'Plătit' : order.payment_status}
                  </span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between">
                    <span className="text-lg font-medium text-gray-900 dark:text-white">Total:</span>
                    <span className="text-lg font-bold text-orange-600">{formatCurrency(order.total)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Timeline */}
            {order.status_history && order.status_history.length > 0 && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-orange-600" />
                  Istoric Comandă
                </h2>
                
                <div className="space-y-3">
                  {order.status_history.map((history, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-2 h-2 bg-orange-600 rounded-full mt-1.5"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {orderStatuses[history.status]?.label || history.status}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDate(history.created_at)}
                        </p>
                        {history.note && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {history.note}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminOrderDetails;