#!/usr/bin/env python3
"""Test cart in backend"""

from pymongo import MongoClient
import os

# Connect to MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['local_producer_app']

# Check carts
print("=== ALL CARTS IN DATABASE ===")
carts = list(db.carts.find())
for cart in carts:
    print(f"Session ID: {cart.get('session_id')}")
    print(f"Items: {len(cart.get('items', []))}")
    print(f"Created: {cart.get('created_at')}")
    print(f"Updated: {cart.get('updated_at')}")
    print("-" * 40)

# Check specific cart
cart_id = "cart_1750617115201_1gebhch9e"
print(f"\n=== LOOKING FOR CART: {cart_id} ===")
cart = db.carts.find_one({"session_id": cart_id})
if cart:
    print("Cart found!")
    print(f"Items: {cart.get('items')}")
else:
    print("Cart NOT found!")