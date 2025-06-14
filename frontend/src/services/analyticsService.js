/**
 * Analytics Service for Local Producer Web Application
 * 
 * Service for sending analytics data to backend API and managing
 * analytics data synchronization with Romanian business intelligence.
 */

import axios from 'axios';

// Analytics API configuration
const ANALYTICS_API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080/api',
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000
};

// Create axios instance for analytics
const analyticsAPI = axios.create({
  baseURL: ANALYTICS_API_CONFIG.baseURL,
  timeout: ANALYTICS_API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication
analyticsAPI.interceptors.request.use(
  (config) => {
    // Add timestamp to all requests
    config.headers['X-Request-Timestamp'] = new Date().toISOString();
    
    // Add session ID if available
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
analyticsAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Retry failed requests
    if (error.response?.status >= 500 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Wait before retrying
      await new Promise(resolve => 
        setTimeout(resolve, ANALYTICS_API_CONFIG.retryDelay)
      );
      
      return analyticsAPI(originalRequest);
    }
    
    return Promise.reject(error);
  }
);

/**
 * Analytics Service Class
 */
class AnalyticsService {
  constructor() {
    this.eventQueue = [];
    this.batchSize = 50;
    this.flushInterval = 30000; // 30 seconds
    this.isOnline = navigator.onLine;
    
    // Set up online/offline detection
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushOfflineEvents();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
    
    // Set up automatic flushing
    setInterval(() => {
      this.flushEvents();
    }, this.flushInterval);
    
    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flushEvents(true);
    });
  }

  /**
   * Send batch of analytics events to backend
   */
  async sendEvents(events, immediate = false) {
    if (!events || events.length === 0) return;

    try {
      const payload = {
        events: events.map(event => ({
          ...event,
          client_timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          screen_resolution: `${screen.width}x${screen.height}`,
          viewport_size: `${window.innerWidth}x${window.innerHeight}`,
          language: navigator.language,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          connection_type: navigator.connection?.effectiveType || 'unknown'
        })),
        batch_info: {
          batch_id: `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          batch_size: events.length,
          immediate,
          client_time: new Date().toISOString()
        }
      };

      const response = await analyticsAPI.post('/analytics/events', payload);
      
      console.log(`Analytics batch sent: ${events.length} events`);
      return response.data;
    } catch (error) {
      console.error('Failed to send analytics events:', error);
      
      // Store events for retry if offline
      if (!this.isOnline) {
        this.storeOfflineEvents(events);
      }
      
      throw error;
    }
  }

  /**
   * Track business metrics specific to Romanian marketplace
   */
  async trackBusinessMetrics(metrics) {
    try {
      const payload = {
        ...metrics,
        timestamp: new Date().toISOString(),
        market: 'romania',
        currency: 'RON',
        business_type: 'local_marketplace'
      };

      const response = await analyticsAPI.post('/analytics/business-metrics', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track business metrics:', error);
      throw error;
    }
  }

  /**
   * Track user journey and behavior
   */
  async trackUserJourney(journeyData) {
    try {
      const payload = {
        ...journeyData,
        timestamp: new Date().toISOString(),
        session_id: localStorage.getItem('session_id'),
        page_url: window.location.href,
        referrer: document.referrer
      };

      const response = await analyticsAPI.post('/analytics/user-journey', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track user journey:', error);
      throw error;
    }
  }

  /**
   * Track performance metrics
   */
  async trackPerformance(performanceData) {
    try {
      const payload = {
        ...performanceData,
        timestamp: new Date().toISOString(),
        page_url: window.location.href,
        user_agent: navigator.userAgent,
        connection_speed: navigator.connection?.effectiveType || 'unknown'
      };

      const response = await analyticsAPI.post('/analytics/performance', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track performance:', error);
      throw error;
    }
  }

  /**
   * Track conversion funnel
   */
  async trackConversion(conversionData) {
    try {
      const payload = {
        ...conversionData,
        timestamp: new Date().toISOString(),
        session_id: localStorage.getItem('session_id'),
        market: 'romania',
        currency: 'RON'
      };

      const response = await analyticsAPI.post('/analytics/conversions', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track conversion:', error);
      throw error;
    }
  }

  /**
   * Get analytics dashboard data
   */
  async getDashboardData(timeRange = '7d', metrics = []) {
    try {
      const params = new URLSearchParams({
        time_range: timeRange,
        metrics: metrics.join(','),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      });

      const response = await analyticsAPI.get(`/analytics/dashboard?${params}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get dashboard data:', error);
      throw error;
    }
  }

  /**
   * Get real-time analytics data
   */
  async getRealTimeData() {
    try {
      const response = await analyticsAPI.get('/analytics/realtime');
      return response.data;
    } catch (error) {
      console.error('Failed to get real-time data:', error);
      throw error;
    }
  }

  /**
   * Track Romanian business KPIs
   */
  async trackRomanianKPIs(kpiData) {
    try {
      const payload = {
        ...kpiData,
        timestamp: new Date().toISOString(),
        market: 'romania',
        business_context: {
          local_producers: true,
          traditional_products: true,
          seasonal_availability: true,
          romanian_cuisine: true
        }
      };

      const response = await analyticsAPI.post('/analytics/romanian-kpis', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track Romanian KPIs:', error);
      throw error;
    }
  }

  /**
   * Add event to queue for batch processing
   */
  queueEvent(event) {
    this.eventQueue.push({
      ...event,
      queued_at: new Date().toISOString()
    });

    // Flush if queue is full
    if (this.eventQueue.length >= this.batchSize) {
      this.flushEvents();
    }
  }

  /**
   * Flush queued events to backend
   */
  async flushEvents(immediate = false) {
    if (this.eventQueue.length === 0 || !this.isOnline) return;

    const eventsToSend = this.eventQueue.splice(0, this.batchSize);
    
    try {
      await this.sendEvents(eventsToSend, immediate);
    } catch (error) {
      // Re-add events to queue on failure
      this.eventQueue.unshift(...eventsToSend);
    }
  }

  /**
   * Store events offline for later sync
   */
  storeOfflineEvents(events) {
    try {
      const stored = JSON.parse(localStorage.getItem('offline_analytics') || '[]');
      stored.push(...events);
      
      // Limit offline storage to prevent bloat
      if (stored.length > 1000) {
        stored.splice(0, stored.length - 1000);
      }
      
      localStorage.setItem('offline_analytics', JSON.stringify(stored));
    } catch (error) {
      console.error('Failed to store offline events:', error);
    }
  }

  /**
   * Flush offline events when back online
   */
  async flushOfflineEvents() {
    try {
      const stored = JSON.parse(localStorage.getItem('offline_analytics') || '[]');
      if (stored.length === 0) return;

      await this.sendEvents(stored);
      localStorage.removeItem('offline_analytics');
      
      console.log(`Synced ${stored.length} offline analytics events`);
    } catch (error) {
      console.error('Failed to flush offline events:', error);
    }
  }

  /**
   * Export analytics data
   */
  async exportData(format = 'json', timeRange = '30d', filters = {}) {
    try {
      const params = new URLSearchParams({
        format,
        time_range: timeRange,
        ...filters
      });

      const response = await analyticsAPI.get(`/analytics/export?${params}`, {
        responseType: format === 'csv' ? 'blob' : 'json'
      });

      return response.data;
    } catch (error) {
      console.error('Failed to export analytics data:', error);
      throw error;
    }
  }

  /**
   * Generate analytics report
   */
  async generateReport(reportType = 'business', timeRange = '7d', options = {}) {
    try {
      const payload = {
        report_type: reportType,
        time_range: timeRange,
        options: {
          ...options,
          locale: 'ro-RO',
          currency: 'RON',
          market: 'romania'
        }
      };

      const response = await analyticsAPI.post('/analytics/reports', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to generate report:', error);
      throw error;
    }
  }

  /**
   * Track A/B test results
   */
  async trackABTest(testData) {
    try {
      const payload = {
        ...testData,
        timestamp: new Date().toISOString(),
        session_id: localStorage.getItem('session_id'),
        market: 'romania'
      };

      const response = await analyticsAPI.post('/analytics/ab-tests', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track A/B test:', error);
      throw error;
    }
  }

  /**
   * Track customer cohorts
   */
  async trackCohort(cohortData) {
    try {
      const payload = {
        ...cohortData,
        timestamp: new Date().toISOString(),
        market: 'romania',
        currency: 'RON'
      };

      const response = await analyticsAPI.post('/analytics/cohorts', payload);
      return response.data;
    } catch (error) {
      console.error('Failed to track cohort:', error);
      throw error;
    }
  }

  /**
   * Get analytics insights powered by AI
   */
  async getInsights(dataRange = '30d', metrics = []) {
    try {
      const params = new URLSearchParams({
        data_range: dataRange,
        metrics: metrics.join(','),
        market: 'romania',
        language: 'ro'
      });

      const response = await analyticsAPI.get(`/analytics/insights?${params}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get analytics insights:', error);
      throw error;
    }
  }
}

// Create singleton instance
const analyticsService = new AnalyticsService();

// Export service methods
export const sendAnalyticsEvents = (events, immediate) => 
  analyticsService.sendEvents(events, immediate);

export const trackBusinessMetrics = (metrics) => 
  analyticsService.trackBusinessMetrics(metrics);

export const trackUserJourney = (journeyData) => 
  analyticsService.trackUserJourney(journeyData);

export const trackPerformance = (performanceData) => 
  analyticsService.trackPerformance(performanceData);

export const trackConversion = (conversionData) => 
  analyticsService.trackConversion(conversionData);

export const getDashboardData = (timeRange, metrics) => 
  analyticsService.getDashboardData(timeRange, metrics);

export const getRealTimeData = () => 
  analyticsService.getRealTimeData();

export const trackRomanianKPIs = (kpiData) => 
  analyticsService.trackRomanianKPIs(kpiData);

export const queueAnalyticsEvent = (event) => 
  analyticsService.queueEvent(event);

export const exportAnalyticsData = (format, timeRange, filters) => 
  analyticsService.exportData(format, timeRange, filters);

export const generateAnalyticsReport = (reportType, timeRange, options) => 
  analyticsService.generateReport(reportType, timeRange, options);

export const trackABTest = (testData) => 
  analyticsService.trackABTest(testData);

export const trackCohort = (cohortData) => 
  analyticsService.trackCohort(cohortData);

export const getAnalyticsInsights = (dataRange, metrics) => 
  analyticsService.getInsights(dataRange, metrics);

export default analyticsService;