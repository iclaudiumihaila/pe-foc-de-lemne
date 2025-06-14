"""
SEO Utilities for Local Producer Web Application Backend

This module provides SEO utility functions for generating sitemaps,
meta tags, and Romanian language optimization.
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import quote


# SEO Configuration
SEO_CONFIG = {
    "site_name": "Pe Foc de Lemne - Produse Locale Românești",
    "base_url": "https://pefocdelemne.ro",
    "default_image": "/images/og-default.jpg",
    "business_name": "Pe Foc de Lemne",
    "description": "Marketplace pentru produse locale românești de la producători verificați",
    "keywords": [
        "produse locale",
        "producători români", 
        "mâncare tradițională",
        "produse naturale",
        "fermieri locali",
        "alimente bio",
        "comandă online",
        "România"
    ]
}

# Romanian character mapping for URL slugs
ROMANIAN_CHAR_MAP = {
    'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
    'Ă': 'A', 'Â': 'A', 'Î': 'I', 'Ș': 'S', 'Ț': 'T'
}


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate SEO-friendly slug from Romanian text.
    
    Args:
        text (str): Input text
        max_length (int): Maximum slug length
        
    Returns:
        str: SEO-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace Romanian characters
    for ro_char, latin_char in ROMANIAN_CHAR_MAP.items():
        slug = slug.replace(ro_char.lower(), latin_char)
    
    # Remove non-alphanumeric characters and replace with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens and limit length
    slug = slug.strip('-')[:max_length]
    
    # Remove trailing hyphen if text was truncated
    slug = slug.rstrip('-')
    
    return slug


def generate_sitemap_xml(urls: List[Dict[str, str]]) -> str:
    """
    Generate XML sitemap from list of URLs.
    
    Args:
        urls (List[Dict]): List of URL dictionaries with loc, lastmod, changefreq, priority
        
    Returns:
        str: XML sitemap content
    """
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
    ]
    
    for url_data in urls:
        xml_lines.append('  <url>')
        
        # Required loc element
        loc = url_data.get('loc', '')
        if loc:
            # Ensure URL is properly encoded
            xml_lines.append(f'    <loc>{escape_xml(loc)}</loc>')
        
        # Optional lastmod
        lastmod = url_data.get('lastmod')
        if lastmod:
            xml_lines.append(f'    <lastmod>{lastmod}</lastmod>')
        
        # Optional changefreq
        changefreq = url_data.get('changefreq')
        if changefreq:
            xml_lines.append(f'    <changefreq>{changefreq}</changefreq>')
        
        # Optional priority
        priority = url_data.get('priority')
        if priority:
            xml_lines.append(f'    <priority>{priority}</priority>')
        
        # Optional image information
        images = url_data.get('images', [])
        for image_url in images:
            xml_lines.append('    <image:image>')
            xml_lines.append(f'      <image:loc>{escape_xml(image_url)}</image:loc>')
            xml_lines.append('    </image:image>')
        
        xml_lines.append('  </url>')
    
    xml_lines.append('</urlset>')
    
    return '\n'.join(xml_lines)


def escape_xml(text: str) -> str:
    """
    Escape special XML characters.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: XML-escaped text
    """
    if not text:
        return ""
    
    # Replace XML special characters
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text


def generate_meta_description(text: str, max_length: int = 160) -> str:
    """
    Generate SEO-optimized meta description from text.
    
    Args:
        text (str): Source text
        max_length (int): Maximum description length
        
    Returns:
        str: Optimized meta description
    """
    if not text:
        return ""
    
    # Remove HTML tags if present
    clean_text = re.sub(r'<[^>]*>', '', text)
    
    # Remove extra whitespace
    clean_text = ' '.join(clean_text.split())
    
    # Truncate if too long and add ellipsis
    if len(clean_text) > max_length:
        # Find last complete word within limit
        truncated = clean_text[:max_length - 3]
        last_space = truncated.rfind(' ')
        if last_space > max_length // 2:  # Only truncate at word boundary if reasonable
            clean_text = truncated[:last_space] + '...'
        else:
            clean_text = truncated + '...'
    
    return clean_text


def generate_product_meta_tags(product: Dict[str, Any], category: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Generate meta tags for product pages.
    
    Args:
        product (Dict): Product data
        category (Dict, optional): Category data
        
    Returns:
        Dict[str, str]: Meta tags dictionary
    """
    product_name = product.get('name', '')
    category_name = category.get('name', 'Produs Local') if category else 'Produs Local'
    price = product.get('price', 0)
    description = product.get('description', '')
    
    # Generate title
    title = f"{product_name} - {category_name} | Pe Foc de Lemne"
    
    # Generate description
    meta_desc = generate_meta_description(
        f"{description} Comandă {product_name} de la producătorul local. Preț: {price} RON. Livrare rapidă în România."
    )
    
    # Generate keywords
    keywords = [
        product_name,
        category_name,
        'produs local',
        'românesc',
        'natural',
        'comandă online',
        'livrare rapidă'
    ]
    
    if product.get('producer'):
        keywords.append(product['producer'])
    
    return {
        'title': title,
        'description': meta_desc,
        'keywords': ', '.join(filter(None, keywords)),
        'og:title': title,
        'og:description': meta_desc,
        'og:type': 'product',
        'product:price:amount': str(price),
        'product:price:currency': 'RON',
        'product:availability': 'in stock' if product.get('stock_quantity', 0) > 0 else 'out of stock',
        'product:category': category_name,
        'product:brand': product.get('producer', SEO_CONFIG['business_name'])
    }


def generate_category_meta_tags(category: Dict[str, Any], product_count: int = 0) -> Dict[str, str]:
    """
    Generate meta tags for category pages.
    
    Args:
        category (Dict): Category data
        product_count (int): Number of products in category
        
    Returns:
        Dict[str, str]: Meta tags dictionary
    """
    category_name = category.get('name', '')
    category_desc = category.get('description', '')
    
    # Generate title
    title = f"{category_name} - Produse Locale Românești | Pe Foc de Lemne"
    
    # Generate description
    if category_desc:
        meta_desc = generate_meta_description(
            f"Descoperă {product_count} produse din categoria {category_name}. {category_desc} Produse locale românești de calitate superioară."
        )
    else:
        meta_desc = generate_meta_description(
            f"Descoperă {product_count} produse din categoria {category_name}. Produse locale românești de la producători verificați."
        )
    
    # Generate keywords
    keywords = [
        category_name,
        f"produse {category_name}",
        f"{category_name} locale",
        f"{category_name} românești",
        'produse naturale',
        'producători verificați',
        'comandă online'
    ]
    
    return {
        'title': title,
        'description': meta_desc,
        'keywords': ', '.join(keywords),
        'og:title': title,
        'og:description': meta_desc,
        'og:type': 'website'
    }


def generate_alt_text(name: str, category: str = '', context: str = 'product') -> str:
    """
    Generate SEO-optimized alt text for images.
    
    Args:
        name (str): Product/item name
        category (str): Category name
        context (str): Image context (product, category, hero, etc.)
        
    Returns:
        str: Optimized alt text
    """
    if context == 'product':
        return f"{name} - produs local românesc {category} de calitate".strip()
    elif context == 'category':
        return f"Categoria {category} - produse locale românești"
    elif context == 'hero':
        return "Pe Foc de Lemne - marketplace pentru produse locale românești"
    elif context == 'logo':
        return "Pe Foc de Lemne - logo marketplace produse locale"
    else:
        return f"{name} - produs local românesc".strip()


def validate_robots_txt_rules(user_agent: str, path: str) -> bool:
    """
    Validate if a path is allowed by robots.txt rules.
    
    Args:
        user_agent (str): User agent string
        path (str): Path to validate
        
    Returns:
        bool: True if allowed, False if disallowed
    """
    # Define disallowed paths
    disallowed_patterns = [
        '/admin/',
        '/administrare/',
        '/api/',
        '/comanda',
        '/cos/checkout',
        '/confirmare-comanda'
    ]
    
    # Check search parameters
    disallowed_params = ['?q=', '?search=', '?filter=']
    
    # Check if path matches disallowed patterns
    for pattern in disallowed_patterns:
        if path.startswith(pattern):
            return False
    
    # Check for disallowed parameters
    for param in disallowed_params:
        if param in path:
            return False
    
    return True


def generate_breadcrumb_schema(breadcrumbs: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generate JSON-LD breadcrumb schema.
    
    Args:
        breadcrumbs (List[Dict]): List of breadcrumb items with 'name' and 'url'
        
    Returns:
        Dict: JSON-LD breadcrumb schema
    """
    if not breadcrumbs:
        return {}
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": item.get('name', ''),
                "item": f"{SEO_CONFIG['base_url']}{item.get('url', '')}"
            }
            for index, item in enumerate(breadcrumbs)
        ]
    }


def generate_product_schema(product: Dict[str, Any], category: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate JSON-LD product schema.
    
    Args:
        product (Dict): Product data
        category (Dict, optional): Category data
        
    Returns:
        Dict: JSON-LD product schema
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.get('name', ''),
        "description": product.get('description', ''),
        "category": category.get('name', '') if category else '',
        "brand": {
            "@type": "Brand",
            "name": product.get('producer', SEO_CONFIG['business_name'])
        },
        "offers": {
            "@type": "Offer",
            "price": str(product.get('price', 0)),
            "priceCurrency": "RON",
            "availability": "https://schema.org/InStock" if product.get('stock_quantity', 0) > 0 else "https://schema.org/OutOfStock",
            "seller": {
                "@type": "Organization",
                "name": SEO_CONFIG['business_name']
            }
        }
    }
    
    # Add images if available
    images = product.get('images', [])
    if images:
        schema['image'] = [f"{SEO_CONFIG['base_url']}{img}" for img in images]
    
    # Add weight if available
    if product.get('weight_grams'):
        schema['weight'] = {
            "@type": "QuantitativeValue",
            "value": product['weight_grams'],
            "unitCode": "GRM"
        }
    
    return schema


def optimize_for_local_seo(content: Dict[str, Any], location: str = "România") -> Dict[str, Any]:
    """
    Optimize content for local SEO.
    
    Args:
        content (Dict): Content to optimize
        location (str): Location for optimization
        
    Returns:
        Dict: Optimized content
    """
    # Add location-based keywords
    if 'keywords' in content:
        local_keywords = [
            f"{location}",
            f"local {location}",
            f"produse {location}",
            "livrare locală",
            "producători locali"
        ]
        content['keywords'] = f"{content['keywords']}, {', '.join(local_keywords)}"
    
    # Add location to description if not present
    if 'description' in content and location.lower() not in content['description'].lower():
        content['description'] = f"{content['description']} Disponibil în {location}."
    
    return content