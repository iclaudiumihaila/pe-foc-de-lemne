"""Test send code endpoint"""
import requests
import json

url = "http://localhost:8000/api/checkout/phone/send-code"
data = {"phone": "0745123456"}

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")