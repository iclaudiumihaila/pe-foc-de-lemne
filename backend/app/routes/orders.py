"""
Order Management Routes for Local Producer Web Application

This module provides order management endpoints including order creation with
cart integration, SMS verification, and admin order management.
"""

import logging
import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services.order_service import get_order_service, OrderValidationError, OrderCreationError
from app.services.sms_service import get_sms_service
from app.utils.validators import validate_json, validate_phone_number
from app.utils.error_handlers import (
    ValidationError, AuthorizationError, NotFoundError, SMSError,
    success_response, create_error_response
)
from app.routes.auth import require_auth
from app.utils.auth_middleware import require_admin_auth, log_admin_action

# Create orders blueprint
orders_bp = Blueprint('orders', __name__)

# Admin role decorator
def require_admin(f):
    """Decorator to require admin role for endpoints."""
    @require_auth
    def decorated_function(*args, **kwargs):
        user = request.current_user
        if user.role != User.ROLE_ADMIN:
            raise AuthorizationError("Admin access required")
        return f(*args, **kwargs)
    return decorated_function


# Order creation JSON schema for cart-based workflow
ORDER_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "cart_session_id": {
            "type": "string",
            "minLength": 1,
            "description": "Session ID for the shopping cart"
        },
        "customer_info": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "pattern": "^\\+[1-9]\\d{1,14}$",
                    "description": "Customer phone number in E.164 format"
                },
                "customer_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "description": "Customer full name"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Customer email address (optional)"
                },
                "special_instructions": {
                    "type": "string",
                    "maxLength": 500,
                    "description": "Special delivery instructions (optional)"
                }
            },
            "required": ["phone_number", "customer_name"],
            "additionalProperties": False
        },
        "phone_verification_session_id": {
            "type": "string",
            "minLength": 1,
            "description": "Session ID for phone verification"
        }
    },
    "required": ["cart_session_id", "customer_info", "phone_verification_session_id"],
    "additionalProperties": False
}


@orders_bp.route('', methods=['POST'])
@validate_json(ORDER_CREATE_SCHEMA)
def create_order():
    """
    Create new order from cart with SMS verification.
    
    Integrates with OrderService for comprehensive business logic validation,
    cart processing, inventory management, and atomic order creation.
    
    Required payload:
    - cart_session_id: String
    - customer_info: Object with phone_number, customer_name, email (optional), special_instructions (optional)
    - phone_verification_session_id: String
    
    Returns: Order confirmation with order number and details
    """
    try:
        data = request.get_json()
        
        # Extract validated data
        cart_session_id = data['cart_session_id']
        customer_info = data['customer_info']
        phone_verification_session_id = data['phone_verification_session_id']
        
        # Create order using OrderService
        order_service = get_order_service()
        result = order_service.create_order(
            cart_session_id=cart_session_id,
            customer_info=customer_info,
            phone_verification_session_id=phone_verification_session_id
        )
        
        return jsonify(result), 201
        
    except OrderValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': e.error_code,
            'details': e.details
        }), 400
        
    except OrderCreationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': e.error_code,
            'details': e.details
        }), 500
        
    except Exception as e:
        logging.error(f"Unexpected error creating order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while creating the order',
            'error_code': 'ORDER_500'
        }), 500


# Legacy order creation endpoint (kept for backward compatibility)
# Order creation JSON schema for legacy direct order creation
LEGACY_ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "customer_phone": {
            "type": "string",
            "pattern": "^\\+?[1-9]\\d{1,14}$"
        },
        "customer_name": {
            "type": "string",
            "minLength": 2,
            "maxLength": 50
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "pattern": "^[0-9a-fA-F]{24}$"
                    },
                    "quantity": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["product_id", "quantity"],
                "additionalProperties": False
            }
        },
        "delivery_type": {
            "type": "string",
            "enum": ["pickup", "delivery"]
        },
        "delivery_address": {
            "type": ["object", "null"],
            "properties": {
                "street": {"type": "string", "maxLength": 100},
                "city": {"type": "string", "maxLength": 50},
                "postal_code": {"type": "string", "maxLength": 20},
                "notes": {"type": "string", "maxLength": 200}
            },
            "required": ["street", "city"],
            "additionalProperties": False
        },
        "delivery_phone": {
            "type": ["string", "null"],
            "pattern": "^\\+?[1-9]\\d{1,14}$"
        },
        "requested_time": {
            "type": ["string", "null"],
            "format": "date-time"
        },
        "special_instructions": {
            "type": ["string", "null"],
            "maxLength": 500
        },
        "verification_code": {
            "type": "string",
            "pattern": "^\\d{6}$"
        }
    },
    "required": ["customer_phone", "customer_name", "items", "delivery_type", "verification_code"],
    "additionalProperties": False
}


@orders_bp.route('/legacy', methods=['POST'])
@validate_json(LEGACY_ORDER_SCHEMA)
def create_order_legacy():
    """
    Legacy order creation endpoint (backward compatibility).
    
    Direct order creation without cart workflow.
    Requires SMS verification code to confirm order creation.
    Validates product availability and calculates totals.
    """
    try:
        data = request.validated_json
        
        # Normalize phone number
        customer_phone = validate_phone_number(data['customer_phone'])
        
        # Verify SMS code
        sms_service = get_sms_service()
        verification_code = data['verification_code']
        
        # For order creation, we expect the verification code to be stored in session
        # or we need to validate against recent SMS codes
        # Here we'll validate against the SMS service
        try:
            # Check if verification code is valid for this phone number
            # Note: This assumes SMS service stores recent codes for validation
            is_valid = sms_service.validate_recent_code(customer_phone, verification_code)
            if not is_valid:
                response, status = create_error_response(
                    "SMS_002",
                    "Invalid or expired verification code",
                    400
                )
                return jsonify(response), status
        except Exception as e:
            logging.warning(f"SMS verification failed for order: {str(e)}")
            response, status = create_error_response(
                "SMS_002", 
                "Phone verification required",
                403
            )
            return jsonify(response), status
        
        # Validate and process items
        items_data = data['items']
        processed_items = []
        total_amount = 0
        
        for item in items_data:
            product = Product.find_by_id(item['product_id'])
            if not product:
                response, status = create_error_response(
                    "VAL_001",
                    f"Product not found: {item['product_id']}",
                    400
                )
                return jsonify(response), status
            
            # Check availability
            if not product.is_available:
                response, status = create_error_response(
                    "VAL_001",
                    f"Product is not available: {product.name}",
                    400
                )
                return jsonify(response), status
            
            # Check stock
            if product.stock_quantity < item['quantity']:
                response, status = create_error_response(
                    "STOCK_001",
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}",
                    409
                )
                return jsonify(response), status
            
            # Calculate item total
            item_total = product.price * item['quantity']
            total_amount += item_total
            
            # Prepare processed item
            processed_item = {
                'product_id': product._id,
                'product_name': product.name,
                'product_price': float(product.price),
                'quantity': item['quantity'],
                'item_total': float(item_total)
            }
            processed_items.append(processed_item)
        
        # Parse requested time if provided
        requested_time = None
        if data.get('requested_time'):
            try:
                requested_time = datetime.fromisoformat(data['requested_time'].replace('Z', '+00:00'))
                # Validate that requested time is in the future
                if requested_time <= datetime.utcnow():
                    response, status = create_error_response(
                        "VAL_001",
                        "Requested time must be in the future",
                        400
                    )
                    return jsonify(response), status
            except ValueError:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid requested time format",
                    400
                )
                return jsonify(response), status
        
        # Create order
        order = Order.create(
            customer_phone=customer_phone,
            customer_name=data['customer_name'],
            items=processed_items,
            delivery_type=data['delivery_type'],
            delivery_address=data.get('delivery_address'),
            delivery_phone=data.get('delivery_phone'),
            requested_time=requested_time,
            special_instructions=data.get('special_instructions')
        )
        
        # Update product stock quantities
        for item in items_data:
            product = Product.find_by_id(item['product_id'])
            if product:
                product.update_stock(item['quantity'], 'subtract')
        
        # Send order confirmation SMS
        try:
            confirmation_message = f"Order confirmed! Order #{order.order_number}. Total: ${order.total:.2f}. We'll notify you when ready."
            sms_service.send_notification(customer_phone, confirmation_message)
        except Exception as e:
            logging.warning(f"Failed to send order confirmation SMS: {str(e)}")
            # Don't fail the order creation if SMS fails
        
        # Return created order
        order_dict = order.to_dict()
        
        logging.info(f"Legacy order created: {order.order_number} for {customer_phone[-4:]}")
        
        return jsonify(success_response(
            {'order': order_dict},
            f"Order created successfully: {order.order_number}"
        )), 201
        
    except ValidationError as e:
        response, status = create_error_response(
            "VAL_001",
            str(e),
            400
        )
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Error creating legacy order: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to create order",
            500
        )
        return jsonify(response), status


@orders_bp.route('/customer/<phone>', methods=['GET'])
def get_customer_orders(phone):
    """
    Get customer orders by phone number.
    
    Args:
        phone (str): Customer phone number
        
    Query Parameters:
        - limit (int): Maximum number of orders to return (default: 10, max: 50)
        - status (str): Filter by order status
    """
    try:
        # Validate and normalize phone number
        try:
            normalized_phone = validate_phone_number(phone)
        except ValidationError:
            response, status = create_error_response(
                "VAL_001",
                "Invalid phone number format",
                400
            )
            return jsonify(response), status
        
        # Parse query parameters
        limit = min(50, max(1, int(request.args.get('limit', 10))))
        status_filter = request.args.get('status')
        
        # Validate status filter
        if status_filter and status_filter not in Order.VALID_STATUSES:
            response, status = create_error_response(
                "VAL_001",
                f"Invalid status. Valid statuses: {', '.join(Order.VALID_STATUSES)}",
                400
            )
            return jsonify(response), status
        
        # Find customer orders
        orders = Order.find_by_customer_phone(
            normalized_phone, 
            limit=limit,
            status_filter=status_filter
        )
        
        # Convert to dict format
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            orders_data.append(order_dict)
        
        response_data = {
            'customer_phone': normalized_phone,
            'orders': orders_data,
            'total_orders': len(orders_data),
            'filters': {
                'limit': limit,
                'status': status_filter
            }
        }
        
        logging.info(f"Customer orders retrieved: {normalized_phone[-4:]} - {len(orders_data)} orders")
        
        return jsonify(success_response(
            response_data,
            f"Retrieved {len(orders_data)} orders"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving customer orders: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve orders",
            500
        )
        return jsonify(response), status


@orders_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get individual order details by ID or order number.
    
    Args:
        order_id (str): Order ObjectId or order number
    """
    try:
        # Try to find by ObjectId first, then by order number
        order = None
        
        # Check if it's a valid ObjectId format
        if re.match(r'^[0-9a-fA-F]{24}$', order_id):
            order = Order.find_by_id(order_id)
        
        # If not found by ID, try by order number
        if not order:
            order = Order.find_by_order_number(order_id)
        
        # If still not found, return 404
        if not order:
            response, status = create_error_response(
                "NOT_001",
                "Order not found",
                404
            )
            return jsonify(response), status
        
        # Get order data
        order_dict = order.to_dict()
        
        logging.info(f"Order retrieved: {order.order_number}")
        
        return jsonify(success_response(
            {'order': order_dict},
            "Order retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving order: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve order",
            500
        )
        return jsonify(response), status


@orders_bp.route('/<order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """
    Cancel order (customer or admin).
    
    Customers can cancel pending orders.
    Admins can cancel any non-delivered order.
    
    Args:
        order_id (str): Order ObjectId or order number
    """
    try:
        # Find order
        order = None
        if re.match(r'^[0-9a-fA-F]{24}$', order_id):
            order = Order.find_by_id(order_id)
        else:
            order = Order.find_by_order_number(order_id)
        
        if not order:
            response, status = create_error_response(
                "NOT_001",
                "Order not found",
                404
            )
            return jsonify(response), status
        
        # Check if order can be cancelled
        if order.status == Order.STATUS_CANCELLED:
            return jsonify(success_response(
                {'order_id': order_id, 'cancelled': True},
                "Order is already cancelled"
            )), 200
        
        if order.status == Order.STATUS_DELIVERED:
            response, status = create_error_response(
                "VAL_001",
                "Cannot cancel delivered order",
                400
            )
            return jsonify(response), status
        
        # Check authorization
        is_admin = False
        try:
            # Check if user is authenticated admin
            user_id = session.get('user_id')
            if user_id:
                from app.models.user import User
                user = User.find_by_id(user_id)
                if user and user.role == User.ROLE_ADMIN:
                    is_admin = True
        except:
            pass
        
        # Non-admin users can only cancel pending orders
        if not is_admin and order.status != Order.STATUS_PENDING:
            response, status = create_error_response(
                "AUTH_003",
                "Only pending orders can be cancelled by customers",
                403
            )
            return jsonify(response), status
        
        # Cancel the order
        success = order.update_status(Order.STATUS_CANCELLED)
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Failed to cancel order",
                500
            )
            return jsonify(response), status
        
        # Restore product stock
        for item in order.items:
            product = Product.find_by_id(item['product_id'])
            if product:
                product.update_stock(item['quantity'], 'add')
        
        # Send cancellation SMS to customer
        try:
            sms_service = get_sms_service()
            cancellation_message = f"Order #{order.order_number} has been cancelled. Stock has been restored."
            sms_service.send_notification(order.customer_phone, cancellation_message)
        except Exception as e:
            logging.warning(f"Failed to send cancellation SMS: {str(e)}")
        
        actor = "admin" if is_admin else "customer"
        logging.info(f"Order cancelled by {actor}: {order.order_number}")
        
        return jsonify(success_response(
            {
                'order_id': order_id,
                'order_number': order.order_number,
                'cancelled': True,
                'cancelled_by': actor
            },
            "Order cancelled successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error cancelling order: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to cancel order",
            500
        )
        return jsonify(response), status


@orders_bp.route('/', methods=['GET'])
@require_admin
def list_orders():
    """
    List all orders with filtering (admin only).
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - limit (int): Items per page (default: 20, max: 100)
        - status (str): Filter by order status
        - customer_phone (str): Filter by customer phone
        - date_from (str): Filter orders from date (YYYY-MM-DD)
        - date_to (str): Filter orders to date (YYYY-MM-DD)
        - sort_by (str): Sort field (created_at, total, status) (default: created_at)
        - sort_order (str): Sort order (asc, desc) (default: desc)
    """
    try:
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        status_filter = request.args.get('status')
        customer_phone = request.args.get('customer_phone')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate parameters
        if status_filter and status_filter not in Order.VALID_STATUSES:
            response, status = create_error_response(
                "VAL_001",
                f"Invalid status. Valid statuses: {', '.join(Order.VALID_STATUSES)}",
                400
            )
            return jsonify(response), status
        
        valid_sort_fields = ['created_at', 'total', 'status', 'order_number']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Build query
        query = {}
        
        if status_filter:
            query['status'] = status_filter
        
        if customer_phone:
            try:
                normalized_phone = validate_phone_number(customer_phone)
                query['customer_phone'] = normalized_phone
            except ValidationError:
                response, status = create_error_response(
                    "VAL_001",
                    "Invalid customer phone format",
                    400
                )
                return jsonify(response), status
        
        # Date range filtering
        if date_from or date_to:
            date_query = {}
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from)
                    date_query['$gte'] = from_date
                except ValueError:
                    response, status = create_error_response(
                        "VAL_001",
                        "Invalid date_from format. Use YYYY-MM-DD",
                        400
                    )
                    return jsonify(response), status
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to) + timedelta(days=1)
                    date_query['$lt'] = to_date
                except ValueError:
                    response, status = create_error_response(
                        "VAL_001",
                        "Invalid date_to format. Use YYYY-MM-DD",
                        400
                    )
                    return jsonify(response), status
            
            query['created_at'] = date_query
        
        # Build aggregation pipeline
        pipeline = [
            {'$match': query},
            {'$sort': {sort_by: sort_direction}},
            {
                '$facet': {
                    'orders': [
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
        from app.database import get_database
        db = get_database()
        collection = db[Order.COLLECTION_NAME]
        
        result = list(collection.aggregate(pipeline))[0]
        orders_data = result['orders']
        total_count = result['total_count'][0]['count'] if result['total_count'] else 0
        
        # Convert orders to dict format
        orders = []
        for order_doc in orders_data:
            order = Order(order_doc)
            order_dict = order.to_dict(include_internal=True)
            orders.append(order_dict)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = {
            'orders': orders,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'status': status_filter,
                'customer_phone': customer_phone,
                'date_from': date_from,
                'date_to': date_to,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
        
        user = request.current_user
        logging.info(f"Orders listed by admin {user.phone_number[-4:]}: {len(orders)} items")
        
        return jsonify(success_response(
            response_data,
            f"Retrieved {len(orders)} orders"
        )), 200
        
    except Exception as e:
        logging.error(f"Error listing orders: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve orders",
            500
        )
        return jsonify(response), status


@orders_bp.route('/<order_id>/status', methods=['PUT'])
@require_admin
def update_order_status(order_id):
    """
    Update order status (admin only).
    
    Args:
        order_id (str): Order ObjectId or order number
        
    Expects JSON with new status.
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            response, status = create_error_response(
                "VAL_001",
                "Status is required",
                400
            )
            return jsonify(response), status
        
        new_status = data['status']
        if new_status not in Order.VALID_STATUSES:
            response, status = create_error_response(
                "VAL_001",
                f"Invalid status. Valid statuses: {', '.join(Order.VALID_STATUSES)}",
                400
            )
            return jsonify(response), status
        
        # Find order
        order = None
        if re.match(r'^[0-9a-fA-F]{24}$', order_id):
            order = Order.find_by_id(order_id)
        else:
            order = Order.find_by_order_number(order_id)
        
        if not order:
            response, status = create_error_response(
                "NOT_001",
                "Order not found",
                404
            )
            return jsonify(response), status
        
        # Update status
        old_status = order.status
        success = order.update_status(new_status)
        
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Failed to update order status",
                500
            )
            return jsonify(response), status
        
        # Send status update SMS to customer
        try:
            sms_service = get_sms_service()
            status_messages = {
                Order.STATUS_CONFIRMED: f"Order #{order.order_number} confirmed! We'll start preparing your order.",
                Order.STATUS_PREPARING: f"Order #{order.order_number} is being prepared.",
                Order.STATUS_READY: f"Order #{order.order_number} is ready for pickup/delivery!",
                Order.STATUS_DELIVERED: f"Order #{order.order_number} has been delivered. Thank you!"
            }
            
            if new_status in status_messages:
                message = status_messages[new_status]
                sms_service.send_notification(order.customer_phone, message)
        except Exception as e:
            logging.warning(f"Failed to send status update SMS: {str(e)}")
        
        user = request.current_user
        logging.info(f"Order status updated by admin {user.phone_number[-4:]}: {order.order_number} ({old_status} -> {new_status})")
        
        return jsonify(success_response(
            {
                'order_id': order_id,
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status,
                'updated': True
            },
            f"Order status updated to {new_status}"
        )), 200
        
    except Exception as e:
        logging.error(f"Error updating order status: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to update order status",
            500
        )
        return jsonify(response), status


@orders_bp.route('/admin/orders', methods=['GET'])
@require_admin_auth
def get_admin_orders():
    """
    Get all orders for admin management (admin only).
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - limit (int): Items per page (default: 20, max: 100)
        - status (str): Filter by order status (pending, confirmed, completed, cancelled)
        - customer_phone (str): Filter by customer phone number
        - customer_name (str): Filter by customer name
        - start_date (str): Filter orders from this date (YYYY-MM-DD format)
        - end_date (str): Filter orders until this date (YYYY-MM-DD format)
        - min_total (float): Minimum order total filter
        - max_total (float): Maximum order total filter
        - sort_by (str): Sort field (created_at, total, status, customer_name) (default: created_at)
        - sort_order (str): Sort order (asc, desc) (default: desc)
    
    Romanian localized endpoint for admin order management with comprehensive
    filtering, sorting, and pagination capabilities.
    """
    try:
        from flask import g
        admin_user = g.current_admin_user
        
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(100, max(1, int(request.args.get('limit', 20))))
        status_filter = request.args.get('status')
        customer_phone = request.args.get('customer_phone')
        customer_name = request.args.get('customer_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_total = request.args.get('min_total')
        max_total = request.args.get('max_total')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort parameters
        valid_sort_fields = ['created_at', 'updated_at', 'total', 'status', 'customer_name', 'order_number']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Build query filters
        query = {}
        
        # Filter by status
        if status_filter:
            valid_statuses = [Order.STATUS_PENDING, Order.STATUS_CONFIRMED, 
                            Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]
            if status_filter in valid_statuses:
                query['status'] = status_filter
            else:
                response, status = create_error_response(
                    "VAL_001",
                    f"Status invalid. Valori permise: {', '.join(valid_statuses)}",
                    400
                )
                return jsonify(response), status
        
        # Filter by customer phone
        if customer_phone:
            # Support partial phone number matching
            query['customer_phone'] = {'$regex': re.escape(customer_phone), '$options': 'i'}
        
        # Filter by customer name
        if customer_name:
            query['customer_name'] = {'$regex': re.escape(customer_name), '$options': 'i'}
        
        # Filter by date range
        date_filter = {}
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                date_filter['$gte'] = start_datetime
            except ValueError:
                response, status = create_error_response(
                    "VAL_001",
                    "Data de început invalidă. Folosiți formatul YYYY-MM-DD",
                    400
                )
                return jsonify(response), status
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                # Add one day to include the entire end date
                end_datetime = end_datetime + timedelta(days=1)
                date_filter['$lt'] = end_datetime
            except ValueError:
                response, status = create_error_response(
                    "VAL_001",
                    "Data de sfârșit invalidă. Folosiți formatul YYYY-MM-DD",
                    400
                )
                return jsonify(response), status
        
        if date_filter:
            query['created_at'] = date_filter
        
        # Filter by total amount range
        total_filter = {}
        if min_total:
            try:
                min_amount = float(min_total)
                if min_amount < 0:
                    response, status = create_error_response(
                        "VAL_001",
                        "Suma minimă nu poate fi negativă",
                        400
                    )
                    return jsonify(response), status
                total_filter['$gte'] = min_amount
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Suma minimă invalidă. Introduceți un număr valid",
                    400
                )
                return jsonify(response), status
        
        if max_total:
            try:
                max_amount = float(max_total)
                if max_amount < 0:
                    response, status = create_error_response(
                        "VAL_001",
                        "Suma maximă nu poate fi negativă",
                        400
                    )
                    return jsonify(response), status
                total_filter['$lte'] = max_amount
            except (ValueError, TypeError):
                response, status = create_error_response(
                    "VAL_001",
                    "Suma maximă invalidă. Introduceți un număr valid",
                    400
                )
                return jsonify(response), status
        
        if total_filter:
            query['total'] = total_filter
        
        # Validate min/max total relationship
        if min_total and max_total:
            try:
                if float(min_total) > float(max_total):
                    response, status = create_error_response(
                        "VAL_001",
                        "Suma minimă nu poate fi mai mare decât suma maximă",
                        400
                    )
                    return jsonify(response), status
            except (ValueError, TypeError):
                pass  # Already handled above
        
        # Build aggregation pipeline for efficient data retrieval
        pipeline = [
            {'$match': query},
            {'$sort': {sort_by: sort_direction}},
            {
                '$facet': {
                    'orders': [
                        {'$skip': (page - 1) * limit},
                        {'$limit': limit}
                    ],
                    'total_count': [
                        {'$count': 'count'}
                    ],
                    'statistics': [
                        {
                            '$group': {
                                '_id': None,
                                'total_revenue': {'$sum': '$total'},
                                'avg_order_value': {'$avg': '$total'},
                                'status_counts': {
                                    '$push': '$status'
                                }
                            }
                        }
                    ]
                }
            }
        ]
        
        # Execute aggregation
        from app.database import get_database
        db = get_database()
        collection = db[Order.COLLECTION_NAME]
        
        result = list(collection.aggregate(pipeline))[0]
        orders_data = result['orders']
        total_count = result['total_count'][0]['count'] if result['total_count'] else 0
        
        # Process statistics
        statistics = {
            'total_orders': total_count,
            'total_revenue': 0,
            'avg_order_value': 0,
            'status_breakdown': {}
        }
        
        if result['statistics']:
            stats = result['statistics'][0]
            statistics['total_revenue'] = stats.get('total_revenue', 0)
            statistics['avg_order_value'] = stats.get('avg_order_value', 0)
            
            # Count status breakdown
            status_counts = {}
            for status in stats.get('status_counts', []):
                status_counts[status] = status_counts.get(status, 0) + 1
            statistics['status_breakdown'] = status_counts
        
        # Convert orders to dict format with enhanced information
        orders = []
        for order_doc in orders_data:
            order = Order(order_doc)
            order_dict = order.to_dict(include_internal=True)
            
            # Add computed fields for admin convenience
            order_dict['days_since_created'] = (datetime.utcnow() - order.created_at).days
            order_dict['item_count'] = len(order.items) if order.items else 0
            
            # Add Romanian status description
            status_descriptions = {
                Order.STATUS_PENDING: "În așteptare",
                Order.STATUS_CONFIRMED: "Confirmată",
                Order.STATUS_COMPLETED: "Finalizată",
                Order.STATUS_CANCELLED: "Anulată"
            }
            order_dict['status_description'] = status_descriptions.get(order.status, order.status)
            
            orders.append(order_dict)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response_data = {
            'orders': orders,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'status': status_filter,
                'customer_phone': customer_phone,
                'customer_name': customer_name,
                'start_date': start_date,
                'end_date': end_date,
                'min_total': min_total,
                'max_total': max_total,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'statistics': statistics
        }
        
        # Log admin action for audit trail
        log_admin_action(
            "Comenzi vizualizate", 
            {
                "total_orders": total_count,
                "page": page,
                "filters_applied": bool(status_filter or customer_phone or customer_name or start_date or end_date or min_total or max_total)
            }
        )
        
        logging.info(f"Admin orders retrieved by {admin_user['phone_number'][-4:]}: {len(orders)} orders (page {page}/{total_pages})")
        
        return jsonify(success_response(
            response_data,
            f"Au fost găsite {total_count} comenzi"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving admin orders: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare la încărcarea comenzilor. Încercați din nou",
            500
        )
        return jsonify(response), status


@orders_bp.route('/admin/orders/<order_id>/status', methods=['PUT'])
@require_admin_auth
def update_admin_order_status(order_id):
    """
    Update order status (admin only) with enhanced validation and Romanian localization.
    
    Args:
        order_id (str): Order ObjectId or order number
        
    Expects JSON with new status:
    {
        "status": "confirmed" | "completed" | "cancelled"
    }
    
    Romanian localized endpoint for admin order status management with
    business rule enforcement, customer notifications, and audit logging.
    """
    try:
        from flask import g
        admin_user = g.current_admin_user
        
        # Validate request payload
        data = request.get_json()
        if not data or 'status' not in data:
            response, status = create_error_response(
                "VAL_001",
                "Statusul comenzii este obligatoriu în datele trimise",
                400
            )
            return jsonify(response), status
        
        new_status = data['status'].strip()
        if not new_status:
            response, status = create_error_response(
                "VAL_001",
                "Statusul comenzii nu poate fi gol",
                400
            )
            return jsonify(response), status
        
        # Validate status value
        valid_statuses = [Order.STATUS_PENDING, Order.STATUS_CONFIRMED, 
                         Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]
        if new_status not in valid_statuses:
            valid_status_names = {
                Order.STATUS_PENDING: "în așteptare",
                Order.STATUS_CONFIRMED: "confirmată", 
                Order.STATUS_COMPLETED: "finalizată",
                Order.STATUS_CANCELLED: "anulată"
            }
            valid_list = [f"{status} ({valid_status_names[status]})" for status in valid_statuses]
            response, status = create_error_response(
                "VAL_001",
                f"Status invalid. Statusuri permise: {', '.join(valid_list)}",
                400
            )
            return jsonify(response), status
        
        # Find order by ID or order number
        order = None
        if re.match(r'^[0-9a-fA-F]{24}$', order_id):
            order = Order.find_by_id(order_id)
        else:
            order = Order.find_by_order_number(order_id)
        
        if not order:
            response, status = create_error_response(
                "NOT_001",
                "Comanda specificată nu a fost găsită în sistem",
                404
            )
            return jsonify(response), status
        
        # Store current status for comparison and logging
        old_status = order.status
        
        # Check if status is already the same
        if old_status == new_status:
            status_descriptions = {
                Order.STATUS_PENDING: "în așteptare",
                Order.STATUS_CONFIRMED: "confirmată",
                Order.STATUS_COMPLETED: "finalizată", 
                Order.STATUS_CANCELLED: "anulată"
            }
            current_desc = status_descriptions.get(old_status, old_status)
            return jsonify(success_response(
                {
                    'order_id': order_id,
                    'order_number': order.order_number,
                    'status': old_status,
                    'status_description': current_desc,
                    'changed': False
                },
                f"Comanda #{order.order_number} este deja în statusul '{current_desc}'"
            )), 200
        
        # Validate status transitions based on business rules
        transition_rules = {
            Order.STATUS_PENDING: [Order.STATUS_CONFIRMED, Order.STATUS_CANCELLED],
            Order.STATUS_CONFIRMED: [Order.STATUS_COMPLETED, Order.STATUS_CANCELLED],
            Order.STATUS_COMPLETED: [],  # No further transitions allowed
            Order.STATUS_CANCELLED: []   # No further transitions allowed
        }
        
        allowed_transitions = transition_rules.get(old_status, [])
        if new_status not in allowed_transitions:
            old_desc = {
                Order.STATUS_PENDING: "în așteptare",
                Order.STATUS_CONFIRMED: "confirmată",
                Order.STATUS_COMPLETED: "finalizată",
                Order.STATUS_CANCELLED: "anulată"
            }.get(old_status, old_status)
            
            new_desc = {
                Order.STATUS_PENDING: "în așteptare", 
                Order.STATUS_CONFIRMED: "confirmată",
                Order.STATUS_COMPLETED: "finalizată",
                Order.STATUS_CANCELLED: "anulată"
            }.get(new_status, new_status)
            
            if not allowed_transitions:
                response, status = create_error_response(
                    "VAL_001",
                    f"Comanda cu statusul '{old_desc}' nu mai poate fi modificată",
                    400
                )
                return jsonify(response), status
            else:
                allowed_desc = [
                    {
                        Order.STATUS_PENDING: "în așteptare",
                        Order.STATUS_CONFIRMED: "confirmată", 
                        Order.STATUS_COMPLETED: "finalizată",
                        Order.STATUS_CANCELLED: "anulată"
                    }.get(s, s) for s in allowed_transitions
                ]
                response, status = create_error_response(
                    "VAL_001",
                    f"Tranziția de la '{old_desc}' la '{new_desc}' nu este permisă. Statusuri permise: {', '.join(allowed_desc)}",
                    400
                )
                return jsonify(response), status
        
        # Update order status
        success = order.update_status(new_status)
        
        if not success:
            response, status = create_error_response(
                "DB_001",
                "Eroare la actualizarea statusului comenzii. Încercați din nou",
                500
            )
            return jsonify(response), status
        
        # Send SMS notification to customer with Romanian messages
        try:
            sms_service = get_sms_service()
            status_messages = {
                Order.STATUS_CONFIRMED: f"Comanda #{order.order_number} a fost confirmată! Vom începe să vă pregătim comanda.",
                Order.STATUS_COMPLETED: f"Comanda #{order.order_number} a fost finalizată cu succes. Mulțumim pentru încredere!",
                Order.STATUS_CANCELLED: f"Comanda #{order.order_number} a fost anulată. Pentru întrebări, vă rugăm să ne contactați."
            }
            
            if new_status in status_messages:
                message = status_messages[new_status]
                sms_service.send_notification(order.customer_phone, message)
                logging.info(f"Status update SMS sent to {order.customer_phone[-4:]} for order {order.order_number}")
        except Exception as e:
            logging.warning(f"Failed to send status update SMS for order {order.order_number}: {str(e)}")
            # Don't fail the status update if SMS fails
        
        # Prepare response with Romanian status descriptions
        status_descriptions = {
            Order.STATUS_PENDING: "în așteptare",
            Order.STATUS_CONFIRMED: "confirmată",
            Order.STATUS_COMPLETED: "finalizată",
            Order.STATUS_CANCELLED: "anulată"
        }
        
        old_status_desc = status_descriptions.get(old_status, old_status)
        new_status_desc = status_descriptions.get(new_status, new_status)
        
        response_data = {
            'order_id': order_id,
            'order_number': order.order_number,
            'old_status': old_status,
            'old_status_description': old_status_desc,
            'new_status': new_status,
            'new_status_description': new_status_desc,
            'updated': True,
            'customer_phone': order.customer_phone,
            'customer_name': order.customer_name,
            'total': order.total
        }
        
        # Log admin action for audit trail
        log_admin_action(
            "Status comandă actualizat", 
            {
                "order_id": order_id,
                "order_number": order.order_number,
                "old_status": old_status,
                "new_status": new_status,
                "customer_phone": order.customer_phone[-4:] if order.customer_phone else None
            }
        )
        
        logging.info(f"Order status updated by admin {admin_user['phone_number'][-4:]}: {order.order_number} ({old_status_desc} → {new_status_desc})")
        
        return jsonify(success_response(
            response_data,
            f"Statusul comenzii #{order.order_number} a fost actualizat de la '{old_status_desc}' la '{new_status_desc}'"
        )), 200
        
    except Exception as e:
        logging.error(f"Error updating admin order status: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Eroare neașteptată la actualizarea statusului comenzii. Încercați din nou",
            500
        )
        return jsonify(response), status


@orders_bp.route('/<order_id>/admin', methods=['GET'])
@require_admin
def get_order_admin(order_id):
    """
    Get order details with internal information (admin only).
    
    Args:
        order_id (str): Order ObjectId or order number
    """
    try:
        # Find order
        order = None
        if re.match(r'^[0-9a-fA-F]{24}$', order_id):
            order = Order.find_by_id(order_id)
        else:
            order = Order.find_by_order_number(order_id)
        
        if not order:
            response, status = create_error_response(
                "NOT_001",
                "Order not found",
                404
            )
            return jsonify(response), status
        
        # Get order data with internal fields
        order_dict = order.to_dict(include_internal=True)
        
        user = request.current_user
        logging.info(f"Order admin details retrieved by {user.phone_number[-4:]}: {order.order_number}")
        
        return jsonify(success_response(
            {'order': order_dict},
            "Order details retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving order admin details: {str(e)}")
        response, status = create_error_response(
            "DB_001",
            "Failed to retrieve order",
            500
        )
        return jsonify(response), status