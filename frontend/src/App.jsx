import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { CartProvider } from './contexts/CartContext';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/common/Toast';
import ErrorBoundary from './components/common/ErrorBoundary';
import { PageLoading } from './components/common/Loading';
import ScrollToTop from './components/common/ScrollToTop';
import MetaTags from './components/SEO/MetaTags';
import { LocalBusinessStructuredData } from './components/SEO/StructuredData';
import GoogleAnalytics, { RomanianBusinessAnalytics } from './components/Analytics/GoogleAnalytics';
import CookieConsent from './components/Analytics/CookieConsent';
import { FloatingIndicatorManager } from './components/animations/FloatingIndicator';
import { performanceMonitor } from './utils/performance';
import { SEO_TEMPLATES } from './data/seoTemplates';
import PublicLayout from './layouts/PublicLayout';
import AdminLayout from './layouts/AdminLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';
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

const SwipeProducts = React.lazy(() => 
  import('./pages/SwipeProducts').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'SwipeProducts' });
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

const TestPhoneVerification = React.lazy(() => 
  import('./pages/TestPhoneVerification').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'TestPhoneVerification' });
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

const AdminProducts = React.lazy(() => 
  import('./pages/admin/Products').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminProducts' });
    return module;
  })
);

const AdminCategories = React.lazy(() => 
  import('./pages/admin/Categories').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminCategories' });
    return module;
  })
);

const AdminOrders = React.lazy(() => 
  import('./pages/admin/Orders').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminOrders' });
    return module;
  })
);

const AdminOrderDetails = React.lazy(() => 
  import('./pages/admin/OrderDetails').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminOrderDetails' });
    return module;
  })
);

const AdminSMSProviders = React.lazy(() => 
  import('./pages/admin/SMSProviders').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'AdminSMSProviders' });
    return module;
  })
);

const NotFound = React.lazy(() => 
  import('./pages/NotFound').then(module => {
    performanceMonitor.recordMetric('Page Lazy Load', performance.now(), { page: 'NotFound' });
    return module;
  })
);

// Conditional cookie consent component
const ConditionalCookieConsent = () => {
  const location = window.location.pathname;
  // Hide cookie consent on swipe page
  if (location === '/products/swipe') {
    return null;
  }
  return <CookieConsent />;
};

function App() {
  return (
    <ErrorBoundary>
      <HelmetProvider>
        <ToastProvider>
          <AuthProvider>
            <CartProvider>
              <Router>
                <ScrollToTop />
              
              {/* Global SEO meta tags */}
              <MetaTags {...SEO_TEMPLATES.home} />
              <LocalBusinessStructuredData />
              
              {/* Analytics Integration */}
              <GoogleAnalytics 
                measurementId={process.env.REACT_APP_GA4_MEASUREMENT_ID}
                debugMode={process.env.NODE_ENV === 'development'}
              />
              <RomanianBusinessAnalytics />
              
              <Suspense fallback={<PageLoading message="Se încarcă pagina..." />}>
                <Routes>
                  {/* Public Routes */}
                  <Route element={<PublicLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/products/swipe" element={<SwipeProducts />} />
                    <Route path="/products" element={<Products />} />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/comanda" element={<Checkout />} />
                    <Route path="/confirmare-comanda/:orderNumber" element={<OrderConfirmation />} />
                    <Route path="/test-phone" element={<TestPhoneVerification />} />
                    <Route path="*" element={<NotFound />} />
                  </Route>
                  
                  {/* Admin Routes */}
                  <Route path="/admin/login" element={<AdminLogin />} />
                  <Route path="/admin" element={
                    <ProtectedRoute requireAdmin>
                      <AdminLayout />
                    </ProtectedRoute>
                  }>
                    <Route index element={<Navigate to="/admin/dashboard" replace />} />
                    <Route path="dashboard" element={<AdminDashboard />} />
                    <Route path="products" element={<AdminProducts />} />
                    <Route path="categories" element={<AdminCategories />} />
                    <Route path="orders" element={<AdminOrders />} />
                    <Route path="orders/:id" element={<AdminOrderDetails />} />
                    <Route path="sms-providers" element={<AdminSMSProviders />} />
                  </Route>
                </Routes>
              </Suspense>
              
              {/* Cookie Consent for GDPR Compliance - Hidden on swipe page */}
              <ConditionalCookieConsent />
              
              {/* Floating Indicator Manager for Add to Cart animations */}
              <FloatingIndicatorManager />
            </Router>
          </CartProvider>
        </AuthProvider>
        </ToastProvider>
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App;