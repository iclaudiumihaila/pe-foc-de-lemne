#!/usr/bin/env python3
"""
Seed test data for Pe Foc de Lemne application
"""

import os
import sys
from datetime import datetime
from bson import ObjectId
import bcrypt

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database, init_mongodb
from app.config import DevelopmentConfig
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

def clear_collections():
    """Clear existing data"""
    db = get_database()
    print("Clearing existing data...")
    db.categories.delete_many({})
    db.products.delete_many({})
    db.users.delete_many({})
    print("Collections cleared.")

def seed_categories():
    """Create test categories"""
    db = get_database()
    categories = [
        {
            "_id": ObjectId(),
            "name": "Lactate",
            "description": "Produse lactate proaspete de la ferma",
            "display_order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Carne și Mezeluri",
            "description": "Carne proaspătă și mezeluri tradiționale",
            "display_order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Legume și Fructe",
            "description": "Legume și fructe de sezon",
            "display_order": 3,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Produse de Panificație",
            "description": "Pâine și produse de patiserie artizanale",
            "display_order": 4,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Conserve și Dulcețuri",
            "description": "Conserve și dulcețuri făcute în casă",
            "display_order": 5,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = db.categories.insert_many(categories)
    print(f"Created {len(result.inserted_ids)} categories")
    return {cat["name"]: cat["_id"] for cat in categories}

def seed_products(category_ids):
    """Create test products"""
    db = get_database()
    products = [
        # Lactate
        {
            "_id": ObjectId(),
            "name": "Brânză de vacă proaspătă",
            "description": "Brânză de vacă proaspătă, făcută tradițional din lapte integral de la vaci hrănite natural.",
            "price": 25.50,
            "category_id": category_ids["Lactate"],
            "images": ["branza-vaca.jpg"],
            "stock_quantity": 50,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Lapte proaspăt de fermă",
            "description": "Lapte proaspăt, nepasteurizat, direct de la fermă. Bogat în nutrienți naturali.",
            "price": 8.00,
            "category_id": category_ids["Lactate"],
            "images": ["lapte-ferma.jpg"],
            "stock_quantity": 100,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Smântână 30% grăsime",
            "description": "Smântână groasă și cremoasă, perfectă pentru mâncăruri tradiționale românești.",
            "price": 12.00,
            "category_id": category_ids["Lactate"],
            "images": ["smantana.jpg"],
            "stock_quantity": 40,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Carne și Mezeluri
        {
            "_id": ObjectId(),
            "name": "Cârnați de casă afumați",
            "description": "Cârnați tradiționali românești, afumați natural cu lemn de fag. Rețetă de familie.",
            "price": 45.00,
            "category_id": category_ids["Carne și Mezeluri"],
            "images": ["carnati-casa.jpg"],
            "stock_quantity": 30,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Slănină afumată",
            "description": "Slănină de porc afumată tradițional, condimentată cu boia și usturoi.",
            "price": 35.00,
            "category_id": category_ids["Carne și Mezeluri"],
            "images": ["slanina-afumata.jpg"],
            "stock_quantity": 25,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Legume și Fructe
        {
            "_id": ObjectId(),
            "name": "Roșii de grădină",
            "description": "Roșii coapte natural, cultivate fără pesticide. Gust autentic de roșie românească.",
            "price": 8.50,
            "category_id": category_ids["Legume și Fructe"],
            "images": ["rosii-gradina.jpg"],
            "stock_quantity": 80,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Mere ionatan",
            "description": "Mere ionatan din livada proprie, dulci și aromate. Perfecte pentru desert sau plăcinte.",
            "price": 5.00,
            "category_id": category_ids["Legume și Fructe"],
            "images": ["mere-ionatan.jpg"],
            "stock_quantity": 150,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Produse de Panificație
        {
            "_id": ObjectId(),
            "name": "Pâine de casă cu maia",
            "description": "Pâine tradițională făcută cu maia naturală, coaptă în cuptor cu lemne.",
            "price": 12.00,
            "category_id": category_ids["Produse de Panificație"],
            "images": ["paine-casa.jpg"],
            "stock_quantity": 20,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Cozonac cu nucă",
            "description": "Cozonac pufos cu umplutură generoasă de nucă, făcut după rețeta bunicii.",
            "price": 35.00,
            "category_id": category_ids["Produse de Panificație"],
            "images": ["cozonac-nuca.jpg"],
            "stock_quantity": 15,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Conserve și Dulcețuri
        {
            "_id": ObjectId(),
            "name": "Dulceață de caise",
            "description": "Dulceață de caise făcută în casă, cu bucăți mari de fruct și zahăr redus.",
            "price": 18.00,
            "category_id": category_ids["Conserve și Dulcețuri"],
            "images": ["dulceata-caise.jpg"],
            "stock_quantity": 35,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Zacuscă de vinete",
            "description": "Zacuscă tradițională de vinete, preparată după rețeta moldovenească autentică.",
            "price": 22.00,
            "category_id": category_ids["Conserve și Dulcețuri"],
            "images": ["zacusca-vinete.jpg"],
            "stock_quantity": 45,
            "is_available": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = db.products.insert_many(products)
    print(f"Created {len(result.inserted_ids)} products")

def seed_admin_user():
    """Create admin user"""
    db = get_database()
    
    # Hash password
    password = "admin123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    admin_user = {
        "_id": ObjectId(),
        "phone_number": "+40700000000",
        "name": "Administrator",
        "role": "admin",
        "password_hash": hashed_password.decode('utf-8'),
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(admin_user)
    print(f"Created admin user - Phone: {admin_user['phone_number']}, Password: {password}")

def create_indexes():
    """Create database indexes"""
    db = get_database()
    
    # User indexes
    db.users.create_index("phone_number", unique=True)
    
    # Product indexes
    db.products.create_index("name")
    db.products.create_index("category_id")
    db.products.create_index("active")
    
    # Category indexes
    db.categories.create_index("display_order")
    
    # Order indexes
    db.orders.create_index("order_number", unique=True)
    db.orders.create_index("customer_phone")
    db.orders.create_index("status")
    db.orders.create_index("created_at")
    
    print("Created database indexes")

def main():
    """Main seed function"""
    print("Starting database seeding...")
    
    try:
        # Initialize database connection
        init_mongodb(DevelopmentConfig)
        # Clear existing data
        clear_collections()
        
        # Create indexes
        create_indexes()
        
        # Seed data
        category_ids = seed_categories()
        seed_products(category_ids)
        seed_admin_user()
        
        print("\nDatabase seeding completed successfully!")
        print("\nYou can now:")
        print("1. Browse products at http://localhost:3000")
        print("2. Login as admin with phone: +40700000000, password: admin123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()