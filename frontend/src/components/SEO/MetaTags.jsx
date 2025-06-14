/**
 * MetaTags Component for Local Producer Web Application
 * 
 * React component for rendering SEO meta tags in the document head.
 * Supports Open Graph, Twitter Cards, and Romanian language optimization.
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import { generateMetaTags, generateStructuredData, SEO_CONFIG } from '../../utils/seo';

const MetaTags = ({
  title,
  description,
  keywords = [],
  image,
  url,
  type = 'website',
  product,
  article,
  breadcrumbs,
  canonical,
  robots,
  noindex = false,
  nofollow = false
}) => {
  // Get current URL if not provided
  const currentUrl = url || (typeof window !== 'undefined' ? window.location.pathname : '/');
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

  // Generate structured data
  const websiteStructuredData = generateStructuredData('WebSite', {});
  const organizationStructuredData = generateStructuredData('Organization', {});
  
  let productStructuredData = null;
  if (product) {
    productStructuredData = generateStructuredData('Product', product);
  }

  let breadcrumbStructuredData = null;
  if (breadcrumbs && breadcrumbs.length > 0) {
    breadcrumbStructuredData = generateStructuredData('BreadcrumbList', { breadcrumbs });
  }

  // Determine robots meta content
  const robotsContent = robots || (noindex || nofollow ? 
    `${noindex ? 'noindex' : 'index'}, ${nofollow ? 'nofollow' : 'follow'}` : 
    'index, follow'
  );

  // Canonical URL
  const canonicalUrl = canonical || fullUrl;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{metaTags.title}</title>
      <meta name="description" content={metaTags.description} />
      <meta name="keywords" content={metaTags.keywords} />
      <meta name="robots" content={robotsContent} />
      <meta name="language" content="Romanian" />
      <meta name="author" content={SEO_CONFIG.business.name} />
      
      {/* Viewport and mobile optimization */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="theme-color" content="#059669" />
      <meta name="msapplication-TileColor" content="#059669" />
      
      {/* Canonical URL */}
      <link rel="canonical" href={canonicalUrl} />
      
      {/* Open Graph Meta Tags */}
      <meta property="og:title" content={metaTags['og:title']} />
      <meta property="og:description" content={metaTags['og:description']} />
      <meta property="og:image" content={metaTags['og:image']} />
      <meta property="og:url" content={metaTags['og:url']} />
      <meta property="og:type" content={metaTags['og:type']} />
      <meta property="og:site_name" content={metaTags['og:site_name']} />
      <meta property="og:locale" content={metaTags['og:locale']} />
      
      {/* Product-specific Open Graph tags */}
      {product && (
        <>
          <meta property="product:price:amount" content={metaTags['product:price:amount']} />
          <meta property="product:price:currency" content={metaTags['product:price:currency']} />
          <meta property="product:availability" content={metaTags['product:availability']} />
          <meta property="product:category" content={metaTags['product:category']} />
          <meta property="product:brand" content={metaTags['product:brand']} />
        </>
      )}
      
      {/* Article-specific Open Graph tags */}
      {article && (
        <>
          <meta property="article:published_time" content={metaTags['article:published_time']} />
          <meta property="article:modified_time" content={metaTags['article:modified_time']} />
          <meta property="article:author" content={metaTags['article:author']} />
          <meta property="article:section" content={metaTags['article:section']} />
          <meta property="article:tag" content={metaTags['article:tag']} />
        </>
      )}
      
      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content={metaTags['twitter:card']} />
      <meta name="twitter:title" content={metaTags['twitter:title']} />
      <meta name="twitter:description" content={metaTags['twitter:description']} />
      <meta name="twitter:image" content={metaTags['twitter:image']} />
      <meta name="twitter:site" content={metaTags['twitter:site']} />
      <meta name="twitter:creator" content={metaTags['twitter:creator']} />
      
      {/* Additional meta tags for Romanian market */}
      <meta name="geo.region" content="RO" />
      <meta name="geo.country" content="Romania" />
      <meta name="dc.language" content="ro" />
      <meta name="content-language" content="ro" />
      
      {/* Favicon and app icons */}
      <link rel="icon" type="image/x-icon" href="/favicon.ico" />
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="manifest" href="/manifest.json" />
      
      {/* Preconnect to external domains for performance */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      
      {/* DNS prefetch for performance optimization */}
      <link rel="dns-prefetch" href="//www.google-analytics.com" />
      <link rel="dns-prefetch" href="//www.googletagmanager.com" />
      
      {/* Structured Data - Website */}
      <script type="application/ld+json">
        {JSON.stringify(websiteStructuredData, null, 2)}
      </script>
      
      {/* Structured Data - Organization */}
      <script type="application/ld+json">
        {JSON.stringify(organizationStructuredData, null, 2)}
      </script>
      
      {/* Structured Data - Product (if applicable) */}
      {productStructuredData && (
        <script type="application/ld+json">
          {JSON.stringify(productStructuredData, null, 2)}
        </script>
      )}
      
      {/* Structured Data - Breadcrumbs (if applicable) */}
      {breadcrumbStructuredData && (
        <script type="application/ld+json">
          {JSON.stringify(breadcrumbStructuredData, null, 2)}
        </script>
      )}
      
      {/* Local Business Structured Data for homepage */}
      {currentUrl === '/' && (
        <script type="application/ld+json">
          {JSON.stringify(generateStructuredData('LocalBusiness', {}), null, 2)}
        </script>
      )}
      
      {/* Additional page-specific structured data */}
      {type === 'website' && currentUrl === '/' && (
        <script type="application/ld+json">
          {JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            '@id': `${SEO_CONFIG.baseUrl}/#webpage`,
            url: SEO_CONFIG.baseUrl,
            name: SEO_CONFIG.siteName,
            isPartOf: {
              '@id': `${SEO_CONFIG.baseUrl}/#website`
            },
            about: {
              '@id': `${SEO_CONFIG.baseUrl}/#organization`
            },
            description: SEO_CONFIG.business.description,
            inLanguage: 'ro-RO'
          }, null, 2)}
        </script>
      )}
    </Helmet>
  );
};

export default MetaTags;