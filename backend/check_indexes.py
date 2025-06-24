#!/usr/bin/env python3
"""Check MongoDB indexes"""

from app import create_app
from app.database import get_database

app = create_app()

with app.app_context():
    db = get_database()
    
    # Check products collection indexes
    print("Products Collection Indexes:")
    for idx in db.products.list_indexes():
        print(f"  {idx}")
    
    print("\nCreating text index for products...")
    try:
        # Create text index on name and description fields
        db.products.create_index([
            ('name', 'text'),
            ('description', 'text')
        ], name='product_text_search')
        print("Text index created successfully!")
    except Exception as e:
        print(f"Error creating text index: {e}")
    
    print("\nProducts Collection Indexes after creating text index:")
    for idx in db.products.list_indexes():
        print(f"  {idx}")