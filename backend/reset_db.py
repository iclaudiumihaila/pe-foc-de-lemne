#!/usr/bin/env python3
"""Reset database - drop all collections and recreate with seed data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_mongodb, get_database, Collections
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)

def reset_database():
    """Drop all collections and recreate with seed data"""
    try:
        # Initialize MongoDB connection
        print("Connecting to MongoDB...")
        client, db = init_mongodb(Config)
        print(f"✓ Connected to MongoDB: {Config.MONGODB_DB_NAME}")
        
        # Drop all collections
        print("\nDropping all collections...")
        collections = [Collections.USERS, Collections.PRODUCTS, Collections.CATEGORIES, 
                      Collections.ORDERS, Collections.CART_SESSIONS]
        
        for collection_name in collections:
            try:
                db.drop_collection(collection_name)
                print(f"  ✓ Dropped {collection_name}")
            except Exception as e:
                print(f"  ⚠ Could not drop {collection_name}: {e}")
        
        print("\n✓ Database reset complete!")
        print("Run test_db_connection.py to recreate indexes and seed data.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    reset_database()