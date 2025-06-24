#!/usr/bin/env python3
import requests
import json

def test_orders_api():
    # Step 1: Login
    print("1. Testing admin login...")
    login_data = {
        'username': '+40700000001',
        'password': 'admin123'
    }
    
    login_response = requests.post('http://localhost:8000/api/auth/admin/login', json=login_data)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   Error: {login_response.text}")
        return
    
    data = login_response.json()
    if not data.get('success'):
        print(f"   Failed: {data}")
        return
    
    token = data['data']['tokens']['access_token']
    print(f"   ✓ Got token: {token[:30]}...")
    
    # Step 2: Fetch orders
    print("\n2. Testing orders API...")
    headers = {'Authorization': f'Bearer {token}'}
    orders_response = requests.get('http://localhost:8000/api/admin/orders', headers=headers)
    print(f"   Status: {orders_response.status_code}")
    
    if orders_response.status_code == 200:
        orders_data = orders_response.json()
        print(f"   ✓ Total orders: {orders_data.get('total', 0)}")
        print(f"   ✓ Current page: {orders_data.get('page', 1)}")
        print(f"   ✓ Total pages: {orders_data.get('total_pages', 1)}")
        
        if orders_data.get('orders'):
            print(f"\n   First order:")
            order = orders_data['orders'][0]
            print(f"     - Order #: {order['order_number']}")
            print(f"     - Customer: {order['customer_name']}")
            print(f"     - Phone: {order['customer_phone']}")
            print(f"     - Total: {order['total']} RON")
            print(f"     - Status: {order['status']}")
    else:
        print(f"   Error: {orders_response.text}")

if __name__ == "__main__":
    test_orders_api()