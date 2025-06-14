/**
 * Google Analytics Component for Local Producer Web Application
 * 
 * React component for Google Analytics 4 integration with enhanced
 * e-commerce tracking and Romanian localization.
 */

import React, { useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useAnalytics } from '../../hooks/useAnalytics';

const GoogleAnalytics = ({ measurementId, debugMode = false }) => {
  const { consentGiven } = useAnalytics();

  useEffect(() => {
    // Only load GA4 if consent is given and measurement ID is provided
    if (!consentGiven || !measurementId || measurementId === 'G-XXXXXXXXXX') {
      return;
    }

    // Initialize Google Analytics 4
    const initializeGA4 = () => {
      // Create dataLayer if it doesn't exist
      window.dataLayer = window.dataLayer || [];
      
      function gtag() {
        window.dataLayer.push(arguments);
      }
      
      // Make gtag globally available
      window.gtag = gtag;
      
      // Initialize with current timestamp
      gtag('js', new Date());
      
      // Configure GA4 with Romanian localization and privacy settings
      gtag('config', measurementId, {
        // Privacy settings
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false,
        
        // Romanian localization
        country: 'RO',
        language: 'ro',
        currency: 'RON',
        
        // Cookie settings
        cookie_flags: 'SameSite=Strict;Secure',
        cookie_expires: 7776000, // 90 days
        
        // Debug mode for development
        debug_mode: debugMode,
        
        // Enhanced measurement settings
        enhanced_measurement: {
          scrolls: true,
          outbound_clicks: true,
          site_search: true,
          video_engagement: false,
          file_downloads: true
        },
        
        // Custom dimensions
        custom_map: {
          custom_parameter_1: 'producer_name',
          custom_parameter_2: 'product_category',
          custom_parameter_3: 'user_type',
          custom_parameter_4: 'order_value_range',
          custom_parameter_5: 'delivery_method'
        },
        
        // Page view settings
        send_page_view: false, // We'll handle this manually
        
        // Romanian business context
        business_type: 'local_marketplace',
        industry: 'food_and_beverage',
        market: 'romania'
      });

      // Set up enhanced e-commerce for Romanian marketplace
      gtag('config', measurementId, {
        // E-commerce settings
        ecommerce: {
          currency: 'RON',
          payment_type: ['card', 'cash_on_delivery', 'bank_transfer'],
          shipping_tier: ['standard', 'express', 'pickup'],
          item_list_name: 'Produse Locale Românești'
        },
        
        // User properties for Romanian market
        user_properties: {
          preferred_language: 'ro',
          market_segment: 'local_food',
          customer_type: 'b2c'
        }
      });

      // Set up conversion events for Romanian business
      const conversionEvents = [
        'purchase',
        'add_to_cart',
        'begin_checkout',
        'contact_form_submit',
        'newsletter_signup',
        'phone_call_click'
      ];

      conversionEvents.forEach(eventName => {
        gtag('config', measurementId, {
          custom_map: { [eventName]: true }
        });
      });

      console.log('Google Analytics 4 initialized for Romanian marketplace');
    };

    initializeGA4();
  }, [consentGiven, measurementId, debugMode]);

  // Don't render anything if consent not given or no measurement ID
  if (!consentGiven || !measurementId || measurementId === 'G-XXXXXXXXXX') {
    return null;
  }

  return (
    <Helmet>
      {/* Google Analytics 4 Script */}
      <script
        async
        src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
      />
      
      {/* Enhanced E-commerce Configuration */}
      <script>
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          
          // Romanian marketplace configuration
          gtag('config', '${measurementId}', {
            // Privacy and compliance
            anonymize_ip: true,
            cookie_flags: 'SameSite=Strict;Secure',
            
            // Romanian localization
            country: 'RO',
            language: 'ro',
            currency: 'RON',
            
            // Business context
            custom_map: {
              'custom_parameter_1': 'producer_name',
              'custom_parameter_2': 'product_category',
              'custom_parameter_3': 'delivery_area',
              'custom_parameter_4': 'order_size',
              'custom_parameter_5': 'customer_segment'
            },
            
            // Enhanced measurement
            enhanced_measurement: {
              scrolls: true,
              outbound_clicks: true,
              site_search: true,
              file_downloads: true
            },
            
            // Debug mode
            debug_mode: ${debugMode}
          });
          
          // Set Romanian user properties
          gtag('set', {
            'country': 'Romania',
            'language': 'Romanian',
            'currency': 'RON',
            'market_type': 'local_produce',
            'business_model': 'marketplace'
          });
          
          // Romanian e-commerce configuration
          gtag('config', '${measurementId}', {
            'ecommerce': {
              'currency': 'RON',
              'item_list_name': 'Produse Locale',
              'item_list_id': 'homepage_products',
              'payment_types': ['card', 'cash_delivery', 'transfer'],
              'shipping_methods': ['standard', 'express', 'pickup']
            }
          });
          
          // Enhanced e-commerce events for Romanian marketplace
          const marketplaceEvents = {
            'producer_view': 'custom',
            'product_compare': 'custom', 
            'category_filter': 'custom',
            'search_no_results': 'custom',
            'delivery_option_select': 'custom',
            'payment_method_select': 'custom',
            'sms_verification': 'custom',
            'order_status_check': 'custom'
          };
          
          // Register custom events
          Object.keys(marketplaceEvents).forEach(eventName => {
            gtag('config', '${measurementId}', {
              'custom_map': {
                [eventName]: true
              }
            });
          });
        `}
      </script>
      
      {/* Romanian Business Schema for Analytics */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "WebSite",
          "name": "Pe Foc de Lemne",
          "alternateName": "Produse Locale Românești",
          "url": "https://pefocdelemne.ro",
          "sameAs": [
            "https://www.facebook.com/pefocdelemne",
            "https://www.instagram.com/pefocdelemne"
          ],
          "potentialAction": {
            "@type": "SearchAction",
            "target": "https://pefocdelemne.ro/produse?q={search_term_string}",
            "query-input": "required name=search_term_string"
          },
          "publisher": {
            "@type": "Organization",
            "@id": "https://pefocdelemne.ro/#organization",
            "name": "Pe Foc de Lemne",
            "description": "Marketplace pentru produse locale românești",
            "address": {
              "@type": "PostalAddress",
              "addressCountry": "RO",
              "addressRegion": "București"
            }
          },
          "audience": {
            "@type": "PeopleAudience",
            "geographicArea": {
              "@type": "Country",
              "name": "Romania"
            },
            "audienceType": "local food consumers"
          },
          "inLanguage": "ro-RO",
          "isAccessibleForFree": true,
          "usageInfo": "https://pefocdelemne.ro/termeni",
          "copyrightHolder": {
            "@id": "https://pefocdelemne.ro/#organization"
          }
        }, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Enhanced E-commerce Events Component
 * Provides pre-configured event tracking for Romanian marketplace
 */
export const GoogleAnalyticsEcommerce = ({ children }) => {
  const { consentGiven } = useAnalytics();

  useEffect(() => {
    if (!consentGiven || !window.gtag) return;

    // Set up Romanian e-commerce tracking
    window.gtag('config', process.env.REACT_APP_GA4_MEASUREMENT_ID, {
      // Romanian currency and locale
      'currency': 'RON',
      'country': 'RO',
      'language': 'ro',
      
      // Local business parameters
      'business_type': 'local_marketplace',
      'target_market': 'romania',
      'product_category': 'food_beverage',
      
      // Enhanced e-commerce settings
      'enhanced_ecommerce': true,
      'ecommerce_version': '4',
      
      // Romanian marketplace events
      'custom_events': {
        'producer_interaction': true,
        'local_delivery': true,
        'sms_verification': true,
        'romanian_payment': true
      }
    });

    // Track marketplace-specific events
    const trackMarketplaceEvent = (eventName, parameters) => {
      window.gtag('event', eventName, {
        ...parameters,
        'market': 'romanian_local',
        'platform': 'web_marketplace',
        'currency': 'RON'
      });
    };

    // Make marketplace tracking globally available
    window.trackMarketplaceEvent = trackMarketplaceEvent;

  }, [consentGiven]);

  return consentGiven ? children : null;
};

/**
 * Romanian Business Intelligence Component
 * Tracks Romanian-specific business metrics
 */
export const RomanianBusinessAnalytics = () => {
  const { consentGiven } = useAnalytics();

  useEffect(() => {
    if (!consentGiven || !window.gtag) return;

    // Set Romanian business context
    window.gtag('set', {
      // Geographic context
      'country': 'Romania',
      'region': 'Eastern Europe',
      'timezone': 'Europe/Bucharest',
      
      // Business context
      'industry': 'Local Food Marketplace',
      'business_model': 'B2C Marketplace',
      'target_audience': 'Romanian Consumers',
      
      // Product context
      'product_type': 'Local Produce',
      'delivery_area': 'Romania',
      'payment_currency': 'RON',
      
      // Language and cultural context
      'content_language': 'Romanian',
      'cultural_context': 'Romanian Traditional Food',
      'seasonal_products': true
    });

    // Track Romanian business metrics
    const businessMetrics = {
      'local_producer_count': 0,
      'product_categories': 8,
      'delivery_areas': 41, // Romanian counties
      'seasonal_availability': true,
      'traditional_products': true
    };

    window.gtag('event', 'business_context', {
      'event_category': 'Romanian Business',
      'event_label': 'Marketplace Initialization',
      'custom_parameter_1': 'local_marketplace',
      'custom_parameter_2': 'traditional_products',
      'value': Object.keys(businessMetrics).length
    });

  }, [consentGiven]);

  return null;
};

export default GoogleAnalytics;