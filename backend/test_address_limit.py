"""Test address limit"""
import requests
from app.database import init_mongodb
from app.models.customer_phone import CustomerPhone
from bson import ObjectId
from datetime import datetime

# Initialize database
init_mongodb()

# Create a customer with 49 addresses
phone = "+40799112233"
customer = CustomerPhone({'phone': phone})

# Add 49 addresses
customer.addresses = []
for i in range(49):
    customer.addresses.append({
        '_id': ObjectId(),
        'street': f'Test Street {i+1}',
        'city': 'Test City',
        'county': 'Cluj',
        'postal_code': '400001',
        'notes': '',
        'is_default': i == 0,
        'usage_count': 0,
        'created_at': datetime.utcnow()
    })

customer.save()
print(f"Created customer with {len(customer.addresses)} addresses")

# Get token
send_response = requests.post("http://localhost:8000/api/checkout/phone/send-code", 
                             json={"phone": "0799112233"})
code = send_response.json().get('debug_code')

verify_response = requests.post("http://localhost:8000/api/checkout/phone/verify-code",
                               json={"phone": "0799112233", "code": code})
token = verify_response.json().get('token')

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Try to add 50th address (should succeed)
print("\nAdding 50th address (should succeed):")
response = requests.post("http://localhost:8000/api/checkout/addresses",
                        json={
                            "street": "Address 50",
                            "city": "București",
                            "county": "București",
                            "postal_code": "010101",
                            "notes": "The 50th address"
                        },
                        headers=headers)
print(f"Status: {response.status_code}")
print(f"Success: {response.json().get('success')}")
print(f"Total addresses: {response.json().get('total_addresses', 'N/A')}")

# Try to add 51st address (should fail)
print("\nAdding 51st address (should fail):")
response = requests.post("http://localhost:8000/api/checkout/addresses",
                        json={
                            "street": "Address 51",
                            "city": "București",
                            "county": "București",
                            "postal_code": "010101",
                            "notes": "Should fail"
                        },
                        headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")