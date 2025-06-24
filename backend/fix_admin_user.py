#!/usr/bin/env python3
"""Fix admin user password"""

from pymongo import MongoClient
from app.config import Config
import bcrypt
from datetime import datetime

client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]

# Find admin user
admin = db.users.find_one({"role": "admin"})
if admin:
    print(f"Found admin user: {admin['phone_number']}")
    
    # Hash password using bcrypt (same as User model)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw("admin123".encode('utf-8'), salt)
    password_hash = hashed.decode('utf-8')
    
    # Update password
    result = db.users.update_one(
        {"_id": admin["_id"]},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.utcnow()
            }
        }
    )
    print("✓ Updated admin password to: admin123")
else:
    print("No admin user found")