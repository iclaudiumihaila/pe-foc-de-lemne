#!/usr/bin/env python3
"""Seed categories for Pe Foc de Lemne store"""

from pymongo import MongoClient
from app.config import Config
from datetime import datetime
from bson import ObjectId

def seed_categories():
    """Seed initial categories for the firewood store"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    # Clear existing categories
    db.categories.delete_many({})
    print("Cleared existing categories")
    
    # Define categories for local Romanian products
    categories = [
        {
            "_id": ObjectId(),
            "name": "Lactate",
            "slug": "lactate",
            "description": "Produse lactate proaspete de la producători locali",
            "parent_id": None,
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Carne și Mezeluri",
            "slug": "carne-si-mezeluri",
            "description": "Carne proaspătă și mezeluri tradiționale românești",
            "parent_id": None,
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Legume și Fructe",
            "slug": "legume-si-fructe",
            "description": "Legume și fructe proaspete din grădinile locale",
            "parent_id": None,
            "order": 3,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Produse de Panificație",
            "slug": "produse-de-panificatie",
            "description": "Pâine, cozonaci și alte produse de brutărie artizanale",
            "parent_id": None,
            "order": 4,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Conserve și Dulcețuri",
            "slug": "conserve-si-dulceturi",
            "description": "Conserve, dulcețuri și murături făcute în casă",
            "parent_id": None,
            "order": 5,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Miere și Produse Apicole",
            "slug": "miere-si-produse-apicole",
            "description": "Miere naturală și produse apicole de la stupinele locale",
            "parent_id": None,
            "order": 6,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Băuturi Tradiționale",
            "slug": "bauturi-traditionale",
            "description": "Țuică, vin și alte băuturi tradiționale românești",
            "parent_id": None,
            "order": 7,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Store parent category IDs for subcategories
    parent_ids = {}
    
    # Insert main categories
    for category in categories:
        result = db.categories.insert_one(category)
        parent_ids[category['name']] = category['_id']
        print(f"Created category: {category['name']}")
    
    # Define subcategories for local products
    subcategories = [
        # Lactate subcategories
        {
            "_id": ObjectId(),
            "name": "Brânzeturi",
            "slug": "branzeturi",
            "description": "Brânză de vacă, telemea, cașcaval și alte brânzeturi tradiționale",
            "parent_id": parent_ids["Lactate"],
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Lapte și Smântână",
            "slug": "lapte-si-smantana",
            "description": "Lapte proaspăt și smântână de la ferme locale",
            "parent_id": parent_ids["Lactate"],
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Carne și Mezeluri subcategories
        {
            "_id": ObjectId(),
            "name": "Carne Proaspătă",
            "slug": "carne-proaspata",
            "description": "Carne de porc, vită și pui de la crescători locali",
            "parent_id": parent_ids["Carne și Mezeluri"],
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Mezeluri Tradiționale",
            "slug": "mezeluri-traditionale",
            "description": "Cârnați, slănină, șuncă și alte specialități afumate",
            "parent_id": parent_ids["Carne și Mezeluri"],
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Legume și Fructe subcategories
        {
            "_id": ObjectId(),
            "name": "Legume de Sezon",
            "slug": "legume-de-sezon",
            "description": "Legume proaspete cultivate local",
            "parent_id": parent_ids["Legume și Fructe"],
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Fructe de Sezon",
            "slug": "fructe-de-sezon",
            "description": "Fructe proaspete din livezile locale",
            "parent_id": parent_ids["Legume și Fructe"],
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert subcategories
    for subcategory in subcategories:
        db.categories.insert_one(subcategory)
        print(f"  Created subcategory: {subcategory['name']}")
    
    print(f"\nTotal categories created: {len(categories) + len(subcategories)}")
    
    # Create indexes
    db.categories.create_index("slug", unique=True)
    db.categories.create_index("parent_id")
    db.categories.create_index([("parent_id", 1), ("order", 1)])
    print("Created indexes for categories")

if __name__ == '__main__':
    seed_categories()
    print("\nCategories seeded successfully!")