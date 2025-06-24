#!/usr/bin/env python3
"""Test image upload functionality"""

import requests
import os
from PIL import Image
import io

# First, let's create a test image
def create_test_image():
    """Create a test image for upload"""
    img = Image.new('RGB', (800, 600), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

# Login as admin
print("Logging in as admin...")
login_response = requests.post('http://localhost:8000/api/auth/admin/login', json={
    'username': '+40700000001',
    'password': 'admin123'
})

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()['data']['tokens']['access_token']
print("✓ Logged in successfully")

# Test single image upload
print("\nTesting single image upload...")
headers = {'Authorization': f'Bearer {token}'}
files = {'image': ('test_product.jpg', create_test_image(), 'image/jpeg')}

response = requests.post(
    'http://localhost:8000/api/admin/products/upload-image',
    headers=headers,
    files=files
)

if response.status_code == 200:
    data = response.json()
    print("✓ Image uploaded successfully!")
    print(f"  Filename: {data['data']['filename']}")
    print(f"  Main URL: {data['data']['url']}")
    print("  Available sizes:")
    for size, url in data['data']['sizes'].items():
        print(f"    - {size}: {url}")
else:
    print(f"✗ Upload failed: {response.status_code} - {response.text}")

# Test multiple image upload
print("\nTesting multiple image upload...")
files = [
    ('images', ('test1.jpg', create_test_image(), 'image/jpeg')),
    ('images', ('test2.jpg', create_test_image(), 'image/jpeg')),
    ('images', ('test3.jpg', create_test_image(), 'image/jpeg'))
]

response = requests.post(
    'http://localhost:8000/api/admin/products/upload-images',
    headers=headers,
    files=files
)

if response.status_code in [200, 207]:
    data = response.json()
    print(f"✓ {data['message']}")
    print(f"  Uploaded: {len(data['data']['uploaded'])} images")
    if data['data']['errors']:
        print(f"  Errors: {len(data['data']['errors'])}")
else:
    print(f"✗ Upload failed: {response.status_code} - {response.text}")