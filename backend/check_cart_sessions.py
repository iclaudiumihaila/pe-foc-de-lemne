#!/usr/bin/env python3
"""Check cart sessions in database"""

from pymongo import MongoClient
from datetime import datetime
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['local_producer_app']

# Check cart sessions
cart_sessions = list(db.cart_sessions.find())

print(f"Total cart sessions: {len(cart_sessions)}")
print("-" * 80)

for cart in cart_sessions:
    print(f"Session ID: {cart.get('session_id')}")
    print(f"_id: {cart.get('_id')}")
    print(f"Items: {len(cart.get('items', []))}")
    if cart.get('items'):
        for item in cart['items']:
            print(f"  - {item.get('product_name', 'Unknown')} x {item.get('quantity')}")
    print(f"Created: {cart.get('created_at')}")
    print(f"Updated: {cart.get('updated_at')}")
    print(f"Expires: {cart.get('expires_at')}")
    
    # Check if expired
    if cart.get('expires_at'):
        is_expired = datetime.utcnow() > cart['expires_at']
        print(f"Expired: {is_expired}")
    
    print("-" * 80)

# Also check for the specific session ID we're looking for
session_id = "68595ba9e007086edd6d650b"
specific_cart = db.cart_sessions.find_one({'session_id': session_id})
if specific_cart:
    print(f"\nFound specific cart session: {session_id}")
    print(json.dumps(specific_cart, default=str, indent=2))
else:
    print(f"\nCart session {session_id} NOT FOUND")