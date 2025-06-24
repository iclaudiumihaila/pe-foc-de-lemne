#!/usr/bin/env python3
"""Clear all test data including carts, sessions, and customer data"""

from pymongo import MongoClient
import os

# Connect to MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['local_producer_app']

# Clear all carts
print("Clearing all carts...")
result = db.carts.delete_many({})
print(f"Deleted {result.deleted_count} carts")

# Clear all sessions
print("\nClearing all sessions...")
result = db.sessions.delete_many({})
print(f"Deleted {result.deleted_count} sessions")

# Clear test customer phone records
print("\nClearing test customer phone records...")
result = db.customer_phones.delete_many({"phone": "0775156791"})
print(f"Deleted {result.deleted_count} customer phone records")

# Clear test customer addresses
print("\nClearing test customer addresses...")
result = db.customer_addresses.delete_many({"phone": "0775156791"})
print(f"Deleted {result.deleted_count} customer addresses")

# Clear test verification codes
print("\nClearing test verification codes...")
result = db.verification_codes.delete_many({"phone": "0775156791"})
print(f"Deleted {result.deleted_count} verification codes")

# Clear test SMS logs
print("\nClearing test SMS logs...")
result = db.sms_logs.delete_many({"phone": "0775156791"})
print(f"Deleted {result.deleted_count} SMS logs")

print("\n✅ All test data cleared successfully!")