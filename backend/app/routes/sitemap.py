"""
Sitemap Generator Routes for Local Producer Web Application

This module provides dynamic sitemap generation for SEO optimization,
including product and category pages with Romanian language support.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, Response, request
from app.models.product import Product
from app.models.category import Category
from app.utils.error_handlers import create_error_response
from app.utils.seo import generate_sitemap_xml, SEO_CONFIG

# Create sitemap blueprint
sitemap_bp = Blueprint('sitemap', __name__)


@sitemap_bp.route('/sitemap.xml', methods=['GET'])
def generate_sitemap():
    """
    Generate dynamic XML sitemap including all public pages.
    
    Returns:
        XML sitemap following sitemaps.org protocol
    """
    try:
        from app.database import get_database
        db = get_database()
        
        # Base static pages
        urls = [
            {
                'loc': f'{SEO_CONFIG["base_url"]}/',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '1.0'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/produse',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '0.9'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/cos',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.7'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/comanda',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.8'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/despre',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.6'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/contact',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.6'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/termeni',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'yearly',
                'priority': '0.3'
            },
            {
                'loc': f'{SEO_CONFIG["base_url"]}/confidentialitate',
                'lastmod': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'changefreq': 'yearly',
                'priority': '0.3'
            }
        ]

        # Add category pages
        try:
            categories = list(db[Category.COLLECTION_NAME].find({'is_active': True}))
            for category_doc in categories:
                category = Category(category_doc)
                urls.append({
                    'loc': f'{SEO_CONFIG["base_url"]}/produse?categoria={category.slug}',
                    'lastmod': category.updated_at.strftime('%Y-%m-%d') if category.updated_at else datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'changefreq': 'daily',
                    'priority': '0.8'
                })
                
            logging.info(f"Added {len(categories)} category pages to sitemap")
        except Exception as e:
            logging.warning(f"Could not fetch categories for sitemap: {str(e)}")

        # Add product pages (limit to available products)
        try:
            # Get available products with pagination for large datasets
            products_cursor = db[Product.COLLECTION_NAME].find({
                'is_available': True,
                'stock_quantity': {'$gt': 0}
            }).limit(1000)  # Limit to prevent huge sitemaps
            
            product_count = 0
            for product_doc in products_cursor:
                product = Product(product_doc)
                # Use slug if available, otherwise use ID
                product_url = f'/produs/{product.slug}' if hasattr(product, 'slug') and product.slug else f'/produs/{str(product._id)}'
                
                urls.append({
                    'loc': f'{SEO_CONFIG["base_url"]}{product_url}',
                    'lastmod': product.updated_at.strftime('%Y-%m-%d') if product.updated_at else product.created_at.strftime('%Y-%m-%d'),
                    'changefreq': 'weekly',
                    'priority': '0.7'
                })
                product_count += 1
                
            logging.info(f"Added {product_count} product pages to sitemap")
        except Exception as e:
            logging.warning(f"Could not fetch products for sitemap: {str(e)}")

        # Generate XML sitemap
        sitemap_xml = generate_sitemap_xml(urls)
        
        logging.info(f"Generated sitemap with {len(urls)} URLs")
        
        return Response(
            sitemap_xml,
            mimetype='application/xml',
            headers={
                'Content-Type': 'application/xml; charset=utf-8',
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Last-Modified': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
        )
        
    except Exception as e:
        logging.error(f"Error generating sitemap: {str(e)}")
        response, status = create_error_response(
            "SITEMAP_001",
            "Failed to generate sitemap",
            500
        )
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?>\n<!-- Sitemap generation error -->',
            mimetype='application/xml',
            status=500
        )


@sitemap_bp.route('/robots.txt', methods=['GET'])
def robots_txt():
    """
    Generate robots.txt file with sitemap reference.
    
    Returns:
        robots.txt content
    """
    try:
        robots_content = f"""User-agent: *
Allow: /

# Disallow admin pages
Disallow: /admin/
Disallow: /administrare/

# Disallow checkout and cart pages
Disallow: /comanda
Disallow: /cos/checkout
Disallow: /confirmare-comanda

# Disallow search result pages with parameters
Disallow: /*?q=*
Disallow: /*?search=*
Disallow: /*?filter=*

# Disallow API endpoints
Disallow: /api/

# Allow important pages
Allow: /produse
Allow: /produse?categoria=*
Allow: /despre
Allow: /contact

# Sitemap location
Sitemap: {SEO_CONFIG["base_url"]}/sitemap.xml

# Crawl delay for better server performance
Crawl-delay: 1

# Specific rules for major search engines
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: Slurp
Allow: /
Crawl-delay: 2

# Block known bad bots
User-agent: BadBot
Disallow: /

User-agent: ScrapyBot
Disallow: /

User-agent: MJ12bot
Disallow: /
"""

        return Response(
            robots_content,
            mimetype='text/plain',
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
            }
        )
        
    except Exception as e:
        logging.error(f"Error generating robots.txt: {str(e)}")
        return Response(
            "User-agent: *\nDisallow: /\n",
            mimetype='text/plain',
            status=500
        )


# SEO utility functions for use in other routes
def add_seo_headers(response, page_type='default'):
    """
    Add SEO-related headers to responses.
    
    Args:
        response: Flask response object
        page_type: Type of page for specific headers
    
    Returns:
        Modified response with SEO headers
    """
    # Add security and SEO headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Add caching headers based on page type
    if page_type == 'product':
        response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
    elif page_type == 'category':
        response.headers['Cache-Control'] = 'public, max-age=1800'  # 30 minutes
    elif page_type == 'home':
        response.headers['Cache-Control'] = 'public, max-age=1800'  # 30 minutes
    else:
        response.headers['Cache-Control'] = 'public, max-age=300'   # 5 minutes
    
    return response