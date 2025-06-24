#!/usr/bin/env python3
"""Create cart via API"""

import requests
import json

# API endpoint
api_url = "http://localhost:8000/api/cart/"

# Cart data
cart_data = {
    "product_id": "6858391f678080b011b561e2",
    "quantity": 1
    # Don't send session_id, let backend create it
}

# Make request
headers = {
    "Content-Type": "application/json"
}

response = requests.post(api_url, json=cart_data, headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nCart created successfully!")
    print(f"Session ID: {data.get('cart', {}).get('session_id')}")
    print(f"Items: {len(data.get('cart', {}).get('items', []))}")
else:
    print(f"\nError creating cart: {response.text}")