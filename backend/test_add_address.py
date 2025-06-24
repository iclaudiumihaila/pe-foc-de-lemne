"""Test add address endpoint"""
import requests
import json

base_url = "http://localhost:8000/api/checkout"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZSI6Iis0MDc1NTY2Nzc4OCIsImN1c3RvbWVyX2lkIjoiNjg1N2RkNmZjNjYwNTRkMmY3ODJhZWUwIiwiZXhwIjoxNzUwNjc1MTgzLCJpYXQiOjE3NTA1ODg3ODMsInR5cGUiOiJjaGVja291dF9zZXNzaW9uIn0.z3Q2WlsBJZTsFnxgow7jrZleC5un8yIQnJ5pMQr8-pU"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Test 1: Add a valid address
print("1. Testing valid address:")
address_data = {
    "street": "Strada Republicii 45, Bl. B3, Ap. 7",
    "city": "Constanța",
    "county": "Constanța",
    "postal_code": "900001",
    "notes": "Lângă farmacia Dona"
}

response = requests.post(f"{base_url}/addresses", json=address_data, headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 2: Add address with validation errors
print("\n2. Testing invalid address (missing fields):")
invalid_data = {
    "street": "Test",
    "city": "",
    "county": "InvalidCounty",
    "postal_code": "123"
}

response = requests.post(f"{base_url}/addresses", json=invalid_data, headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 3: Add address without authentication
print("\n3. Testing without authentication:")
response = requests.post(f"{base_url}/addresses", json=address_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Test 4: Add address with set_as_default
print("\n4. Testing add with set_as_default:")
default_address = {
    "street": "Bulevardul Unirii 200",
    "city": "București",
    "county": "București",
    "postal_code": "030001",
    "notes": "Etaj 5, interfon 501",
    "set_as_default": True
}

response = requests.post(f"{base_url}/addresses", json=default_address, headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))