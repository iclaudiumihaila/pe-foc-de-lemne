#!/usr/bin/env python3
"""Setup admin user and seed products"""

import requests
import json
from pymongo import MongoClient
from app.config import Config
import bcrypt
from datetime import datetime
from bson import ObjectId

def create_admin_user():
    """Create admin user directly in database"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    # Check if admin already exists
    existing_admin = db.users.find_one({"role": "admin"})
    if existing_admin:
        print("Admin user already exists")
        return True
    
    # Create admin user
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw("admin123".encode('utf-8'), salt)
    password_hash = hashed.decode('utf-8')
    
    admin_user = {
        "_id": ObjectId(),
        "name": "Admin",
        "phone_number": "+40700000001",  # Romanian phone format
        "password_hash": password_hash,
        "role": "admin",
        "is_active": True,
        "is_verified": True,  # Admin doesn't need SMS verification
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(admin_user)
    print("✓ Created admin user")
    print(f"  Phone: {admin_user['phone_number']}")
    print(f"  Password: admin123")
    return True

def login_admin():
    """Login as admin and get token"""
    response = requests.post('http://localhost:8000/api/auth/admin/login', 
        json={
            'username': '+40700000001',
            'password': 'admin123'
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Admin logged in successfully")
        # The token is nested in data.tokens.access_token
        if 'data' in data and 'tokens' in data['data']:
            return data['data']['tokens']['access_token']
        elif 'tokens' in data:
            return data['tokens']['access_token']
        else:
            print(f"Unexpected response format: {data}")
            return None
    else:
        print(f"✗ Failed to login: {response.status_code} - {response.text}")
        return None

def seed_products(auth_token):
    """Seed products using the API"""
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    # Get category IDs
    categories = {}
    for cat in db.categories.find():
        categories[cat['name']] = str(cat['_id'])
    
    print(f"\nFound {len(categories)} categories")
    
    # Products data with Unsplash image URLs
    products = [
        # Lactate - Brânzeturi
        {
            "name": "Brânză de vacă proaspătă",
            "description": "Brânză de vacă tradițională, făcută din lapte proaspăt de la ferma locală. Textură cremoasă și gust delicat.",
            "category_id": categories.get("Brânzeturi"),
            "price": 25.99,
            "unit": "kg",
            "stock_quantity": 50,
            "is_available": True,
            "producer": "Ferma Familia Popescu",
            "images": [
                "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800&q=80",
                "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800&q=80"
            ]
        },
        {
            "name": "Telemea de oaie",
            "description": "Telemea tradițională românească din lapte de oaie, maturată în saramură. Gustul autentic al munților.",
            "category_id": categories.get("Brânzeturi"),
            "price": 32.50,
            "unit": "kg",
            "stock_quantity": 30,
            "is_available": True,
            "producer": "Stâna din Deal",
            "images": [
                "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=800&q=80"
            ]
        },
        
        # Lactate - Lapte și Smântână
        {
            "name": "Lapte proaspăt de fermă",
            "description": "Lapte integral, proaspăt muls, de la vaci hrănite natural. Bogat în nutrienți și vitamine.",
            "category_id": categories.get("Lapte și Smântână"),
            "price": 8.00,
            "unit": "litru",
            "stock_quantity": 100,
            "is_available": True,
            "producer": "Ferma Bio Verde",
            "images": [
                "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800&q=80"
            ]
        },
        {
            "name": "Smântână 30% grăsime",
            "description": "Smântână groasă și cremoasă, perfectă pentru mâncărurile tradiționale românești.",
            "category_id": categories.get("Lapte și Smântână"),
            "price": 12.00,
            "unit": "borcan 400g",
            "stock_quantity": 40,
            "is_available": True,
            "producer": "Lactate Țărănești",
            "images": [
                "https://images.unsplash.com/photo-1555792903-8b6d850ba396?w=800&q=80"
            ]
        },
        
        # Carne și Mezeluri - Mezeluri Tradiționale
        {
            "name": "Cârnați de casă afumați",
            "description": "Cârnați tradiționali românești, afumați natural cu lemn de fag. Condimentați cu usturoi și piper.",
            "category_id": categories.get("Mezeluri Tradiționale"),
            "price": 45.00,
            "unit": "kg",
            "stock_quantity": 25,
            "is_available": True,
            "producer": "Măcelăria Tradițională",
            "images": [
                "https://images.unsplash.com/photo-1624362770755-8328d5f5a281?w=800&q=80"
            ]
        },
        {
            "name": "Slănină afumată",
            "description": "Slănină de porc afumată tradițional, condimentată cu boia și usturoi. Ideală pentru gustări.",
            "category_id": categories.get("Mezeluri Tradiționale"),
            "price": 35.00,
            "unit": "kg",
            "stock_quantity": 20,
            "is_available": True,
            "producer": "Afumătoria din Sat",
            "images": [
                "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=800&q=80"
            ]
        },
        
        # Legume și Fructe - Legume de Sezon
        {
            "name": "Roșii de grădină",
            "description": "Roșii coapte natural, cultivate fără pesticide. Gust autentic de roșie românească.",
            "category_id": categories.get("Legume de Sezon"),
            "price": 8.50,
            "unit": "kg",
            "stock_quantity": 60,
            "is_available": True,
            "producer": "Grădina Bunicii",
            "images": [
                "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=800&q=80"
            ]
        },
        {
            "name": "Cartofi noi",
            "description": "Cartofi proaspeți, săpați direct din grădină. Ideali pentru orice fel de mâncare.",
            "category_id": categories.get("Legume de Sezon"),
            "price": 4.50,
            "unit": "kg",
            "stock_quantity": 100,
            "is_available": True,
            "producer": "Ferma Ecologică",
            "images": [
                "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=800&q=80"
            ]
        },
        
        # Legume și Fructe - Fructe de Sezon
        {
            "name": "Mere ionatan",
            "description": "Mere ionatan din livada proprie, dulci și aromate. Perfecte pentru desert sau plăcinte.",
            "category_id": categories.get("Fructe de Sezon"),
            "price": 5.00,
            "unit": "kg",
            "stock_quantity": 80,
            "is_available": True,
            "producer": "Livada cu Mere",
            "images": [
                "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=800&q=80"
            ]
        },
        {
            "name": "Prune pentru magiun",
            "description": "Prune românești, ideale pentru prepararea magiunului tradițional sau pentru consum proaspăt.",
            "category_id": categories.get("Fructe de Sezon"),
            "price": 6.00,
            "unit": "kg",
            "stock_quantity": 70,
            "is_available": True,
            "producer": "Pomicultorul Local",
            "images": [
                "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=800&q=80"
            ]
        },
        
        # Produse de Panificație
        {
            "name": "Pâine de casă cu maia",
            "description": "Pâine tradițională făcută cu maia naturală, coaptă în cuptor cu lemne. Coajă crocantă și miez pufos.",
            "category_id": categories.get("Produse de Panificație"),
            "price": 12.00,
            "unit": "bucată",
            "stock_quantity": 30,
            "is_available": True,
            "producer": "Brutăria Satului",
            "images": [
                "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=800&q=80"
            ]
        },
        {
            "name": "Cozonac cu nucă",
            "description": "Cozonac pufos cu umplutură generoasă de nucă, făcut după rețeta bunicii.",
            "category_id": categories.get("Produse de Panificație"),
            "price": 35.00,
            "unit": "bucată",
            "stock_quantity": 15,
            "is_available": True,
            "producer": "Cofetăria Tradițională",
            "images": [
                "https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=800&q=80"
            ]
        },
        
        # Conserve și Dulcețuri
        {
            "name": "Dulceață de caise",
            "description": "Dulceață de caise făcută în casă, cu bucăți mari de fruct și zahăr redus. Rețetă tradițională.",
            "category_id": categories.get("Conserve și Dulcețuri"),
            "price": 18.00,
            "unit": "borcan 400g",
            "stock_quantity": 40,
            "is_available": True,
            "producer": "Dulcețuri de Acasă",
            "images": [
                "https://images.unsplash.com/photo-1597045415647-5e0a9c3ca63f?w=800&q=80"
            ]
        },
        {
            "name": "Zacuscă de vinete",
            "description": "Zacuscă tradițională de vinete, preparată după rețeta moldovenească autentică.",
            "category_id": categories.get("Conserve și Dulcețuri"),
            "price": 22.00,
            "unit": "borcan 500g",
            "stock_quantity": 35,
            "is_available": True,
            "producer": "Conserve Tradiționale",
            "images": [
                "https://images.unsplash.com/photo-1636551599784-dca2adc1cbaa?w=800&q=80"
            ]
        },
        
        # Miere și Produse Apicole
        {
            "name": "Miere de salcâm",
            "description": "Miere pură de salcâm, recoltată din stupinele proprii. Gust delicat și aromă florală.",
            "category_id": categories.get("Miere și Produse Apicole"),
            "price": 40.00,
            "unit": "borcan 500g",
            "stock_quantity": 50,
            "is_available": True,
            "producer": "Stupina din Deal",
            "images": [
                "https://images.unsplash.com/photo-1587049352846-4a222e784c38?w=800&q=80"
            ]
        },
        {
            "name": "Polen de albine",
            "description": "Polen natural, bogat în vitamine și minerale. Supliment alimentar de excepție.",
            "category_id": categories.get("Miere și Produse Apicole"),
            "price": 55.00,
            "unit": "borcan 250g",
            "stock_quantity": 20,
            "is_available": True,
            "producer": "Apicola Naturală",
            "images": [
                "https://images.unsplash.com/photo-1568526381923-caf3fd520382?w=800&q=80"
            ]
        },
        
        # Băuturi Tradiționale
        {
            "name": "Țuică de prune",
            "description": "Țuică tradițională românească, distilată de două ori. Tărie 50 grade.",
            "category_id": categories.get("Băuturi Tradiționale"),
            "price": 60.00,
            "unit": "sticlă 0.7L",
            "stock_quantity": 30,
            "is_available": True,
            "producer": "Distileria Tradițională",
            "images": [
                "https://images.unsplash.com/photo-1608885898953-bcc1fd7e01f0?w=800&q=80"
            ]
        },
        {
            "name": "Vin roșu de casă",
            "description": "Vin roșu sec, produs din struguri selectați manual. Maturat în butoaie de stejar.",
            "category_id": categories.get("Băuturi Tradiționale"),
            "price": 45.00,
            "unit": "sticlă 0.75L",
            "stock_quantity": 40,
            "is_available": True,
            "producer": "Crama Familiei",
            "images": [
                "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=800&q=80"
            ]
        }
    ]
    
    # Create products via API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }
    
    created_count = 0
    for product in products:
        if not product.get('category_id'):
            print(f"✗ Skipping {product['name']} - no category found")
            continue
            
        response = requests.post(
            'http://localhost:8000/api/admin/products',
            json=product,
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"✓ Created product: {product['name']}")
            created_count += 1
        else:
            print(f"✗ Failed to create {product['name']}: {response.status_code} - {response.text}")
    
    print(f"\nTotal products created: {created_count}/{len(products)}")

if __name__ == '__main__':
    print("=== Setting up Admin and Seeding Products ===\n")
    
    # Create admin user
    if not create_admin_user():
        print("Failed to create admin user")
        exit(1)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("Failed to login as admin")
        exit(1)
    
    # Seed products
    seed_products(token)
    print("\nSetup completed!")