#!/usr/bin/env python3
"""
Create a test cart in the database for checkout testing
"""

import os
import sys
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.database import init_mongodb, get_database
from app.config import Config

# Initialize database
init_mongodb(Config)
db = get_database()

# Define cart session ID that frontend will use
cart_session_id = "test_cart_checkout"

# Get products from database
products = list(db.products.find().limit(2))

if len(products) < 2:
    print("Error: Need at least 2 products in database")
    sys.exit(1)

# Create cart items
cart_items = []
for i, product in enumerate(products[:2]):
    item = {
        '_id': ObjectId(),
        'product_id': product['_id'],
        'name': product['name'],
        'price': product['price'],
        'quantity': 1,
        'image_url': product.get('image_url', ''),
        'added_at': datetime.utcnow()
    }
    cart_items.append(item)
    print(f"Adding to cart: {item['name']} - {item['price']} RON")

# Calculate totals
subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
total_items = sum(item['quantity'] for item in cart_items)

# Create cart document
cart = {
    '_id': ObjectId(),
    'session_id': cart_session_id,
    'items': cart_items,
    'total_items': total_items,
    'subtotal': subtotal,
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow(),
    'expires_at': datetime.utcnow().replace(hour=23, minute=59, second=59)
}

# Delete existing cart with same session ID
db.carts.delete_one({'session_id': cart_session_id})

# Insert new cart
result = db.carts.insert_one(cart)

print(f"\nCart created successfully!")
print(f"Cart ID: {result.inserted_id}")
print(f"Session ID: {cart_session_id}")
print(f"Total items: {total_items}")
print(f"Subtotal: {subtotal} RON")
print(f"\nUse this session ID in the frontend: {cart_session_id}")