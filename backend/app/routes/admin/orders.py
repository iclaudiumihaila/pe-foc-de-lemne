from flask import request, jsonify
from app.routes.admin import admin_bp
from app.models.order import Order
from app.database import get_database
from app.utils.auth_middleware import require_admin_auth as admin_required
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@admin_bp.route('/orders', methods=['GET'])
@admin_bp.route('/orders/', methods=['GET'])
@admin_required
def get_admin_orders():
    """Get all orders with filters and pagination"""
    try:
        db = get_database()
        # Pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        phone = request.args.get('phone')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if phone:
            query['customer_phone'] = {'$regex': phone, '$options': 'i'}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = datetime.fromisoformat(start_date)
            if end_date:
                date_query['$lte'] = datetime.fromisoformat(end_date)
            query['created_at'] = date_query
        
        # Get total count
        total = db.orders.count_documents(query)
        
        # Get orders
        orders = list(db.orders.find(query).sort('created_at', -1).skip(skip).limit(limit))
        
        # Format response
        formatted_orders = []
        for order in orders:
            # Calculate total
            total_amount = 0
            for item in order.get('items', []):
                total_amount += item.get('price', 0) * item.get('quantity', 0)
            
            # Extract delivery city from customer address
            delivery_city = ''
            customer_address = order.get('customer_address', '')
            if customer_address and isinstance(customer_address, str):
                # Simple extraction - assumes city is after comma
                parts = customer_address.split(',')
                if len(parts) > 1:
                    delivery_city = parts[-1].strip()
            
            formatted_orders.append({
                'id': str(order['_id']),
                'order_number': order.get('order_number', ''),
                'customer_name': order.get('customer_name', ''),
                'customer_phone': order.get('customer_phone', ''),
                'customer_address': order.get('customer_address', ''),
                'status': order.get('status', 'pending'),
                'total': total_amount,
                'items_count': len(order.get('items', [])),
                'payment_method': order.get('payment_method', 'cash'),
                'delivery_method': order.get('delivery_method', 'pickup'),
                'delivery_city': delivery_city,
                'created_at': order.get('created_at', datetime.utcnow()).isoformat()
            })
        
        return jsonify({
            'orders': formatted_orders,
            'total': total,
            'page': page,
            'total_pages': (total + limit - 1) // limit
        })
        
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

@admin_bp.route('/orders/<order_id>', methods=['GET'])
@admin_required
def get_admin_order(order_id):
    """Get full order details"""
    try:
        db = get_database()
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get product details for items
        product_ids = [item.get('product_id') for item in order.get('items', []) if item.get('product_id')]
        products = {str(p['_id']): p for p in db.products.find({'_id': {'$in': [ObjectId(pid) for pid in product_ids]}})}
        
        # Format items with product details
        formatted_items = []
        total_amount = 0
        for item in order.get('items', []):
            product = products.get(str(item.get('product_id', '')), {})
            item_total = item.get('price', 0) * item.get('quantity', 0)
            total_amount += item_total
            
            formatted_items.append({
                'product_id': str(item.get('product_id', '')),
                'product_name': product.get('name', item.get('product_name', '')),
                'price': item.get('price', 0),
                'quantity': item.get('quantity', 0),
                'total': item_total
            })
        
        # Extract delivery address details
        delivery_address_str = ''
        delivery_city = ''
        delivery_county = ''
        delivery_zip = ''
        
        # Check if we have delivery_address as an object
        delivery_address_obj = order.get('delivery_address', {})
        if isinstance(delivery_address_obj, dict):
            # Extract from object format
            delivery_address_str = delivery_address_obj.get('street', '')
            delivery_city = delivery_address_obj.get('city', '')
            delivery_county = delivery_address_obj.get('county', '')
            delivery_zip = delivery_address_obj.get('postal_code', '')
        else:
            # Fallback to customer_address if delivery_address is not an object
            customer_address = order.get('customer_address', '')
            if customer_address and isinstance(customer_address, str):
                delivery_address_str = customer_address
                # Simple extraction - assumes format like "Street, City, County ZIP"
                parts = [p.strip() for p in customer_address.split(',')]
                if len(parts) >= 2:
                    delivery_city = parts[1]
                if len(parts) >= 3:
                    # Try to extract county and zip from last part
                    last_part = parts[2]
                    zip_parts = last_part.split()
                    if zip_parts:
                        # Last element might be zip code
                        if zip_parts[-1].isdigit() and len(zip_parts) > 1:
                            delivery_zip = zip_parts[-1]
                            delivery_county = ' '.join(zip_parts[:-1])
                        else:
                            delivery_county = last_part
        
        # Calculate shipping cost (could be based on delivery method)
        shipping_cost = 20 if order.get('delivery_method') == 'delivery' else 0
        
        # Calculate subtotal (total without shipping)
        subtotal = total_amount
        total_with_shipping = subtotal + shipping_cost
        
        return jsonify({
            'id': str(order['_id']),
            'order_number': order.get('order_number', ''),
            'customer_name': order.get('customer_name', ''),
            'customer_phone': order.get('customer_phone', ''),
            'customer_email': order.get('customer_email', ''),
            'delivery_address': delivery_address_str,  # Changed from customer_address
            'delivery_city': delivery_city,  # Added
            'delivery_county': delivery_county,  # Added
            'delivery_zip': delivery_zip,  # Added
            'status': order.get('status', 'pending'),
            'items': formatted_items,
            'subtotal': subtotal,  # Added
            'shipping_cost': shipping_cost,  # Added
            'total': total_with_shipping,  # Changed from total_amount
            'payment_method': order.get('payment_method', 'cash'),
            'payment_status': 'paid' if order.get('status') == 'delivered' else 'pending',  # Added
            'delivery_method': order.get('delivery_method', 'pickup'),
            'delivery_notes': delivery_address_obj.get('notes', '') if isinstance(delivery_address_obj, dict) else order.get('notes', ''),  # Changed from notes
            'status_history': order.get('status_history', []),  # Added
            'created_at': order.get('created_at', datetime.utcnow()).isoformat(),
            'updated_at': order.get('updated_at', datetime.utcnow()).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching order: {str(e)}")
        return jsonify({'error': 'Failed to fetch order'}), 500

@admin_bp.route('/orders/<order_id>/status', methods=['PUT'])
@admin_required
def update_admin_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'processing', 'ready', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Update order
        db = get_database()
        result = db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': new_status,
                    'updatedAt': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Order not found'}), 404
        
        # Log status change
        logger.info(f"Order {order_id} status updated to {new_status}")
        
        return jsonify({
            'message': 'Order status updated successfully',
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        return jsonify({'error': 'Failed to update order status'}), 500