from flask import request, jsonify
from app.routes.admin import admin_bp
from app.models.product import Product
from app.database import get_database
from app.utils.auth_middleware import require_admin_auth as admin_required
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)

@admin_bp.route('/products', methods=['GET'])
@admin_bp.route('/products/', methods=['GET'])
@admin_required
def get_admin_products():
    """Get all products with pagination for admin"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        
        # Validate pagination
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Build query
        query = {}
        if available_only:
            query['is_available'] = True
        
        # Get database
        db = get_database()
        
        # Count total products
        total_items = db.products.count_documents(query)
        total_pages = (total_items + limit - 1) // limit
        
        # Get products with pagination
        sort_direction = 1 if sort_order == 'asc' else -1
        products = list(db.products.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit))
        
        # Get category names
        category_ids = [p.get('category_id') for p in products if p.get('category_id')]
        categories = {str(c['_id']): c['name'] for c in db.categories.find({'_id': {'$in': category_ids}})}
        
        # Format products for response
        formatted_products = []
        for product in products:
            # Use Product model's to_dict method for consistency
            try:
                # Create Product instance to leverage its formatting
                p = Product(product)
                product_dict = p.to_dict()
                
                # Add category name for admin display
                if product.get('category_id'):
                    product_dict['categoryName'] = categories.get(str(product['category_id']), 'Unknown')
                    product_dict['category'] = str(product['category_id'])
                
                # Ensure backward compatibility with admin panel expectations
                product_dict['active'] = product_dict.get('is_available', True)
                product_dict['stock'] = product_dict.get('stock_quantity', 0)
                product_dict['image'] = product_dict.get('images', [])[0] if product_dict.get('images') else ''
                product_dict['createdAt'] = product_dict.get('created_at', '')
                
                formatted_products.append(product_dict)
            except Exception as e:
                logger.error(f"Error formatting product {product.get('_id')}: {str(e)}")
                # Fallback to direct formatting
                formatted_products.append({
                    'id': str(product['_id']),
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'price': product.get('price', 0),
                    'category': str(product.get('category_id', '')),
                    'categoryName': categories.get(str(product.get('category_id', '')), 'Unknown'),
                    'active': product.get('is_available', True),
                    'stock': product.get('stock_quantity', 0),
                    'image': product.get('images', [])[0] if product.get('images') else '',
                    'createdAt': product.get('created_at', datetime.utcnow()).isoformat()
                })
        
        return jsonify({
            'products': formatted_products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_pages': total_pages,
                'total_items': total_items,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@admin_bp.route('/products/<product_id>', methods=['GET'])
@admin_required
def get_admin_product(product_id):
    """Get single product details"""
    try:
        product = Product.find_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get category name
        db = get_database()
        category_name = 'Unknown'
        if product.category_id:
            category = db.categories.find_one({'_id': product.category_id})
            if category:
                category_name = category['name']
        
        # Format response with backward compatibility
        product_dict = product.to_dict()
        product_dict.update({
            'category': str(product.category_id) if product.category_id else '',
            'categoryName': category_name,
            'active': product_dict.get('is_available', True),
            'stock': product_dict.get('stock_quantity', 0),
            'image': product_dict.get('images', [])[0] if product_dict.get('images') else '',
            'createdAt': product_dict.get('created_at', '')
        })
        
        return jsonify(product_dict)
        
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        return jsonify({'error': 'Failed to fetch product'}), 500

@admin_bp.route('/products', methods=['POST'])
@admin_bp.route('/products/', methods=['POST'])
@admin_required
def create_admin_product():
    """Create new product using Product model"""
    try:
        data = request.get_json()
        
        # Map admin panel fields to Product model fields
        product_data = {
            'name': data.get('name'),
            'description': data.get('description', ''),
            'price': data.get('price'),
            'category_id': data.get('category_id') or data.get('category'),  # Support both field names
            'subcategory_id': data.get('subcategory_id'),
            'images': [],  # Handle images separately
            'stock_quantity': int(data.get('stock_quantity', data.get('stock', 0))),
            'unit': data.get('unit', 'bucată'),
            'is_available': data.get('is_available', data.get('active', True)),
            'weight_grams': data.get('weight_grams'),
            'preparation_time_hours': data.get('preparation_time_hours'),
            'producer': data.get('producer'),
            'is_organic': data.get('is_organic', False),
            'is_seasonal': data.get('is_seasonal', False),
            'allergens': data.get('allergens', []),
            'nutritional_info': data.get('nutritional_info', {}),
            'storage_instructions': data.get('storage_instructions'),
            'serving_suggestions': data.get('serving_suggestions')
        }
        
        # Handle images
        if data.get('images') and isinstance(data['images'], list):
            product_data['images'] = data['images']
        elif data.get('image'):
            # Convert single image to array
            product_data['images'] = [data['image']]
        
        # Create product using model
        product = Product.create(**product_data)
        
        logger.info(f"Product created successfully: {product.name} (ID: {product._id})")
        
        return jsonify({
            'id': str(product._id),
            'message': 'Product created successfully'
        }), 201
        
    except DuplicateKeyError:
        return jsonify({'error': 'A product with this name already exists'}), 400
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': f'Failed to create product: {str(e)}'}), 500

@admin_bp.route('/products/<product_id>', methods=['PUT'])
@admin_required
def update_admin_product(product_id):
    """Update product using Product model"""
    try:
        # Find existing product
        product = Product.find_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Build update data, mapping admin fields to model fields
        update_data = {}
        
        # Handle field mappings
        field_mappings = {
            'name': 'name',
            'description': 'description',
            'price': 'price',
            'category': 'category_id',
            'category_id': 'category_id',
            'subcategory_id': 'subcategory_id',
            'active': 'is_available',
            'is_available': 'is_available',
            'stock': 'stock_quantity',
            'stock_quantity': 'stock_quantity',
            'unit': 'unit',
            'weight_grams': 'weight_grams',
            'preparation_time_hours': 'preparation_time_hours',
            'producer': 'producer',
            'is_organic': 'is_organic',
            'is_seasonal': 'is_seasonal',
            'allergens': 'allergens',
            'nutritional_info': 'nutritional_info',
            'storage_instructions': 'storage_instructions',
            'serving_suggestions': 'serving_suggestions'
        }
        
        for admin_field, model_field in field_mappings.items():
            if admin_field in data:
                update_data[model_field] = data[admin_field]
        
        # Handle images specially
        if 'images' in data and isinstance(data['images'], list):
            update_data['images'] = data['images']
        elif 'image' in data:
            # Convert single image to array
            update_data['images'] = [data['image']] if data['image'] else []
        
        # Update product
        success = product.update(update_data)
        
        if success:
            logger.info(f"Product updated successfully: {product_id}")
            return jsonify({'message': 'Product updated successfully'})
        else:
            return jsonify({'error': 'No changes were made'}), 400
        
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        return jsonify({'error': f'Failed to update product: {str(e)}'}), 500

@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_admin_product(product_id):
    """Delete product (soft delete)"""
    try:
        # Find product
        product = Product.find_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Soft delete by setting is_available to false and stock to 0
        product.update({
            'is_available': False,
            'stock_quantity': 0
        })
        
        logger.info(f"Product soft deleted: {product_id}")
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return jsonify({'error': 'Failed to delete product'}), 500