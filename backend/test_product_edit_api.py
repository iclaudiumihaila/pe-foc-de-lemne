#!/usr/bin/env python3
"""
Test product edit API functionality thoroughly
"""
import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:8000/api"
ADMIN_BASE = f"{API_BASE}/admin"

def get_admin_token():
    """Login as admin and get token"""
    login_data = {
        "username": "+40700000000",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_BASE}/auth/admin/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Failed to login as admin: {response.status_code}")
        print(f"Response: {response.text}")
        return None
        
    data = response.json()
    
    # Check for token in different possible locations
    token = None
    if 'token' in data:
        token = data['token']
    elif 'data' in data and 'tokens' in data['data']:
        token = data['data']['tokens'].get('access_token')
    elif 'data' in data and 'token' in data['data']:
        token = data['data']['token']
    
    if token:
        print(f"✅ Successfully logged in as admin")
        return token
    else:
        print(f"❌ No token in response: {data}")
        return None


def test_get_products(token):
    """Test getting products list"""
    print("\n🔍 Testing GET /admin/products")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ADMIN_BASE}/products?limit=5", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Response structure:")
        print(f"  - Keys: {list(data.keys())}")
        
        if 'success' in data and 'data' in data:
            # Wrapped response
            actual_data = data['data']
            print(f"  - Has wrapper with success={data['success']}")
            print(f"  - Actual data keys: {list(actual_data.keys())}")
        else:
            actual_data = data
            
        if 'products' in actual_data:
            products = actual_data['products']
            print(f"  - Found {len(products)} products")
            
            if products:
                print(f"\n  First product structure:")
                first_product = products[0]
                for key, value in first_product.items():
                    print(f"    - {key}: {type(value).__name__} = {value}")
                return first_product
        else:
            print(f"  - No 'products' key found")
    else:
        print(f"❌ Failed: {response.text}")
    
    return None


def test_get_single_product(token, product_id):
    """Test getting single product details"""
    print(f"\n🔍 Testing GET /admin/products/{product_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ADMIN_BASE}/products/{product_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Product details:")
        for key, value in data.items():
            print(f"  - {key}: {type(value).__name__} = {value}")
        return data
    else:
        print(f"❌ Failed: {response.text}")
    
    return None


def test_update_product(token, product_id, update_data):
    """Test updating a product"""
    print(f"\n📝 Testing PUT /admin/products/{product_id}")
    print(f"Update data: {json.dumps(update_data, indent=2)}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{ADMIN_BASE}/products/{product_id}", 
                          json=update_data, 
                          headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Response:")
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"❌ Failed:")
        print(f"Response text: {response.text}")
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            pass
    
    return None


def test_categories(token):
    """Test getting categories"""
    print("\n🔍 Testing GET /admin/categories")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ADMIN_BASE}/categories", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Response structure:")
        print(f"  - Keys: {list(data.keys())}")
        
        if 'success' in data and 'data' in data:
            actual_data = data['data']
            print(f"  - Has wrapper with success={data['success']}")
            
            if 'categories' in actual_data:
                categories = actual_data['categories']
                print(f"  - Found {len(categories)} categories")
                for cat in categories[:3]:  # Show first 3
                    print(f"    • {cat.get('name')} (id: {cat.get('id')})")
                return categories
        else:
            # Direct categories array?
            if isinstance(data, list):
                print(f"  - Direct array with {len(data)} categories")
                for cat in data[:3]:
                    print(f"    • {cat.get('name')} (id: {cat.get('id')})")
                return data
            elif 'categories' in data:
                categories = data['categories']
                print(f"  - Found {len(categories)} categories")
                for cat in categories[:3]:
                    print(f"    • {cat.get('name')} (id: {cat.get('id')})")
                return categories
    else:
        print(f"❌ Failed: {response.text}")
    
    return None


def main():
    print("🚀 Product Edit API Test Suite")
    print("=" * 60)
    
    # Step 1: Get admin token
    token = get_admin_token()
    if not token:
        print("\n❌ Cannot proceed without admin token")
        return
    
    # Step 2: Get products list
    first_product = test_get_products(token)
    if not first_product:
        print("\n❌ Cannot proceed without products")
        return
    
    product_id = first_product.get('id')
    print(f"\n📦 Using product ID: {product_id}")
    
    # Step 3: Get single product details
    product_details = test_get_single_product(token, product_id)
    
    # Step 4: Get categories
    categories = test_categories(token)
    
    # Step 5: Test various update scenarios
    print("\n" + "="*60)
    print("🧪 TESTING UPDATE SCENARIOS")
    print("="*60)
    
    # Test 5.1: Update name only
    print("\n### Test 5.1: Update name only")
    test_update_product(token, product_id, {
        "name": f"Test Product Updated {datetime.now().strftime('%H:%M:%S')}"
    })
    
    # Test 5.2: Update all fields
    print("\n### Test 5.2: Update all fields")
    all_fields_update = {
        "name": f"Fully Updated Product {datetime.now().strftime('%H:%M:%S')}",
        "description": "This is a completely updated product description with all fields changed",
        "price": 99.99,
        "stock": 50,
        "weight_grams": 500,
        "preparation_time_hours": 2,
        "is_available": True,
        "images": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
    }
    
    # Add category if we have one
    if categories and len(categories) > 0:
        # Try to use a different category than current
        current_cat = product_details.get('category_id') if product_details else None
        for cat in categories:
            if cat.get('id') != current_cat:
                all_fields_update['category_id'] = cat.get('id')
                print(f"  - Setting category_id to: {cat.get('id')} ({cat.get('name')})")
                break
    
    result = test_update_product(token, product_id, all_fields_update)
    
    # Test 5.3: Verify the update worked
    print("\n### Test 5.3: Verify update by getting product again")
    updated_product = test_get_single_product(token, product_id)
    
    if updated_product:
        print("\n🔍 Comparing expected vs actual values:")
        for field, expected in all_fields_update.items():
            actual = updated_product.get(field)
            
            # Handle field name mappings
            if field == 'stock' and 'stock_quantity' in updated_product:
                actual = updated_product.get('stock_quantity')
            elif field == 'category_id' and 'category' in updated_product:
                actual = updated_product.get('category')
                
            if actual == expected:
                print(f"  ✅ {field}: {expected}")
            else:
                print(f"  ❌ {field}: expected {expected}, got {actual}")
    
    # Test 5.4: Test with invalid data
    print("\n### Test 5.4: Test with invalid price")
    test_update_product(token, product_id, {
        "price": "not-a-number"
    })
    
    print("\n### Test 5.5: Test with empty name")
    test_update_product(token, product_id, {
        "name": ""
    })
    
    print("\n### Test 5.6: Test with invalid category_id")
    test_update_product(token, product_id, {
        "category_id": "invalid-id-123"
    })
    
    print("\n" + "="*60)
    print("✅ Test suite completed!")


if __name__ == "__main__":
    main()