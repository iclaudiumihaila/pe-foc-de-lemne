#!/usr/bin/env python3
from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]

# Find the product named 'asdasdasd' that was mentioned in the fix output
product = db.products.find_one({'name': 'asdasdasd'})
if product:
    print('Product found: asdasdasd')
    for key, value in product.items():
        if key != '_id':
            print(f'  {key}: {value}')
        else:
            print(f'  {key}: {str(value)}')