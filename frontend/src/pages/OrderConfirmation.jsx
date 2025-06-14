import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const OrderConfirmation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [orderData, setOrderData] = useState(null);

  useEffect(() => {
    // Get order data from navigation state (passed from checkout)
    if (location.state?.orderData) {
      setOrderData(location.state.orderData);
    } else {
      // If no order data, redirect to home
      navigate('/');
    }
  }, [location.state, navigate]);

  // Format price for display
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ro-RO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Print order confirmation
  const handlePrint = () => {
    window.print();
  };

  if (!orderData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-gray-600">Se încarcă confirmarea comenzii...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Comanda confirmată!
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Mulțumim pentru comandă, {orderData.customer.firstName}!
          </p>
          <p className="text-gray-500">
            Comanda dvs. a fost plasată cu succes și va fi procesată în curând.
          </p>
        </div>

        {/* Order Number and Basic Info */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8 text-center">
          <h2 className="text-2xl font-bold text-green-800 mb-2">
            Numărul comenzii: {orderData.orderNumber}
          </h2>
          <p className="text-green-700 mb-4">
            Data comenzii: {formatDate(orderData.orderDate)}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handlePrint}
              className="inline-flex items-center px-4 py-3 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors min-h-[44px] justify-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
              </svg>
              Printează confirmarea
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          {/* Order Details */}
          <div className="space-y-6">
            {/* Customer Information */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Informații de livrare
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Nume:</span>
                  <span className="font-medium">{orderData.customer.firstName} {orderData.customer.lastName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Telefon:</span>
                  <span className="font-medium">{orderData.customer.phone} ✅</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Email:</span>
                  <span className="font-medium">{orderData.customer.email}</span>
                </div>
                <div className="flex justify-between items-start">
                  <span className="text-gray-600">Adresă:</span>
                  <span className="font-medium text-right max-w-xs">
                    {orderData.delivery.address}
                  </span>
                </div>
                {orderData.delivery.notes && (
                  <div className="flex justify-between items-start">
                    <span className="text-gray-600">Observații:</span>
                    <span className="font-medium text-right max-w-xs">
                      {orderData.delivery.notes}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Order Items */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Produsele comandate
              </h3>
              <div className="space-y-3">
                {orderData.items.map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-3 border-b border-gray-200 last:border-b-0">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{item.name}</h4>
                      <p className="text-sm text-gray-600">
                        {formatPrice(item.price)} × {item.quantity} {item.unit || 'buc'}
                      </p>
                    </div>
                    <div className="font-medium text-gray-900">
                      {formatPrice(item.subtotal)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing Summary */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Rezumatul comenzii
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="font-medium">{formatPrice(orderData.pricing.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">TVA (19%):</span>
                  <span className="font-medium">{formatPrice(orderData.pricing.tax)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Livrare locală:</span>
                  <span className="font-medium text-green-600">Gratuită</span>
                </div>
                <div className="border-t border-gray-200 pt-3 flex justify-between">
                  <span className="text-lg font-semibold text-gray-900">Total plătit:</span>
                  <span className="text-xl font-bold text-green-600">
                    {formatPrice(orderData.pricing.total)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Next Steps and Information */}
          <div className="space-y-6">
            {/* What's Next */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Ce urmează?
              </h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-sm">1</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Confirmarea comenzii</h4>
                    <p className="text-sm text-gray-600">
                      Veți primi un SMS de confirmare în următoarele minute cu detaliile comenzii.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-sm">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Pregătirea comenzii</h4>
                    <p className="text-sm text-gray-600">
                      Producătorii locali vor pregăti produsele dvs. proaspete. Estimare: 1-2 zile lucrătoare.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-sm">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Livrarea</h4>
                    <p className="text-sm text-gray-600">
                      Vă vom contacta telefonic pentru programarea livrării. Livrarea se face între orele 9:00-18:00.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Local Producer Message */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-3">
                🌱 Mulțumim că susțineți producătorii locali!
              </h3>
              <div className="text-sm text-green-700 space-y-2">
                <p>Prin această comandă, susțineți:</p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Familiile de fermieri din comunitatea locală</li>
                  <li>Agricultura sustenabilă și ecologică</li>
                  <li>Economia locală și dezvoltarea regiunii</li>
                  <li>Reducerea amprenta de carbon prin transport scurt</li>
                </ul>
                <p className="font-medium mt-3">
                  Împreună construim o comunitate mai puternică! 🤝
                </p>
              </div>
            </div>

            {/* Contact Support */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Aveți întrebări?
              </h3>
              <p className="text-gray-600 mb-4">
                Echipa noastră este disponibilă pentru orice întrebări despre comanda dvs.
              </p>
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-3">
                  <span className="text-blue-600">📞</span>
                  <div>
                    <span className="font-medium">Telefon:</span>
                    <span className="ml-2">0700 123 456</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-blue-600">📧</span>
                  <div>
                    <span className="font-medium">Email:</span>
                    <span className="ml-2">comenzi@pefocdelemne.ro</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-blue-600">⏰</span>
                  <div>
                    <span className="font-medium">Program:</span>
                    <span className="ml-2">Luni - Duminică, 8:00 - 20:00</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-12 text-center">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              Continuați să explorați produsele noastre locale
            </h3>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/products"
                className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors min-h-[44px] flex items-center justify-center"
              >
                🛒 Explorează produsele
              </Link>
              <Link
                to="/"
                className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors min-h-[44px] flex items-center justify-center"
              >
                🏠 Înapoi acasă
              </Link>
            </div>
            
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                Mulțumim că alegeți produsele locale de la Pe Foc de Lemne! 🌟
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;