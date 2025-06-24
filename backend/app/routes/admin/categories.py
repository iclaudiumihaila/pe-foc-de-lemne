from flask import request, jsonify
from app.routes.admin import admin_bp
from app.models.category import Category
from app.database import get_database
from app.utils.auth_middleware import require_admin_auth as admin_required
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

@admin_bp.route('/categories', methods=['GET'])
@admin_bp.route('/categories/', methods=['GET'])
@admin_required
def get_admin_categories():
    """Get all categories"""
    try:
        db = get_database()
        categories = list(db.categories.find())
        
        formatted_categories = []
        for category in categories:
            formatted_categories.append({
                'id': str(category['_id']),
                'name': category['name'],
                'slug': category.get('slug', ''),
                'description': category.get('description', ''),
                'parent': str(category.get('parent', '')) if category.get('parent') else None,
                'order': category.get('order', 0),
                'active': category.get('active', True)
            })
        
        return jsonify({'categories': formatted_categories})
        
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({'error': 'Failed to fetch categories'}), 500

@admin_bp.route('/categories/tree', methods=['GET'])
@admin_required
def get_admin_categories_tree():
    """Get categories in hierarchical tree structure"""
    try:
        db = get_database()
        categories = list(db.categories.find().sort('order', 1))
        
        # Build tree structure
        category_map = {}
        roots = []
        
        # First pass: create category map
        for cat in categories:
            cat_data = {
                'id': str(cat['_id']),
                'name': cat['name'],
                'slug': cat.get('slug', ''),
                'description': cat.get('description', ''),
                'order': cat.get('order', 0),
                'active': cat.get('active', True),
                'is_active': cat.get('is_active', cat.get('active', True)),  # Support both field names
                'parent': str(cat.get('parent', '')) if cat.get('parent') else None,
                'parent_id': str(cat.get('parent', '')) if cat.get('parent') else None,  # Duplicate for frontend compatibility
                'children': []
            }
            category_map[str(cat['_id'])] = cat_data
        
        # Second pass: build tree
        for cat in categories:
            cat_id = str(cat['_id'])
            parent_id = str(cat.get('parent', '')) if cat.get('parent') else None
            
            if parent_id and parent_id in category_map:
                category_map[parent_id]['children'].append(category_map[cat_id])
            else:
                roots.append(category_map[cat_id])
        
        return jsonify({'categories': roots})
        
    except Exception as e:
        logger.error(f"Error fetching category tree: {str(e)}")
        return jsonify({'error': 'Failed to fetch category tree'}), 500

@admin_bp.route('/categories', methods=['POST'])
@admin_bp.route('/categories/', methods=['POST'])
@admin_required
def create_admin_category():
    """Create new category"""
    try:
        db = get_database()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category with same name exists
        existing = db.categories.find_one({'name': data['name']})
        if existing:
            return jsonify({'error': 'Category with this name already exists'}), 400
        
        # Create category document
        category = {
            'name': data['name'],
            'slug': data.get('slug', data['name'].lower().replace(' ', '-')),
            'description': data.get('description', ''),
            'order': data.get('order', 0),
            'active': data.get('active', True),
            'is_active': data.get('active', True)  # Keep both for compatibility
        }
        
        # Add parent if provided
        if data.get('parent'):
            category['parent'] = ObjectId(data['parent'])
        
        # Insert category
        result = db.categories.insert_one(category)
        
        return jsonify({
            'id': str(result.inserted_id),
            'message': 'Category created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        return jsonify({'error': 'Failed to create category'}), 500

@admin_bp.route('/categories/<category_id>', methods=['PUT'])
@admin_required
def update_admin_category(category_id):
    """Update category"""
    try:
        db = get_database()
        data = request.get_json()
        
        # Build update document
        update = {}
        if 'name' in data:
            update['name'] = data['name']
        if 'slug' in data:
            update['slug'] = data['slug']
        if 'description' in data:
            update['description'] = data['description']
        if 'parent' in data:
            update['parent'] = ObjectId(data['parent']) if data['parent'] else None
        if 'order' in data:
            update['order'] = data['order']
        if 'active' in data:
            update['active'] = data['active']
            update['is_active'] = data['active']  # Keep both for compatibility
        
        # Update category
        result = db.categories.update_one(
            {'_id': ObjectId(category_id)},
            {'$set': update}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({'message': 'Category updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        return jsonify({'error': 'Failed to update category'}), 500

@admin_bp.route('/categories/<category_id>', methods=['DELETE'])
@admin_required
def delete_admin_category(category_id):
    """Delete category (with product check)"""
    try:
        db = get_database()
        
        # Check if category has products
        product_count = db.products.count_documents({'category': ObjectId(category_id)})
        if product_count > 0:
            return jsonify({
                'error': f'Cannot delete category. {product_count} products are using this category.'
            }), 400
        
        # Check if category has subcategories
        subcategory_count = db.categories.count_documents({'parent': ObjectId(category_id)})
        if subcategory_count > 0:
            return jsonify({
                'error': f'Cannot delete category. {subcategory_count} subcategories exist.'
            }), 400
        
        # Delete category
        result = db.categories.delete_one({'_id': ObjectId(category_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({'message': 'Category deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        return jsonify({'error': 'Failed to delete category'}), 500