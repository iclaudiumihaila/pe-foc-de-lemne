"""Test update address endpoint"""
import requests
import json

base_url = "http://localhost:8000/api/checkout"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6Iis0MDc1NTY2Nzc4OCIsImN1c3RvbWVyX2lkIjoiNjg1N2RkNmZjNjYwNTRkMmY3ODJhZWUwIiwiZXhwIjoxNzUwNjc1MTgzLCJpYXQiOjE3NTA1ODg3ODMsInR5cGUiOiJjaGVja291dF9zZXNzaW9uIn0.z3Q2WlsBJZTsFnxgow7jrZleC5un8yIQnJ5pMQr8-pU"
headers = {"Authorization": f"Bearer {token}"}

# First get addresses to find an ID
print("1. Getting current addresses:")
response = requests.get(f"{base_url}/addresses", headers=headers)
addresses = response.json().get('addresses', [])
if not addresses:
    print("No addresses found")
    exit(1)

# Take the first non-default address
address_to_update = None
for addr in addresses:
    if not addr['is_default']:
        address_to_update = addr
        break

if not address_to_update:
    address_to_update = addresses[0]

print(f"Address to update: {address_to_update['street']}, {address_to_update['city']}")
print(f"ID: {address_to_update['id']}")

# Test 2: Update address fields
print("\n2. Testing update with new data:")
update_data = {
    "street": "Strada Modificată 999",
    "notes": "Note actualizate - etaj 2"
}

headers['Content-Type'] = 'application/json'
response = requests.put(f"{base_url}/addresses/{address_to_update['id']}", 
                       json=update_data, headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 3: Update with partial data (only city)
print("\n3. Testing partial update (only city):")
response = requests.put(f"{base_url}/addresses/{address_to_update['id']}", 
                       json={"city": "Brașov"}, headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
if result.get('success'):
    addr = result['address']
    print(f"Updated address: {addr['street']}, {addr['city']}")

# Test 4: Set as default
print("\n4. Testing set_as_default:")
response = requests.put(f"{base_url}/addresses/{address_to_update['id']}", 
                       json={"set_as_default": True}, headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
if result.get('success'):
    print(f"Is default now: {result['address']['is_default']}")

# Test 5: Invalid address ID
print("\n5. Testing invalid address ID:")
response = requests.put(f"{base_url}/addresses/invalid-id-123", 
                       json={"city": "Test"}, headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 6: Non-existent address ID
print("\n6. Testing non-existent address ID:")
response = requests.put(f"{base_url}/addresses/507f1f77bcf86cd799439011", 
                       json={"city": "Test"}, headers=headers)
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")

# Test 7: Without authentication
print("\n7. Testing without authentication:")
response = requests.put(f"{base_url}/addresses/{address_to_update['id']}", 
                       json={"city": "Test"})
print(f"Status: {response.status_code}")
print(f"Error: {response.json().get('error', {}).get('message', 'N/A')}")