"""
Order Management Routes for Local Producer Web Application

This module provides order management endpoints including order creation with
cart integration, SMS verification, and admin order management.
Updated to support phone-based checkout without traditional user accounts.
"""

import logging
import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, g, current_app
from bson import ObjectId
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.models.customer_phone import CustomerPhone
from app.services.order_service import get_order_service, OrderValidationError, OrderCreationError
from app.services.sms_service import get_sms_service
from app.services.sms_provider import SMSService
from app.utils.validators import validate_json, validate_phone_number
from app.utils.error_handlers import (
    ValidationError, AuthorizationError, NotFoundError, SMSError,
    success_response, create_error_response
)
from app.routes.auth import require_auth
from app.utils.auth_middleware import require_admin_auth, log_admin_action
from app.utils.checkout_auth import checkout_auth_optional, checkout_auth_required

# Create orders blueprint
orders_bp = Blueprint('orders', __name__)

# Logger for this module
logger = logging.getLogger(__name__)

# Admin role decorator
def require_admin(f):
    """Decorator to require admin role for endpoints."""
    from functools import wraps
    @require_auth
    @wraps(f)
    def admin_decorated_function(*args, **kwargs):
        user = request.current_user
        if user.role != User.ROLE_ADMIN:
            raise AuthorizationError("Admin access required")
        return f(*args, **kwargs)
    return admin_decorated_function


# Order creation JSON schema for phone-based checkout
ORDER_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "cart_session_id": {
            "type": "string",
            "minLength": 1,
            "description": "Session ID for the shopping cart"
        },
        "address_id": {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{24}$",
            "description": "ID of saved address (for authenticated users)"
        },
        "customer_info": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "pattern": "^(0|\\+40)7[0-9]{8}$",
                    "description": "Romanian phone number"
                },
                "customer_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "description": "Customer full name"
                },
                "delivery_address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string", "minLength": 5, "maxLength": 100},
                        "city": {"type": "string", "minLength": 2, "maxLength": 50},
                        "county": {"type": "string", "minLength": 2, "maxLength": 50},
                        "postal_code": {"type": "string", "pattern": "^[0-9]{6}$"},
                        "notes": {"type": "string", "maxLength": 200}
                    },
                    "required": ["street", "city", "county", "postal_code"],
                    "additionalProperties": False,
                    "description": "Delivery address (for guest checkout)"
                },
                "special_instructions": {
                    "type": "string",
                    "maxLength": 500,
                    "description": "Special delivery instructions (optional)"
                }
            },
            "required": ["customer_name"],
            "additionalProperties": False
        }
    },
    "required": ["cart_session_id", "customer_info"],
    "additionalProperties": False
}


@orders_bp.route('', methods=['POST'])
@checkout_auth_optional
@validate_json(ORDER_CREATE_SCHEMA)
def create_order():
    """
    Create new order from cart with phone-based checkout.
    
    Supports both authenticated (with saved addresses) and guest checkout.
    For authenticated users: Use address_id to select saved address.
    For guests: Provide phone_number and delivery_address in customer_info.
    
    Required payload:
    - cart_session_id: String
    - customer_info: Object with customer_name, special_instructions (optional)
    - address_id: String (for authenticated users)
    OR
    - customer_info.phone_number: String (for guests)
    - customer_info.delivery_address: Object (for guests)
    
    Returns: Order confirmation with order number and details
    """
    try:
        data = request.get_json()
        cart_session_id = data['cart_session_id']
        customer_info = data['customer_info']
        
        # DEBUG LOGGING
        logger.info(f"=== ORDER CREATION DEBUG ===")
        logger.info(f"g.is_authenticated: {getattr(g, 'is_authenticated', 'NOT SET')}")
        logger.info(f"g.customer_phone: {getattr(g, 'customer_phone', 'NOT SET')}")
        logger.info(f"g.customer_id: {getattr(g, 'customer_id', 'NOT SET')}")
        logger.info(f"Request headers Authorization: {request.headers.get('Authorization', 'NOT SET')}")
        logger.info(f"Cart session ID: {cart_session_id}")
        logger.info(f"Customer info: {customer_info}")
        logger.info(f"Address ID in data: {data.get('address_id', 'NOT PROVIDED')}")
        
        # Determine checkout flow based on authentication
        if g.is_authenticated:
            # Authenticated flow - use saved address
            address_id = data.get('address_id')
            if not address_id:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'ADDRESS_REQUIRED',
                        'message': 'Selectați o adresă de livrare'
                    }
                }), 400
            
            # Get customer and verify address ownership
            customer = CustomerPhone.find_by_phone(g.customer_phone)
            if not customer:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'CUSTOMER_NOT_FOUND',
                        'message': 'Contul nu a fost găsit'
                    }
                }), 404
            
            # Find selected address
            from bson import ObjectId
            try:
                address_obj_id = ObjectId(address_id)
            except Exception as e:
                logger.error(f"Invalid address ID format: {address_id}")
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_ADDRESS_ID',
                        'message': 'ID adresă invalid'
                    }
                }), 400
            selected_address = None
            for addr in customer.addresses:
                if addr['_id'] == address_obj_id:
                    selected_address = addr
                    break
            
            if not selected_address:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'ADDRESS_NOT_FOUND',
                        'message': 'Adresa selectată nu a fost găsită'
                    }
                }), 404
            
            # Prepare order data
            order_phone = customer.phone
            order_name = customer_info.get('customer_name', customer.name)
            delivery_address = {
                'street': selected_address['street'],
                'city': selected_address['city'],
                'county': selected_address['county'],
                'postal_code': selected_address['postal_code'],
                'notes': selected_address.get('notes', '')
            }
            
            # Mark address as used
            customer.mark_address_used(address_id)
            customer.save()
            
        else:
            # Guest flow - validate provided info
            logger.info(f"=== GUEST FLOW - NOT AUTHENTICATED ===")
            logger.info(f"Phone number in customer_info: {customer_info.get('phone_number', 'NOT PROVIDED')}")
            if not customer_info.get('phone_number'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'PHONE_REQUIRED',
                        'message': 'Numărul de telefon este obligatoriu pentru comandă'
                    }
                }), 400
            
            if not customer_info.get('delivery_address'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'ADDRESS_REQUIRED',
                        'message': 'Adresa de livrare este obligatorie'
                    }
                }), 400
            
            # Create/update customer record
            order_phone = customer_info['phone_number']
            order_name = customer_info['customer_name']
            delivery_address = customer_info['delivery_address']
            
            # Normalize phone
            temp_customer = CustomerPhone()
            order_phone = temp_customer.normalize_phone(order_phone)
            
            # Create or update customer
            customer = CustomerPhone.find_by_phone(order_phone)
            if customer:
                # Update name if different
                if customer.name != order_name:
                    customer.name = order_name
                
                # Check if address already exists
                address_exists = False
                for addr in customer.addresses:
                    if (addr['street'] == delivery_address['street'] and
                        addr['city'] == delivery_address['city'] and
                        addr['postal_code'] == delivery_address['postal_code']):
                        address_exists = True
                        addr['usage_count'] = addr.get('usage_count', 0) + 1
                        addr['last_used'] = datetime.utcnow()
                        break
                
                # Add new address if doesn't exist
                if not address_exists and len(customer.addresses) < CustomerPhone.MAX_ADDRESSES:
                    from bson import ObjectId
                    new_address = {
                        '_id': ObjectId(),
                        'street': delivery_address['street'],
                        'city': delivery_address['city'],
                        'county': delivery_address['county'],
                        'postal_code': delivery_address['postal_code'],
                        'notes': delivery_address.get('notes', ''),
                        'is_default': len(customer.addresses) == 0,
                        'usage_count': 1,
                        'last_used': datetime.utcnow(),
                        'created_at': datetime.utcnow()
                    }
                    customer.addresses.append(new_address)
                
                # Don't save here, will save after order creation
            else:
                # Create new customer
                from bson import ObjectId
                customer = CustomerPhone({
                    'phone': order_phone,
                    'name': order_name,
                    'addresses': [{
                        '_id': ObjectId(),
                        'street': delivery_address['street'],
                        'city': delivery_address['city'],
                        'county': delivery_address['county'],
                        'postal_code': delivery_address['postal_code'],
                        'notes': delivery_address.get('notes', ''),
                        'is_default': True,
                        'usage_count': 1,
                        'last_used': datetime.utcnow(),
                        'created_at': datetime.utcnow()
                    }]
                })
                # Don't save here, will save after order creation
        
        # Get cart items (simplified - should use cart service)
        from app.database import get_database
        db = get_database()
        cart = db.cart_sessions.find_one({'session_id': cart_session_id})
        
        if not cart or not cart.get('items'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CART_EMPTY',
                    'message': 'Coșul de cumpărături este gol'
                }
            }), 400
        
        # Calculate total
        total_amount = sum(item['quantity'] * item.get('price', item.get('unit_price', 0)) for item in cart['items'])
        
        # Create order
        from bson import ObjectId
        from app.services.order_service import OrderService
        
        # Use OrderService to generate incremental order number
        order_service = OrderService()
        order_number = order_service._generate_order_number()
        
        order_data = {
            'order_number': order_number,
            'customer_phone': order_phone,
            'customer_name': order_name,
            'delivery_address': delivery_address,
            'items': cart['items'],
            'total_amount': total_amount,
            'status': 'pending',
            'special_instructions': customer_info.get('special_instructions', ''),
            'created_at': datetime.utcnow()
        }
        
        result = db.orders.insert_one(order_data)
        order_data['_id'] = result.inserted_id
        
        # Update customer order count and save
        customer.total_orders += 1
        customer.last_order_date = datetime.utcnow()
        
        # Handle concurrent update with retry
        for retry in range(3):
            try:
                customer.save()
                break
            except ValueError as e:
                if "Concurrent update" in str(e) and retry < 2:
                    # Reload customer and try again
                    logger.warning(f"Concurrent update detected, retrying ({retry + 1}/3)")
                    fresh_customer = CustomerPhone.find_by_phone(order_phone)
                    if fresh_customer:
                        fresh_customer.total_orders += 1
                        fresh_customer.last_order_date = datetime.utcnow()
                        customer = fresh_customer
                    else:
                        # Customer was deleted somehow, recreate
                        customer.total_orders = 1
                        customer.last_order_date = datetime.utcnow()
                else:
                    raise
        
        # Clear cart
        db.carts.delete_one({'session_id': cart_session_id})
        
        # Send order confirmation SMS
        try:
            SMSService.send_order_confirmation(order_phone, order_data['order_number'])
        except Exception as e:
            logger.warning(f"Failed to send order confirmation SMS: {str(e)}")
        
        # Return order confirmation
        return jsonify({
            'success': True,
            'order': {
                'order_number': order_data['order_number'],
                'total_amount': total_amount,
                'status': 'pending',
                'delivery_address': delivery_address,
                'estimated_delivery': '24-48 ore'
            },
            'message': 'Comandă plasată cu succes!'
        }), 201
        
    except Exception as e:
        import traceback
        logging.error(f"Error creating order: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'ORDER_ERROR',
                'message': 'Eroare la plasarea comenzii. Încercați din nou.',
                'debug': str(e) if current_app.config.get('DEBUG') else None
            }
        }), 500


# Legacy order creation endpoint (kept for backward compatibility)
# Order creation JSON schema for legacy direct order creation
@orders_bp.route('/status', methods=['GET'])
def get_order_status():
    """
    Get order status by phone number and order number.
    
    No authentication required - customers can check their order status
    using just their phone number and order number.
    
    Query Parameters:
    - phone: Customer phone number
    - order_number: Order number (e.g., PFL-20250622-XXXXXXXX)
    
    Returns order details with current status and delivery timeline.
    """
    try:
        # Get query parameters
        phone = request.args.get('phone')
        order_number = request.args.get('order_number')
        
        if not phone:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PHONE_REQUIRED',
                    'message': 'Numărul de telefon este obligatoriu'
                }
            }), 400
        
        if not order_number:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ORDER_NUMBER_REQUIRED',
                    'message': 'Numărul comenzii este obligatoriu'
                }
            }), 400
        
        # Normalize phone number
        temp_customer = CustomerPhone()
        try:
            normalized_phone = temp_customer.normalize_phone(phone)
        except Exception:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PHONE',
                    'message': 'Format telefon invalid'
                }
            }), 400
        
        # Find order
        from app.database import get_database
        db = get_database()
        order = db.orders.find_one({
            'customer_phone': normalized_phone,
            'order_number': order_number
        })
        
        if not order:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ORDER_NOT_FOUND',
                    'message': 'Comanda nu a fost găsită. Verificați numărul comenzii și telefonul.'
                }
            }), 404
        
        # Calculate status timeline
        created_at = order['created_at']
        now = datetime.utcnow()
        hours_since_order = (now - created_at).total_seconds() / 3600
        
        # Status progression timeline
        status_timeline = {
            'pending': {
                'label': 'În așteptare',
                'description': 'Comanda a fost primită',
                'completed': True,
                'timestamp': created_at.isoformat()
            },
            'confirmed': {
                'label': 'Confirmată',
                'description': 'Comanda a fost confirmată telefonic',
                'completed': order['status'] in ['confirmed', 'preparing', 'ready', 'delivering', 'delivered'],
                'timestamp': order.get('confirmed_at', '').isoformat() if order.get('confirmed_at') else None
            },
            'preparing': {
                'label': 'În preparare',
                'description': 'Comanda se pregătește',
                'completed': order['status'] in ['preparing', 'ready', 'delivering', 'delivered'],
                'timestamp': order.get('preparing_at', '').isoformat() if order.get('preparing_at') else None
            },
            'ready': {
                'label': 'Pregătită',
                'description': 'Comanda este gata pentru livrare',
                'completed': order['status'] in ['ready', 'delivering', 'delivered'],
                'timestamp': order.get('ready_at', '').isoformat() if order.get('ready_at') else None
            },
            'delivering': {
                'label': 'În livrare',
                'description': 'Comanda este pe drum',
                'completed': order['status'] in ['delivering', 'delivered'],
                'timestamp': order.get('delivering_at', '').isoformat() if order.get('delivering_at') else None
            },
            'delivered': {
                'label': 'Livrată',
                'description': 'Comanda a fost livrată',
                'completed': order['status'] == 'delivered',
                'timestamp': order.get('delivered_at', '').isoformat() if order.get('delivered_at') else None
            }
        }
        
        # Estimate delivery time
        if order['status'] == 'delivered':
            estimated_delivery = None
            delivery_message = 'Comanda a fost livrată'
        elif order['status'] == 'cancelled':
            estimated_delivery = None
            delivery_message = 'Comanda a fost anulată'
        elif hours_since_order < 24:
            estimated_delivery = '24-48 ore'
            delivery_message = 'Livrare estimată în 24-48 ore'
        else:
            estimated_delivery = 'În curând'
            delivery_message = 'Vă vom contacta pentru confirmare'
        
        # Prepare response
        response_data = {
            'success': True,
            'order': {
                'order_number': order['order_number'],
                'status': order['status'],
                'status_label': status_timeline.get(order['status'], {}).get('label', order['status']),
                'created_at': order['created_at'].isoformat(),
                'customer_name': order['customer_name'],
                'phone_masked': f"****{normalized_phone[-4:]}",
                'total_amount': order.get('total_amount', 0),
                'items_count': len(order.get('items', [])),
                'delivery_address': {
                    'city': order['delivery_address']['city'],
                    'county': order['delivery_address']['county']
                    # Don't include full address for privacy
                },
                'estimated_delivery': estimated_delivery,
                'delivery_message': delivery_message,
                'timeline': status_timeline,
                'special_instructions': order.get('special_instructions', '')
            }
        }
        
        # Add cancellation reason if cancelled
        if order['status'] == 'cancelled':
            response_data['order']['cancellation_reason'] = order.get('cancellation_reason', 'Anulată la cerere')
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare la verificarea comenzii. Încercați din nou.'
            }
        }), 500


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