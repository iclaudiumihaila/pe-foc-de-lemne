#!/usr/bin/env python3
"""
Test script for admin CRUD operations
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_admin_token():
    """Get admin JWT token"""
    login_data = {
        "username": "+40700000000",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/admin/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['tokens']['access_token']
    return None

def test_category_crud(token):
    """Test category CRUD operations"""
    print("\n=== Testing Category CRUD ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a new category
    print("\n1. Creating new category:")
    new_category = {
        "name": "Produse de Test",
        "slug": "produse-test",
        "description": "Categorie pentru teste",
        "display_order": 999
    }
    
    response = requests.post(f"{BASE_URL}/admin/categories", json=new_category, headers=headers)
    print(f"Create Status: {response.status_code}")
    
    if response.status_code == 201:
        category = response.json()['data']
        category_id = category['_id']
        print(f"Created category: {category['name']} (ID: {category_id})")
        
        # Update the category
        print("\n2. Updating category:")
        update_data = {
            "description": "Categorie actualizată pentru teste",
            "display_order": 998
        }
        
        response = requests.put(f"{BASE_URL}/admin/categories/{category_id}", 
                               json=update_data, headers=headers)
        print(f"Update Status: {response.status_code}")
        
        # Delete the category
        print("\n3. Deleting category:")
        response = requests.delete(f"{BASE_URL}/admin/categories/{category_id}", headers=headers)
        print(f"Delete Status: {response.status_code}")
    else:
        print(response.json())

def test_product_crud(token):
    """Test product CRUD operations"""
    print("\n=== Testing Product CRUD ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get a category ID
    response = requests.get(f"{BASE_URL}/admin/categories", headers=headers)
    if response.status_code == 200 and response.json()['data']['categories']:
        category_id = response.json()['data']['categories'][0]['_id']
        
        # Create a new product
        print("\n1. Creating new product:")
        new_product = {
            "name": "Produs de Test",
            "description": "Acesta este un produs de test pentru verificarea API-ului",
            "price": 99.99,
            "category_id": category_id,
            "stock_quantity": 50,
            "weight_grams": 1000,
            "is_available": True
        }
        
        response = requests.post(f"{BASE_URL}/admin/products", json=new_product, headers=headers)
        print(f"Create Status: {response.status_code}")
        
        if response.status_code == 201:
            product = response.json()['data']
            product_id = product['_id']
            print(f"Created product: {product['name']} (ID: {product_id})")
            
            # Update the product
            print("\n2. Updating product:")
            update_data = {
                "price": 89.99,
                "stock_quantity": 45,
                "featured": True
            }
            
            response = requests.put(f"{BASE_URL}/admin/products/{product_id}", 
                                   json=update_data, headers=headers)
            print(f"Update Status: {response.status_code}")
            
            # Delete the product
            print("\n3. Deleting product:")
            response = requests.delete(f"{BASE_URL}/admin/products/{product_id}", headers=headers)
            print(f"Delete Status: {response.status_code}")
        else:
            print(response.json())

def test_order_status_update(token):
    """Test order status update"""
    print("\n=== Testing Order Status Update ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get an order to update
    response = requests.get(f"{BASE_URL}/admin/orders?status=pending&limit=1", headers=headers)
    if response.status_code == 200 and response.json()['data']['orders']:
        order = response.json()['data']['orders'][0]
        order_id = order['_id']
        
        print(f"\nUpdating order {order['order_number']} from '{order['status']}' to 'confirmed':")
        
        update_data = {
            "status": "confirmed",
            "notes": "Comandă confirmată prin API de test",
            "notify_customer": False
        }
        
        response = requests.put(f"{BASE_URL}/admin/orders/{order_id}/status", 
                               json=update_data, headers=headers)
        print(f"Update Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()['data']
            print(f"Order updated: {result['previous_status']} -> {result['new_status']}")
        else:
            print(response.json())

if __name__ == "__main__":
    print("Testing Admin CRUD Operations")
    print("=============================")
    
    # Get admin token
    token = get_admin_token()
    
    if token:
        print("\nAdmin token obtained successfully!")
        
        # Test CRUD operations
        test_category_crud(token)
        test_product_crud(token)
        test_order_status_update(token)
        
        print("\n\nAll tests completed!")
    else:
        print("\nFailed to obtain admin token.")