"""Simple order creation test"""
import requests
import json
from bson import ObjectId
from datetime import datetime
from app.database import init_mongodb, get_database

# Initialize database
init_mongodb()
db = get_database()

# First, get real products
products = list(db.products.find({'is_available': True}).limit(2))
if len(products) < 2:
    print("Not enough products in database")
    exit(1)

print(f"Found products: {[p['name'] for p in products]}")

# Create a cart
cart_session_id = f"test-{ObjectId()}"
cart_data = {
    'session_id': cart_session_id,
    'items': [
        {
            'product_id': str(products[0]['_id']),
            'product_name': products[0]['name'],
            'quantity': 2,
            'unit_price': float(products[0]['price'])
        },
        {
            'product_id': str(products[1]['_id']),
            'product_name': products[1]['name'],
            'quantity': 1,
            'unit_price': float(products[1]['price'])
        }
    ],
    'created_at': datetime.utcnow()
}
db.carts.insert_one(cart_data)
print(f"\nCart created: {cart_session_id}")
print(f"Cart total: {sum(item['quantity'] * item['unit_price'] for item in cart_data['items'])} lei")

# Test guest checkout
print("\nTesting guest checkout:")
order_data = {
    "cart_session_id": cart_session_id,
    "customer_info": {
        "customer_name": "Test Customer",
        "phone_number": "0722112233",
        "delivery_address": {
            "street": "Strada Test 123",
            "city": "București",
            "county": "București",
            "postal_code": "010101",
            "notes": "Test order"
        }
    }
}

response = requests.post("http://localhost:8000/api/orders", json=order_data)
print(f"Status: {response.status_code}")
result = response.json()

if result.get('success'):
    print(f"Order created successfully!")
    print(f"Order number: {result['order']['order_number']}")
    print(f"Total: {result['order']['total_amount']} lei")
else:
    print(f"Error: {result}")
    
    # Check if cart exists
    cart = db.carts.find_one({'session_id': cart_session_id})
    print(f"\nCart exists: {cart is not None}")
    if cart:
        print(f"Cart items: {len(cart.get('items', []))}")