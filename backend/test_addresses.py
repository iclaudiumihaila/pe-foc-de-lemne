"""Test address management"""
import requests
import json
from app.database import init_mongodb
from app.models.customer_phone import CustomerPhone
from bson import ObjectId
from datetime import datetime

# Initialize database
init_mongodb()

# Add a test address directly to database
phone = "+40755667788"
customer = CustomerPhone.find_by_phone(phone)

if customer:
    # Add a test address
    test_address = {
        '_id': ObjectId(),
        'street': 'Strada Primăverii 25, Bl. A2, Sc. 1, Ap. 12',
        'city': 'București',
        'county': 'București',
        'postal_code': '010101',
        'notes': 'Interfon: 12, etaj 3',
        'is_default': True,
        'usage_count': 5,
        'last_used': datetime.utcnow(),
        'created_at': datetime.utcnow()
    }
    
    customer.addresses = [test_address]
    customer.save()
    print(f"Added test address to customer {phone}")
    
    # Now test the GET endpoint
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6Iis0MDc1NTY2Nzc4OCIsImN1c3RvbWVyX2lkIjoiNjg1N2RkNmZjNjYwNTRkMmY3ODJhZWUwIiwiZXhwIjoxNzUwNjc1MTgzLCJpYXQiOjE3NTA1ODg3ODMsInR5cGUiOiJjaGVja291dF9zZXNzaW9uIn0.z3Q2WlsBJZTsFnxgow7jrZleC5un8yIQnJ5pMQr8-pU"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/checkout/addresses", headers=headers)
    
    print(f"\nStatus: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print(f"Customer not found for phone {phone}")