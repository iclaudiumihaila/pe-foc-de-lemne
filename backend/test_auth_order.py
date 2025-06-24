"""Test authenticated order creation"""
import requests
import json
from bson import ObjectId
from datetime import datetime
from app.database import init_mongodb, get_database

# Initialize database
init_mongodb()
db = get_database()

base_url = "http://localhost:8000"

# Get auth token
print("1. Getting authentication token...")
phone = "0755667788"
send_response = requests.post(f"{base_url}/api/checkout/phone/send-code",
                             json={"phone": phone})
if not send_response.json().get('success'):
    print("Failed to send code")
    exit(1)

code = send_response.json().get('debug_code')
print(f"Code: {code}")

verify_response = requests.post(f"{base_url}/api/checkout/phone/verify-code",
                               json={"phone": phone, "code": code})
if not verify_response.json().get('success'):
    print("Failed to verify code")
    exit(1)

token = verify_response.json().get('token')
headers = {"Authorization": f"Bearer {token}"}
print("Authenticated successfully")

# Get addresses
print("\n2. Getting saved addresses...")
addresses_response = requests.get(f"{base_url}/api/checkout/addresses", headers=headers)
addresses = addresses_response.json().get('addresses', [])
print(f"Found {len(addresses)} addresses")

if not addresses:
    print("No addresses found, exiting")
    exit(1)

# Use first address
address = addresses[0]
print(f"Using address: {address['street']}, {address['city']}")

# Create cart
print("\n3. Creating cart...")
products = list(db.products.find({'is_available': True}).limit(2))
cart_session_id = f"auth-test-{ObjectId()}"
cart_data = {
    'session_id': cart_session_id,
    'items': [
        {
            'product_id': str(products[0]['_id']),
            'product_name': products[0]['name'],
            'quantity': 3,
            'unit_price': float(products[0]['price'])
        }
    ],
    'created_at': datetime.utcnow()
}
db.carts.insert_one(cart_data)
total = sum(item['quantity'] * item['unit_price'] for item in cart_data['items'])
print(f"Cart total: {total} lei")

# Place order
print("\n4. Placing order...")
order_data = {
    "cart_session_id": cart_session_id,
    "address_id": address['id'],
    "customer_info": {
        "customer_name": "Test Auth Customer",
        "special_instructions": "Test authenticated order"
    }
}

response = requests.post(f"{base_url}/api/orders", 
                        json=order_data, 
                        headers=headers)
print(f"Status: {response.status_code}")
result = response.json()

if result.get('success'):
    print(f"Order created successfully!")
    print(f"Order number: {result['order']['order_number']}")
    print(f"Total: {result['order']['total_amount']} lei")
    print(f"Delivery to: {result['order']['delivery_address']['street']}, {result['order']['delivery_address']['city']}")
else:
    print(f"Error: {result}")

# Check order history
print("\n5. Checking order history...")
history_response = requests.get(f"{base_url}/api/orders/customer/{phone}")
print(f"Status: {history_response.status_code}")
if history_response.status_code == 200:
    orders = history_response.json().get('data', {}).get('orders', [])
    print(f"Found {len(orders)} orders for this phone number")