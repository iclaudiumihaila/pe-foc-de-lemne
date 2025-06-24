#!/usr/bin/env python3
import bcrypt
from app.database import get_database, init_mongodb
from app.config import DevelopmentConfig

# Initialize database
init_mongodb(DevelopmentConfig)
db = get_database()

# Find admin user
admin = db.users.find_one({"phone_number": "+40700000000"})
if admin:
    print(f"Admin found: {admin['name']}")
    print(f"Phone: {admin['phone_number']}")
    print(f"Role: {admin['role']}")
    print(f"Is verified: {admin.get('is_verified', False)}")
    print(f"Has password: {'password' in admin}")
    
    # Test password
    test_password = "admin123"
    if 'password' in admin:
        # Ensure password is bytes
        stored_password = admin['password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        result = bcrypt.checkpw(test_password.encode('utf-8'), stored_password)
        print(f"Password 'admin123' matches: {result}")
else:
    print("Admin user not found!")