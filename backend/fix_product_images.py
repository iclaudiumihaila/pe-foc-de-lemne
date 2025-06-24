#!/usr/bin/env python3
"""
Fix product images with placeholder URLs
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database, init_mongodb
from app.config import DevelopmentConfig

# Placeholder images from a reliable source
PLACEHOLDER_IMAGES = {
    "Lactate": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=300&fit=crop",  # Dairy
    "Carne și Mezeluri": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400&h=300&fit=crop",  # Meat
    "Legume și Fructe": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&h=300&fit=crop",  # Vegetables
    "Produse de Panificație": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop",  # Bread
    "Conserve și Dulcețuri": "https://images.unsplash.com/photo-1562967914-608f82629710?w=400&h=300&fit=crop",  # Preserves
}

# Specific product images
PRODUCT_IMAGES = {
    "Brânză de vacă proaspătă": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400&h=300&fit=crop",
    "Lapte proaspăt de fermă": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop",
    "Smântână 30% grăsime": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=300&fit=crop",
    "Cârnați de casă afumați": "https://images.unsplash.com/photo-1601924582970-9238bcb495d9?w=400&h=300&fit=crop",
    "Slănină afumată": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400&h=300&fit=crop",
    "Roșii de grădină": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&h=300&fit=crop",
    "Mere ionatan": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=300&fit=crop",
    "Pâine de casă cu maia": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=400&h=300&fit=crop",
    "Cozonac cu nucă": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop",
    "Dulceață de caise": "https://images.unsplash.com/photo-1562967914-608f82629710?w=400&h=300&fit=crop",
    "Zacuscă de vinete": "https://images.unsplash.com/photo-1601001435957-74f0958a93c8?w=400&h=300&fit=crop",
}

def fix_product_images():
    """Update products with proper image URLs"""
    try:
        # Initialize database
        init_mongodb(DevelopmentConfig)
        db = get_database()
        
        print("Fixing product images...")
        
        # Get all products with their categories
        products = list(db.products.find())
        print(f"Found {len(products)} products")
        
        # Get categories for mapping
        categories = {cat['_id']: cat['name'] for cat in db.categories.find()}
        
        # Update each product
        updated_count = 0
        for product in products:
            product_name = product.get('name', '')
            category_name = categories.get(product.get('category_id'))
            
            # Get specific image or fallback to category image
            image_url = PRODUCT_IMAGES.get(
                product_name, 
                PLACEHOLDER_IMAGES.get(category_name, PLACEHOLDER_IMAGES["Lactate"])
            )
            
            # Update the product
            db.products.update_one(
                {'_id': product['_id']},
                {
                    '$set': {
                        'images': [image_url],
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            updated_count += 1
            print(f"  ✓ Updated {product_name} with image")
        
        print(f"\n✓ Updated {updated_count} products with proper image URLs!")
        
    except Exception as e:
        print(f"Error fixing product images: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    fix_product_images()