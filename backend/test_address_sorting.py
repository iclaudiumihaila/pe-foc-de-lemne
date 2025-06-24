"""Test address sorting"""
import requests
import json
from app.database import init_mongodb
from app.models.customer_phone import CustomerPhone
from bson import ObjectId
from datetime import datetime, timedelta

# Initialize database
init_mongodb()

# Add multiple test addresses
phone = "+40755667788"
customer = CustomerPhone.find_by_phone(phone)

if customer:
    # Create multiple addresses with different properties
    addresses = [
        {
            '_id': ObjectId(),
            'street': 'Strada Florilor 10',
            'city': 'Cluj-Napoca',
            'county': 'Cluj',
            'postal_code': '400100',
            'notes': 'Birou',
            'is_default': False,
            'usage_count': 10,  # High usage but not default
            'last_used': datetime.utcnow() - timedelta(days=1),
            'created_at': datetime.utcnow() - timedelta(days=30)
        },
        {
            '_id': ObjectId(),
            'street': 'Strada Primăverii 25, Bl. A2, Sc. 1, Ap. 12',
            'city': 'București',
            'county': 'București',
            'postal_code': '010101',
            'notes': 'Interfon: 12, etaj 3',
            'is_default': True,  # This should be first
            'usage_count': 5,
            'last_used': datetime.utcnow(),
            'created_at': datetime.utcnow() - timedelta(days=60)
        },
        {
            '_id': ObjectId(),
            'street': 'Bulevardul Eroilor 15',
            'city': 'Timișoara',
            'county': 'Timiș',
            'postal_code': '300000',
            'notes': '',
            'is_default': False,
            'usage_count': 2,  # Low usage
            'last_used': datetime.utcnow() - timedelta(days=10),
            'created_at': datetime.utcnow() - timedelta(days=7)
        }
    ]
    
    customer.addresses = addresses
    customer.save()
    print(f"Added {len(addresses)} test addresses")
    
    # Test the GET endpoint
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6Iis0MDc1NTY2Nzc4OCIsImN1c3RvbWVyX2lkIjoiNjg1N2RkNmZjNjYwNTRkMmY3ODJhZWUwIiwiZXhwIjoxNzUwNjc1MTgzLCJpYXQiOjE3NTA1ODg3ODMsInR5cGUiOiJjaGVja291dF9zZXNzaW9uIn0.z3Q2WlsBJZTsFnxgow7jrZleC5un8yIQnJ5pMQr8-pU"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/checkout/addresses", headers=headers)
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        print(f"\nTotal addresses: {result['count']}")
        print("\nAddresses in order:")
        for i, addr in enumerate(result['addresses'], 1):
            print(f"\n{i}. {addr['street']}, {addr['city']}")
            print(f"   Default: {addr['is_default']}, Usage: {addr['usage_count']}")
else:
    print(f"Customer not found")