"""Test JWT authentication"""
import requests
import json

base_url = "http://localhost:8000/api/checkout"
phone = "0755667788"

# Step 1: Send verification code
print("1. Sending verification code...")
response = requests.post(f"{base_url}/phone/send-code", json={"phone": phone})
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if not result.get('success'):
    print("Failed to send code")
    exit(1)

code = result.get('debug_code')
print(f"\nCode received: {code}")

# Step 2: Verify code and get token
print("\n2. Verifying code...")
response = requests.post(f"{base_url}/phone/verify-code", json={"phone": phone, "code": code})
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if not result.get('success'):
    print("Failed to verify code")
    exit(1)

token = result.get('token')
print(f"\nToken received: {token[:50]}...")

# Step 3: Test authenticated endpoint without token
print("\n3. Testing /addresses WITHOUT token...")
response = requests.get(f"{base_url}/addresses")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Step 4: Test authenticated endpoint with token
print("\n4. Testing /addresses WITH token...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/addresses", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Step 5: Test with invalid token
print("\n5. Testing /addresses with INVALID token...")
headers = {"Authorization": "Bearer invalid-token-12345"}
response = requests.get(f"{base_url}/addresses", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))