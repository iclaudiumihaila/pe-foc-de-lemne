/**
 * Analytics Hooks for Local Producer Web Application
 * 
 * React hooks for analytics tracking, performance monitoring,
 * and Romanian business intelligence.
 */

import { useEffect, useCallback, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  trackPageView,
  trackCustomEvent,
  trackEcommerceEvent,
  trackProductView,
  trackAddToCart,
  trackPurchase,
  trackSearch,
  setAnalyticsConsent,
  getAnalyticsConsent,
  EVENT_CATEGORIES,
  CUSTOM_EVENTS,
  ECOMMERCE_EVENTS
} from '../utils/analytics';

/**
 * Main analytics hook for page tracking and consent management
 */
export const useAnalytics = () => {
  const location = useLocation();
  const [consentGiven, setConsentGiven] = useState(getAnalyticsConsent());
  const [isInitialized, setIsInitialized] = useState(false);

  // Track page views on route changes
  useEffect(() => {
    if (consentGiven) {
      const pageTitle = document.title;
      trackPageView(location.pathname, pageTitle);
    }
  }, [location.pathname, consentGiven]);

  // Initialize analytics
  useEffect(() => {
    if (consentGiven && !isInitialized) {
      setIsInitialized(true);
    }
  }, [consentGiven, isInitialized]);

  const giveConsent = useCallback(() => {
    setAnalyticsConsent(true);
    setConsentGiven(true);
  }, []);

  const revokeConsent = useCallback(() => {
    setAnalyticsConsent(false);
    setConsentGiven(false);
  }, []);

  const trackEvent = useCallback((category, action, data) => {
    if (consentGiven) {
      trackCustomEvent(category, action, data);
    }
  }, [consentGiven]);

  const trackEcommerce = useCallback((eventName, eventData) => {
    if (consentGiven) {
      trackEcommerceEvent(eventName, eventData);
    }
  }, [consentGiven]);

  return {
    consentGiven,
    isInitialized,
    giveConsent,
    revokeConsent,
    trackEvent,
    trackEcommerce,
    trackPageView: (page, title) => consentGiven && trackPageView(page, title)
  };
};

/**
 * Hook for tracking product interactions
 */
export const useProductAnalytics = () => {
  const { consentGiven } = useAnalytics();

  const trackView = useCallback((product) => {
    if (consentGiven) {
      trackProductView(product);
      trackCustomEvent(EVENT_CATEGORIES.PRODUCT, 'product_viewed', {
        productId: product.id,
        productName: product.name,
        category: product.category,
        price: product.price,
        producer: product.producer,
        timestamp: new Date().toISOString()
      });
    }
  }, [consentGiven]);

  const trackAddToCart = useCallback((product, quantity = 1) => {
    if (consentGiven) {
      trackAddToCart(product, quantity);
      trackCustomEvent(EVENT_CATEGORIES.CART, 'add_to_cart', {
        productId: product.id,
        productName: product.name,
        quantity,
        price: product.price,
        totalValue: product.price * quantity,
        producer: product.producer
      });
    }
  }, [consentGiven]);

  const trackRemoveFromCart = useCallback((product, quantity = 1) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.CART, 'remove_from_cart', {
        productId: product.id,
        productName: product.name,
        quantity,
        price: product.price,
        producer: product.producer
      });
    }
  }, [consentGiven]);

  const trackProductFilter = useCallback((filters) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.PRODUCT, CUSTOM_EVENTS.PRODUCT_FILTER, {
        filters,
        filterCount: Object.keys(filters).length,
        activeFilters: Object.entries(filters).filter(([_, value]) => value).map(([key, _]) => key)
      });
    }
  }, [consentGiven]);

  return {
    trackView,
    trackAddToCart,
    trackRemoveFromCart,
    trackProductFilter
  };
};

/**
 * Hook for tracking search interactions
 */
export const useSearchAnalytics = () => {
  const { consentGiven } = useAnalytics();
  const searchSessionRef = useRef(null);

  const trackSearchStart = useCallback((query) => {
    if (consentGiven) {
      searchSessionRef.current = {
        query,
        startTime: Date.now(),
        sessionId: `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      };
      
      trackCustomEvent(EVENT_CATEGORIES.SEARCH, 'search_initiated', {
        query,
        sessionId: searchSessionRef.current.sessionId
      });
    }
  }, [consentGiven]);

  const trackSearchResults = useCallback((query, results, filters = {}) => {
    if (consentGiven) {
      const resultsCount = Array.isArray(results) ? results.length : results;
      
      trackSearch(query, resultsCount);
      
      trackCustomEvent(EVENT_CATEGORIES.SEARCH, CUSTOM_EVENTS.SEARCH_PERFORMED, {
        query,
        resultsCount,
        filters,
        hasFilters: Object.keys(filters).length > 0,
        sessionId: searchSessionRef.current?.sessionId,
        searchDuration: searchSessionRef.current ? Date.now() - searchSessionRef.current.startTime : null
      });
    }
  }, [consentGiven]);

  const trackSearchClick = useCallback((product, position) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.SEARCH, 'search_result_click', {
        productId: product.id,
        productName: product.name,
        position,
        query: searchSessionRef.current?.query,
        sessionId: searchSessionRef.current?.sessionId
      });
    }
  }, [consentGiven]);

  const trackNoResults = useCallback((query) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.SEARCH, 'search_no_results', {
        query,
        sessionId: searchSessionRef.current?.sessionId
      });
    }
  }, [consentGiven]);

  return {
    trackSearchStart,
    trackSearchResults,
    trackSearchClick,
    trackNoResults
  };
};

/**
 * Hook for tracking cart and checkout interactions
 */
export const useCheckoutAnalytics = () => {
  const { consentGiven } = useAnalytics();
  const checkoutSessionRef = useRef(null);

  const trackViewCart = useCallback((cartItems) => {
    if (consentGiven) {
      const cartValue = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      
      trackEcommerceEvent(ECOMMERCE_EVENTS.VIEW_CART, {
        currency: 'RON',
        value: cartValue,
        items: cartItems.map(item => ({
          id: item.id,
          name: item.name,
          category: item.category,
          price: item.price,
          quantity: item.quantity,
          producer: item.producer
        }))
      });
    }
  }, [consentGiven]);

  const trackBeginCheckout = useCallback((cartItems, cartValue) => {
    if (consentGiven) {
      checkoutSessionRef.current = {
        startTime: Date.now(),
        sessionId: `checkout_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        cartValue,
        itemCount: cartItems.length
      };

      trackEcommerceEvent(ECOMMERCE_EVENTS.BEGIN_CHECKOUT, {
        currency: 'RON',
        value: cartValue,
        items: cartItems.map(item => ({
          id: item.id,
          name: item.name,
          category: item.category,
          price: item.price,
          quantity: item.quantity,
          producer: item.producer
        }))
      });
    }
  }, [consentGiven]);

  const trackCheckoutStep = useCallback((step, stepName, additionalData = {}) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.CHECKOUT, 'checkout_step', {
        step,
        stepName,
        sessionId: checkoutSessionRef.current?.sessionId,
        timeFromStart: checkoutSessionRef.current ? Date.now() - checkoutSessionRef.current.startTime : null,
        ...additionalData
      });
    }
  }, [consentGiven]);

  const trackAddPaymentInfo = useCallback((paymentMethod) => {
    if (consentGiven) {
      trackEcommerceEvent(ECOMMERCE_EVENTS.ADD_PAYMENT_INFO, {
        currency: 'RON',
        value: checkoutSessionRef.current?.cartValue || 0,
        payment_type: paymentMethod
      });
      
      trackCheckoutStep(3, 'payment_info', { paymentMethod });
    }
  }, [consentGiven, trackCheckoutStep]);

  const trackPurchaseComplete = useCallback((order) => {
    if (consentGiven) {
      trackPurchase(order);
      
      trackCustomEvent(EVENT_CATEGORIES.ECOMMERCE, 'purchase_completed', {
        orderId: order.id,
        orderValue: order.total,
        itemCount: order.items.length,
        paymentMethod: order.paymentMethod,
        deliveryMethod: order.deliveryMethod,
        sessionId: checkoutSessionRef.current?.sessionId,
        checkoutDuration: checkoutSessionRef.current ? Date.now() - checkoutSessionRef.current.startTime : null
      });

      // Reset checkout session
      checkoutSessionRef.current = null;
    }
  }, [consentGiven]);

  const trackCheckoutError = useCallback((error, step) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.ERROR, 'checkout_error', {
        error: error.message || error,
        step,
        sessionId: checkoutSessionRef.current?.sessionId
      });
    }
  }, [consentGiven]);

  return {
    trackViewCart,
    trackBeginCheckout,
    trackCheckoutStep,
    trackAddPaymentInfo,
    trackPurchaseComplete,
    trackCheckoutError
  };
};

/**
 * Hook for tracking user interactions and engagement
 */
export const useUserAnalytics = () => {
  const { consentGiven } = useAnalytics();
  const sessionStartTime = useRef(Date.now());
  const pageStartTime = useRef(Date.now());

  const trackButtonClick = useCallback((buttonName, context = {}) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'button_click', {
        buttonName,
        page: window.location.pathname,
        ...context
      });
    }
  }, [consentGiven]);

  const trackFormSubmission = useCallback((formName, formData = {}) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'form_submit', {
        formName,
        page: window.location.pathname,
        formFields: Object.keys(formData),
        ...formData
      });
    }
  }, [consentGiven]);

  const trackModalOpen = useCallback((modalName, trigger) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'modal_open', {
        modalName,
        trigger,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackTimeOnPage = useCallback(() => {
    if (consentGiven) {
      const timeSpent = Math.round((Date.now() - pageStartTime.current) / 1000);
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'time_on_page', {
        timeSpent,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackSMSVerification = useCallback((step, success = null) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, CUSTOM_EVENTS.SMS_VERIFICATION, {
        step, // 'sent', 'entered', 'verified'
        success,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  // Track time on page when component unmounts
  useEffect(() => {
    pageStartTime.current = Date.now();
    
    return () => {
      trackTimeOnPage();
    };
  }, [trackTimeOnPage]);

  return {
    trackButtonClick,
    trackFormSubmission,
    trackModalOpen,
    trackTimeOnPage,
    trackSMSVerification
  };
};

/**
 * Hook for tracking performance metrics
 */
export const usePerformanceAnalytics = () => {
  const { consentGiven } = useAnalytics();

  const trackAPICall = useCallback((endpoint, method, duration, success, error = null) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.PERFORMANCE, 'api_call', {
        endpoint,
        method,
        duration,
        success,
        error: error?.message || error,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackComponentRender = useCallback((componentName, renderTime) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.PERFORMANCE, 'component_render', {
        componentName,
        renderTime,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackImageLoad = useCallback((imageSrc, loadTime, success) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.PERFORMANCE, 'image_load', {
        imageSrc,
        loadTime,
        success,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackError = useCallback((error, context = {}) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.ERROR, CUSTOM_EVENTS.ERROR_OCCURRED, {
        message: error.message || error,
        stack: error.stack,
        page: window.location.pathname,
        userAgent: navigator.userAgent,
        ...context
      });
    }
  }, [consentGiven]);

  return {
    trackAPICall,
    trackComponentRender,
    trackImageLoad,
    trackError
  };
};

/**
 * Hook for tracking business-specific metrics
 */
export const useBusinessAnalytics = () => {
  const { consentGiven } = useAnalytics();

  const trackProducerView = useCallback((producer) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.PRODUCER, CUSTOM_EVENTS.PRODUCER_VIEW, {
        producerId: producer.id,
        producerName: producer.name,
        location: producer.location,
        productCount: producer.productCount
      });
    }
  }, [consentGiven]);

  const trackCategoryBrowse = useCallback((category, productCount) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.CATEGORY, CUSTOM_EVENTS.CATEGORY_BROWSE, {
        categoryId: category.id,
        categoryName: category.name,
        productCount,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackContactForm = useCallback((formType, inquiry) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, CUSTOM_EVENTS.CONTACT_FORM, {
        formType,
        inquiryType: inquiry.type,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  const trackOrderTracking = useCallback((orderNumber, status) => {
    if (consentGiven) {
      trackCustomEvent(EVENT_CATEGORIES.ECOMMERCE, CUSTOM_EVENTS.ORDER_TRACKING, {
        orderNumber,
        status,
        page: window.location.pathname
      });
    }
  }, [consentGiven]);

  return {
    trackProducerView,
    trackCategoryBrowse,
    trackContactForm,
    trackOrderTracking
  };
};

export default useAnalytics;