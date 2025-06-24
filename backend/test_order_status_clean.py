"""Test order status endpoint - clean version"""
import requests
import json
from bson import ObjectId
from datetime import datetime, timedelta
from app.database import init_mongodb, get_database

# Initialize database
init_mongodb()
db = get_database()

base_url = "http://localhost:8000"

# Create orders with different statuses
print("Creating test orders with different statuses...")
statuses_data = [
    ('pending', 'În așteptare', 'Livrare estimată în 24-48 ore'),
    ('confirmed', 'Confirmată', 'Livrare estimată în 24-48 ore'),
    ('preparing', 'În preparare', 'Livrare estimată în 24-48 ore'),
    ('delivering', 'În livrare', 'Livrare estimată în 24-48 ore'),
    ('delivered', 'Livrată', 'Comanda a fost livrată'),
    ('cancelled', 'În așteptare', 'Comanda a fost anulată')
]

test_phone = "+40722445566"

for status, expected_label, expected_message in statuses_data:
    order_number = f"PFL-STATUS-{status.upper()}-{str(ObjectId())[:4]}"
    
    order_data = {
        'order_number': order_number,
        'customer_phone': test_phone,
        'customer_name': f'Test {status.title()}',
        'delivery_address': {
            'street': 'Strada Test 123',
            'city': 'Cluj-Napoca',
            'county': 'Cluj',
            'postal_code': '400100',
            'notes': f'Test {status} order'
        },
        'items': [
            {
                'product_name': 'Test Product',
                'quantity': 1,
                'unit_price': 50.0
            }
        ],
        'total_amount': 50.0,
        'status': status,
        'special_instructions': f'Testing {status} status',
        'created_at': datetime.utcnow() - timedelta(hours=2)
    }
    
    # Add timestamp fields based on status
    if status in ['confirmed', 'preparing', 'ready', 'delivering', 'delivered']:
        order_data['confirmed_at'] = datetime.utcnow() - timedelta(hours=1.5)
    if status in ['preparing', 'ready', 'delivering', 'delivered']:
        order_data['preparing_at'] = datetime.utcnow() - timedelta(hours=1)
    if status in ['ready', 'delivering', 'delivered']:
        order_data['ready_at'] = datetime.utcnow() - timedelta(minutes=45)
    if status in ['delivering', 'delivered']:
        order_data['delivering_at'] = datetime.utcnow() - timedelta(minutes=30)
    if status == 'delivered':
        order_data['delivered_at'] = datetime.utcnow() - timedelta(minutes=10)
    if status == 'cancelled':
        order_data['cancellation_reason'] = 'Client a anulat comanda'
    
    db.orders.insert_one(order_data)
    
    # Test the status endpoint
    response = requests.get(f"{base_url}/api/orders/status", params={
        'phone': '0722445566',
        'order_number': order_number
    })
    
    if response.status_code == 200:
        result = response.json()['order']
        print(f"\n{status.upper()}:")
        print(f"  Status: {result['status_label']}")
        print(f"  Message: {result['delivery_message']}")
        
        # Show completed steps
        completed_steps = [info['label'] for key, info in result['timeline'].items() if info['completed']]
        print(f"  Completed: {' → '.join(completed_steps)}")
        
        if status == 'cancelled':
            print(f"  Reason: {result.get('cancellation_reason', 'N/A')}")

# Test validation
print("\n\nTesting validation:")
print("1. Invalid phone format:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'phone': '123',
    'order_number': 'TEST'
})
print(f"   Status: {response.status_code}, Error: {response.json().get('error', {}).get('message', 'N/A')}")

print("\n2. Missing order number:")
response = requests.get(f"{base_url}/api/orders/status", params={
    'phone': '0722445566'
})
print(f"   Status: {response.status_code}, Error: {response.json().get('error', {}).get('message', 'N/A')}")