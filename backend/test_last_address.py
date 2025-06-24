"""Test last address protection"""
import requests
from app.database import init_mongodb
from app.models.customer_phone import CustomerPhone
from bson import ObjectId
from datetime import datetime

# Initialize database
init_mongodb()

# Create a customer with only 1 address
phone = "+40788998877"
customer = CustomerPhone({'phone': phone})
customer.addresses = [{
    '_id': ObjectId(),
    'street': 'Last Address Street 1',
    'city': 'București',
    'county': 'București',
    'postal_code': '010101',
    'notes': 'The only address',
    'is_default': True,
    'usage_count': 0,
    'created_at': datetime.utcnow()
}]
customer.save()

print(f"Created customer with 1 address")

# Get auth token
send_response = requests.post("http://localhost:8000/api/checkout/phone/send-code", 
                             json={"phone": "0788998877"})
code = send_response.json().get('debug_code')

verify_response = requests.post("http://localhost:8000/api/checkout/phone/verify-code",
                               json={"phone": "0788998877", "code": code})
token = verify_response.json().get('token')

headers = {"Authorization": f"Bearer {token}"}

# Get the address
response = requests.get("http://localhost:8000/api/checkout/addresses", headers=headers)
addresses = response.json().get('addresses', [])
print(f"\nAddresses: {len(addresses)}")
address_id = addresses[0]['id']

# Try to delete the last address
print(f"\nTrying to delete the last address (ID: {address_id}):")
response = requests.delete(f"http://localhost:8000/api/checkout/addresses/{address_id}", 
                          headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")