import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import CheckoutForm from '../components/checkout/CheckoutForm';
import { SectionErrorBoundary } from '../components/common/ErrorBoundary';
import { ArrowLeft } from 'lucide-react';

const Checkout = () => {
  // Detect mobile device
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Modern Mobile Header - matching cart design */}
      <header className="sticky top-0 z-40 bg-white shadow-sm">
        <div className="flex items-center px-4 py-3">
          <Link to="/cart" className="p-2 -m-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </Link>
          <h1 className="flex-1 text-center text-xl font-semibold text-gray-900">
            Finalizare comandă
          </h1>
          <div className="w-10" /> {/* Spacer for centering */}
        </div>
      </header>

      <div className="pb-24"> {/* Add padding for fixed bottom summary on mobile */}
        <SectionErrorBoundary>
          <CheckoutForm isMobile={isMobile} />
        </SectionErrorBoundary>
      </div>
    </div>
  );
};

export default Checkout;