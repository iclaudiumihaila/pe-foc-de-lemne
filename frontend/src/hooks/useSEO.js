/**
 * SEO Hook for Local Producer Web Application
 * 
 * React hook for managing SEO meta tags, structured data,
 * and dynamic SEO optimization throughout the application.
 */

import { useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { generateMetaTags, generateStructuredData, SEO_CONFIG } from '../utils/seo';

/**
 * Custom hook for SEO management
 */
export const useSEO = (seoData = {}) => {
  const location = useLocation();
  const previousDataRef = useRef({});
  const structuredDataRef = useRef(new Set());

  const {
    title,
    description,
    keywords = [],
    image,
    type = 'website',
    product,
    article,
    breadcrumbs,
    canonical,
    robots,
    noindex = false,
    nofollow = false
  } = seoData;

  /**
   * Update document title
   */
  const updateTitle = useCallback((newTitle) => {
    if (newTitle && newTitle !== document.title) {
      document.title = newTitle;
    }
  }, []);

  /**
   * Create or update meta tag
   */
  const updateMetaTag = useCallback((name, content, isProperty = false) => {
    if (!content) return;

    const attribute = isProperty ? 'property' : 'name';
    const selector = `meta[${attribute}="${name}"]`;
    
    let metaTag = document.querySelector(selector);
    
    if (metaTag) {
      metaTag.setAttribute('content', content);
    } else {
      metaTag = document.createElement('meta');
      metaTag.setAttribute(attribute, name);
      metaTag.setAttribute('content', content);
      metaTag.setAttribute('data-seo-hook', 'true');
      document.head.appendChild(metaTag);
    }
  }, []);

  /**
   * Create or update link tag
   */
  const updateLinkTag = useCallback((rel, href, attributes = {}) => {
    if (!href) return;

    const selector = `link[rel="${rel}"]`;
    let linkTag = document.querySelector(selector);
    
    if (linkTag) {
      linkTag.setAttribute('href', href);
    } else {
      linkTag = document.createElement('link');
      linkTag.setAttribute('rel', rel);
      linkTag.setAttribute('href', href);
      linkTag.setAttribute('data-seo-hook', 'true');
      
      // Add additional attributes
      Object.entries(attributes).forEach(([key, value]) => {
        linkTag.setAttribute(key, value);
      });
      
      document.head.appendChild(linkTag);
    }
  }, []);

  /**
   * Add or update structured data script
   */
  const updateStructuredData = useCallback((type, data) => {
    const structuredData = generateStructuredData(type, data);
    const scriptId = `structured-data-${type.toLowerCase()}`;
    
    // Remove existing script if it exists
    const existingScript = document.getElementById(scriptId);
    if (existingScript) {
      existingScript.remove();
    }

    // Create new script tag
    const script = document.createElement('script');
    script.id = scriptId;
    script.type = 'application/ld+json';
    script.setAttribute('data-seo-hook', 'true');
    script.textContent = JSON.stringify(structuredData, null, 2);
    
    document.head.appendChild(script);
    structuredDataRef.current.add(scriptId);
  }, []);

  /**
   * Remove all SEO tags added by this hook
   */
  const clearSEOTags = useCallback(() => {
    // Remove meta tags
    const seoMetaTags = document.querySelectorAll('meta[data-seo-hook="true"]');
    seoMetaTags.forEach(tag => tag.remove());

    // Remove link tags
    const seoLinkTags = document.querySelectorAll('link[data-seo-hook="true"]');
    seoLinkTags.forEach(tag => tag.remove());

    // Remove structured data scripts
    structuredDataRef.current.forEach(scriptId => {
      const script = document.getElementById(scriptId);
      if (script) script.remove();
    });
    structuredDataRef.current.clear();
  }, []);

  /**
   * Update all SEO elements
   */
  const updateSEO = useCallback(() => {
    const currentUrl = location.pathname + location.search;
    const fullUrl = `${SEO_CONFIG.baseUrl}${currentUrl}`;
    
    // Generate meta tags
    const metaTags = generateMetaTags({
      title,
      description,
      keywords,
      image,
      url: currentUrl,
      type,
      product,
      article
    });

    // Update document title
    updateTitle(metaTags.title);

    // Update meta tags
    Object.entries(metaTags).forEach(([name, content]) => {
      if (name === 'title') return; // Already handled above
      
      const isProperty = name.startsWith('og:') || name.startsWith('article:') || name.startsWith('product:');
      updateMetaTag(name, content, isProperty);
    });

    // Update canonical URL
    const canonicalUrl = canonical || fullUrl;
    updateLinkTag('canonical', canonicalUrl);

    // Update robots meta tag
    const robotsContent = robots || (noindex || nofollow ? 
      `${noindex ? 'noindex' : 'index'}, ${nofollow ? 'nofollow' : 'follow'}` : 
      'index, follow'
    );
    updateMetaTag('robots', robotsContent);

    // Add structured data
    updateStructuredData('WebSite', {});
    updateStructuredData('Organization', {});

    // Add product structured data if available
    if (product) {
      updateStructuredData('Product', product);
    }

    // Add breadcrumb structured data if available
    if (breadcrumbs && breadcrumbs.length > 0) {
      updateStructuredData('BreadcrumbList', { breadcrumbs });
    }

    // Store current data for comparison
    previousDataRef.current = { ...seoData, url: currentUrl };
  }, [
    location,
    title,
    description,
    keywords,
    image,
    type,
    product,
    article,
    breadcrumbs,
    canonical,
    robots,
    noindex,
    nofollow,
    updateTitle,
    updateMetaTag,
    updateLinkTag,
    updateStructuredData
  ]);

  /**
   * Check if SEO data has changed
   */
  const hasDataChanged = useCallback(() => {
    const currentData = { ...seoData, url: location.pathname + location.search };
    return JSON.stringify(currentData) !== JSON.stringify(previousDataRef.current);
  }, [seoData, location]);

  // Update SEO when component mounts or data changes
  useEffect(() => {
    if (hasDataChanged()) {
      updateSEO();
    }
  }, [updateSEO, hasDataChanged]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearSEOTags();
    };
  }, [clearSEOTags]);

  return {
    updateSEO,
    clearSEOTags,
    updateTitle,
    updateMetaTag,
    updateLinkTag,
    updateStructuredData
  };
};

/**
 * Hook for page-specific SEO optimization
 */
export const usePageSEO = (pageConfig) => {
  const location = useLocation();
  
  const {
    pageType,
    title,
    description,
    keywords = [],
    product,
    category,
    breadcrumbs
  } = pageConfig;

  // Generate dynamic SEO data based on page type
  const seoData = {
    title,
    description,
    keywords,
    type: pageType === 'product' ? 'product' : 'website',
    product: pageType === 'product' ? product : undefined,
    breadcrumbs,
    robots: pageType === 'admin' ? 'noindex, nofollow' : 'index, follow'
  };

  // Add category-specific keywords
  if (category) {
    seoData.keywords = [...keywords, `produse ${category}`, `${category} local`];
  }

  return useSEO(seoData);
};

/**
 * Hook for product SEO optimization
 */
export const useProductSEO = (product, category) => {
  if (!product) return useSEO({});

  const seoData = {
    title: `${product.name} - ${category?.name || 'Produs Local'}`,
    description: `${product.description?.substring(0, 150)} Comandă online de la ${product.producer || 'Pe Foc de Lemne'}. Livrare rapidă în România.`,
    keywords: [
      product.name,
      category?.name || '',
      'produs local',
      'românesc',
      'natural',
      'comandă online'
    ].filter(Boolean),
    image: product.images?.[0],
    type: 'product',
    product: {
      name: product.name,
      description: product.description,
      price: product.price,
      images: product.images,
      category: category?.name,
      producer: product.producer,
      inStock: product.stock_quantity > 0,
      weight: product.weight_grams
    },
    breadcrumbs: [
      { name: 'Acasă', url: '/' },
      { name: 'Produse', url: '/produse' },
      { name: category?.name || 'Categorie', url: `/produse?categoria=${category?.slug}` },
      { name: product.name, url: `/produs/${product.slug || product._id}` }
    ]
  };

  return useSEO(seoData);
};

/**
 * Hook for category page SEO optimization
 */
export const useCategorySEO = (category, products = []) => {
  if (!category) return useSEO({});

  const productCount = products.length;
  
  const seoData = {
    title: `${category.name} - Produse Locale Românești`,
    description: `Descoperă ${productCount} produse din categoria ${category.name}. ${category.description || ''} Produse locale românești de calitate superioară.`,
    keywords: [
      category.name,
      `produse ${category.name}`,
      'produse locale',
      'românești',
      'naturale',
      'bio'
    ],
    breadcrumbs: [
      { name: 'Acasă', url: '/' },
      { name: 'Produse', url: '/produse' },
      { name: category.name, url: `/produse?categoria=${category.slug}` }
    ]
  };

  return useSEO(seoData);
};

/**
 * Hook for search results SEO optimization
 */
export const useSearchSEO = (query, results = []) => {
  const resultCount = results.length;
  
  const seoData = {
    title: `Căutare: "${query}" - Pe Foc de Lemne`,
    description: `${resultCount} rezultate găsite pentru "${query}". Produse locale românești de la producători verificați.`,
    keywords: [query, 'căutare produse', 'produse locale', 'românești'],
    robots: 'noindex, follow', // Don't index search result pages
    canonical: '/produse' // Point to main products page
  };

  return useSEO(seoData);
};

export default useSEO;