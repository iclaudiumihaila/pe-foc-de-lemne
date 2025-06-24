#!/usr/bin/env python3
"""Check MongoDB data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_mongodb, get_database, Collections
from app.config import Config
from bson import ObjectId

def check_data():
    """Check what data exists in MongoDB"""
    try:
        # Initialize MongoDB connection
        print("Connecting to MongoDB...")
        client, db = init_mongodb(Config)
        print(f"✓ Connected to database: {Config.MONGODB_DB_NAME}")
        
        # Check categories
        categories_collection = db[Collections.CATEGORIES]
        categories = list(categories_collection.find())
        print(f"\nCategories ({len(categories)}):")
        for cat in categories:
            print(f"  - {cat.get('name')} (active: {cat.get('active', False)})")
        
        # Check products
        products_collection = db[Collections.PRODUCTS]
        products = list(products_collection.find())
        print(f"\nProducts ({len(products)}):")
        for prod in products:
            print(f"  - {prod.get('name')} (price: {prod.get('price')}, active: {prod.get('active', False)}, stock: {prod.get('stock')})")
        
        # Check for 'active' field
        active_products = list(products_collection.find({"active": True}))
        print(f"\nActive products: {len(active_products)}")
        
        # Check product structure
        if products:
            print(f"\nSample product structure:")
            sample = products[0]
            for key, value in sample.items():
                print(f"  {key}: {value} ({type(value).__name__})")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data()