/**
 * SEO Utilities for Local Producer Web Application
 * 
 * Comprehensive SEO utilities for meta tags, structured data,
 * and Romanian language optimization.
 */

// Romanian language SEO keywords and phrases
export const ROMANIAN_SEO_KEYWORDS = {
  general: [
    'produse locale',
    'producători români',
    'mâncare tradițională',
    'produse naturale',
    'fermieri locali',
    'alimente bio',
    'produse casnice',
    'mâncare sănătoasă'
  ],
  categories: {
    'lactate': ['lapte proaspăt', 'brânză de țară', 'smântână', 'iaurt natural'],
    'carne': ['carne de vită', 'carne de porc', 'pui de țară', 'carne bio'],
    'legume': ['legume proaspete', 'legume de sezon', 'legume bio', 'salate'],
    'fructe': ['fructe proaspete', 'fructe de sezon', 'mere', 'pere'],
    'panificatie': ['pâine de casă', 'cozonac', 'prăjituri', 'produse de panificație'],
    'conserve': ['murături', 'gem de casă', 'conserve naturale', 'dulceață']
  }
};

// Base SEO configuration for the application
export const SEO_CONFIG = {
  siteName: 'Pe Foc de Lemne - Produse Locale Românești',
  baseUrl: process.env.REACT_APP_BASE_URL || 'https://pefocdelemne.ro',
  defaultImage: '/images/og-default.jpg',
  twitterHandle: '@pefocdelemne',
  facebookPageId: 'pefocdelemne',
  business: {
    name: 'Pe Foc de Lemne',
    description: 'Marketplace pentru produse locale românești de la producători verificați',
    address: {
      streetAddress: 'Strada Producătorilor nr. 1',
      addressLocality: 'București',
      addressRegion: 'București',
      postalCode: '010101',
      addressCountry: 'RO'
    },
    phone: '+40 700 000 000',
    email: 'contact@pefocdelemne.ro',
    priceRange: '$$'
  }
};

/**
 * Generate SEO-friendly slug from Romanian text
 */
export const generateSlug = (text) => {
  const romanianChars = {
    'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
    'Ă': 'A', 'Â': 'A', 'Î': 'I', 'Ș': 'S', 'Ț': 'T'
  };
  
  return text
    .toLowerCase()
    .replace(/[ăâîșț]/g, char => romanianChars[char])
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 50);
};

/**
 * Generate meta tags for a page
 */
export const generateMetaTags = ({
  title,
  description,
  keywords = [],
  image,
  url,
  type = 'website',
  product,
  article
}) => {
  const fullTitle = title ? `${title} | ${SEO_CONFIG.siteName}` : SEO_CONFIG.siteName;
  const fullUrl = url ? `${SEO_CONFIG.baseUrl}${url}` : SEO_CONFIG.baseUrl;
  const fullImage = image ? `${SEO_CONFIG.baseUrl}${image}` : `${SEO_CONFIG.baseUrl}${SEO_CONFIG.defaultImage}`;
  
  // Combine keywords with Romanian SEO keywords
  const allKeywords = [
    ...keywords,
    ...ROMANIAN_SEO_KEYWORDS.general
  ].join(', ');

  const metaTags = {
    // Basic meta tags
    title: fullTitle,
    description: description?.substring(0, 160) || 'Produse locale românești de la producători verificați. Comandă online produse naturale, bio și tradiționale.',
    keywords: allKeywords.substring(0, 255),
    
    // Open Graph tags
    'og:title': fullTitle,
    'og:description': description?.substring(0, 300) || 'Descoperă produse locale românești autentice de la producători verificați. Mâncare sănătoasă, naturală și tradițională.',
    'og:image': fullImage,
    'og:url': fullUrl,
    'og:type': type,
    'og:site_name': SEO_CONFIG.siteName,
    'og:locale': 'ro_RO',
    
    // Twitter Card tags
    'twitter:card': 'summary_large_image',
    'twitter:title': fullTitle.substring(0, 70),
    'twitter:description': description?.substring(0, 200) || 'Produse locale românești de la producători verificați',
    'twitter:image': fullImage,
    'twitter:site': SEO_CONFIG.twitterHandle,
    'twitter:creator': SEO_CONFIG.twitterHandle,
    
    // Additional meta tags
    'robots': 'index, follow',
    'language': 'Romanian',
    'author': SEO_CONFIG.business.name,
    'viewport': 'width=device-width, initial-scale=1.0',
    'theme-color': '#059669',
    'canonical': fullUrl
  };

  // Add product-specific meta tags
  if (product) {
    metaTags['og:type'] = 'product';
    metaTags['product:price:amount'] = product.price;
    metaTags['product:price:currency'] = 'RON';
    metaTags['product:availability'] = product.inStock ? 'in stock' : 'out of stock';
    metaTags['product:category'] = product.category;
    metaTags['product:brand'] = product.producer || SEO_CONFIG.business.name;
  }

  // Add article-specific meta tags
  if (article) {
    metaTags['og:type'] = 'article';
    metaTags['article:published_time'] = article.publishedTime;
    metaTags['article:modified_time'] = article.modifiedTime;
    metaTags['article:author'] = article.author || SEO_CONFIG.business.name;
    metaTags['article:section'] = article.section;
    metaTags['article:tag'] = article.tags?.join(', ');
  }

  return metaTags;
};

/**
 * Generate JSON-LD structured data
 */
export const generateStructuredData = (type, data) => {
  const baseContext = {
    '@context': 'https://schema.org',
    '@type': type
  };

  switch (type) {
    case 'LocalBusiness':
      return {
        ...baseContext,
        name: SEO_CONFIG.business.name,
        description: SEO_CONFIG.business.description,
        url: SEO_CONFIG.baseUrl,
        telephone: SEO_CONFIG.business.phone,
        email: SEO_CONFIG.business.email,
        priceRange: SEO_CONFIG.business.priceRange,
        address: {
          '@type': 'PostalAddress',
          ...SEO_CONFIG.business.address
        },
        geo: {
          '@type': 'GeoCoordinates',
          latitude: data?.latitude || 44.4268,
          longitude: data?.longitude || 26.1025
        },
        openingHours: data?.openingHours || ['Mo-Su 08:00-20:00'],
        paymentAccepted: ['Cash', 'Credit Card', 'Bank Transfer'],
        currenciesAccepted: 'RON',
        areaServed: {
          '@type': 'Country',
          name: 'Romania'
        },
        serviceType: 'Online Marketplace',
        logo: `${SEO_CONFIG.baseUrl}/images/logo.png`,
        image: `${SEO_CONFIG.baseUrl}/images/business-photo.jpg`,
        sameAs: [
          `https://www.facebook.com/${SEO_CONFIG.facebookPageId}`,
          `https://twitter.com/${SEO_CONFIG.twitterHandle.substring(1)}`
        ]
      };

    case 'Product':
      return {
        ...baseContext,
        name: data.name,
        description: data.description,
        image: data.images?.map(img => `${SEO_CONFIG.baseUrl}${img}`) || [],
        brand: {
          '@type': 'Brand',
          name: data.producer || SEO_CONFIG.business.name
        },
        manufacturer: {
          '@type': 'Organization',
          name: data.producer || SEO_CONFIG.business.name
        },
        offers: {
          '@type': 'Offer',
          price: data.price,
          priceCurrency: 'RON',
          availability: data.inStock 
            ? 'https://schema.org/InStock' 
            : 'https://schema.org/OutOfStock',
          seller: {
            '@type': 'Organization',
            name: SEO_CONFIG.business.name
          },
          priceValidUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          shippingDetails: {
            '@type': 'OfferShippingDetails',
            shippingRate: {
              '@type': 'MonetaryAmount',
              value: '0',
              currency: 'RON'
            },
            deliveryTime: {
              '@type': 'ShippingDeliveryTime',
              minValue: 1,
              maxValue: 3,
              unitCode: 'DAY'
            }
          }
        },
        category: data.category,
        weight: data.weight ? {
          '@type': 'QuantitativeValue',
          value: data.weight,
          unitCode: 'GRM'
        } : undefined,
        aggregateRating: data.rating ? {
          '@type': 'AggregateRating',
          ratingValue: data.rating.average,
          reviewCount: data.rating.count,
          bestRating: 5,
          worstRating: 1
        } : undefined,
        review: data.reviews?.map(review => ({
          '@type': 'Review',
          author: {
            '@type': 'Person',
            name: review.author
          },
          reviewRating: {
            '@type': 'Rating',
            ratingValue: review.rating,
            bestRating: 5,
            worstRating: 1
          },
          reviewBody: review.text,
          datePublished: review.date
        })) || []
      };

    case 'WebSite':
      return {
        ...baseContext,
        name: SEO_CONFIG.siteName,
        url: SEO_CONFIG.baseUrl,
        description: SEO_CONFIG.business.description,
        inLanguage: 'ro-RO',
        publisher: {
          '@type': 'Organization',
          name: SEO_CONFIG.business.name,
          logo: {
            '@type': 'ImageObject',
            url: `${SEO_CONFIG.baseUrl}/images/logo.png`
          }
        },
        potentialAction: {
          '@type': 'SearchAction',
          target: `${SEO_CONFIG.baseUrl}/produse?q={search_term_string}`,
          'query-input': 'required name=search_term_string'
        }
      };

    case 'BreadcrumbList':
      return {
        ...baseContext,
        itemListElement: data.breadcrumbs?.map((item, index) => ({
          '@type': 'ListItem',
          position: index + 1,
          name: item.name,
          item: `${SEO_CONFIG.baseUrl}${item.url}`
        })) || []
      };

    case 'Organization':
      return {
        ...baseContext,
        name: SEO_CONFIG.business.name,
        url: SEO_CONFIG.baseUrl,
        logo: `${SEO_CONFIG.baseUrl}/images/logo.png`,
        description: SEO_CONFIG.business.description,
        address: {
          '@type': 'PostalAddress',
          ...SEO_CONFIG.business.address
        },
        contactPoint: {
          '@type': 'ContactPoint',
          telephone: SEO_CONFIG.business.phone,
          contactType: 'Customer Service',
          areaServed: 'RO',
          availableLanguage: 'Romanian'
        },
        sameAs: [
          `https://www.facebook.com/${SEO_CONFIG.facebookPageId}`,
          `https://twitter.com/${SEO_CONFIG.twitterHandle.substring(1)}`
        ]
      };

    default:
      return baseContext;
  }
};

/**
 * Generate XML sitemap data
 */
export const generateSitemapData = (pages = []) => {
  const staticPages = [
    { url: '/', priority: 1.0, changefreq: 'daily' },
    { url: '/produse', priority: 0.9, changefreq: 'daily' },
    { url: '/cos', priority: 0.7, changefreq: 'weekly' },
    { url: '/comanda', priority: 0.8, changefreq: 'monthly' },
    { url: '/despre', priority: 0.6, changefreq: 'monthly' },
    { url: '/contact', priority: 0.6, changefreq: 'monthly' },
    { url: '/termeni', priority: 0.3, changefreq: 'yearly' },
    { url: '/confidentialitate', priority: 0.3, changefreq: 'yearly' }
  ];

  const allPages = [...staticPages, ...pages];
  
  return allPages.map(page => ({
    loc: `${SEO_CONFIG.baseUrl}${page.url}`,
    lastmod: page.lastmod || new Date().toISOString().split('T')[0],
    changefreq: page.changefreq || 'weekly',
    priority: page.priority || 0.5
  }));
};

/**
 * Validate and optimize meta description
 */
export const optimizeMetaDescription = (description, maxLength = 160) => {
  if (!description) return '';
  
  // Remove HTML tags
  const cleanDescription = description.replace(/<[^>]*>/g, '');
  
  // Truncate if too long and add ellipsis
  if (cleanDescription.length > maxLength) {
    return cleanDescription.substring(0, maxLength - 3).trim() + '...';
  }
  
  return cleanDescription;
};

/**
 * Generate Romanian language keywords for a category
 */
export const getCategoryKeywords = (categorySlug) => {
  return ROMANIAN_SEO_KEYWORDS.categories[categorySlug] || ROMANIAN_SEO_KEYWORDS.general;
};

/**
 * Create SEO-friendly alt text for images
 */
export const generateAltText = (productName, category, type = 'product') => {
  switch (type) {
    case 'product':
      return `${productName} - produs local românesc ${category} de calitate`;
    case 'category':
      return `Categoria ${category} - produse locale românești`;
    case 'hero':
      return `Pe Foc de Lemne - marketplace pentru produse locale românești`;
    case 'logo':
      return `Pe Foc de Lemne - logo marketplace produse locale`;
    default:
      return `${productName} - produs local românesc`;
  }
};

/**
 * Check if URL is canonical
 */
export const isCanonicalUrl = (url) => {
  // Remove trailing slashes and query parameters for canonical check
  const cleanUrl = url.replace(/\/$/, '').split('?')[0];
  return cleanUrl;
};

/**
 * Generate hreflang tags for multi-language support
 */
export const generateHreflangTags = (currentPath) => {
  return [
    {
      hreflang: 'ro',
      href: `${SEO_CONFIG.baseUrl}${currentPath}`
    },
    {
      hreflang: 'x-default',
      href: `${SEO_CONFIG.baseUrl}${currentPath}`
    }
  ];
};

/**
 * Create robots meta tag based on page type
 */
export const generateRobotsTag = (pageType, isPublished = true) => {
  if (!isPublished) return 'noindex, nofollow';
  
  switch (pageType) {
    case 'admin':
    case 'checkout':
    case 'order-confirmation':
      return 'noindex, nofollow';
    case 'product':
    case 'category':
    case 'home':
      return 'index, follow';
    case 'search':
      return 'noindex, follow';
    default:
      return 'index, follow';
  }
};

const seoUtils = {
  generateMetaTags,
  generateStructuredData,
  generateSitemapData,
  generateSlug,
  optimizeMetaDescription,
  getCategoryKeywords,
  generateAltText,
  isCanonicalUrl,
  generateHreflangTags,
  generateRobotsTag,
  SEO_CONFIG,
  ROMANIAN_SEO_KEYWORDS
};

export default seoUtils;