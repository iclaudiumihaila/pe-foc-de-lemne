from flask import request, jsonify
from app.routes.admin import admin_bp
from app.models.product import Product
from app.models.category import Category
from app.database import get_database
from app.utils.auth_middleware import require_admin_auth as admin_required
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@admin_bp.route('/products', methods=['GET'])
@admin_bp.route('/products/', methods=['GET'])
@admin_required
def get_admin_products():
    """Get all products with pagination, search, and filters"""
    try:
        db = get_database()
        # Pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Search and filters
        search = request.args.get('search', '')
        category = request.args.get('category')
        status = request.args.get('status')
        
        # Build query
        query = {}
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        if category:
            query['category'] = ObjectId(category)
        if status:
            query['active'] = status == 'active'
        
        # Get total count
        total = db.products.count_documents(query)
        
        # Get products
        products = list(db.products.find(query).skip(skip).limit(limit))
        
        # Get category names
        category_ids = [p.get('category') for p in products if p.get('category')]
        categories = {str(c['_id']): c['name'] for c in db.categories.find({'_id': {'$in': category_ids}})}
        
        # Format response
        formatted_products = []
        for product in products:
            formatted_products.append({
                'id': str(product['_id']),
                'name': product['name'],
                'description': product.get('description', ''),
                'price': product['price'],
                'category': str(product.get('category', '')),
                'categoryName': categories.get(str(product.get('category', '')), ''),
                'active': product.get('active', True),
                'stock': product.get('stock', 0),
                'image': product.get('image', ''),
                'createdAt': product.get('createdAt', datetime.utcnow()).isoformat()
            })
        
        return jsonify({
            'products': formatted_products,
            'total': total,
            'page': page,
            'totalPages': (total + limit - 1) // limit
        })
        
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@admin_bp.route('/products/<product_id>', methods=['GET'])
@admin_required
def get_admin_product(product_id):
    """Get single product details"""
    try:
        db = get_database()
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get category name
        category_name = ''
        if product.get('category'):
            category = db.categories.find_one({'_id': product['category']})
            if category:
                category_name = category['name']
        
        return jsonify({
            'id': str(product['_id']),
            'name': product['name'],
            'description': product.get('description', ''),
            'price': product['price'],
            'category': str(product.get('category', '')),
            'categoryName': category_name,
            'active': product.get('active', True),
            'stock': product.get('stock', 0),
            'image': product.get('image', ''),
            'createdAt': product.get('createdAt', datetime.utcnow()).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        return jsonify({'error': 'Failed to fetch product'}), 500

@admin_bp.route('/products', methods=['POST'])
@admin_bp.route('/products/', methods=['POST'])
@admin_required
def create_admin_product():
    """Create new product"""
    try:
        db = get_database()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('price'):
            return jsonify({'error': 'Name and price are required'}), 400
        
        # Create product document
        product = {
            'name': data['name'],
            'description': data.get('description', ''),
            'price': float(data['price']),
            'active': data.get('active', True),
            'stock': int(data.get('stock', 0)),
            'image': data.get('image', ''),
            'createdAt': datetime.utcnow()
        }
        
        # Add category if provided
        if data.get('category'):
            product['category'] = ObjectId(data['category'])
        
        # Insert product
        result = db.products.insert_one(product)
        product['_id'] = result.inserted_id
        
        return jsonify({
            'id': str(product['_id']),
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500

@admin_bp.route('/products/<product_id>', methods=['PUT'])
@admin_required
def update_admin_product(product_id):
    """Update product"""
    try:
        db = get_database()
        data = request.get_json()
        
        # Build update document
        update = {}
        if 'name' in data:
            update['name'] = data['name']
        if 'description' in data:
            update['description'] = data['description']
        if 'price' in data:
            update['price'] = float(data['price'])
        if 'category' in data:
            update['category'] = ObjectId(data['category']) if data['category'] else None
        if 'active' in data:
            update['active'] = data['active']
        if 'stock' in data:
            update['stock'] = int(data['stock'])
        if 'image' in data:
            update['image'] = data['image']
        
        # Update product
        result = db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'message': 'Product updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        return jsonify({'error': 'Failed to update product'}), 500

@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_admin_product(product_id):
    """Delete product"""
    try:
        db = get_database()
        # Soft delete by setting active to false
        result = db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'active': False}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return jsonify({'error': 'Failed to delete product'}), 500