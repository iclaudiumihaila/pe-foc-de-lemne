"""
Category Management Routes for Local Producer Web Application

This module provides category management endpoints including listing, details,
product relationships, and admin category management.
"""

import logging
import re
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.database import get_database
from app.utils.validators import validate_json
from app.utils.error_handlers import (
    ValidationError, AuthorizationError, NotFoundError,
    success_response, create_error_response
)
from app.utils.auth_middleware import require_admin_auth, log_admin_action

# Create categories blueprint
categories_bp = Blueprint('categories', __name__)

# Remove old admin role decorator - now using require_admin_auth from auth_middleware


# Category JSON schema for validation
CATEGORY_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 2,
            "maxLength": 50
        },
        "description": {
            "type": ["string", "null"],
            "maxLength": 500
        },
        "display_order": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10000
        }
    },
    "required": ["name"],
    "additionalProperties": False
}


@categories_bp.route('/', methods=['GET'])
def list_categories():
    """
    List all categories with product counts.
    
    Query Parameters:
        - active_only (bool): Only show active categories (default: true)
        - include_counts (bool): Include product counts (default: true)
    """
    try:
        # Parse query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        include_counts = request.args.get('include_counts', 'true').lower() == 'true'
        
        # Get categories
        categories = Category.find_all(active_only=active_only)
        
        # Convert to dict format
        categories_data = []
        for category in categories:
            category_dict = category.to_dict()
            
            # Update product count if requested
            if include_counts:
                category.update_product_count()
                category_dict['product_count'] = category.product_count
            
            categories_data.append(category_dict)
        
        response_data = {
            'categories': categories_data,
            'total_count': len(categories_data),
            'filters': {
                'active_only': active_only,
                'include_counts': include_counts
            }
        }
        
        logging.info(f"Categories listed: {len(categories_data)} items (active_only: {active_only})")
        
        return jsonify(success_response(
            response_data,
            f"Retrieved {len(categories_data)} categories"
        )), 200
        
    except Exception as e:
        logging.error(f"Error listing categories: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve categories",
            500
        )
        return jsonify(response), status


@categories_bp.route('/<category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get individual category details by ID or slug.
    
    Args:
        category_id (str): Category ObjectId or URL slug
    """
    try:
        # Try to find by ObjectId first, then by slug
        category = None
        
        # Check if it's a valid ObjectId format
        if re.match(r'^[0-9a-fA-F]{24}$', category_id):
            category = Category.find_by_id(category_id)
        
        # If not found by ID, try by slug
        if not category:
            category = Category.find_by_slug(category_id)
        
        # If still not found, return 404
        if not category:
            response, status = create_error_response(
                "NOT_001",
                "Category not found",
                404
            )
            return jsonify(response), status
        
        # Update product count
        category.update_product_count()
        
        # Get category data
        category_dict = category.to_dict()
        
        logging.info(f"Category retrieved: {category.name} (ID: {category_id})")
        
        return jsonify(success_response(
            {'category': category_dict},
            "Category retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving category: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve category",
            500
        )
        return jsonify(response), status


@categories_bp.route('/<category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """
    Get products within a category with pagination.
    
    Args:
        category_id (str): Category ObjectId or URL slug
        
    Query Parameters:
        - page (int): Page number (default: 1)
        - limit (int): Items per page (default: 20, max: 100)
        - available_only (bool): Only show available products (default: true)
        - sort_by (str): Sort field (name, price, created_at) (default: name)
        - sort_order (str): Sort order (asc, desc) (default: asc)
    """
    try:
        # Find category first
        category = None
        
        # Check if it's a valid ObjectId format
        if re.match(r'^[0-9a-fA-F]{24}$', category_id):
            category = Category.find_by_id(category_id)
        
        # If not found by ID, try by slug
        if not category:
            category = Category.find_by_slug(category_id)
        
        # If still not found, return 404
        if not category:
            response, status = create_error_response(
                "NOT_001",
                "Category not found",
                404
            )
            return jsonify(response), status
        
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        available_only = request.args.get('available_only', 'true').lower() == 'true'
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Validate sort parameters
        valid_sort_fields = ['name', 'price', 'created_at', 'stock_quantity']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
        
        sort_direction = 1 if sort_order == 'asc' else -1
        
        # Build query
        query = {'category_id': category._id}
        
        # Filter by availability
        if available_only:
            query['is_available'] = True
            query['stock_quantity'] = {'$gt': 0}
        
        # Build aggregation pipeline
        pipeline = [
            {'$match': query},
            {'$sort': {sort_by: sort_direction}},
            {
                '$facet': {
                    'products': [
                        {'$skip': (page - 1) * limit},
                        {'$limit': limit}
                    ],
                    'total_count': [
                        {'$count': 'count'}
                    ]
                }
            }
        ]
        
        # Execute aggregation
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
            
            # Add category information
            product_dict['category'] = {
                'id': str(category._id),
                'name': category.name,
                'slug': category.slug
            }
            
            products.append(product_dict)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = {
            'category': category.to_dict(),
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
                'available_only': available_only,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
        
        logging.info(f"Category products listed: {category.name} - {len(products)} items")
        
        return jsonify(success_response(
            response_data,
            f"Retrieved {len(products)} products from {category.name}"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving category products: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve category products",
            500
        )
        return jsonify(response), status


@categories_bp.route('/', methods=['POST'])
@require_admin_auth
@validate_json(CATEGORY_SCHEMA)
def create_category():
    """
    Create new category (admin only).
    
    Expects JSON with category data including name and optional description, display_order.
    All error messages are in Romanian for local producer marketplace.
    """
    try:
        from flask import g
        data = request.validated_json
        admin_user = g.current_admin_user
        
        # Validate required fields with Romanian messages
        name = data.get('name', '').strip()
        if not name:
            response, status = create_error_response(
                "VAL_001",
                "Numele categoriei este obligatoriu",
                400
            )
            return jsonify(response), status
        
        # Validate category name length
        if len(name) < 2:
            response, status = create_error_response(
                "VAL_001",
                "Numele categoriei trebuie să aibă cel puțin 2 caractere",
                400
            )
            return jsonify(response), status
        
        if len(name) > 50:
            response, status = create_error_response(
                "VAL_001",
                "Numele categoriei nu poate avea mai mult de 50 de caractere",
                400
            )
            return jsonify(response), status
        
        # Check for duplicate category name (case-insensitive)
        db = get_database()
        collection = db[Category.COLLECTION_NAME]
        existing_category = collection.find_one({
            'name': {'$regex': f'^{re.escape(name)}$', '$options': 'i'},
            'is_active': True
        })
        
        if existing_category:
            response, status = create_error_response(
                "VAL_001",
                f"O categorie cu numele '{name}' există deja în sistem",
                409
            )
            return jsonify(response), status
        
        # Validate description if provided
        description = data.get('description')
        if description is not None:
            description = description.strip()
            if len(description) > 500:
                response, status = create_error_response(
                    "VAL_001",
                    "Descrierea categoriei nu poate avea mai mult de 500 de caractere",
                    400
                )
                return jsonify(response), status
        
        # Validate display_order if provided
        display_order = data.get('display_order')
        if display_order is not None:
            try:
                display_order = int(display_order)
                if display_order < 0:
                    response, status = create_error_response(
                        "VAL_001",
                        "Ordinea de afișare trebuie să fie un număr pozitiv",
                        400
                    )
                    return jsonify(response), status
                if display_order > 10000:
                    response, status = create_error_response(
                        "VAL_001",
                        "Ordinea de afișare nu poate depăși 10000",
                        400
                    )
                    return jsonify(response), status
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Ordinea de afișare trebuie să fie un număr întreg",
                    400
                )
                return jsonify(response), status
        
        # Create category with additional error handling
        try:
            category = Category.create(
                name=name,
                created_by=admin_user['user_id'],
                description=description,
                display_order=display_order
            )
        except Exception as e:
            if "duplicate" in str(e).lower() or "exists" in str(e).lower():
                response, status = create_error_response(
                    "VAL_001",
                    f"O categorie cu numele '{name}' există deja în sistem",
                    409
                )
                return jsonify(response), status
            else:
                logging.error(f"Database error creating category: {str(e)}")
                response, status = create_error_response(
                    "DB_001",
                    "Eroare la crearea categoriei în baza de date",
                    500
                )
                return jsonify(response), status
        
        # Return created category
        category_dict = category.to_dict(include_internal=True)
        
        # Log admin action for audit trail
        log_admin_action(
            "Categorie creată", 
            {
                "category_id": str(category._id),
                "category_name": category.name,
                "category_slug": category.slug,
                "display_order": category.display_order
            }
        )
        
        logging.info(f"Category created by admin {admin_user['phone_number'][-4:]}: {category.name}")
        
        return jsonify(success_response(
            {'category': category_dict},
            f"Categoria '{category.name}' a fost creată cu succes!"
        )), 201
        
    except ValidationError as e:
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error creating category: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare la crearea categoriei. Vă rugăm să încercați din nou.",
            500
        )
        return jsonify(response), status


@categories_bp.route('/<category_id>', methods=['PUT'])
@require_admin_auth
def update_category(category_id):
    """
    Update existing category (admin only).
    
    Supports partial updates for category fields with comprehensive validation,
    duplicate checking, change tracking, and Romanian localization.
    
    Args:
        category_id (str): Category ObjectId
    """
    try:
        from flask import g
        data = request.get_json()
        admin_user = g.current_admin_user
        
        # Validate request body
        if not data:
            response, status = create_error_response(
                "VAL_001",
                "Nu au fost furnizate date pentru actualizare",
                400
            )
            return jsonify(response), status
        
        # Find category
        category = Category.find_by_id(category_id)
        if not category:
            response, status = create_error_response(
                "NOT_001",
                "Categoria nu a fost găsită",
                404
            )
            return jsonify(response), status
        
        # Store original values for change tracking
        original_values = {
            'name': category.name,
            'description': category.description,
            'display_order': category.display_order,
            'is_active': category.is_active
        }
        
        # Validate and prepare update data
        update_data = {}
        changes = {}
        
        # Validate name if provided
        if 'name' in data:
            name = data['name'].strip() if data['name'] else ''
            if not name:
                response, status = create_error_response(
                    "VAL_001",
                    "Numele categoriei nu poate fi gol",
                    400
                )
                return jsonify(response), status
            
            if len(name) < 2:
                response, status = create_error_response(
                    "VAL_001",
                    "Numele categoriei trebuie să aibă cel puțin 2 caractere",
                    400
                )
                return jsonify(response), status
            
            if len(name) > 50:
                response, status = create_error_response(
                    "VAL_001",
                    "Numele categoriei nu poate avea mai mult de 50 de caractere",
                    400
                )
                return jsonify(response), status
            
            # Check for duplicate name (excluding current category)
            if name.lower() != category.name.lower():
                db = get_database()
                collection = db[Category.COLLECTION_NAME]
                existing_category = collection.find_one({
                    '_id': {'$ne': category._id},
                    'name': {'$regex': f'^{re.escape(name)}$', '$options': 'i'},
                    'is_active': True
                })
                
                if existing_category:
                    response, status = create_error_response(
                        "VAL_001",
                        f"O categorie cu numele '{name}' există deja în sistem",
                        409
                    )
                    return jsonify(response), status
            
            update_data['name'] = name
            if name != original_values['name']:
                changes['name'] = {
                    'old': original_values['name'],
                    'new': name
                }
        
        # Validate description if provided
        if 'description' in data:
            description = data['description']
            if description is not None:
                description = description.strip()
                if len(description) > 500:
                    response, status = create_error_response(
                        "VAL_001",
                        "Descrierea categoriei nu poate avea mai mult de 500 de caractere",
                        400
                    )
                    return jsonify(response), status
            
            update_data['description'] = description
            if description != original_values['description']:
                changes['description'] = {
                    'old': original_values['description'],
                    'new': description
                }
        
        # Validate display_order if provided
        if 'display_order' in data:
            display_order = data['display_order']
            if display_order is not None:
                try:
                    display_order = int(display_order)
                    if display_order < 0:
                        response, status = create_error_response(
                            "VAL_001",
                            "Ordinea de afișare trebuie să fie un număr pozitiv",
                            400
                        )
                        return jsonify(response), status
                    if display_order > 10000:
                        response, status = create_error_response(
                            "VAL_001",
                            "Ordinea de afișare nu poate depăși 10000",
                            400
                        )
                        return jsonify(response), status
                except (ValueError, TypeError):
                    response, status = create_error_response(
                        "VAL_001",
                        "Ordinea de afișare trebuie să fie un număr întreg",
                        400
                    )
                    return jsonify(response), status
            
            update_data['display_order'] = display_order
            if display_order != original_values['display_order']:
                changes['display_order'] = {
                    'old': original_values['display_order'],
                    'new': display_order
                }
        
        # Validate is_active if provided
        if 'is_active' in data:
            is_active = bool(data['is_active'])
            update_data['is_active'] = is_active
            if is_active != original_values['is_active']:
                changes['is_active'] = {
                    'old': original_values['is_active'],
                    'new': is_active
                }
        
        # Check if any changes were made
        if not update_data:
            response, status = create_error_response(
                "VAL_001",
                "Nu au fost furnizate modificări valide",
                400
            )
            return jsonify(response), status
        
        # Update category with error handling
        try:
            success = category.update(update_data)
            if not success:
                response, status = create_error_response(
                    "DB_001",
                    "Nu au fost efectuate modificări la categorie",
                    400
                )
                return jsonify(response), status
        except Exception as e:
            if "duplicate" in str(e).lower() or "exists" in str(e).lower():
                response, status = create_error_response(
                    "VAL_001",
                    f"O categorie cu numele specificat există deja în sistem",
                    409
                )
                return jsonify(response), status
            else:
                logging.error(f"Database error updating category: {str(e)}")
                response, status = create_error_response(
                    "DB_001",
                    "Eroare la actualizarea categoriei în baza de date",
                    500
                )
                return jsonify(response), status
        
        # Get updated category
        category_dict = category.to_dict(include_internal=True)
        
        # Determine audit log message based on changes
        audit_message = "Categorie actualizată"
        if 'is_active' in changes:
            if changes['is_active']['new']:
                audit_message = "Categorie reactivată"
            else:
                audit_message = "Categorie dezactivată"
        
        # Log admin action for audit trail
        log_admin_action(
            audit_message,
            {
                "category_id": str(category._id),
                "category_name": category.name,
                "changes": changes,
                "fields_updated": list(update_data.keys())
            }
        )
        
        # Determine success message
        success_message = f"Categoria '{category.name}' a fost actualizată cu succes!"
        if 'is_active' in changes:
            if changes['is_active']['new']:
                success_message = f"Categoria '{category.name}' a fost reactivată cu succes!"
            else:
                success_message = f"Categoria '{category.name}' a fost dezactivată cu succes!"
        
        logging.info(f"Category updated by admin {admin_user['phone_number'][-4:]}: {category.name}")
        
        # Build response data
        response_data = {
            'category': category_dict
        }
        
        # Include changes in response if any were made
        if changes:
            response_data['changes'] = changes
        
        return jsonify(success_response(
            response_data,
            success_message
        )), 200
        
    except ValidationError as e:
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error updating category: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare la actualizarea categoriei. Vă rugăm să încercați din nou.",
            500
        )
        return jsonify(response), status


@categories_bp.route('/<category_id>', methods=['DELETE'])
@require_admin_auth
def delete_category(category_id):
    """
    Delete category (admin only) with product relationship validation.
    
    Performs soft delete by setting is_active=False with comprehensive Romanian localization,
    business rule validation, and data integrity protection.
    
    Args:
        category_id (str): Category ObjectId
    """
    try:
        from flask import g
        admin_user = g.current_admin_user
        
        # Validate ObjectId format
        try:
            ObjectId(category_id)
        except Exception:
            response, status = create_error_response(
                "VAL_001",
                "ID-ul categoriei nu este valid",
                400
            )
            return jsonify(response), status
        
        # Find category
        category = Category.find_by_id(category_id)
        if not category:
            response, status = create_error_response(
                "NOT_001",
                "Categoria nu a fost găsită",
                404
            )
            return jsonify(response), status
        
        # Check if category is already deleted
        if not category.is_active:
            # Log admin action for already deleted category
            log_admin_action(
                "Categorie deja dezactivată - nici o acțiune",
                {
                    "category_id": str(category._id),
                    "category_name": category.name,
                    "was_active": False
                }
            )
            
            return jsonify(success_response(
                {
                    'category_id': category_id,
                    'category_name': category.name,
                    'deleted': True,
                    'was_active': False
                },
                "Categoria este deja dezactivată"
            )), 200
        
        # Check if category has products with detailed counting
        category.update_product_count()
        if category.product_count > 0:
            # Log failed deletion attempt for audit
            log_admin_action(
                "Tentativă de ștergere categorie cu produse",
                {
                    "category_id": str(category._id),
                    "category_name": category.name,
                    "product_count": category.product_count,
                    "reason": "Categoria conține produse active"
                }
            )
            
            response, status = create_error_response(
                "CONFLICT_001",
                f"Nu se poate șterge categoria care conține {category.product_count} produse",
                409,
                {
                    "category_id": category_id,
                    "category_name": category.name,
                    "product_count": category.product_count,
                    "guidance": "Pentru a șterge categoria, mutați sau ștergeți mai întâi produsele"
                }
            )
            return jsonify(response), status
        
        # Store category data before deletion for response
        category_name = category.name
        was_active = category.is_active
        
        # Soft delete category
        success = category.delete()
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Eroare la dezactivarea categoriei în baza de date",
                500
            )
            return jsonify(response), status
        
        # Log successful admin action for audit trail
        log_admin_action(
            "Categorie dezactivată",
            {
                "category_id": str(category._id),
                "category_name": category_name,
                "was_active": was_active,
                "product_count": 0
            }
        )
        
        logging.info(f"Category deleted by admin {admin_user['phone_number'][-4:]}: {category_name}")
        
        # Build comprehensive response
        response_data = {
            'category_id': category_id,
            'category_name': category_name,
            'deleted': True,
            'was_active': was_active,
            'product_count': 0,
            'deleted_at': category.updated_at.isoformat() if hasattr(category, 'updated_at') and category.updated_at else None
        }
        
        return jsonify(success_response(
            response_data,
            f"Categoria '{category_name}' a fost dezactivată cu succes"
        )), 200
        
    except Exception as e:
        logging.error(f"Error deleting category: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare la dezactivarea categoriei. Vă rugăm să încercați din nou.",
            500
        )
        return jsonify(response), status


@categories_bp.route('/<category_id>/product-count', methods=['POST'])
@require_admin_auth
def refresh_category_product_count(category_id):
    """
    Manually refresh category product count (admin only).
    
    Useful for maintenance when counts get out of sync.
    
    Args:
        category_id (str): Category ObjectId
    """
    try:
        from flask import g
        admin_user = g.current_admin_user
        
        # Find category
        category = Category.find_by_id(category_id)
        if not category:
            response, status = create_error_response(
                "NOT_001",
                "Category not found",
                404
            )
            return jsonify(response), status
        
        # Refresh product count
        old_count = category.product_count
        success = category.update_product_count()
        
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Failed to refresh product count",
                500
            )
            return jsonify(response), status
        
        logging.info(f"Product count refreshed by admin {admin_user['phone_number'][-4:]}: {category.name} ({old_count} -> {category.product_count})")
        
        return jsonify(success_response(
            {
                'category_id': category_id,
                'category_name': category.name,
                'old_count': old_count,
                'new_count': category.product_count,
                'updated': True
            },
            f"Product count refreshed: {old_count} -> {category.product_count}"
        )), 200
        
    except Exception as e:
        logging.error(f"Error refreshing product count: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to refresh product count",
            500
        )
        return jsonify(response), status