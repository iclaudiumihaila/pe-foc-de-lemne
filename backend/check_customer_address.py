#!/usr/bin/env python3
"""Check customer address structure"""

from pymongo import MongoClient
from bson import ObjectId
import os

# Connect to MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['local_producer_app']

# Check customer
customer = db.customer_phones.find_one({"phone": "+40775156791"})
if customer:
    print("Customer found!")
    print(f"ID: {customer['_id']}")
    print(f"Phone: {customer['phone']}")
    print(f"Addresses: {len(customer.get('addresses', []))}")
    
    for i, addr in enumerate(customer.get('addresses', [])):
        print(f"\nAddress {i+1}:")
        print(f"  ID: {addr.get('_id')} (type: {type(addr.get('_id'))})")
        print(f"  Street: {addr.get('street')}")
        print(f"  City: {addr.get('city')}")
        print(f"  Is Default: {addr.get('is_default')}")
        
        # Check if ID matches
        test_id = "685840702489e3424f4920a9"
        print(f"\n  Comparing with frontend ID: {test_id}")
        print(f"  String match: {str(addr.get('_id')) == test_id}")
        print(f"  ObjectId match: {addr.get('_id') == ObjectId(test_id)}")
else:
    print("Customer not found!")