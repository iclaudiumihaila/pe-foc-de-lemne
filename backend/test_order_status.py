"""Test order status endpoint"""
import requests
import json
from bson import ObjectId
from datetime import datetime, timedelta
from app.database import init_mongodb, get_database

# Initialize database
init_mongodb()
db = get_database()

base_url = "http://localhost:8000"

# First, create a test order directly in database
print("1. Creating test order...")
test_phone = "+40722112233"
order_number = f"PFL-{datetime.utcnow().strftime('%Y%m%d')}-{str(ObjectId())[:8]}"

order_data = {
    'order_number': order_number,
    'customer_phone': test_phone,
    'customer_name': 'Test Customer',
    'delivery_address': {
        'street': 'Strada Test 123',
        'city': 'București',
        'county': 'București',
        'postal_code': '010101',
        'notes': 'Test order'
    },
    'items': [
        {
            'product_name': 'Test Product',
            'quantity': 2,
            'unit_price': 50.0
        }
    ],
    'total_amount': 100.0,
    'status': 'pending',
    'special_instructions': 'Test order for status endpoint',
    'created_at': datetime.utcnow()
}

db.orders.insert_one(order_data)
print(f"Order created: {order_number}")

# Test 2: Check order status with correct data
print("\n2. Testing order status with correct data:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'phone': '0722112233',
    'order_number': order_number
})
print(f"Status: {response.status_code}")
result = response.json()

if result.get('success'):
    order = result['order']
    print(f"\nOrder found:")
    print(f"- Number: {order['order_number']}")
    print(f"- Status: {order['status_label']}")
    print(f"- Customer: {order['customer_name']}")
    print(f"- Phone: {order['phone_masked']}")
    print(f"- Total: {order['total_amount']} lei")
    print(f"- Delivery: {order['delivery_message']}")
    print(f"\nTimeline:")
    for status_key, status_info in order['timeline'].items():
        if status_info['completed']:
            print(f"✓ {status_info['label']} - {status_info['description']}")
        else:
            print(f"○ {status_info['label']} - {status_info['description']}")
else:
    print(f"Error: {result}")

# Test 3: Try with wrong order number
print("\n3. Testing with wrong order number:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'phone': '0722112233',
    'order_number': 'WRONG-NUMBER'
})
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 4: Try with wrong phone
print("\n4. Testing with wrong phone:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'phone': '0799999999',
    'order_number': order_number
})
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 5: Missing parameters
print("\n5. Testing with missing phone:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'order_number': order_number
})
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 6: Create order with different statuses
print("\n6. Testing different order statuses:")
statuses = ['confirmed', 'preparing', 'delivering', 'delivered', 'cancelled']
for status in statuses:
    test_order = order_data.copy()
    test_order['order_number'] = f"PFL-TEST-{status}"
    test_order['status'] = status
    
    # Add timestamp fields for timeline
    if status in ['confirmed', 'preparing', 'ready', 'delivering', 'delivered']:
        test_order['confirmed_at'] = datetime.utcnow() - timedelta(hours=2)
    if status in ['preparing', 'ready', 'delivering', 'delivered']:
        test_order['preparing_at'] = datetime.utcnow() - timedelta(hours=1.5)
    if status in ['ready', 'delivering', 'delivered']:
        test_order['ready_at'] = datetime.utcnow() - timedelta(hours=1)
    if status in ['delivering', 'delivered']:
        test_order['delivering_at'] = datetime.utcnow() - timedelta(minutes=30)
    if status == 'delivered':
        test_order['delivered_at'] = datetime.utcnow() - timedelta(minutes=10)
    if status == 'cancelled':
        test_order['cancellation_reason'] = 'Stoc insuficient'
    
    db.orders.insert_one(test_order)
    
    # Check status
    response = requests.get(f"{base_url}/api/orders/status", params={
        'phone': '0722112233',
        'order_number': test_order['order_number']
    })
    
    if response.status_code == 200:
        order_info = response.json()['order']
        print(f"\n{status.upper()}: {order_info['status_label']} - {order_info['delivery_message']}")