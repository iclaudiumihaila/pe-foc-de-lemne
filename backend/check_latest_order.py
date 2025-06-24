#!/usr/bin/env python3
"""Check the latest order in the database"""

from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]

# Get the latest order
latest_order = db.orders.find_one(sort=[('created_at', -1)])
if latest_order:
    print(f"Latest order ID: {latest_order.get('_id')}")
    print(f"Order number: {latest_order.get('order_number')}")
    print(f"Customer: {latest_order.get('customer_name')}")
    print(f"Phone: {latest_order.get('customer_phone')}")
    print(f"Total: {latest_order.get('total')}")
    print(f"Status: {latest_order.get('status')}")
    print(f"Items: {len(latest_order.get('items', []))}")
else:
    print('No orders found')

# Also check order counter
counter = db.order_sequences.find_one({'_id': 'global_order_counter'})
if counter:
    print(f"\nCurrent order counter: {counter.get('sequence')}")
else:
    print("\nNo order counter found")