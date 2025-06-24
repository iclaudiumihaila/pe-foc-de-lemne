#!/usr/bin/env python3
"""
Check admin users in the database
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database, init_mongodb
from app.config import DevelopmentConfig

def check_admin_users():
    """Check for admin users in the database"""
    try:
        # Initialize database connection
        init_mongodb(DevelopmentConfig)
        db = get_database()
        
        print("Checking for admin users in MongoDB...")
        print("=" * 50)
        
        # Check if users collection exists
        collections = db.list_collection_names()
        if 'users' not in collections:
            print("ERROR: 'users' collection does not exist!")
            print(f"Available collections: {collections}")
            return
        
        # Count total users
        total_users = db.users.count_documents({})
        print(f"\nTotal users in database: {total_users}")
        
        # Find admin users
        admin_users = list(db.users.find({"role": "admin"}))
        print(f"Admin users found: {len(admin_users)}")
        
        if admin_users:
            print("\nAdmin User Details:")
            print("-" * 50)
            for idx, admin in enumerate(admin_users, 1):
                print(f"\nAdmin #{idx}:")
                print(f"  ID: {admin.get('_id')}")
                print(f"  Name: {admin.get('name', 'N/A')}")
                print(f"  Phone: {admin.get('phone_number', 'N/A')}")
                print(f"  Role: {admin.get('role')}")
                print(f"  Created: {admin.get('created_at', 'N/A')}")
                print(f"  Last Login: {admin.get('last_login', 'Never')}")
                print(f"  Has Password: {'Yes' if admin.get('password') else 'No'}")
        else:
            print("\nNo admin users found in database!")
            print("\nTo create an admin user, run: python seed_data.py")
        
        # Check for users with different role values
        print("\n" + "=" * 50)
        print("Checking all unique roles in database:")
        roles = db.users.distinct("role")
        print(f"Found roles: {roles}")
        
        # Count users by role
        for role in roles:
            count = db.users.count_documents({"role": role})
            print(f"  {role}: {count} users")
        
        # Check if there's an admin_users collection (legacy)
        if 'admin_users' in collections:
            admin_count = db.admin_users.count_documents({})
            print(f"\nWARNING: Found legacy 'admin_users' collection with {admin_count} documents")
            print("This collection is not used by the current application")
            
    except Exception as e:
        print(f"\nError checking admin users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin_users()