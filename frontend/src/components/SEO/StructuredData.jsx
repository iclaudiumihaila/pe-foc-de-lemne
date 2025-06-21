/**
 * StructuredData Component for Local Producer Web Application
 * 
 * React component for rendering JSON-LD structured data scripts.
 * Optimized for Romanian local business and e-commerce SEO.
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import { generateStructuredData, SEO_CONFIG } from '../../utils/seo';

const StructuredData = ({ type, data, id }) => {
  const structuredData = generateStructuredData(type, data);
  
  // Add unique ID if provided
  if (id) {
    structuredData['@id'] = `${SEO_CONFIG.baseUrl}/#${id}`;
  }

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(structuredData, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Product structured data component
 */
export const ProductStructuredData = ({ product, category, reviews = [] }) => {
  const productData = {
    name: product.name,
    description: product.description,
    price: product.price,
    images: product.images,
    category: category?.name,
    producer: product.producer,
    inStock: product.stock_quantity > 0,
    weight: product.weight_grams,
    reviews: reviews.map(review => ({
      author: review.customer_name || 'Client verificat',
      rating: review.rating,
      text: review.comment,
      date: review.created_at
    })),
    rating: reviews.length > 0 ? {
      average: reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length,
      count: reviews.length
    } : null
  };

  return (
    <StructuredData 
      type="Product" 
      data={productData} 
      id={`product-${product._id}`}
    />
  );
};

/**
 * Local Business structured data component
 */
export const LocalBusinessStructuredData = ({ customData = {} }) => {
  const businessData = {
    latitude: 44.4268, // București coordinates
    longitude: 26.1025,
    openingHours: [
      'Mo-Fr 08:00-20:00',
      'Sa-Su 09:00-18:00'
    ],
    ...customData
  };

  return (
    <StructuredData 
      type="LocalBusiness" 
      data={businessData} 
      id="local-business"
    />
  );
};

/**
 * Breadcrumb structured data component
 */
export const BreadcrumbStructuredData = ({ breadcrumbs }) => {
  if (!breadcrumbs || breadcrumbs.length === 0) return null;

  return (
    <StructuredData 
      type="BreadcrumbList" 
      data={{ breadcrumbs }} 
      id="breadcrumbs"
    />
  );
};

/**
 * FAQ structured data component
 */
export const FAQStructuredData = ({ faqs }) => {
  if (!faqs || faqs.length === 0) return null;

  const faqData = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer
      }
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(faqData, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Review structured data component
 */
export const ReviewStructuredData = ({ reviews, product }) => {
  if (!reviews || reviews.length === 0) return null;

  const reviewData = {
    '@context': 'https://schema.org',
    '@type': 'Review',
    itemReviewed: {
      '@type': 'Product',
      name: product.name,
      image: product.images?.[0] ? `${SEO_CONFIG.baseUrl}${product.images[0]}` : null,
      offers: {
        '@type': 'Offer',
        price: product.price,
        priceCurrency: 'RON'
      }
    },
    reviewRating: {
      '@type': 'Rating',
      ratingValue: reviews[0].rating,
      bestRating: 5,
      worstRating: 1
    },
    author: {
      '@type': 'Person',
      name: reviews[0].customer_name || 'Client verificat'
    },
    reviewBody: reviews[0].comment,
    datePublished: reviews[0].created_at
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(reviewData, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Recipe structured data component (for food products)
 */
export const RecipeStructuredData = ({ recipe }) => {
  if (!recipe) return null;

  const recipeData = {
    '@context': 'https://schema.org',
    '@type': 'Recipe',
    name: recipe.name,
    image: recipe.images?.map(img => `${SEO_CONFIG.baseUrl}${img}`) || [],
    description: recipe.description,
    keywords: recipe.keywords?.join(', '),
    author: {
      '@type': 'Person',
      name: recipe.chef || SEO_CONFIG.business.name
    },
    datePublished: recipe.datePublished,
    prepTime: recipe.prepTime ? `PT${recipe.prepTime}M` : undefined,
    cookTime: recipe.cookTime ? `PT${recipe.cookTime}M` : undefined,
    totalTime: recipe.totalTime ? `PT${recipe.totalTime}M` : undefined,
    recipeCategory: recipe.category,
    recipeCuisine: 'Romanian',
    recipeYield: recipe.servings || '4 porții',
    nutrition: recipe.nutrition ? {
      '@type': 'NutritionInformation',
      calories: recipe.nutrition.calories,
      fatContent: recipe.nutrition.fat,
      carbohydrateContent: recipe.nutrition.carbs,
      proteinContent: recipe.nutrition.protein
    } : undefined,
    recipeIngredient: recipe.ingredients || [],
    recipeInstructions: recipe.instructions?.map((step, index) => ({
      '@type': 'HowToStep',
      position: index + 1,
      text: step
    })) || [],
    aggregateRating: recipe.rating ? {
      '@type': 'AggregateRating',
      ratingValue: recipe.rating.average,
      reviewCount: recipe.rating.count,
      bestRating: 5,
      worstRating: 1
    } : undefined
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(recipeData, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Article structured data component
 */
export const ArticleStructuredData = ({ article }) => {
  if (!article) return null;

  const articleData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: article.description,
    image: article.image ? `${SEO_CONFIG.baseUrl}${article.image}` : null,
    author: {
      '@type': 'Person',
      name: article.author || SEO_CONFIG.business.name
    },
    publisher: {
      '@type': 'Organization',
      name: SEO_CONFIG.business.name,
      logo: {
        '@type': 'ImageObject',
        url: `${SEO_CONFIG.baseUrl}/images/logo.png`
      }
    },
    datePublished: article.publishedDate,
    dateModified: article.modifiedDate || article.publishedDate,
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${SEO_CONFIG.baseUrl}${article.url}`
    },
    articleSection: article.category,
    keywords: article.keywords?.join(', '),
    wordCount: article.wordCount,
    inLanguage: 'ro-RO'
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(articleData, null, 2)}
      </script>
    </Helmet>
  );
};

/**
 * Event structured data component
 */
export const EventStructuredData = ({ event }) => {
  if (!event) return null;

  const eventData = {
    '@context': 'https://schema.org',
    '@type': 'Event',
    name: event.name,
    description: event.description,
    image: event.image ? `${SEO_CONFIG.baseUrl}${event.image}` : null,
    startDate: event.startDate,
    endDate: event.endDate,
    eventStatus: 'https://schema.org/EventScheduled',
    eventAttendanceMode: event.isOnline ? 
      'https://schema.org/OnlineEventAttendanceMode' : 
      'https://schema.org/OfflineEventAttendanceMode',
    location: event.isOnline ? {
      '@type': 'VirtualLocation',
      url: event.url
    } : {
      '@type': 'Place',
      name: event.venueName,
      address: {
        '@type': 'PostalAddress',
        streetAddress: event.address,
        addressLocality: event.city,
        addressCountry: 'RO'
      }
    },
    organizer: {
      '@type': 'Organization',
      name: SEO_CONFIG.business.name,
      url: SEO_CONFIG.baseUrl
    },
    offers: event.price ? {
      '@type': 'Offer',
      price: event.price,
      priceCurrency: 'RON',
      availability: 'https://schema.org/InStock',
      url: `${SEO_CONFIG.baseUrl}${event.url}`
    } : undefined
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(eventData, null, 2)}
      </script>
    </Helmet>
  );
};

export default StructuredData;