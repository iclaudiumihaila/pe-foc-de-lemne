#!/usr/bin/env python3
"""
Test order creation with the test cart
"""

import requests
import json

# API endpoint
base_url = "http://localhost:8000/api"

# Get checkout token from localStorage
print("Testing order creation with test cart...")
print("Cart session ID: test_cart_checkout")

# Checkout token from the browser
checkout_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6IjA3NzUxNTY3OTEiLCJzZXNzaW9uX2lkIjoiY2hlY2tvdXRfMTc1MDYxNDIzMzYyM19vNXBxcHBqbWsiLCJleHAiOjE3NTA2MTc4MzN9.A5N8o2gAYS93Wo7RPiKxs_BtlLJqKA_7v1hKGNKz8eI"

# Order data
order_data = {
    "cart_session_id": "test_cart_checkout",
    "address_id": "676820d6b6f9d84233b7e9b9",
    "customer_info": {
        "customer_name": "Test User",
        "special_instructions": ""
    }
}

print(f"\nSending order data:")
print(json.dumps(order_data, indent=2))

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {checkout_token}"
}

try:
    response = requests.post(
        f"{base_url}/orders",
        json=order_data,
        headers=headers
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"\nResponse body:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"\nError: {e}")