#!/usr/bin/env python3
"""
Test script for admin API routes
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def get_admin_token():
    """Get admin JWT token"""
    # First, let's try to login as admin
    login_data = {
        "username": "+40700000000",  # Admin phone from seed data
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/admin/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['tokens']['access_token']
    else:
        print(f"Admin login failed: {response.status_code}")
        print(response.json())
        return None

def test_admin_products(token):
    """Test admin product endpoints"""
    print("\n=== Testing Admin Product Endpoints ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List products
    print("\n1. List admin products:")
    response = requests.get(f"{BASE_URL}/admin/products", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data']['products'])} products")
        print(f"Pagination: {data['data']['pagination']}")
    else:
        print(response.json())
    
    # Test 2: Get single product
    print("\n2. Get single product:")
    # We need a product ID first - get it from admin products list
    if response.status_code == 200 and data['data']['products']:
        product_id = data['data']['products'][0]['_id']
        response = requests.get(f"{BASE_URL}/admin/products/{product_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            product = response.json()['data']
            print(f"Product: {product['name']} - {product['price']} RON")
        else:
            print(response.json())

def test_admin_categories(token):
    """Test admin category endpoints"""
    print("\n=== Testing Admin Category Endpoints ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List categories
    print("\n1. List all categories:")
    response = requests.get(f"{BASE_URL}/admin/categories", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['data']['total']} categories")
    else:
        print(response.json())
    
    # Test 2: Get category tree
    print("\n2. Get category tree:")
    response = requests.get(f"{BASE_URL}/admin/categories/tree", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Tree has {len(data['data']['tree'])} root categories")
    else:
        print(response.json())

def test_admin_orders(token):
    """Test admin order endpoints"""
    print("\n=== Testing Admin Order Endpoints ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List orders
    print("\n1. List all orders:")
    response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['data']['pagination']['total']} orders")
        print(f"Summary: {data['data']['summary']}")
    else:
        print(response.json())
    
    # Test 2: Get single order (if any exist)
    if response.status_code == 200 and data['data']['orders']:
        order_id = data['data']['orders'][0]['_id']
        print(f"\n2. Get order details for {order_id}:")
        response = requests.get(f"{BASE_URL}/admin/orders/{order_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            order = response.json()['data']
            print(f"Order #{order['order_number']} - Status: {order['status']}")
            if 'customer' in order:
                print(f"Customer: {order['customer']['name']} ({order['customer']['phone']})")
            else:
                print(f"Customer phone: {order.get('customer_phone', 'N/A')}")
            print(f"Total: {order.get('total_amount', order.get('total', 'N/A'))} RON")
        else:
            print(response.json())

def test_unauthorized_access():
    """Test that endpoints require authentication"""
    print("\n=== Testing Unauthorized Access ===")
    
    endpoints = [
        "/admin/products",
        "/admin/categories",
        "/admin/orders"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"{endpoint}: {response.status_code} (should be 401)")

if __name__ == "__main__":
    print("Testing Admin API Routes")
    print("========================")
    
    # Test unauthorized access first
    test_unauthorized_access()
    
    # Get admin token
    token = get_admin_token()
    
    if token:
        print(f"\nAdmin token obtained successfully!")
        
        # Test each admin endpoint
        test_admin_products(token)
        test_admin_categories(token)
        test_admin_orders(token)
    else:
        print("\nFailed to obtain admin token. Make sure the backend is running and admin user exists.")