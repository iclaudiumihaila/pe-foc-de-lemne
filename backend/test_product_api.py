#!/usr/bin/env python3
"""Test the product creation API endpoint"""

import requests
import json
import sys

# API endpoint
BASE_URL = "http://localhost:8000/api"

# Test data
test_product = {
    "name": "Test Product API",
    "description": "This is a test product created via API to verify the endpoint works correctly",
    "price": 25.99,
    "category_id": "68598a089ca62a297d0804df",  # Use a known category ID
    "stock_quantity": 10,
    "images": [],
    "is_available": True,
    "weight_grams": 500,
    "preparation_time_hours": 24
}

# First, we need to login as admin
login_data = {
    "username": "admin",
    "password": "admin123"
}

# Login
print("Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/auth/admin/login", json=login_data)
if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.json())
    sys.exit(1)

# Get the token
token = login_response.json().get('access_token')
if not token:
    print("No access token received")
    sys.exit(1)

print("Login successful!")

# Create product
print("\nCreating product...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

create_response = requests.post(f"{BASE_URL}/admin/products", json=test_product, headers=headers)
print(f"Response Status: {create_response.status_code}")
print(f"Response Body: {json.dumps(create_response.json(), indent=2)}")

if create_response.status_code == 201:
    print("\n✅ Product created successfully!")
else:
    print("\n❌ Product creation failed!")
    
# Get all products to verify
print("\nFetching all products...")
get_response = requests.get(f"{BASE_URL}/admin/products", headers=headers)
if get_response.status_code == 200:
    products = get_response.json().get('products', [])
    print(f"Total products: {len(products)}")
    # Find our test product
    test_products = [p for p in products if 'Test Product' in p.get('name', '')]
    if test_products:
        print("\nTest products found:")
        for p in test_products:
            print(f"  - {p['name']} (ID: {p['id']})")