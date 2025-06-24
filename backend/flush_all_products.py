#!/usr/bin/env python3
"""Delete all products from the database"""

from app import create_app
from app.config import DevelopmentConfig
from app.database import get_database

# Initialize the app
app = create_app(DevelopmentConfig)
with app.app_context():
    db = get_database()
    
    # Count products before deletion
    count_before = db.products.count_documents({})
    print(f"Found {count_before} products in database")
    
    if count_before > 0:
        # Delete all products
        result = db.products.delete_many({})
        print(f"Deleted {result.deleted_count} products")
    else:
        print("No products to delete")
    
    # Verify deletion
    count_after = db.products.count_documents({})
    print(f"Products remaining: {count_after}")
    
    print("\n✅ All products have been flushed from the database")