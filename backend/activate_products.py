#!/usr/bin/env python3
"""Activate all products in the database."""

from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['local_producer_app']

# Update all products to be active
result = db.products.update_many(
    {},
    {
        '$set': {
            'is_available': True,
            'updated_at': datetime.utcnow()
        }
    }
)

print(f"Updated {result.modified_count} products to be active")

# Also activate all categories
result = db.categories.update_many(
    {},
    {
        '$set': {
            'is_active': True,
            'updated_at': datetime.utcnow()
        }
    }
)

print(f"Updated {result.modified_count} categories to be active")

# Show current status
products = list(db.products.find({}, {'name': 1, 'is_available': 1}))
print("\nCurrent products:")
for p in products:
    print(f"  - {p['name']}: available={p.get('is_available', False)}")