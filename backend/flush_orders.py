#!/usr/bin/env python3
"""
Script to flush all orders from the database and reset the order counter
"""

from pymongo import MongoClient
from app.config import Config

def flush_all_orders():
    """Delete all orders and reset the order counter"""
    # Connect to MongoDB
    client = MongoClient(Config.MONGODB_URI)
    db = client[Config.MONGODB_DB_NAME]
    
    # Delete all orders
    result = db.orders.delete_many({})
    print(f"Deleted {result.deleted_count} orders from the database")
    
    # Reset the order counter to start from 10000
    db.order_sequences.delete_many({})
    print("Reset order sequences")
    
    # Set the global counter to 10000
    db.order_sequences.update_one(
        {'_id': 'global_order_counter'},
        {'$set': {'sequence': 10000}},
        upsert=True
    )
    print("Set order counter to start from 10000")
    
    # Also clear any cart sessions if needed
    cart_result = db.carts.delete_many({})
    print(f"Deleted {cart_result.deleted_count} cart sessions")
    
    print("\nAll orders have been flushed successfully!")
    print("Next order number will be: 10001")

if __name__ == '__main__':
    flush_all_orders()