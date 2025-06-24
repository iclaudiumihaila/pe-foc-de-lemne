#!/usr/bin/env python3
"""
Simple test to verify admin authentication
"""

import bcrypt
from app.database import get_database

def check_admin_auth():
    db = get_database()
    
    # Find admin user
    admin = db.users.find_one({"role": "admin"})
    
    if admin:
        print(f"Admin found:")
        print(f"  Phone: {admin.get('phone_number')}")
        print(f"  Name: {admin.get('name')}")
        print(f"  Has password_hash: {'password_hash' in admin}")
        
        if 'password_hash' in admin:
            # Test password verification
            test_password = "admin123"
            stored_hash = admin['password_hash']
            
            # Handle both string and bytes
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            matches = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash)
            print(f"  Password 'admin123' matches: {matches}")
            
            # Show first few chars of hash
            print(f"  Hash starts with: {admin['password_hash'][:20]}...")
    else:
        print("No admin user found!")
        
    # Show all users
    print("\nAll users:")
    for user in db.users.find():
        print(f"  - {user.get('phone_number')} ({user.get('role')}) - has password: {'password_hash' in user}")

if __name__ == "__main__":
    check_admin_auth()