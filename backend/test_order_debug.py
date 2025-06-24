#!/usr/bin/env python3
"""
Debug order creation
"""

import requests
import json
import jwt

# API endpoint
base_url = "http://localhost:8000/api"

# Get checkout token
checkout_token = input("Enter checkout token from browser: ").strip()

# Decode token to see what's in it
try:
    # Don't verify since we don't have the secret key here
    decoded = jwt.decode(checkout_token, options={"verify_signature": False})
    print("\nToken contents:")
    print(json.dumps(decoded, indent=2))
except Exception as e:
    print(f"Could not decode token: {e}")

# First check if we're authenticated
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {checkout_token}"
}

print("\n1. Checking authentication status...")
response = requests.get(f"{base_url}/checkout/addresses", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Now try to create order
print("\n2. Creating order...")
order_data = {
    "cart_session_id": "test_cart_checkout",
    "address_id": "676820d6b6f9d84233b7e9b9",
    "customer_info": {
        "customer_name": "Test User",
        "special_instructions": ""
    }
}

print("Sending:", json.dumps(order_data, indent=2))

response = requests.post(
    f"{base_url}/orders",
    json=order_data,
    headers=headers
)

print(f"\nResponse status: {response.status_code}")
print(f"Response body:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))