#!/usr/bin/env python3
"""
Create products via API
"""
import requests
import json

# Admin token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg1ODM0MWQ5MmVkMzNlOWNiMTQ4YjBlIiwicGhvbmVfbnVtYmVyIjoiKzQwNzAwMDAwMDAwIiwibmFtZSI6IkFkbWluaXN0cmF0b3IiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3NTA2MTEyMjMsImV4cCI6MTc1MDY0MDAyMywiaXNzIjoicGUtZm9jLWRlLWxlbW5lLWFkbWluIiwiYXVkIjoicGUtZm9jLWRlLWxlbW5lLWFkbWluLXBhbmVsIn0.OVGeGrP3G--PzX2PKxxHPKVYHQofdgqhGdcTGhRuR4E"

# API endpoint
API_URL = "http://localhost:8000/api/products/admin/products"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# Category IDs
categories = {
    "Lactate": "6858341d92ed33e9cb148afe",
    "Carne și Mezeluri": "6858341d92ed33e9cb148aff",
    "Legume și Fructe": "6858341d92ed33e9cb148b00",
    "Produse de Panificație": "6858341d92ed33e9cb148b01",
    "Conserve și Dulcețuri": "6858341d92ed33e9cb148b02"
}

# Products to create
products = [
    # Lactate - already created Brânză de vacă
    {
        "name": "Lapte proaspăt de fermă",
        "description": "Lapte proaspăt, nepasteurizat, direct de la fermă. Bogat în nutrienți naturali.",
        "price": 8.00,
        "category_id": categories["Lactate"],
        "images": ["lapte-ferma.jpg"],
        "stock_quantity": 100,
        "weight_grams": 1000,
        "preparation_time_hours": 1
    },
    {
        "name": "Smântână 30% grăsime",
        "description": "Smântână groasă și cremoasă, perfectă pentru mâncăruri tradiționale românești.",
        "price": 12.00,
        "category_id": categories["Lactate"],
        "images": ["smantana.jpg"],
        "stock_quantity": 40,
        "weight_grams": 400,
        "preparation_time_hours": 12
    },
    
    # Carne și Mezeluri
    {
        "name": "Cârnați de casă afumați",
        "description": "Cârnați tradiționali românești, afumați natural cu lemn de fag. Rețetă de familie.",
        "price": 45.00,
        "category_id": categories["Carne și Mezeluri"],
        "images": ["carnati-casa.jpg"],
        "stock_quantity": 30,
        "weight_grams": 1000,
        "preparation_time_hours": 48
    },
    {
        "name": "Slănină afumată",
        "description": "Slănină de porc afumată tradițional, condimentată cu boia și usturoi.",
        "price": 35.00,
        "category_id": categories["Carne și Mezeluri"],
        "images": ["slanina-afumata.jpg"],
        "stock_quantity": 25,
        "weight_grams": 500,
        "preparation_time_hours": 72
    },
    
    # Legume și Fructe
    {
        "name": "Roșii de grădină",
        "description": "Roșii coapte natural, cultivate fără pesticide. Gust autentic de roșie românească.",
        "price": 8.50,
        "category_id": categories["Legume și Fructe"],
        "images": ["rosii-gradina.jpg"],
        "stock_quantity": 80,
        "weight_grams": 1000,
        "preparation_time_hours": 1
    },
    {
        "name": "Mere ionatan",
        "description": "Mere ionatan din livada proprie, dulci și aromate. Perfecte pentru desert sau plăcinte.",
        "price": 5.00,
        "category_id": categories["Legume și Fructe"],
        "images": ["mere-ionatan.jpg"],
        "stock_quantity": 150,
        "weight_grams": 1000,
        "preparation_time_hours": 1
    },
    
    # Produse de Panificație
    {
        "name": "Pâine de casă cu maia",
        "description": "Pâine tradițională făcută cu maia naturală, coaptă în cuptor cu lemne.",
        "price": 12.00,
        "category_id": categories["Produse de Panificație"],
        "images": ["paine-casa.jpg"],
        "stock_quantity": 20,
        "weight_grams": 800,
        "preparation_time_hours": 24
    },
    {
        "name": "Cozonac cu nucă",
        "description": "Cozonac pufos cu umplutură generoasă de nucă, făcut după rețeta bunicii.",
        "price": 35.00,
        "category_id": categories["Produse de Panificație"],
        "images": ["cozonac-nuca.jpg"],
        "stock_quantity": 15,
        "weight_grams": 700,
        "preparation_time_hours": 24
    },
    
    # Conserve și Dulcețuri
    {
        "name": "Dulceață de caise",
        "description": "Dulceață de caise făcută în casă, cu bucăți mari de fruct și zahăr redus.",
        "price": 18.00,
        "category_id": categories["Conserve și Dulcețuri"],
        "images": ["dulceata-caise.jpg"],
        "stock_quantity": 35,
        "weight_grams": 370,
        "preparation_time_hours": 6
    },
    {
        "name": "Zacuscă de vinete",
        "description": "Zacuscă tradițională de vinete, preparată după rețeta moldovenească autentică.",
        "price": 22.00,
        "category_id": categories["Conserve și Dulcețuri"],
        "images": ["zacusca-vinete.jpg"],
        "stock_quantity": 45,
        "weight_grams": 350,
        "preparation_time_hours": 8
    }
]

# Create products
for product in products:
    try:
        response = requests.post(API_URL, headers=headers, json=product)
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            print(f"✓ Created: {product['name']}")
        else:
            print(f"✗ Failed to create {product['name']}: {response.text}")
    except Exception as e:
        print(f"✗ Error creating {product['name']}: {str(e)}")

print("\nAll products created!")