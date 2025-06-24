#!/usr/bin/env python3
"""Create a test product directly in the database"""

from app import create_app
from app.config import DevelopmentConfig
from app.models.product import Product
from bson import ObjectId

# Initialize the app
app = create_app(DevelopmentConfig)
with app.app_context():
    from app.database import get_database
    db = get_database()
    
    # Get a valid category
    category = db.categories.find_one({'is_active': True})
    if not category:
        print("No active categories found!")
        exit(1)
    
    # Get an admin user
    admin = db.users.find_one({'role': 'admin'})
    if not admin:
        print("No admin user found!")
        admin_id = ObjectId()
    else:
        admin_id = admin['_id']
    
    try:
        # Create product using the Product model
        product = Product.create(
            name="Test Product Upload Only",
            description="This is a test product created to verify the system works with upload-only images",
            price=29.99,
            category_id=category['_id'],
            created_by=admin_id,
            images=[],  # No images initially
            stock_quantity=15,
            weight_grams=500,
            preparation_time_hours=24
        )
        
        print(f"✅ Product created successfully!")
        print(f"Product ID: {product._id}")
        print(f"Product Name: {product.name}")
        print(f"Category: {category['name']}")
        print(f"Price: {product.price} RON")
        print(f"Stock: {product.stock_quantity}")
        
    except Exception as e:
        print(f"❌ Error creating product: {e}")