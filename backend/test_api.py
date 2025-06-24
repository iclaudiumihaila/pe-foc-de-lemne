#!/usr/bin/env python3
"""Test API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_endpoint(method, path, data=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n{method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.request(method, url, json=data, headers=headers)
            
        print(f"Status: {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text[:200]}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test health
print("=== Testing Health Endpoint ===")
test_endpoint("GET", "/health")

# Test products
print("\n=== Testing Products Endpoint ===")
test_endpoint("GET", "/products/")

# Test categories
print("\n=== Testing Categories Endpoint ===")
test_endpoint("GET", "/categories")

# Test cart
print("\n=== Testing Cart Endpoint ===")
test_endpoint("GET", "/cart")