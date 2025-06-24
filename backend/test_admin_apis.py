#!/usr/bin/env python3
"""
Test script for admin APIs
Tests all admin endpoints to ensure they're working correctly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_PHONE = "+40700000000"
ADMIN_PASSWORD = "admin123"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, success, message=""):
    """Print test result with color"""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {name}")
    if message:
        print(f"  {YELLOW}→ {message}{RESET}")

def test_admin_login():
    """Test admin login"""
    print(f"\n{BLUE}Testing Admin Login...{RESET}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin/login", json={
            "username": ADMIN_PHONE,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['tokens']['access_token']
                print_test("Admin Login", True, f"Token: {token[:20]}...")
                return token
            else:
                print_test("Admin Login", False, data.get('error', {}).get('message', 'Unknown error'))
                return None
        else:
            print_test("Admin Login", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_test("Admin Login", False, str(e))
        return None

def test_admin_products(token):
    """Test admin products endpoints"""
    print(f"\n{BLUE}Testing Admin Products...{RESET}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list products
    try:
        response = requests.get(f"{BASE_URL}/admin/products", headers=headers)
        success = response.status_code == 200
        print_test("List Products", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            products = data.get('products', [])
            print(f"  Found {len(products)} products")
            
            # Test get single product if any exist
            if products:
                product_id = products[0]['id']
                response = requests.get(f"{BASE_URL}/admin/products/{product_id}", headers=headers)
                print_test("Get Single Product", response.status_code == 200, f"Product ID: {product_id}")
                
    except Exception as e:
        print_test("Products API", False, str(e))

def test_admin_categories(token):
    """Test admin categories endpoints"""
    print(f"\n{BLUE}Testing Admin Categories...{RESET}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list categories
    try:
        response = requests.get(f"{BASE_URL}/admin/categories", headers=headers)
        success = response.status_code == 200
        print_test("List Categories", success, f"Status: {response.status_code}")
        
        # Test tree view
        response = requests.get(f"{BASE_URL}/admin/categories/tree", headers=headers)
        success = response.status_code == 200
        print_test("Categories Tree", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            categories = data.get('categories', [])
            print(f"  Found {len(categories)} root categories")
            
    except Exception as e:
        print_test("Categories API", False, str(e))

def test_admin_orders(token):
    """Test admin orders endpoints"""
    print(f"\n{BLUE}Testing Admin Orders...{RESET}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test list orders
    try:
        response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
        success = response.status_code == 200
        print_test("List Orders", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            orders = data.get('orders', [])
            print(f"  Found {len(orders)} orders")
            
            # Test get single order if any exist
            if orders:
                order_id = orders[0]['id']
                response = requests.get(f"{BASE_URL}/admin/orders/{order_id}", headers=headers)
                print_test("Get Single Order", response.status_code == 200, f"Order ID: {order_id}")
                
    except Exception as e:
        print_test("Orders API", False, str(e))

def main():
    """Run all tests"""
    print(f"{BLUE}=== Admin API Test Suite ==={RESET}")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login first
    token = test_admin_login()
    
    if not token:
        print(f"\n{RED}Cannot proceed without valid admin token{RESET}")
        sys.exit(1)
    
    # Test all admin endpoints
    test_admin_products(token)
    test_admin_categories(token)
    test_admin_orders(token)
    
    print(f"\n{BLUE}=== Test Complete ==={RESET}")

if __name__ == "__main__":
    main()