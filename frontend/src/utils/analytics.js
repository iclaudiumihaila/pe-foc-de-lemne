/**
 * Analytics Utilities for Local Producer Web Application
 * 
 * Comprehensive analytics tracking system with Google Analytics 4,
 * custom business metrics, and Romanian localization.
 */

// Analytics configuration
export const ANALYTICS_CONFIG = {
  // Google Analytics 4 configuration
  ga4: {
    measurementId: process.env.REACT_APP_GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX',
    enabled: process.env.NODE_ENV === 'production',
    debugMode: process.env.NODE_ENV === 'development'
  },
  
  // Custom analytics configuration
  custom: {
    apiEndpoint: '/api/analytics',
    batchSize: 10,
    flushInterval: 30000, // 30 seconds
    enabled: true
  },
  
  // Privacy configuration
  privacy: {
    cookieConsent: true,
    anonymizeIp: true,
    respectDoNotTrack: true,
    consentCookie: 'analytics_consent',
    consentExpiry: 365 // days
  },
  
  // Romanian localization
  locale: {
    language: 'ro',
    currency: 'RON',
    country: 'RO',
    timezone: 'Europe/Bucharest'
  }
};

// Event categories for Romanian business
export const EVENT_CATEGORIES = {
  ECOMMERCE: 'Comerț electronic',
  USER_INTERACTION: 'Interacțiune utilizator',
  PRODUCT: 'Produs',
  CART: 'Coș',
  CHECKOUT: 'Finalizare comandă',
  SEARCH: 'Căutare',
  NAVIGATION: 'Navigare',
  PERFORMANCE: 'Performanță',
  ERROR: 'Eroare',
  PRODUCER: 'Producător',
  CATEGORY: 'Categorie'
};

// Enhanced e-commerce events
export const ECOMMERCE_EVENTS = {
  VIEW_ITEM: 'view_item',
  ADD_TO_CART: 'add_to_cart',
  REMOVE_FROM_CART: 'remove_from_cart',
  VIEW_CART: 'view_cart',
  BEGIN_CHECKOUT: 'begin_checkout',
  ADD_PAYMENT_INFO: 'add_payment_info',
  PURCHASE: 'purchase',
  VIEW_ITEM_LIST: 'view_item_list',
  SELECT_ITEM: 'select_item',
  SEARCH: 'search'
};

// Custom business events
export const CUSTOM_EVENTS = {
  PRODUCER_VIEW: 'producător_vizualizat',
  PRODUCT_FILTER: 'produs_filtrat',
  SEARCH_PERFORMED: 'căutare_efectuată',
  CATEGORY_BROWSE: 'categorie_navigată',
  SMS_VERIFICATION: 'verificare_sms',
  ORDER_TRACKING: 'urmărire_comandă',
  ERROR_OCCURRED: 'eroare_apărută',
  PERFORMANCE_ISSUE: 'problemă_performanță',
  USER_REGISTRATION: 'înregistrare_utilizator',
  CONTACT_FORM: 'formular_contact'
};

// Analytics class for managing tracking
class Analytics {
  constructor() {
    this.initialized = false;
    this.consentGiven = false;
    this.eventQueue = [];
    this.customQueue = [];
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    
    // Check for existing consent
    this.checkConsent();
    
    // Initialize if consent given
    if (this.consentGiven) {
      this.initialize();
    }
    
    // Set up automatic queue flushing
    this.setupQueueFlushing();
  }

  /**
   * Generate unique session ID
   */
  generateSessionId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get or generate user ID
   */
  getUserId() {
    let userId = localStorage.getItem('analytics_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('analytics_user_id', userId);
    }
    return userId;
  }

  /**
   * Check for existing analytics consent
   */
  checkConsent() {
    const consent = localStorage.getItem(ANALYTICS_CONFIG.privacy.consentCookie);
    if (consent === 'true') {
      this.consentGiven = true;
    }
  }

  /**
   * Set analytics consent
   */
  setConsent(consent) {
    this.consentGiven = consent;
    localStorage.setItem(ANALYTICS_CONFIG.privacy.consentCookie, consent.toString());
    
    if (consent) {
      this.initialize();
      // Process queued events
      this.processQueuedEvents();
    } else {
      this.clearData();
    }
  }

  /**
   * Initialize analytics systems
   */
  initialize() {
    if (this.initialized) return;
    
    try {
      // Initialize Google Analytics 4
      this.initializeGA4();
      
      // Initialize custom analytics
      this.initializeCustomAnalytics();
      
      // Set up performance monitoring
      this.setupPerformanceMonitoring();
      
      // Set up error tracking
      this.setupErrorTracking();
      
      this.initialized = true;
      console.log('Analytics initialized successfully');
    } catch (error) {
      console.error('Analytics initialization failed:', error);
    }
  }

  /**
   * Initialize Google Analytics 4
   */
  initializeGA4() {
    if (!ANALYTICS_CONFIG.ga4.enabled || !ANALYTICS_CONFIG.ga4.measurementId) {
      return;
    }

    // Load gtag script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${ANALYTICS_CONFIG.ga4.measurementId}`;
    document.head.appendChild(script);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    
    gtag('js', new Date());
    gtag('config', ANALYTICS_CONFIG.ga4.measurementId, {
      anonymize_ip: ANALYTICS_CONFIG.privacy.anonymizeIp,
      cookie_flags: 'SameSite=None;Secure',
      debug_mode: ANALYTICS_CONFIG.ga4.debugMode,
      custom_map: {
        custom_parameter_1: 'producer_name',
        custom_parameter_2: 'product_category'
      }
    });

    // Set Romanian locale
    gtag('config', ANALYTICS_CONFIG.ga4.measurementId, {
      country: ANALYTICS_CONFIG.locale.country,
      language: ANALYTICS_CONFIG.locale.language,
      currency: ANALYTICS_CONFIG.locale.currency
    });
  }

  /**
   * Initialize custom analytics
   */
  initializeCustomAnalytics() {
    // Set up session tracking
    this.trackSession();
    
    // Track page view
    this.trackPageView();
    
    // Set up automatic event tracking
    this.setupAutomaticTracking();
  }

  /**
   * Track e-commerce event
   */
  trackEcommerceEvent(eventName, eventData) {
    if (!this.consentGiven) {
      this.eventQueue.push({ type: 'ecommerce', eventName, eventData });
      return;
    }

    try {
      // Track in Google Analytics 4
      if (window.gtag && ANALYTICS_CONFIG.ga4.enabled) {
        const gaData = this.formatGA4EcommerceData(eventData);
        window.gtag('event', eventName, gaData);
      }

      // Track in custom analytics
      this.trackCustomEvent('ecommerce', eventName, eventData);

      console.log(`E-commerce event tracked: ${eventName}`, eventData);
    } catch (error) {
      console.error('E-commerce tracking error:', error);
    }
  }

  /**
   * Format data for GA4 e-commerce tracking
   */
  formatGA4EcommerceData(eventData) {
    const formatted = {
      currency: ANALYTICS_CONFIG.locale.currency,
      value: eventData.value || 0,
      ...eventData
    };

    // Format items for GA4
    if (eventData.items) {
      formatted.items = eventData.items.map(item => ({
        item_id: item.id || item.item_id,
        item_name: item.name || item.item_name,
        category: item.category,
        price: item.price,
        quantity: item.quantity || 1,
        item_brand: item.producer || 'Pe Foc de Lemne',
        item_category2: item.subcategory,
        currency: ANALYTICS_CONFIG.locale.currency
      }));
    }

    return formatted;
  }

  /**
   * Track custom business event
   */
  trackCustomEvent(category, action, data = {}) {
    if (!this.consentGiven) {
      this.customQueue.push({ category, action, data });
      return;
    }

    const eventData = {
      category,
      action,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      userId: this.userId,
      page: window.location.pathname,
      data: {
        ...data,
        user_agent: navigator.userAgent,
        language: navigator.language,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
        viewport_size: `${window.innerWidth}x${window.innerHeight}`
      }
    };

    // Add to custom queue for batch processing
    this.customQueue.push(eventData);

    // Track in Google Analytics if enabled
    if (window.gtag && ANALYTICS_CONFIG.ga4.enabled) {
      window.gtag('event', action, {
        event_category: category,
        event_label: data.label,
        value: data.value,
        custom_parameter_1: data.producer_name,
        custom_parameter_2: data.product_category
      });
    }
  }

  /**
   * Track page view
   */
  trackPageView(page = window.location.pathname, title = document.title) {
    if (!this.consentGiven) return;

    // Google Analytics 4
    if (window.gtag && ANALYTICS_CONFIG.ga4.enabled) {
      window.gtag('config', ANALYTICS_CONFIG.ga4.measurementId, {
        page_title: title,
        page_location: window.location.href,
        page_path: page
      });
    }

    // Custom analytics
    this.trackCustomEvent(EVENT_CATEGORIES.NAVIGATION, 'page_view', {
      page,
      title,
      referrer: document.referrer,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Track user session
   */
  trackSession() {
    const sessionData = {
      sessionId: this.sessionId,
      userId: this.userId,
      startTime: new Date().toISOString(),
      userAgent: navigator.userAgent,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      screen: `${window.screen.width}x${window.screen.height}`,
      viewport: `${window.innerWidth}x${window.innerHeight}`
    };

    this.trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'session_start', sessionData);
  }

  /**
   * Set up automatic event tracking
   */
  setupAutomaticTracking() {
    // Track clicks on important elements
    document.addEventListener('click', (e) => {
      const element = e.target;
      
      // Track product card clicks
      if (element.closest('[data-analytics="product-card"]')) {
        const productId = element.closest('[data-analytics="product-card"]').dataset.productId;
        this.trackCustomEvent(EVENT_CATEGORIES.PRODUCT, 'product_click', { productId });
      }
      
      // Track CTA button clicks
      if (element.matches('[data-analytics="cta-button"]')) {
        const ctaType = element.dataset.ctaType;
        this.trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'cta_click', { ctaType });
      }
      
      // Track external links
      if (element.matches('a[href^="http"]') && !element.href.includes(window.location.hostname)) {
        this.trackCustomEvent(EVENT_CATEGORIES.NAVIGATION, 'external_link', { url: element.href });
      }
    });

    // Track form submissions
    document.addEventListener('submit', (e) => {
      const form = e.target;
      if (form.matches('form[data-analytics]')) {
        const formType = form.dataset.analytics;
        this.trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'form_submit', { formType });
      }
    });

    // Track scroll depth
    this.setupScrollTracking();
  }

  /**
   * Set up scroll depth tracking
   */
  setupScrollTracking() {
    let maxScroll = 0;
    let scrollMilestones = [25, 50, 75, 90, 100];
    let triggeredMilestones = new Set();

    const trackScroll = () => {
      const scrollPercent = Math.round(
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
      );
      
      if (scrollPercent > maxScroll) {
        maxScroll = scrollPercent;
        
        // Check for milestone achievements
        scrollMilestones.forEach(milestone => {
          if (scrollPercent >= milestone && !triggeredMilestones.has(milestone)) {
            triggeredMilestones.add(milestone);
            this.trackCustomEvent(EVENT_CATEGORIES.USER_INTERACTION, 'scroll_depth', {
              percentage: milestone,
              page: window.location.pathname
            });
          }
        });
      }
    };

    let scrollTimer;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(trackScroll, 100);
    });
  }

  /**
   * Set up performance monitoring
   */
  setupPerformanceMonitoring() {
    // Track Core Web Vitals
    if ('web-vital' in window) {
      window.webVitals.getCLS(this.trackWebVital.bind(this));
      window.webVitals.getFID(this.trackWebVital.bind(this));
      window.webVitals.getLCP(this.trackWebVital.bind(this));
    }

    // Track page load performance
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0];
      if (perfData) {
        this.trackCustomEvent(EVENT_CATEGORIES.PERFORMANCE, 'page_load', {
          load_time: perfData.loadEventEnd - perfData.loadEventStart,
          dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
          first_byte: perfData.responseStart - perfData.requestStart,
          page: window.location.pathname
        });
      }
    });
  }

  /**
   * Track Core Web Vitals
   */
  trackWebVital(metric) {
    this.trackCustomEvent(EVENT_CATEGORIES.PERFORMANCE, 'web_vital', {
      metric_name: metric.name,
      metric_value: Math.round(metric.value),
      metric_rating: metric.rating,
      page: window.location.pathname
    });

    // Also send to Google Analytics
    if (window.gtag && ANALYTICS_CONFIG.ga4.enabled) {
      window.gtag('event', metric.name, {
        event_category: 'Web Vitals',
        value: Math.round(metric.value),
        metric_rating: metric.rating,
        non_interaction: true
      });
    }
  }

  /**
   * Set up error tracking
   */
  setupErrorTracking() {
    // Track JavaScript errors
    window.addEventListener('error', (e) => {
      this.trackCustomEvent(EVENT_CATEGORIES.ERROR, 'javascript_error', {
        message: e.message,
        filename: e.filename,
        line: e.lineno,
        column: e.colno,
        stack: e.error?.stack,
        page: window.location.pathname
      });
    });

    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (e) => {
      this.trackCustomEvent(EVENT_CATEGORIES.ERROR, 'unhandled_rejection', {
        reason: e.reason?.toString(),
        page: window.location.pathname
      });
    });
  }

  /**
   * Set up queue flushing
   */
  setupQueueFlushing() {
    setInterval(() => {
      this.flushCustomQueue();
    }, ANALYTICS_CONFIG.custom.flushInterval);

    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flushCustomQueue();
    });
  }

  /**
   * Flush custom analytics queue
   */
  async flushCustomQueue() {
    if (this.customQueue.length === 0 || !ANALYTICS_CONFIG.custom.enabled) return;

    const events = this.customQueue.splice(0, ANALYTICS_CONFIG.custom.batchSize);
    
    try {
      await fetch(ANALYTICS_CONFIG.custom.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ events })
      });
    } catch (error) {
      console.error('Failed to send analytics events:', error);
      // Re-add events to queue on failure
      this.customQueue.unshift(...events);
    }
  }

  /**
   * Process queued events after consent given
   */
  processQueuedEvents() {
    // Process e-commerce events
    this.eventQueue.forEach(({ type, eventName, eventData }) => {
      if (type === 'ecommerce') {
        this.trackEcommerceEvent(eventName, eventData);
      }
    });
    this.eventQueue = [];

    // Custom events are already in customQueue and will be flushed
  }

  /**
   * Clear all analytics data
   */
  clearData() {
    localStorage.removeItem(ANALYTICS_CONFIG.privacy.consentCookie);
    localStorage.removeItem('analytics_user_id');
    this.eventQueue = [];
    this.customQueue = [];
  }
}

// Create global analytics instance
const analytics = new Analytics();

// Export analytics functions
export const trackEcommerceEvent = (eventName, eventData) => {
  analytics.trackEcommerceEvent(eventName, eventData);
};

export const trackCustomEvent = (category, action, data) => {
  analytics.trackCustomEvent(category, action, data);
};

export const trackPageView = (page, title) => {
  analytics.trackPageView(page, title);
};

export const setAnalyticsConsent = (consent) => {
  analytics.setConsent(consent);
};

export const getAnalyticsConsent = () => {
  return analytics.consentGiven;
};

// Product-specific tracking functions
export const trackProductView = (product) => {
  trackEcommerceEvent(ECOMMERCE_EVENTS.VIEW_ITEM, {
    currency: ANALYTICS_CONFIG.locale.currency,
    value: product.price,
    items: [{
      id: product.id,
      name: product.name,
      category: product.category,
      price: product.price,
      producer: product.producer
    }]
  });
};

export const trackAddToCart = (product, quantity = 1) => {
  trackEcommerceEvent(ECOMMERCE_EVENTS.ADD_TO_CART, {
    currency: ANALYTICS_CONFIG.locale.currency,
    value: product.price * quantity,
    items: [{
      id: product.id,
      name: product.name,
      category: product.category,
      price: product.price,
      quantity: quantity,
      producer: product.producer
    }]
  });
};

export const trackPurchase = (order) => {
  trackEcommerceEvent(ECOMMERCE_EVENTS.PURCHASE, {
    transaction_id: order.id,
    currency: ANALYTICS_CONFIG.locale.currency,
    value: order.total,
    tax: order.tax || 0,
    shipping: order.shipping || 0,
    items: order.items.map(item => ({
      id: item.product.id,
      name: item.product.name,
      category: item.product.category,
      price: item.product.price,
      quantity: item.quantity,
      producer: item.product.producer
    }))
  });
};

export const trackSearch = (query, resultsCount = 0) => {
  trackEcommerceEvent(ECOMMERCE_EVENTS.SEARCH, {
    search_term: query,
    results_count: resultsCount
  });
  
  trackCustomEvent(EVENT_CATEGORIES.SEARCH, CUSTOM_EVENTS.SEARCH_PERFORMED, {
    query,
    resultsCount,
    timestamp: new Date().toISOString()
  });
};

export default analytics;