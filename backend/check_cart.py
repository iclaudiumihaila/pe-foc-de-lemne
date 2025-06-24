#!/usr/bin/env python3
"""
Check cart in database
"""

import os
import sys
from datetime import datetime
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

# Check all carts
print("=== All Carts in Database ===")
carts = list(db.carts.find())
print(f"Total carts: {len(carts)}")

for cart in carts:
    print(f"\nCart ID: {cart.get('_id')}")
    print(f"Session ID: {cart.get('session_id')}")
    print(f"Items: {len(cart.get('items', []))}")
    print(f"Created: {cart.get('created_at')}")
    print(f"Updated: {cart.get('updated_at')}")
    
    # Show items
    for item in cart.get('items', []):
        print(f"  - {item.get('name')} x{item.get('quantity')} @ {item.get('price')} RON")

# Check specific cart ID from localStorage
print("\n=== Checking Specific Cart ===")
cart_id = input("Enter cartId from browser localStorage: ").strip()
if cart_id:
    cart = db.carts.find_one({'session_id': cart_id})
    if cart:
        print(f"Found cart: {cart}")
    else:
        print(f"Cart not found with session_id: {cart_id}")