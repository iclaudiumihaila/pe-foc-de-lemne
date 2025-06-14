import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { CartProvider } from './contexts/CartContext';
import { ToastProvider } from './components/common/Toast';
import ErrorBoundary from './components/common/ErrorBoundary';
import Header from './components/common/Header';
import { PageLoading } from './components/common/Loading';
import NetworkStatusIndicator from './components/common/NetworkStatusIndicator';
import MetaTags from './components/SEO/MetaTags';
import { LocalBusinessStructuredData } from './components/SEO/StructuredData';
import GoogleAnalytics, { RomanianBusinessAnalytics } from './components/Analytics/GoogleAnalytics';
import CookieConsent from './components/Analytics/CookieConsent';
import { performanceMonitor } from './utils/performance';
import { SEO_TEMPLATES } from './data/seoTemplates';
import './styles/index.css';

// Lazy load pages for better performance
const Home = React.lazy(() => 
  import('./pages/Home').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'Home' });
    return module;
  })
);

const Products = React.lazy(() => 
  import('./pages/Products').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'Products' });
    return module;
  })
);

const Cart = React.lazy(() => 
  import('./pages/Cart').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'Cart' });
    return module;
  })
);

const Checkout = React.lazy(() => 
  import('./pages/Checkout').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'Checkout' });
    return module;
  })
);

const OrderConfirmation = React.lazy(() => 
  import('./pages/OrderConfirmation').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'OrderConfirmation' });
    return module;
  })
);

const AdminLogin = React.lazy(() => 
  import('./pages/AdminLogin').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminLogin' });
    return module;
  })
);

const AdminDashboard = React.lazy(() => 
  import('./pages/AdminDashboard').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminDashboard' });
    return module;
  })
);

const NotFound = React.lazy(() => 
  import('./pages/NotFound').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'NotFound' });
    return module;
  })
);

function App() {
  return (
    <ErrorBoundary>
      <HelmetProvider>
        <ToastProvider>
          <CartProvider>
            <Router>
              {/* Global SEO meta tags */}
              <MetaTags {...SEO_TEMPLATES.home} />
              <LocalBusinessStructuredData />
              
              {/* Analytics Integration */}
              <GoogleAnalytics 
                measurementId={process.env.REACT_APP_GA4_MEASUREMENT_ID}
                debugMode={process.env.NODE_ENV === 'development'}
              />
              <RomanianBusinessAnalytics />
              
              <div className="page-container font-sans">
                <Header />
                <NetworkStatusIndicator />
                <main className="main-content">
                  <Suspense fallback={<PageLoading message="Se încarcă pagina..." />}>
                    <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/produse" element={<Products />} />
                      <Route path="/cos" element={<Cart />} />
                      <Route path="/comanda" element={<Checkout />} />
                      <Route path="/confirmare-comanda/:orderNumber" element={<OrderConfirmation />} />
                      <Route path="/admin/login" element={<AdminLogin />} />
                      <Route path="/admin/dashboard" element={<AdminDashboard />} />
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </Suspense>
                </main>
                <footer className="bg-secondary-800 text-white py-8 mt-16">
                  <div className="max-w-7xl mx-auto px-4 text-center">
                    <p className="font-semibold">&copy; 2024 Pe Foc de Lemne - Produse Locale Românești</p>
                    <p className="opacity-80 mt-2">Sprijinind producătorii locali și agricultura durabilă</p>
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-center space-x-6 text-sm">
                        <a href="/termeni" className="hover:text-primary-300 transition-colors">
                          Termeni și condiții
                        </a>
                        <a href="/confidentialitate" className="hover:text-primary-300 transition-colors">
                          Politica de confidențialitate
                        </a>
                        <a href="/contact" className="hover:text-primary-300 transition-colors">
                          Contact
                        </a>
                      </div>
                      <p className="text-xs opacity-60">
                        Marketplace pentru produse locale românești de la producători verificați
                      </p>
                    </div>
                  </div>
                </footer>
              </div>
              
              {/* Cookie Consent for GDPR Compliance */}
              <CookieConsent />
            </Router>
          </CartProvider>
        </ToastProvider>
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App;