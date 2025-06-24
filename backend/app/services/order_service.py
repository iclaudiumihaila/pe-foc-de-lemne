"""
Order Processing Service for Local Producer Web Application

This module provides comprehensive business logic for order processing
including cart validation, product verification, pricing calculations,
SMS verification integration, and atomic order creation.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Tuple
from bson import ObjectId

from app.database import get_database
from app.models.cart import Cart
from app.models.order import Order
from app.models.product import Product
from app.utils.error_handlers import ValidationError


logger = logging.getLogger(__name__)


class OrderValidationError(Exception):
    """Exception raised for order validation errors."""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class OrderCreationError(Exception):
    """Exception raised for order creation failures."""
    
    def __init__(self, message: str, error_code: str = "ORDER_500", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class OrderService:
    """
    Service for processing orders from cart data with comprehensive validation.
    
    Handles the complete order workflow including cart validation, product 
    verification, SMS verification integration, pricing calculations, and
    atomic order creation with inventory management.
    """
    
    # Tax and delivery configuration
    TAX_RATE = Decimal('0.08')  # 8% tax rate
    FREE_DELIVERY_THRESHOLD = Decimal('50.00')  # Free delivery over $50
    DELIVERY_FEE = Decimal('5.00')  # Standard delivery fee
    
    # Order status constants
    ORDER_STATUS_PENDING = 'pending'
    ORDER_STATUS_CONFIRMED = 'confirmed'
    ORDER_STATUS_CANCELLED = 'cancelled'
    
    def __init__(self):
        """Initialize order service with database connections."""
        self.db = get_database()
        self.orders_collection = self.db.orders
        self.products_collection = self.db.products
        self.verification_sessions_collection = self.db.verification_sessions
        self.order_sequences_collection = self.db.order_sequences
        self.cart_sessions_collection = self.db.cart_sessions
    
    def create_order(self, cart_session_id: str, customer_info: Dict[str, Any], 
                    phone_verification_session_id: str) -> Dict[str, Any]:
        """
        Create order from cart data with comprehensive validation.
        
        Args:
            cart_session_id: Cart session identifier
            customer_info: Customer information dictionary
            phone_verification_session_id: SMS verification session ID
            
        Returns:
            dict: Created order data with order number and details
            
        Raises:
            OrderValidationError: If validation fails
            OrderCreationError: If order creation fails
        """
        try:
            logger.info(f"Starting order creation for cart session: {cart_session_id}")
            
            # Step 1: Validate SMS verification session
            self._validate_verification_session(
                phone_verification_session_id, 
                customer_info.get('phone_number')
            )
            
            # Step 2: Retrieve and validate cart
            cart = self._validate_cart(cart_session_id)
            
            # Step 3: Validate customer information
            self._validate_customer_info(customer_info)
            
            # Step 4: Validate products and inventory
            validated_items = self._validate_products_and_inventory(cart.items)
            
            # Step 5: Calculate pricing and totals
            order_totals = self._calculate_order_totals(validated_items)
            
            # Step 6: Generate unique order number
            order_number = self._generate_order_number()
            
            # Step 7: Create order atomically
            order_id = self._create_order_atomic(
                cart_session_id=cart_session_id,
                customer_info=customer_info,
                items=validated_items,
                totals=order_totals,
                order_number=order_number,
                verification_session_id=phone_verification_session_id
            )
            
            # Step 8: Retrieve created order for response
            created_order = Order.find_by_id(order_id)
            
            logger.info(f"Order created successfully: {order_number}")
            
            return {
                'success': True,
                'order': created_order.to_dict(),
                'message': f'Order {order_number} created successfully'
            }
            
        except (OrderValidationError, OrderCreationError) as e:
            logger.warning(f"Order creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in order creation: {str(e)}")
            raise OrderCreationError(f"Order creation failed: {str(e)}")
    
    def _validate_verification_session(self, session_id: str, phone_number: str):
        """
        Validate SMS verification session.
        
        Args:
            session_id: Verification session ID
            phone_number: Customer phone number
            
        Raises:
            OrderValidationError: If verification session is invalid
        """
        if not session_id:
            raise OrderValidationError(
                "Phone verification session ID is required",
                "ORDER_001",
                {"field": "phone_verification_session_id"}
            )
        
        if not phone_number:
            raise OrderValidationError(
                "Customer phone number is required",
                "ORDER_002", 
                {"field": "phone_number"}
            )
        
        try:
            # Find verification session
            session = self.verification_sessions_collection.find_one({
                'session_id': session_id,
                'verified': True,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if not session:
                raise OrderValidationError(
                    "Invalid or expired phone verification session",
                    "ORDER_003",
                    {
                        "session_id": session_id,
                        "suggestion": "Please verify your phone number again"
                    }
                )
            
            # Verify phone number matches
            if session.get('phone_number') != phone_number:
                raise OrderValidationError(
                    "Phone verification session does not match customer phone number",
                    "ORDER_004",
                    {"verified_phone": session.get('phone_number')[-4:]}
                )
            
            # Check if session already used
            if session.get('used', False):
                raise OrderValidationError(
                    "Phone verification session has already been used",
                    "ORDER_005",
                    {"suggestion": "Please verify your phone number again"}
                )
                
        except OrderValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating verification session: {str(e)}")
            raise OrderValidationError(
                "Unable to validate phone verification",
                "ORDER_006"
            )
    
    def _validate_cart(self, cart_session_id: str) -> Cart:
        """
        Retrieve and validate cart session.
        
        Args:
            cart_session_id: Cart session identifier
            
        Returns:
            Cart: Validated cart object
            
        Raises:
            OrderValidationError: If cart is invalid
        """
        if not cart_session_id:
            raise OrderValidationError(
                "Cart session ID is required",
                "ORDER_007",
                {"field": "cart_session_id"}
            )
        
        try:
            # Retrieve cart from database
            cart = Cart.find_by_session_id(cart_session_id)
            
            if not cart:
                raise OrderValidationError(
                    "Cart session not found",
                    "ORDER_008",
                    {
                        "cart_session_id": cart_session_id,
                        "suggestion": "Please add items to cart again"
                    }
                )
            
            # Check if cart has expired
            if cart.expires_at < datetime.utcnow():
                raise OrderValidationError(
                    "Cart session has expired",
                    "ORDER_009",
                    {
                        "expired_at": cart.expires_at.isoformat(),
                        "suggestion": "Please add items to cart again"
                    }
                )
            
            # Check if cart has items
            if not cart.items or len(cart.items) == 0:
                raise OrderValidationError(
                    "Cart is empty",
                    "ORDER_010",
                    {"suggestion": "Please add items to cart before ordering"}
                )
            
            logger.info(f"Cart validated: {cart_session_id} with {len(cart.items)} items")
            return cart
            
        except OrderValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating cart: {str(e)}")
            raise OrderValidationError(
                "Unable to validate cart session",
                "ORDER_011"
            )
    
    def _validate_customer_info(self, customer_info: Dict[str, Any]):
        """
        Validate customer information completeness.
        
        Args:
            customer_info: Customer information dictionary
            
        Raises:
            OrderValidationError: If customer info is invalid
        """
        required_fields = {
            'phone_number': 'Phone number is required',
            'customer_name': 'Customer name is required'
        }
        
        for field, error_message in required_fields.items():
            if not customer_info.get(field):
                raise OrderValidationError(
                    error_message,
                    "ORDER_012",
                    {"field": field}
                )
        
        # Validate phone number format (basic E.164 check)
        phone = customer_info['phone_number']
        if not phone.startswith('+') or len(phone) < 10:
            raise OrderValidationError(
                "Invalid phone number format. Use E.164 format (+1234567890)",
                "ORDER_013",
                {"field": "phone_number", "value": phone}
            )
        
        # Validate customer name is not empty
        name = customer_info['customer_name'].strip()
        if len(name) < 2:
            raise OrderValidationError(
                "Customer name must be at least 2 characters",
                "ORDER_014",
                {"field": "customer_name"}
            )
        
        logger.info(f"Customer info validated for phone ending in: {phone[-4:]}")
    
    def _validate_products_and_inventory(self, cart_items: List[Any]) -> List[Dict[str, Any]]:
        """
        Validate products exist, are available, and have sufficient inventory.
        
        Args:
            cart_items: List of cart items to validate
            
        Returns:
            list: Validated items with current product information
            
        Raises:
            OrderValidationError: If products are invalid or unavailable
        """
        validated_items = []
        
        for cart_item in cart_items:
            try:
                # Get current product information
                product = Product.find_by_id(cart_item.product_id)
                
                if not product:
                    raise OrderValidationError(
                        f"Product '{cart_item.product_name}' is no longer available",
                        "ORDER_015",
                        {
                            "product_id": cart_item.product_id,
                            "product_name": cart_item.product_name
                        }
                    )
                
                # Check if product is available
                if not product.is_available:
                    raise OrderValidationError(
                        f"Product '{product.name}' is currently unavailable",
                        "ORDER_016",
                        {"product_name": product.name}
                    )
                
                # Check inventory availability
                if product.stock_quantity < cart_item.quantity:
                    raise OrderValidationError(
                        f"Insufficient inventory for '{product.name}'. Available: {product.stock_quantity}, Requested: {cart_item.quantity}",
                        "ORDER_017",
                        {
                            "product_name": product.name,
                            "available_quantity": product.stock_quantity,
                            "requested_quantity": cart_item.quantity
                        }
                    )
                
                # Verify pricing (security check against price tampering)
                current_price = product.price
                cart_price = Decimal(str(cart_item.price))
                
                if abs(current_price - cart_price) > Decimal('0.01'):  # Allow 1 cent tolerance
                    logger.warning(f"Price mismatch for {product.name}: cart={cart_price}, current={current_price}")
                    # Use current price from database
                
                # Create validated item with current pricing
                validated_item = {
                    'product_id': str(product._id),
                    'product_name': product.name,
                    'quantity': cart_item.quantity,
                    'unit_price': float(current_price),
                    'total_price': float(current_price * cart_item.quantity)
                }
                
                validated_items.append(validated_item)
                
            except OrderValidationError:
                raise
            except Exception as e:
                logger.error(f"Error validating product {cart_item.product_id}: {str(e)}")
                raise OrderValidationError(
                    f"Unable to validate product '{cart_item.product_name}'",
                    "ORDER_018"
                )
        
        logger.info(f"Validated {len(validated_items)} cart items")
        return validated_items
    
    def _calculate_order_totals(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate order totals including subtotal, tax, delivery fee, and total.
        
        Args:
            items: List of validated order items
            
        Returns:
            dict: Order totals breakdown
        """
        # Calculate subtotal
        subtotal = sum(Decimal(str(item['total_price'])) for item in items)
        
        # Calculate tax
        tax = (subtotal * self.TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate delivery fee
        delivery_fee = Decimal('0.00') if subtotal >= self.FREE_DELIVERY_THRESHOLD else self.DELIVERY_FEE
        
        # Calculate total
        total = (subtotal + tax + delivery_fee).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        totals = {
            'subtotal': float(subtotal),
            'tax': float(tax),
            'delivery_fee': float(delivery_fee),
            'total': float(total),
            'tax_rate': float(self.TAX_RATE),
            'free_delivery_threshold': float(self.FREE_DELIVERY_THRESHOLD)
        }
        
        logger.info(f"Order totals calculated: subtotal=${totals['subtotal']}, total=${totals['total']}")
        return totals
    
    def _generate_order_number(self) -> str:
        """
        Generate unique incremental order number starting from 10000.
        
        Returns:
            str: Unique order number (e.g., "10001", "10002", etc.)
        """
        try:
            # Use a global counter that starts at 10000
            result = self.order_sequences_collection.find_one_and_update(
                {'_id': 'global_order_counter'},
                {'$inc': {'sequence': 1}},
                upsert=True,
                return_document=True  # Return the updated document
            )
            
            # If this is the first order, start from 10000
            if 'sequence' not in result or result['sequence'] < 10000:
                result = self.order_sequences_collection.find_one_and_update(
                    {'_id': 'global_order_counter'},
                    {'$set': {'sequence': 10000}},
                    upsert=True,
                    return_document=True
                )
            
            order_number = str(result['sequence'])
            
            logger.info(f"Generated order number: {order_number}")
            return order_number
            
        except Exception as e:
            logger.error(f"Error generating order number: {str(e)}")
            # Fallback to timestamp-based number with high starting value
            timestamp = int(datetime.utcnow().timestamp())
            fallback_number = str(10000 + (timestamp % 90000))
            logger.warning(f"Using fallback order number: {fallback_number}")
            return fallback_number
    
    def _create_order_atomic(self, cart_session_id: str, customer_info: Dict[str, Any],
                           items: List[Dict[str, Any]], totals: Dict[str, Any],
                           order_number: str, verification_session_id: str) -> ObjectId:
        """
        Create order atomically with inventory updates and cart cleanup.
        
        Args:
            cart_session_id: Cart session ID to clear
            customer_info: Customer information
            items: Validated order items
            totals: Order totals
            order_number: Generated order number
            verification_session_id: SMS verification session ID
            
        Returns:
            ObjectId: Created order ID
            
        Raises:
            OrderCreationError: If order creation fails
        """
        try:
            # Create order document
            order_data = {
                'order_number': order_number,
                'customer_phone': customer_info['phone_number'],
                'customer_name': customer_info['customer_name'],
                'status': self.ORDER_STATUS_PENDING,
                'items': items,
                'subtotal': totals['subtotal'],
                'total': totals['total'],
                'totals': totals,  # Include detailed totals breakdown
                'delivery_type': 'pickup',  # Default to pickup
                'verification_session_id': verification_session_id,
                'cart_session_id': cart_session_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Add optional customer information
            if customer_info.get('email'):
                order_data['customer_email'] = customer_info['email']
            if customer_info.get('special_instructions'):
                order_data['special_instructions'] = customer_info['special_instructions']
            
            # Start MongoDB transaction for atomic operations
            with self.db.client.start_session() as session:
                with session.start_transaction():
                    try:
                        # 1. Create order
                        order_result = self.orders_collection.insert_one(order_data, session=session)
                        order_id = order_result.inserted_id
                        
                        # 2. Update product inventory
                        for item in items:
                            update_result = self.products_collection.update_one(
                                {'_id': ObjectId(item['product_id'])},
                                {'$inc': {'stock_quantity': -item['quantity']}},
                                session=session
                            )
                            
                            if update_result.matched_count == 0:
                                raise OrderCreationError(
                                    f"Product {item['product_name']} not found during inventory update",
                                    "ORDER_019"
                                )
                        
                        # 3. Mark verification session as used
                        self.verification_sessions_collection.update_one(
                            {'session_id': verification_session_id},
                            {
                                '$set': {
                                    'used': True,
                                    'used_at': datetime.utcnow(),
                                    'order_id': str(order_id)
                                }
                            },
                            session=session
                        )
                        
                        # 4. Clear cart session
                        self.cart_sessions_collection.delete_one(
                            {'session_id': cart_session_id},
                            session=session
                        )
                        
                        # Commit transaction
                        session.commit_transaction()
                        
                        logger.info(f"Order created atomically: {order_number} (ID: {order_id})")
                        return order_id
                        
                    except Exception as e:
                        # Transaction will be automatically aborted
                        logger.error(f"Transaction failed, rolling back: {str(e)}")
                        raise OrderCreationError(
                            f"Failed to create order atomically: {str(e)}",
                            "ORDER_020"
                        )
                        
        except OrderCreationError:
            raise
        except Exception as e:
            logger.error(f"Error in atomic order creation: {str(e)}")
            raise OrderCreationError(
                f"Order creation failed: {str(e)}",
                "ORDER_021"
            )
    
    def get_order_status(self, order_number: str) -> Dict[str, Any]:
        """
        Get order status and details by order number.
        
        Args:
            order_number: Order number to look up
            
        Returns:
            dict: Order status and details
            
        Raises:
            OrderValidationError: If order not found
        """
        try:
            order = Order.find_by_order_number(order_number)
            
            if not order:
                raise OrderValidationError(
                    f"Order {order_number} not found",
                    "ORDER_022",
                    {"order_number": order_number}
                )
            
            return {
                'success': True,
                'order': order.to_dict()
            }
            
        except OrderValidationError:
            raise
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            raise OrderValidationError(
                f"Unable to retrieve order status",
                "ORDER_023"
            )
    
    def cancel_order(self, order_number: str, reason: str = None) -> Dict[str, Any]:
        """
        Cancel an order and restore inventory.
        
        Args:
            order_number: Order number to cancel
            reason: Optional cancellation reason
            
        Returns:
            dict: Cancellation result
            
        Raises:
            OrderValidationError: If order cannot be cancelled
        """
        try:
            order = Order.find_by_order_number(order_number)
            
            if not order:
                raise OrderValidationError(
                    f"Order {order_number} not found",
                    "ORDER_024",
                    {"order_number": order_number}
                )
            
            # Check if order can be cancelled
            if order.status in ['delivered', 'cancelled']:
                raise OrderValidationError(
                    f"Order {order_number} cannot be cancelled (status: {order.status})",
                    "ORDER_025",
                    {"current_status": order.status}
                )
            
            # Start transaction for atomic cancellation
            with self.db.client.start_session() as session:
                with session.start_transaction():
                    try:
                        # 1. Update order status
                        self.orders_collection.update_one(
                            {'order_number': order_number},
                            {
                                '$set': {
                                    'status': self.ORDER_STATUS_CANCELLED,
                                    'cancelled_at': datetime.utcnow(),
                                    'cancellation_reason': reason,
                                    'updated_at': datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        
                        # 2. Restore inventory
                        for item in order.items:
                            self.products_collection.update_one(
                                {'_id': ObjectId(item['product_id'])},
                                {'$inc': {'stock_quantity': item['quantity']}},
                                session=session
                            )
                        
                        session.commit_transaction()
                        
                        logger.info(f"Order cancelled successfully: {order_number}")
                        
                        return {
                            'success': True,
                            'message': f'Order {order_number} cancelled successfully',
                            'order_number': order_number,
                            'cancelled_at': datetime.utcnow().isoformat()
                        }
                        
                    except Exception as e:
                        logger.error(f"Error cancelling order {order_number}: {str(e)}")
                        raise OrderCreationError(
                            f"Failed to cancel order: {str(e)}",
                            "ORDER_026"
                        )
                        
        except (OrderValidationError, OrderCreationError):
            raise
        except Exception as e:
            logger.error(f"Error in order cancellation: {str(e)}")
            raise OrderValidationError(
                f"Unable to cancel order",
                "ORDER_027"
            )


# Global order service instance
_order_service = None


def get_order_service() -> OrderService:
    """Get or create global order service instance."""
    global _order_service
    if _order_service is None:
        _order_service = OrderService()
    return _order_service