import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';

const OrderConfirmation = () => {
  const { orderNumber } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orderNumber) {
      navigate('/');
    }
    // For now, just show success with order number
    // In a real app, you might fetch order details from API
    setLoading(false);
  }, [orderNumber, navigate]);

  if (loading) {
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
    <div className="min-h-screen bg-white py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Comanda a fost plasată cu succes!
          </h1>
          <p className="text-xl text-gray-600">
            Mulțumim pentru comandă!
          </p>
        </div>

        {/* Order Number */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8 text-center">
          <h2 className="text-lg font-medium text-green-800 mb-2">
            Numărul comenzii:
          </h2>
          <p className="text-2xl font-bold text-green-900">
            {orderNumber}
          </p>
          <p className="text-sm text-green-700 mt-3">
            Salvați acest număr pentru referință ulterioară
          </p>
        </div>

        {/* Support Info */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Aveți întrebări?
          </h3>
          <p className="text-gray-600 mb-4 text-sm">
            Suntem aici să vă ajutăm!
          </p>
          <div className="space-y-2 text-sm">
            <div className="flex items-center space-x-3">
              <span className="text-blue-600">📞</span>
              <span>Telefon: 0700 123 456</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-blue-600">📧</span>
              <span>Email: comenzi@pefocdelemne.ro</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/products"
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
            >
              Continuă cumpărăturile
            </Link>
            <Link
              to="/"
              className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Înapoi acasă
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;