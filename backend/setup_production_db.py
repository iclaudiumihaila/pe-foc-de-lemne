#!/usr/bin/env python3
"""
Production database setup script for Pe Foc de Lemne
Creates admin user and ensures indexes are set up
"""

import os
import sys
import bcrypt
from pymongo import MongoClient, ASCENDING, TEXT
from datetime import datetime
import argparse

# Production MongoDB URI
PROD_MONGO_URI = "mongodb://mongo:wHkJtfTKOIDKtkzSxcOIjhCZpbeUPmkF@shuttle.proxy.rlwy.net:58855"
DATABASE_NAME = "pe_foc_de_lemne"

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def create_indexes(db):
    """Create all necessary database indexes"""
    print("Creating database indexes...")
    
    # Users collection
    db.users.create_index("phone_number", unique=True)
    db.users.create_index("role")
    db.users.create_index("created_at")
    print("✓ Users indexes created")
    
    # Products collection
    db.products.create_index("slug", unique=True)
    db.products.create_index("category_id")
    db.products.create_index("is_available")
    db.products.create_index([("name", TEXT), ("description", TEXT)])
    db.products.create_index("price")
    db.products.create_index("created_at")
    print("✓ Products indexes created")
    
    # Categories collection
    db.categories.create_index("slug", unique=True)
    db.categories.create_index("display_order")
    db.categories.create_index("is_active")
    print("✓ Categories indexes created")
    
    # Orders collection
    db.orders.create_index("order_number", unique=True)
    db.orders.create_index("customer_phone")
    db.orders.create_index("status")
    db.orders.create_index("created_at")
    print("✓ Orders indexes created")
    
    # Cart sessions collection
    db.cart_sessions.create_index("session_id", unique=True)
    db.cart_sessions.create_index("created_at", expireAfterSeconds=86400)  # 24 hours
    print("✓ Cart sessions indexes created")
    
    # Customer phones collection
    db.customer_phones.create_index("phone_number", unique=True)
    print("✓ Customer phones indexes created")

def create_admin_user(db, phone_number, password, name="Administrator"):
    """Create an admin user if it doesn't exist"""
    print(f"\nCreating admin user with phone: {phone_number}")
    
    # Check if user already exists
    existing_user = db.users.find_one({"phone_number": phone_number})
    if existing_user:
        print(f"✗ User with phone {phone_number} already exists!")
        # Update to admin if not already
        if existing_user.get('role') != 'admin':
            db.users.update_one(
                {"phone_number": phone_number},
                {"$set": {"role": "admin", "updated_at": datetime.utcnow()}}
            )
            print("✓ Updated existing user to admin role")
        return
    
    # Create new admin user
    admin_user = {
        "phone_number": phone_number,
        "name": name,
        "role": "admin",
        "password_hash": hash_password(password),
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.users.insert_one(admin_user)
    print(f"✓ Admin user created with ID: {result.inserted_id}")

def create_initial_categories(db):
    """Create initial product categories"""
    print("\nCreating initial categories...")
    
    categories = [
        {"name": "Lactate", "slug": "lactate", "display_order": 1},
        {"name": "Carne și Mezeluri", "slug": "carne-mezeluri", "display_order": 2},
        {"name": "Legume și Fructe", "slug": "legume-fructe", "display_order": 3},
        {"name": "Produse de Panificație", "slug": "panificatie", "display_order": 4},
        {"name": "Conserve și Dulcețuri", "slug": "conserve-dulceturi", "display_order": 5},
        {"name": "Băuturi", "slug": "bauturi", "display_order": 6},
        {"name": "Alte Produse", "slug": "alte-produse", "display_order": 7}
    ]
    
    for cat in categories:
        existing = db.categories.find_one({"slug": cat["slug"]})
        if not existing:
            cat.update({
                "description": f"Categoria {cat['name']}",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            db.categories.insert_one(cat)
            print(f"✓ Created category: {cat['name']}")
        else:
            print(f"- Category already exists: {cat['name']}")

def main():
    parser = argparse.ArgumentParser(description='Set up production database')
    parser.add_argument('--admin-phone', required=True, help='Admin phone number (e.g., +40712345678)')
    parser.add_argument('--admin-password', required=True, help='Admin password')
    parser.add_argument('--admin-name', default='Administrator', help='Admin name')
    parser.add_argument('--skip-categories', action='store_true', help='Skip creating categories')
    
    args = parser.parse_args()
    
    print("Connecting to production MongoDB...")
    print(f"URI: {PROD_MONGO_URI[:30]}...")  # Print partial URI for security
    
    try:
        # Connect to MongoDB
        client = MongoClient(PROD_MONGO_URI)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.server_info()
        print("✓ Successfully connected to MongoDB")
        
        # Create indexes
        create_indexes(db)
        
        # Create admin user
        create_admin_user(db, args.admin_phone, args.admin_password, args.admin_name)
        
        # Create categories unless skipped
        if not args.skip_categories:
            create_initial_categories(db)
        
        print("\n✅ Production database setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()