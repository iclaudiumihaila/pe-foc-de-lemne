"""Test delete address endpoint"""
import requests
import json

base_url = "http://localhost:8000/api/checkout"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6Iis0MDc1NTY2Nzc4OCIsImN1c3RvbWVyX2lkIjoiNjg1N2RkNmZjNjYwNTRkMmY3ODJhZWUwIiwiZXhwIjoxNzUwNjc1MTgzLCJpYXQiOjE3NTA1ODg3ODMsInR5cGUiOiJjaGVja291dF9zZXNzaW9uIn0.z3Q2WlsBJZTsFnxgow7jrZleC5un8yIQnJ5pMQr8-pU"
headers = {"Authorization": f"Bearer {token}"}

# First get addresses
print("1. Getting current addresses:")
response = requests.get(f"{base_url}/addresses", headers=headers)
addresses = response.json().get('addresses', [])
print(f"Total addresses: {len(addresses)}")

# Find a non-default address to delete
address_to_delete = None
default_address = None
for addr in addresses:
    if addr['is_default']:
        default_address = addr
    else:
        address_to_delete = addr

if not address_to_delete and addresses:
    address_to_delete = addresses[0]

print(f"\nDefault address: {default_address['street'][:30]}...")
print(f"Address to delete: {address_to_delete['street'][:30]}... (ID: {address_to_delete['id']})")

# Test 2: Delete a non-default address
print("\n2. Testing delete non-default address:")
response = requests.delete(f"{base_url}/addresses/{address_to_delete['id']}", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 3: Delete the default address
print("\n3. Testing delete default address:")
response = requests.delete(f"{base_url}/addresses/{default_address['id']}", headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

# Test 4: Try to delete with invalid ID
print("\n4. Testing delete with invalid ID:")
response = requests.delete(f"{base_url}/addresses/invalid-id", headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 5: Try to delete non-existent address
print("\n5. Testing delete non-existent address:")
response = requests.delete(f"{base_url}/addresses/507f1f77bcf86cd799439011", headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 6: Without authentication
print("\n6. Testing without authentication:")
response = requests.delete(f"{base_url}/addresses/{address_to_delete['id']}")
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 7: Check remaining addresses
print("\n7. Checking remaining addresses:")
response = requests.get(f"{base_url}/addresses", headers=headers)
addresses = response.json().get('addresses', [])
print(f"Remaining addresses: {len(addresses)}")
for addr in addresses:
    print(f"  - {addr['street'][:30]}... (default: {addr['is_default']})")