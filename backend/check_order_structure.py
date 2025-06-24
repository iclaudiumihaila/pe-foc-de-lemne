#!/usr/bin/env python3
"""Check order structure in database"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('MONGODB_DB', 'pe_foc_de_lemne')

client = MongoClient(mongo_uri)
db = client[db_name]

# Find one order
order = db.orders.find_one()

if order:
    print("Order structure:")
    print(f"ID: {order['_id']}")
    print(f"Status: {order.get('status')}")
    print(f"Items count: {len(order.get('items', []))}")
    
    if order.get('items'):
        print("\nFirst item structure:")
        item = order['items'][0]
        print(json.dumps(item, indent=2, default=str))
else:
    print("No orders found")