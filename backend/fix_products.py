#!/usr/bin/env python3
"""Fix product data to match the model schema"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_mongodb, get_database, Collections
from app.config import Config
from datetime import datetime

def fix_products():
    """Update products to match the schema"""
    try:
        # Initialize MongoDB connection
        print("Connecting to MongoDB...")
        client, db = init_mongodb(Config)
        print(f"✓ Connected to database: {Config.MONGODB_DB_NAME}")
        
        # Get products collection
        products_collection = db[Collections.PRODUCTS]
        
        # Update all products
        print("\nUpdating products...")
        
        # First, let's see what we have
        products = list(products_collection.find())
        print(f"Found {len(products)} products")
        
        # Update each product
        for product in products:
            updates = {}
            
            # Rename 'active' to 'is_available'
            if 'active' in product and 'is_available' not in product:
                updates['is_available'] = product['active']
                updates['$unset'] = {'active': 1}
            
            # Rename 'stock' to 'stock_quantity'
            if 'stock' in product and 'stock_quantity' not in product:
                updates['stock_quantity'] = product['stock']
                if '$unset' not in updates:
                    updates['$unset'] = {}
                updates['$unset']['stock'] = 1
            
            # Add missing fields
            if 'slug' not in product:
                # Generate slug from name
                slug = product['name'].lower()
                slug = slug.replace(' ', '-')
                slug = slug.replace('ș', 's').replace('ț', 't').replace('ă', 'a').replace('â', 'a').replace('î', 'i')
                updates['slug'] = slug
            
            if 'created_at' not in product:
                updates['created_at'] = datetime.utcnow()
            
            if 'updated_at' not in product:
                updates['updated_at'] = datetime.utcnow()
            
            if 'preparation_time_hours' not in product:
                updates['preparation_time_hours'] = 24
            
            if 'weight_grams' not in product:
                # Set some reasonable defaults based on unit
                unit = product.get('unit', '')
                if 'kg' in unit:
                    updates['weight_grams'] = 1000
                elif 'g' in unit:
                    updates['weight_grams'] = 500
                elif 'litru' in unit:
                    updates['weight_grams'] = 1000
                else:
                    updates['weight_grams'] = 500
            
            # Rename 'image_url' to 'images' array
            if 'image_url' in product and 'images' not in product:
                updates['images'] = [product['image_url']]
                if '$unset' not in updates:
                    updates['$unset'] = {}
                updates['$unset']['image_url'] = 1
            
            # Apply updates
            if updates:
                # Separate $unset from $set operations
                unset_ops = updates.pop('$unset', None)
                
                if updates:
                    products_collection.update_one(
                        {'_id': product['_id']},
                        {'$set': updates}
                    )
                
                if unset_ops:
                    products_collection.update_one(
                        {'_id': product['_id']},
                        {'$unset': unset_ops}
                    )
                
                print(f"  ✓ Updated {product['name']}")
        
        # Verify the updates
        print("\nVerifying updates...")
        updated_products = list(products_collection.find())
        sample = updated_products[0] if updated_products else None
        
        if sample:
            print(f"\nSample product structure after update:")
            for key, value in sample.items():
                if key != '_id' and key != 'category_id':
                    print(f"  {key}: {value}")
        
        # Count available products
        available_count = products_collection.count_documents({
            'is_available': True,
            'stock_quantity': {'$gt': 0}
        })
        print(f"\nAvailable products: {available_count}")
        
        print("\n✓ Products fixed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    fix_products()