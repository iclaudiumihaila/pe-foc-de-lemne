#!/usr/bin/env python3
"""Check admin user fields"""

from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]

admin = db.users.find_one({'role': 'admin'})
if admin:
    print('Admin user fields:')
    for key in admin.keys():
        if key != 'password_hash':
            print(f'  {key}: {admin[key]}')
        else:
            print(f'  {key}: [hidden]')
else:
    print("No admin user found")