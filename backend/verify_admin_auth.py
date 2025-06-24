#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_mongodb, get_database
from app.services.auth_service import AuthService
from bson import ObjectId

def verify_admin():
    # Initialize database
    init_mongodb()
    db = get_database()
    
    # Find admin user
    admin = db.users.find_one({'role': 'admin'})
    if not admin:
        print("No admin user found!")
        return
    
    print(f"Found admin user: {admin.get('phone_number')}")
    print(f"Has password hash: {'Yes' if admin.get('password_hash') else 'No'}")
    
    # Test authentication
    auth_service = AuthService()
    
    try:
        # Test with phone number
        result = auth_service.authenticate_admin(
            username=admin['phone_number'],
            password='admin123',
            ip_address='127.0.0.1'
        )
        print(f"\n✓ Authentication successful!")
        print(f"Access token: {result['tokens']['access_token'][:50]}...")
    except Exception as e:
        print(f"\n✗ Authentication failed: {str(e)}")
        
        # Debug password verification
        from werkzeug.security import check_password_hash
        if admin.get('password_hash'):
            is_valid = check_password_hash(admin['password_hash'], 'admin123')
            print(f"Password 'admin123' is valid: {is_valid}")

if __name__ == "__main__":
    verify_admin()