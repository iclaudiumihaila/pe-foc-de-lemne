#!/usr/bin/env python3
"""Test database connection and seed initial data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_mongodb, get_database, Collections, create_indexes
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)

def test_and_seed():
    """Test database connection and seed initial data"""
    try:
        # Initialize MongoDB connection
        print("Testing MongoDB connection...")
        client, db = init_mongodb(Config)
        print(f"✓ Connected to MongoDB: {Config.MONGODB_DB_NAME}")
        
        # Create indexes
        print("\nCreating database indexes...")
        index_results = create_indexes()
        for collection, result in index_results.items():
            print(f"  ✓ {collection}: {result}")
        
        # Check for existing categories
        categories_collection = db[Collections.CATEGORIES]
        existing_categories = categories_collection.count_documents({})
        print(f"\nExisting categories: {existing_categories}")
        
        if existing_categories == 0:
            print("Seeding initial categories...")
            categories = [
                {
                    "name": "Legume",
                    "description": "Legume proaspete de sezon",
                    "display_order": 1,
                    "active": True
                },
                {
                    "name": "Fructe", 
                    "description": "Fructe proaspete de la producători locali",
                    "display_order": 2,
                    "active": True
                },
                {
                    "name": "Lactate",
                    "description": "Produse lactate tradiționale",
                    "display_order": 3,
                    "active": True
                },
                {
                    "name": "Produse apicole",
                    "description": "Miere și produse apicole naturale",
                    "display_order": 4,
                    "active": True
                },
                {
                    "name": "Ouă",
                    "description": "Ouă proaspete de la găini crescute în aer liber",
                    "display_order": 5,
                    "active": True
                },
                {
                    "name": "Conserve",
                    "description": "Conserve și murături de casă",
                    "display_order": 6,
                    "active": True
                }
            ]
            
            result = categories_collection.insert_many(categories)
            print(f"  ✓ Inserted {len(result.inserted_ids)} categories")
        
        # Check for existing products
        products_collection = db[Collections.PRODUCTS]
        existing_products = products_collection.count_documents({})
        print(f"\nExisting products: {existing_products}")
        
        if existing_products == 0:
            print("Seeding initial products...")
            
            # Get category IDs
            legume_id = categories_collection.find_one({"name": "Legume"})["_id"]
            fructe_id = categories_collection.find_one({"name": "Fructe"})["_id"]
            lactate_id = categories_collection.find_one({"name": "Lactate"})["_id"]
            apicole_id = categories_collection.find_one({"name": "Produse apicole"})["_id"]
            oua_id = categories_collection.find_one({"name": "Ouă"})["_id"]
            
            products = [
                {
                    "name": "Roșii ecologice",
                    "description": "Roșii crescute natural, fără pesticide",
                    "price": 8.50,
                    "unit": "kg",
                    "category_id": legume_id,
                    "stock": 50,
                    "featured": True,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400",
                    "producer": "Ferma Eco Verde",
                    "organic": True
                },
                {
                    "name": "Miere de salcâm",
                    "description": "Miere pură de salcâm din apiarii locale",
                    "price": 25.00,
                    "unit": "borcan 500g",
                    "category_id": apicole_id,
                    "stock": 30,
                    "featured": True,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400",
                    "producer": "Apicola Muntenia",
                    "organic": True
                },
                {
                    "name": "Brânză de țară",
                    "description": "Brânză tradițională din lapte de vacă",
                    "price": 15.00,
                    "unit": "kg",
                    "category_id": lactate_id,
                    "stock": 25,
                    "featured": True,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400",
                    "producer": "Ferma Tradițională",
                    "organic": False
                },
                {
                    "name": "Ouă de țară",
                    "description": "Ouă proaspete de la găini crescute în curte",
                    "price": 12.00,
                    "unit": "10 bucăți",
                    "category_id": oua_id,
                    "stock": 40,
                    "featured": True,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400",
                    "producer": "Gospodăria Țărănească",
                    "organic": True
                },
                {
                    "name": "Mere ionatan",
                    "description": "Mere crocante și dulci din livada proprie",
                    "price": 4.50,
                    "unit": "kg",
                    "category_id": fructe_id,
                    "stock": 60,
                    "featured": False,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400",
                    "producer": "Livada de Mere",
                    "organic": True
                },
                {
                    "name": "Castraveți murați",
                    "description": "Castraveți murați în saramură, rețetă tradițională",
                    "price": 12.00,
                    "unit": "borcan 700g",
                    "category_id": categories_collection.find_one({"name": "Conserve"})["_id"],
                    "stock": 35,
                    "featured": False,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1633321702518-ee8f24d8b697?w=400",
                    "producer": "Cămara Bunicii",
                    "organic": True
                },
                {
                    "name": "Lapte proaspăt",
                    "description": "Lapte proaspăt de vacă, pasteurizat",
                    "price": 6.00,
                    "unit": "litru",
                    "category_id": lactate_id,
                    "stock": 20,
                    "featured": False,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400",
                    "producer": "Ferma Lactate Fresh",
                    "organic": False
                },
                {
                    "name": "Cartofi noi",
                    "description": "Cartofi noi, cultivați fără tratamente chimice",
                    "price": 3.50,
                    "unit": "kg",
                    "category_id": legume_id,
                    "stock": 80,
                    "featured": False,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400",
                    "producer": "Gospodăria Ecologică",
                    "organic": True
                }
            ]
            
            result = products_collection.insert_many(products)
            print(f"  ✓ Inserted {len(result.inserted_ids)} products")
        
        # Show collection counts
        print("\nDatabase status:")
        print(f"  Categories: {categories_collection.count_documents({})}")
        print(f"  Products: {products_collection.count_documents({})}")
        print(f"  Orders: {db[Collections.ORDERS].count_documents({})}")
        print(f"  Users: {db[Collections.USERS].count_documents({})}")
        print(f"  Cart Sessions: {db[Collections.CART_SESSIONS].count_documents({})}")
        
        print("\n✓ Database setup complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_and_seed()