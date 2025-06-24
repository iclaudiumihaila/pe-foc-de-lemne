#!/usr/bin/env python3
"""
Fix admin user password
"""

import bcrypt
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_admin_password():
    # Connect to MongoDB directly
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGODB_DB', 'pe_foc_de_lemne')
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Find admin user
    admin = db.users.find_one({"role": "admin"})
    
    if admin:
        print(f"Found admin user: {admin.get('phone_number')}")
        
        # Set password
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Update user with password
        result = db.users.update_one(
            {"_id": admin["_id"]},
            {
                "$set": {
                    "password_hash": password_hash.decode('utf-8'),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✓ Admin password updated successfully")
            print(f"  Phone: {admin.get('phone_number')}")
            print(f"  Password: {password}")
        else:
            print("✗ Failed to update admin password")
    else:
        print("✗ No admin user found!")
        
        # Create one
        print("\nCreating admin user...")
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_user = {
            "phone_number": "+40700000000",
            "name": "Administrator",
            "role": "admin",
            "password_hash": password_hash.decode('utf-8'),
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.users.insert_one(admin_user)
        if result.inserted_id:
            print(f"✓ Admin user created successfully")
            print(f"  Phone: {admin_user['phone_number']}")
            print(f"  Password: {password}")

if __name__ == "__main__":
    fix_admin_password()