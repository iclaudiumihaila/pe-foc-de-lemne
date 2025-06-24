#!/usr/bin/env python3
"""Test product creation with fixed endpoint"""

import requests
import json
from app import create_app
from app.config import DevelopmentConfig
from app.database import get_database

# Initialize the app to set up database
app = create_app(DevelopmentConfig)
with app.app_context():
    db = get_database()
    
    # Get a valid category
    category = db.categories.find_one({'is_active': True})
    if not category:
        print("No active categories found!")
        exit(1)
    
    category_id = str(category['_id'])
    print(f"Using category: {category['name']} (ID: {category_id})")
    
    # Get auth token from file
    try:
        with open('/Users/marius/.pe_foc_auth_token', 'r') as f:
            token = f.read().strip()
    except:
        print("No auth token found. Please login first.")
        exit(1)
    
    # Test product data
    product_data = {
        "name": "Test Product with Upload",
        "description": "This is a test product to verify the upload functionality works correctly",
        "price": 29.99,
        "category_id": category_id,
        "stock_quantity": 15,
        "images": [],  # Empty for now, will be filled via upload
        "is_available": True,
        "weight_grams": 500,
        "preparation_time_hours": 24
    }
    
    # Make the request
    response = requests.post(
        'http://localhost:8000/api/admin/products',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json=product_data
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ Product created successfully!")
    else:
        print("\n❌ Product creation failed!")