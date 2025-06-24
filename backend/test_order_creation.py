"""Test order creation with phone-based checkout"""
import requests
import json
from bson import ObjectId
from datetime import datetime
from app.database import init_mongodb, get_database

# Initialize database
init_mongodb()
db = get_database()

base_url = "http://localhost:8000"

# Step 1: Create a cart with items
print("1. Creating cart with items...")
cart_session_id = "test-cart-" + str(ObjectId())[:8]

# Add some products to cart (assuming products exist)
cart_data = {
    'session_id': cart_session_id,
    'items': [
        {
            'product_id': '507f1f77bcf86cd799439011',
            'product_name': 'Lemne de foc stejar',
            'quantity': 2,
            'unit_price': 250.0
        },
        {
            'product_id': '507f1f77bcf86cd799439012',
            'product_name': 'Lemne de foc fag',
            'quantity': 1,
            'unit_price': 200.0
        }
    ],
    'created_at': datetime.utcnow()
}
db.carts.insert_one(cart_data)
print(f"Cart created: {cart_session_id}")

# Test 2: Guest checkout (no authentication)
print("\n2. Testing guest checkout:")
order_data = {
    "cart_session_id": cart_session_id,
    "customer_info": {
        "customer_name": "Ion Popescu",
        "phone_number": "0722334455",
        "delivery_address": {
            "street": "Strada Libertății 10",
            "city": "București",
            "county": "București",
            "postal_code": "010101",
            "notes": "Lângă școală"
        },
        "special_instructions": "Sunați înainte de livrare"
    }
}

response = requests.post(f"{base_url}/api/orders", json=order_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 3: Authenticated checkout
print("\n3. Testing authenticated checkout:")
# First get auth token
send_response = requests.post(f"{base_url}/api/checkout/phone/send-code",
                             json={"phone": "0755667788"})
code = send_response.json().get('debug_code')

verify_response = requests.post(f"{base_url}/api/checkout/phone/verify-code",
                               json={"phone": "0755667788", "code": code})
token = verify_response.json().get('token')

# Get addresses
headers = {"Authorization": f"Bearer {token}"}
addresses_response = requests.get(f"{base_url}/api/checkout/addresses", headers=headers)
addresses = addresses_response.json().get('addresses', [])

if addresses:
    # Create new cart for authenticated test
    auth_cart_id = "auth-cart-" + str(ObjectId())[:8]
    db.carts.insert_one({
        'session_id': auth_cart_id,
        'items': cart_data['items'],
        'created_at': datetime.utcnow()
    })
    
    # Use first address
    address_id = addresses[0]['id']
    
    auth_order_data = {
        "cart_session_id": auth_cart_id,
        "address_id": address_id,
        "customer_info": {
            "customer_name": "Test Authenticated",
            "special_instructions": "Livrare urgentă"
        }
    }
    
    response = requests.post(f"{base_url}/api/orders", 
                            json=auth_order_data, 
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print("No addresses found for authenticated user")

# Test 4: Missing required fields
print("\n4. Testing with missing fields:")
invalid_data = {
    "cart_session_id": "invalid-cart",
    "customer_info": {
        "customer_name": "Test User"
        # Missing phone and address for guest
    }
}

response = requests.post(f"{base_url}/api/orders", json=invalid_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))