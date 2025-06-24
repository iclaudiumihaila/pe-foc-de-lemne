#!/usr/bin/env python3
"""Fix all products in database to match Product model expectations"""

from pymongo import MongoClient
from app.config import Config
from datetime import datetime
from bson import ObjectId
import re

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[ăâ]', 'a', text)
    text = re.sub(r'[îâ]', 'i', text)
    text = re.sub(r'[șş]', 's', text)
    text = re.sub(r'[țţ]', 't', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def fix_products():
    """Fix all products to match the Product model structure"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    # Get the seed data mapping for stock quantities and units
    seed_data = {
        "Brânză de vacă proaspătă": {"stock": 50, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800&q=80",
            "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800&q=80"
        ]},
        "Telemea de oaie": {"stock": 30, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=800&q=80"
        ]},
        "Lapte proaspăt de fermă": {"stock": 100, "unit": "litru", "images": [
            "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800&q=80"
        ]},
        "Smântână 30% grăsime": {"stock": 40, "unit": "borcan 400g", "images": [
            "https://images.unsplash.com/photo-1555792903-8b6d850ba396?w=800&q=80"
        ]},
        "Cârnați de casă afumați": {"stock": 25, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1624362770755-8328d5f5a281?w=800&q=80"
        ]},
        "Slănină afumată": {"stock": 20, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=800&q=80"
        ]},
        "Roșii de grădină": {"stock": 60, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=800&q=80"
        ]},
        "Cartofi noi": {"stock": 100, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=800&q=80"
        ]},
        "Mere ionatan": {"stock": 80, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=800&q=80"
        ]},
        "Prune pentru magiun": {"stock": 70, "unit": "kg", "images": [
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=800&q=80"
        ]},
        "Pâine de casă cu maia": {"stock": 30, "unit": "bucată", "images": [
            "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=800&q=80"
        ]},
        "Cozonac cu nucă": {"stock": 15, "unit": "bucată", "images": [
            "https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=800&q=80"
        ]},
        "Dulceață de caise": {"stock": 40, "unit": "borcan 400g", "images": [
            "https://images.unsplash.com/photo-1597045415647-5e0a9c3ca63f?w=800&q=80"
        ]},
        "Zacuscă de vinete": {"stock": 35, "unit": "borcan 500g", "images": [
            "https://images.unsplash.com/photo-1636551599784-dca2adc1cbaa?w=800&q=80"
        ]},
        "Miere de salcâm": {"stock": 50, "unit": "borcan 500g", "images": [
            "https://images.unsplash.com/photo-1587049352846-4a222e784c38?w=800&q=80"
        ]},
        "Polen de albine": {"stock": 20, "unit": "borcan 250g", "images": [
            "https://images.unsplash.com/photo-1568526381923-caf3fd520382?w=800&q=80"
        ]},
        "Țuică de prune": {"stock": 30, "unit": "sticlă 0.7L", "images": [
            "https://images.unsplash.com/photo-1608885898953-bcc1fd7e01f0?w=800&q=80"
        ]},
        "Vin roșu de casă": {"stock": 40, "unit": "sticlă 0.75L", "images": [
            "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=800&q=80"
        ]}
    }
    
    # Get category mappings
    category_mapping = {
        "Brânză de vacă proaspătă": "Brânzeturi",
        "Telemea de oaie": "Brânzeturi",
        "Lapte proaspăt de fermă": "Lapte și Smântână",
        "Smântână 30% grăsime": "Lapte și Smântână",
        "Cârnați de casă afumați": "Mezeluri Tradiționale",
        "Slănină afumată": "Mezeluri Tradiționale",
        "Roșii de grădină": "Legume de Sezon",
        "Cartofi noi": "Legume de Sezon",
        "Mere ionatan": "Fructe de Sezon",
        "Prune pentru magiun": "Fructe de Sezon",
        "Pâine de casă cu maia": "Produse de Panificație",
        "Cozonac cu nucă": "Produse de Panificație",
        "Dulceață de caise": "Conserve și Dulcețuri",
        "Zacuscă de vinete": "Conserve și Dulcețuri",
        "Miere de salcâm": "Miere și Produse Apicole",
        "Polen de albine": "Miere și Produse Apicole",
        "Țuică de prune": "Băuturi Tradiționale",
        "Vin roșu de casă": "Băuturi Tradiționale"
    }
    
    # Get categories from database
    categories = {}
    for cat in db.categories.find():
        categories[cat['name']] = cat['_id']
    
    # Get all products
    products = list(db.products.find())
    print(f"Found {len(products)} products to fix")
    
    fixed_count = 0
    for product in products:
        print(f"\nProcessing: {product['name']}")
        
        # Build update document with all necessary transformations
        update = {
            # Generate slug from name
            'slug': slugify(product['name']),
            
            # Rename fields to match Product model
            'is_available': product.get('active', True),
            'stock_quantity': seed_data.get(product['name'], {}).get('stock', product.get('stock', 0)),
            
            # Convert image string to images array
            'images': seed_data.get(product['name'], {}).get('images', []),
            
            # Add missing fields
            'unit': seed_data.get(product['name'], {}).get('unit', 'bucată'),
            'updated_at': datetime.utcnow(),
            'views': 0,
            'sales': 0,
            
            # Fix timestamps
            'created_at': product.get('createdAt', datetime.utcnow())
        }
        
        # Add category_id if we have a mapping
        category_name = category_mapping.get(product['name'])
        if category_name and category_name in categories:
            update['category_id'] = categories[category_name]
            print(f"  - Assigning category: {category_name}")
        
        # Remove old fields
        unset = {
            'active': '',
            'stock': '',
            'image': '',
            'createdAt': '',
            'category': ''  # Remove if exists
        }
        
        # Update product
        result = db.products.update_one(
            {'_id': product['_id']},
            {
                '$set': update,
                '$unset': unset
            }
        )
        
        if result.modified_count > 0:
            fixed_count += 1
            print(f"  ✓ Fixed successfully")
            print(f"    - Stock: {update['stock_quantity']} {update['unit']}")
            print(f"    - Images: {len(update['images'])} added")
        else:
            print(f"  ✗ No changes made")
    
    print(f"\n{'='*50}")
    print(f"Fixed {fixed_count} out of {len(products)} products")
    
    # Verify the fix
    print("\nVerifying fix...")
    sample_product = db.products.find_one()
    if sample_product:
        print("\nSample product after fix:")
        for key in ['name', 'slug', 'is_available', 'stock_quantity', 'unit', 'category_id']:
            print(f"  {key}: {sample_product.get(key)}")
        print(f"  images: {len(sample_product.get('images', []))} items")

if __name__ == '__main__':
    fix_products()