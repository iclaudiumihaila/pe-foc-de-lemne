#!/usr/bin/env python3
"""
Check checkout session data
"""

import requests
import json

# API endpoint
base_url = "http://localhost:8000/api"

# Get current checkout token
checkout_token = input("Enter checkout token from browser localStorage: ").strip()

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {checkout_token}"
}

try:
    # Get checkout addresses
    response = requests.get(
        f"{base_url}/checkout/addresses",
        headers=headers
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"\nResponse body:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"\nError: {e}")