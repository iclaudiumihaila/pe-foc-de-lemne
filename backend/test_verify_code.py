"""Test verify code endpoint"""
import requests
import json

# First send a code
send_url = "http://localhost:8000/api/checkout/phone/send-code"
verify_url = "http://localhost:8000/api/checkout/phone/verify-code"

phone = "0788554433"

# Send code
print("Sending code...")
response = requests.post(send_url, json={"phone": phone})
print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success') and result.get('debug_code'):
    code = result['debug_code']
    print(f"\nVerifying with code: {code}")
    
    # Verify code
    response = requests.post(verify_url, json={"phone": phone, "code": code})
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))