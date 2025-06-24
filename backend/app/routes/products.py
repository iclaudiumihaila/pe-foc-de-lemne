"""
Product Catalog Routes for Local Producer Web Application

This module provides product catalog endpoints including listing, search,
individual product details, and admin product management.
"""

import logging
import re
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.utils.validators import validate_json
from app.utils.error_handlers import (
    ValidationError, AuthorizationError, NotFoundError,
    success_response, create_error_response
)
from app.utils.auth_middleware import require_admin_auth, log_admin_action

# Create products blueprint
products_bp = Blueprint('products', __name__)


# Product JSON schema for validation
PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
            "maxLength": 100
        },
        "description": {
            "type": "string", 
            "minLength": 10,
            "maxLength": 1000
        },
        "price": {
            "type": ["number", "string"],
            "minimum": 0.01,
            "maximum": 9999.99
        },
        "category_id": {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{24}$"
        },
        "images": {
            "type": "array",
            "items": {
                "type": "string",
                "format": "uri"
            },
            "maxItems": 10
        },
        "stock_quantity": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10000
        },
        "weight_grams": {
            "type": ["integer", "null"],
            "minimum": 1,
            "maximum": 50000
        },
        "preparation_time_hours": {
            "type": "integer",
            "minimum": 1,
            "maximum": 168
        }
    },
    "required": ["name", "description", "price", "category_id"],
    "additionalProperties": False
}


@products_bp.route('/', methods=['GET'])
def list_products():
    """
    List products with pagination, filtering, sorting, and search.
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - limit (int): Items per page (default: 20, max: 100)
        - category_id (str): Filter by category ObjectId
        - available_only (bool): Only show available products (default: true)
        - sort_by (str): Sort field (name, price, created_at) (default: name)
        - sort_order (str): Sort order (asc, desc) (default: asc)
        - min_price (float): Minimum price filter
        - max_price (float): Maximum price filter
        - q (str): Search query for product name and description
    """
    try:
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        category_id = request.args.get('category_id')
        available_only = request.args.get('available_only', 'true').lower() == 'true'
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        search_query = request.args.get('q', '').strip()
        
        # Validate sort parameters
        valid_sort_fields = ['name', 'price', 'created_at', 'stock_quantity']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
        
        sort_direction = 1 if sort_order == 'asc' else -1
        
        # Build query
        query = {}
        
        # Add search if query provided - use regex for partial matching
        if search_query:
            # Case-insensitive regex search in name and description
            search_regex = {'$regex': search_query, '$options': 'i'}
            query['$or'] = [
                {'name': search_regex},
                {'description': search_regex}
            ]
        
        # Filter by availability
        if available_only:
            query['is_available'] = True
            query['stock_quantity'] = {'$gt': 0}
        
        # Filter by category
        if category_id:
            try:
                category_obj_id = ObjectId(category_id)
                query['category_id'] = category_obj_id
            except Exception:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid category ID format",
                    400
                )
                return jsonify(response), status
        
        # Filter by price range
        price_filter = {}
        if min_price:
            try:
                price_filter['$gte'] = float(min_price)
            except ValueError:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid minimum price format",
                    400
                )
                return jsonify(response), status
        
        if max_price:
            try:
                price_filter['$lte'] = float(max_price)
            except ValueError:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid maximum price format",
                    400
                )
                return jsonify(response), status
        
        if price_filter:
            query['price'] = price_filter
        
        # Build aggregation pipeline
        pipeline = [
            {'$match': query}
        ]
        
        # Add sorting
        pipeline.append({'$sort': {sort_by: sort_direction}})
        
        # Add facet stage for pagination and category lookup
        pipeline.append({
            '$facet': {
                'products': [
                    {'$skip': (page - 1) * limit},
                    {'$limit': limit},
                    {
                        '$lookup': {
                            'from': 'categories',
                            'localField': 'category_id',
                            'foreignField': '_id',
                            'as': 'category'
                        }
                    },
                    {
                        '$addFields': {
                            'category': {'$arrayElemAt': ['$category', 0]}
                        }
                    }
                ],
                'total_count': [
                    {'$count': 'count'}
                ]
            }
        })
        
        # Execute aggregation
        from app.database import get_database
        db = get_database()
        collection = db[Product.COLLECTION_NAME]
        
        result = list(collection.aggregate(pipeline))[0]
        products_data = result['products']
        total_count = result['total_count'][0]['count'] if result['total_count'] else 0
        
        # Convert products to dict format
        products = []
        for product_doc in products_data:
            product = Product(product_doc)
            product_dict = product.to_dict()
            
            
            # Add category information if available
            if 'category' in product_doc and product_doc['category']:
                category_info = Category(product_doc['category'])
                product_dict['category'] = {
                    'id': str(category_info._id),
                    'name': category_info.name,
                    'slug': category_info.slug
                }
            
            products.append(product_dict)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = {
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'category_id': category_id,
                'available_only': available_only,
                'min_price': min_price,
                'max_price': max_price,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
        
        # Add search metadata if searching
        if search_query:
            response_data['search'] = {
                'query': search_query,
                'total_results': total_count,
                'search_active': True
            }
        
        if search_query:
            logging.info(f"Product search: '{search_query}' returned {len(products)} items (page {page}/{total_pages})")
            success_message = f"Found {total_count} products matching '{search_query}'" if total_count > 0 else f"No products found for '{search_query}'"
        else:
            logging.info(f"Products listed: {len(products)} items (page {page}/{total_pages})")
            success_message = f"Retrieved {len(products)} products"
        
        return jsonify(success_response(
            response_data,
            success_message
        )), 200
        
    except Exception as e:
        logging.error(f"Error listing products: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve products",
            500
        )
        return jsonify(response), status


@products_bp.route('/search', methods=['GET'])
def search_products():
    """
    Search products by name and description.
    
    Query Parameters:
        - q (str): Search query (required)
        - page (int): Page number (default: 1)
        - limit (int): Items per page (default: 20, max: 100)
        - category_id (str): Filter by category
        - available_only (bool): Only show available products (default: true)
    """
    try:
        # Get search query
        search_query = request.args.get('q', '').strip()
        if not search_query:
            response, status = create_error_response(
                "VAL_001",
                "Search query is required",
                400
            )
            return jsonify(response), status
        
        # Parse other parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        category_id = request.args.get('category_id')
        available_only = request.args.get('available_only', 'true').lower() == 'true'
        
        # Build base query
        query = {}
        
        # Add text search
        query['$text'] = {'$search': search_query}
        
        # Filter by availability
        if available_only:
            query['is_available'] = True
            query['stock_quantity'] = {'$gt': 0}
        
        # Filter by category
        if category_id:
            try:
                category_obj_id = ObjectId(category_id)
                query['category_id'] = category_obj_id
            except Exception:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid category ID format",
                    400
                )
                return jsonify(response), status
        
        # Build aggregation pipeline with text search scoring
        pipeline = [
            {'$match': query},
            {'$addFields': {'score': {'$meta': 'textScore'}}},
            {'$sort': {'score': {'$meta': 'textScore'}}},
            {
                '$facet': {
                    'products': [
                        {'$skip': (page - 1) * limit},
                        {'$limit': limit},
                        {
                            '$lookup': {
                                'from': 'categories',
                                'localField': 'category_id',
                                'foreignField': '_id',
                                'as': 'category'
                            }
                        },
                        {
                            '$addFields': {
                                'category': {'$arrayElemAt': ['$category', 0]}
                            }
                        }
                    ],
                    'total_count': [
                        {'$count': 'count'}
                    ]
                }
            }
        ]
        
        # Execute search
        from app.database import get_database
        db = get_database()
        collection = db[Product.COLLECTION_NAME]
        
        result = list(collection.aggregate(pipeline))[0]
        products_data = result['products']
        total_count = result['total_count'][0]['count'] if result['total_count'] else 0
        
        # Convert products to dict format
        products = []
        for product_doc in products_data:
            product = Product(product_doc)
            product_dict = product.to_dict()
            
            # Add search score
            product_dict['search_score'] = product_doc.get('score', 0)
            
            # Add category information if available
            if 'category' in product_doc and product_doc['category']:
                category_info = Category(product_doc['category'])
                product_dict['category'] = {
                    'id': str(category_info._id),
                    'name': category_info.name,
                    'slug': category_info.slug
                }
            
            products.append(product_dict)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = {
            'products': products,
            'search_query': search_query,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'category_id': category_id,
                'available_only': available_only
            }
        }
        
        logging.info(f"Product search: '{search_query}' returned {len(products)} results")
        
        return jsonify(success_response(
            response_data,
            f"Found {total_count} products matching '{search_query}'"
        )), 200
        
    except Exception as e:
        logging.error(f"Error searching products: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Product search failed",
            500
        )
        return jsonify(response), status


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get individual product details by ID or slug.
    
    Args:
        product_id (str): Product ObjectId or URL slug
    """
    try:
        # Try to find by ObjectId first, then by slug
        product = None
        
        # Check if it's a valid ObjectId format
        if re.match(r'^[0-9a-fA-F]{24}$', product_id):
            product = Product.find_by_id(product_id)
        
        # If not found by ID, try by slug
        if not product:
            product = Product.find_by_slug(product_id)
        
        # If still not found, return 404
        if not product:
            response, status = create_error_response(
                "NOT_001",
                "Product not found",
                404
            )
            return jsonify(response), status
        
        # Get product data
        product_dict = product.to_dict()
        
        # Add category information
        if product.category_id:
            category = Category.find_by_id(product.category_id)
            if category:
                product_dict['category'] = {
                    'id': str(category._id),
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description
                }
        
        logging.info(f"Product retrieved: {product.name} (ID: {product_id})")
        
        return jsonify(success_response(
            {'product': product_dict},
            "Product retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving product: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve product",
            500
        )
        return jsonify(response), status


@products_bp.route('/admin/products', methods=['POST'])
@require_admin_auth
@validate_json(PRODUCT_SCHEMA)
def create_product():
    """
    Create new product (admin only).
    
    Expects JSON with product data including name, description, price, category_id.
    All error messages are in Romanian for local producer marketplace.
    """
    try:
        from flask import g
        data = request.validated_json
        admin_user = g.current_admin_user
        
        # Validate required fields with Romanian messages
        required_fields = ['name', 'description', 'price', 'category_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            missing_ro = {
                'name': 'numele',
                'description': 'descrierea', 
                'price': 'prețul',
                'category_id': 'categoria'
            }
            missing_list = [missing_ro.get(field, field) for field in missing_fields]
            response, status = create_error_response(
                "VAL_001",
                f"Următoarele câmpuri sunt obligatorii: {', '.join(missing_list)}",
                400
            )
            return jsonify(response), status
        
        # Validate price
        try:
            price = float(data['price'])
            if price <= 0:
                response, status = create_error_response(
                    "VAL_001",
                    "Prețul trebuie să fie un număr pozitiv",
                    400
                )
                return jsonify(response), status
            if price > 9999.99:
                response, status = create_error_response(
                    "VAL_001",
                    "Prețul nu poate fi mai mare de 9999.99 RON",
                    400
                )
                return jsonify(response), status
        except (ValueError, TypeError):
            response, status = create_error_response(
                "VAL_001",
                "Prețul trebuie să fie un număr valid",
                400
            )
            return jsonify(response), status
        
        # Validate stock quantity
        stock_quantity = data.get('stock_quantity', 0)
        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                response, status = create_error_response(
                    "VAL_001",
                    "Cantitatea în stoc nu poate fi negativă",
                    400
                )
                return jsonify(response), status
            if stock_quantity > 10000:
                response, status = create_error_response(
                    "VAL_001",
                    "Cantitatea în stoc nu poate fi mai mare de 10000",
                    400
                )
                return jsonify(response), status
        except (ValueError, TypeError):
            response, status = create_error_response(
                "VAL_001",
                "Cantitatea în stoc trebuie să fie un număr întreg",
                400
            )
            return jsonify(response), status
        
        # Validate name length and uniqueness
        name = data['name'].strip()
        if len(name) < 2:
            response, status = create_error_response(
                "VAL_001",
                "Numele produsului trebuie să aibă cel puțin 2 caractere",
                400
            )
            return jsonify(response), status
        if len(name) > 100:
            response, status = create_error_response(
                "VAL_001",
                "Numele produsului nu poate avea mai mult de 100 de caractere",
                400
            )
            return jsonify(response), status
        
        # Check for duplicate product name
        existing_product = Product.find_by_name(name)
        if existing_product:
            response, status = create_error_response(
                "VAL_001",
                f"Un produs cu numele '{name}' există deja în sistem",
                400
            )
            return jsonify(response), status
        
        # Validate description
        description = data['description'].strip()
        if len(description) < 10:
            response, status = create_error_response(
                "VAL_001",
                "Descrierea produsului trebuie să aibă cel puțin 10 caractere",
                400
            )
            return jsonify(response), status
        if len(description) > 1000:
            response, status = create_error_response(
                "VAL_001",
                "Descrierea produsului nu poate avea mai mult de 1000 de caractere",
                400
            )
            return jsonify(response), status
        
        # Verify category exists and is active
        category = Category.find_by_id(data['category_id'])
        if not category:
            response, status = create_error_response(
                "VAL_001",
                "Categoria specificată nu există în sistem",
                400
            )
            return jsonify(response), status
        
        if not category.is_active:
            response, status = create_error_response(
                "VAL_001",
                f"Categoria '{category.name}' nu este activă și nu poate fi utilizată",
                400
            )
            return jsonify(response), status
        
        # Validate weight if provided
        weight_grams = data.get('weight_grams')
        if weight_grams is not None:
            try:
                weight_grams = int(weight_grams)
                if weight_grams < 1:
                    response, status = create_error_response(
                        "VAL_001",
                        "Greutatea trebuie să fie cel puțin 1 gram",
                        400
                    )
                    return jsonify(response), status
                if weight_grams > 50000:
                    response, status = create_error_response(
                        "VAL_001",
                        "Greutatea nu poate fi mai mare de 50kg (50000 grame)",
                        400
                    )
                    return jsonify(response), status
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Greutatea trebuie să fie un număr întreg în grame",
                    400
                )
                return jsonify(response), status
        
        # Validate preparation time if provided
        prep_time = data.get('preparation_time_hours')
        if prep_time is not None:
            try:
                prep_time = int(prep_time)
                if prep_time < 1:
                    response, status = create_error_response(
                        "VAL_001",
                        "Timpul de preparare trebuie să fie cel puțin 1 oră",
                        400
                    )
                    return jsonify(response), status
                if prep_time > 168:  # 1 week
                    response, status = create_error_response(
                        "VAL_001",
                        "Timpul de preparare nu poate fi mai mare de 168 ore (1 săptămână)",
                        400
                    )
                    return jsonify(response), status
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Timpul de preparare trebuie să fie un număr întreg de ore",
                    400
                )
                return jsonify(response), status
        
        # Validate images if provided
        images = data.get('images', [])
        if images:
            if len(images) > 10:
                response, status = create_error_response(
                    "VAL_001",
                    "Nu puteți adăuga mai mult de 10 imagini per produs",
                    400
                )
                return jsonify(response), status
            
            # Basic URL validation for images
            for i, image_url in enumerate(images):
                if not isinstance(image_url, str) or len(image_url) < 10:
                    response, status = create_error_response(
                        "VAL_001",
                        f"URL-ul imaginii {i+1} nu este valid",
                        400
                    )
                    return jsonify(response), status
        
        # Create product
        try:
            product = Product.create(
                name=name,
                description=description,
                price=price,
                category_id=data['category_id'],
                created_by=admin_user['user_id'],
                images=images,
                stock_quantity=stock_quantity,
                weight_grams=weight_grams,
                preparation_time_hours=prep_time
            )
        except Exception as e:
            logging.error(f"Database error creating product: {str(e)}")
            response, status = create_error_response(
                "DB_001",
                "Eroare la salvarea produsului în baza de date",
                500
            )
            return jsonify(response), status
        
        # Return created product with category info
        product_dict = product.to_dict(include_internal=True)
        product_dict['category'] = {
            'id': str(category._id),
            'name': category.name,
            'slug': category.slug,
            'description': category.description
        }
        
        # Log admin action for audit trail
        log_admin_action(
            "Produs creat", 
            {
                "product_id": str(product._id),
                "product_name": product.name,
                "category": category.name,
                "price": price,
                "stock_quantity": stock_quantity
            }
        )
        
        logging.info(f"Product created by admin {admin_user['phone_number'][-4:]}: {product.name}")
        
        return jsonify(success_response(
            {'product': product_dict},
            f"Produsul '{product.name}' a fost creat cu succes"
        )), 201
        
    except ValidationError as e:
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare neașteptată la crearea produsului. Încercați din nou",
            500
        )
        return jsonify(response), status


@products_bp.route('/admin/products/<product_id>', methods=['PUT'])
@require_admin_auth
def update_product(product_id):
    """
    Update existing product (admin only).
    
    Args:
        product_id (str): Product ObjectId
    """
    try:
        from flask import g
        data = request.get_json()
        if not data:
            response, status = create_error_response(
                "VAL_001",
                "Datele pentru actualizare sunt obligatorii",
                400
            )
            return jsonify(response), status
        
        admin_user = g.current_admin_user
        
        # Find product
        product = Product.find_by_id(product_id)
        if not product:
            response, status = create_error_response(
                "NOT_001",
                "Produsul specificat nu a fost găsit în sistem",
                404
            )
            return jsonify(response), status
        
        # Validate category_id if provided
        if 'category_id' in data:
            category = Category.find_by_id(data['category_id'])
            if not category:
                response, status = create_error_response(
                    "VAL_001",
                    "Categoria specificată nu există în sistem",
                    400
                )
                return jsonify(response), status
            
            if not category.is_active:
                response, status = create_error_response(
                    "VAL_001",
                    f"Categoria '{category.name}' nu este activă și nu poate fi utilizată",
                    400
                )
                return jsonify(response), status
        
        # Validate name if provided (check for duplicates excluding current product)
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                response, status = create_error_response(
                    "VAL_001",
                    "Numele produsului trebuie să aibă cel puțin 2 caractere",
                    400
                )
                return jsonify(response), status
            
            existing_product = Product.find_by_name(name)
            if existing_product and str(existing_product._id) != str(product._id):
                response, status = create_error_response(
                    "VAL_001",
                    f"Un alt produs cu numele '{name}' există deja în sistem",
                    400
                )
                return jsonify(response), status
        
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    response, status = create_error_response(
                        "VAL_001",
                        "Prețul trebuie să fie un număr pozitiv",
                        400
                    )
                    return jsonify(response), status
                if price > 9999.99:
                    response, status = create_error_response(
                        "VAL_001",
                        "Prețul nu poate fi mai mare de 9999.99 RON",
                        400
                    )
                    return jsonify(response), status
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Prețul trebuie să fie un număr valid",
                    400
                )
                return jsonify(response), status
        
        # Update product
        success = product.update(data)
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Nu s-au efectuat modificări asupra produsului",
                400
            )
            return jsonify(response), status
        
        # Get updated product with category info
        product_dict = product.to_dict(include_internal=True)
        if product.category_id:
            category = Category.find_by_id(product.category_id)
            if category:
                product_dict['category'] = {
                    'id': str(category._id),
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description
                }
        
        # Log admin action for audit trail
        log_admin_action(
            "Produs actualizat", 
            {
                "product_id": str(product._id),
                "product_name": product.name,
                "updated_fields": list(data.keys())
            }
        )
        
        logging.info(f"Product updated by admin {admin_user['phone_number'][-4:]}: {product.name}")
        
        return jsonify(success_response(
            {'product': product_dict},
            f"Produsul '{product.name}' a fost actualizat cu succes"
        )), 200
        
    except ValidationError as e:
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error updating product: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare neașteptată la actualizarea produsului. Încercați din nou",
            500
        )
        return jsonify(response), status


@products_bp.route('/admin/products/<product_id>', methods=['DELETE'])
@require_admin_auth
def delete_product(product_id):
    """
    Deactivate product (admin only).
    
    Performs soft delete by setting is_available=False and stock_quantity=0.
    All messages are in Romanian for local producer marketplace.
    
    Args:
        product_id (str): Product ObjectId
    """
    try:
        from flask import g
        admin_user = g.current_admin_user
        
        # Find product
        product = Product.find_by_id(product_id)
        if not product:
            response, status = create_error_response(
                "NOT_001",
                "Produsul specificat nu a fost găsit în sistem",
                404
            )
            return jsonify(response), status
        
        # Check if product is already deleted
        if not product.is_available and product.stock_quantity == 0:
            return jsonify(success_response(
                {
                    'product_id': product_id, 
                    'deleted': True,
                    'name': product.name
                },
                f"Produsul '{product.name}' este deja dezactivat"
            )), 200
        
        # Store product name for logging before deletion
        product_name = product.name
        
        # Soft delete product
        success = product.delete()
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Eroare la dezactivarea produsului. Încercați din nou",
                500
            )
            return jsonify(response), status
        
        # Log admin action for audit trail
        log_admin_action(
            "Produs dezactivat", 
            {
                "product_id": product_id,
                "product_name": product_name
            }
        )
        
        logging.info(f"Product deleted by admin {admin_user['phone_number'][-4:]}: {product_name}")
        
        return jsonify(success_response(
            {
                'product_id': product_id,
                'deleted': True,
                'name': product_name
            },
            f"Produsul '{product_name}' a fost dezactivat cu succes"
        )), 200
        
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare neașteptată la dezactivarea produsului. Încercați din nou",
            500
        )
        return jsonify(response), status