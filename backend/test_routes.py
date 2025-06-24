#!/usr/bin/env python3
"""Test routes directly"""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.config import DevelopmentConfig

# Create test app
app = create_app(DevelopmentConfig)

# Print all routes
print("Registered routes:")
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{methods:7} {rule}")

# Test client
with app.test_client() as client:
    print("\n\nTesting endpoints:")
    
    # Test health
    resp = client.get('/api/health')
    print(f"\nGET /api/health: {resp.status_code}")
    
    # Test products
    resp = client.get('/api/products/')
    print(f"\nGET /api/products/: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.get_json()
        print(f"Products found: {len(data.get('data', {}).get('products', []))}")
    else:
        print(f"Response: {resp.get_json()}")
    
    # Test categories  
    resp = client.get('/api/categories')
    print(f"\nGET /api/categories: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.get_json()
        print(f"Categories found: {len(data.get('data', []))}")
    else:
        print(f"Response: {resp.get_json()}")