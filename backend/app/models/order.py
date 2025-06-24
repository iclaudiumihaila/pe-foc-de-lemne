"""
Order Data Model for Local Producer Web Application

This module provides the Order model class with MongoDB operations,
order lifecycle management, and item tracking.
"""

import re
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.utils.error_handlers import DatabaseError, ValidationError
from app.utils.validators import sanitize_string, validate_phone_number


class Order:
    """
    Order model for managing customer orders, items, and order lifecycle.
    
    This class handles order CRUD operations with MongoDB, status management,
    item tracking, and total calculations.
    """
    
    # Collection name in MongoDB
    COLLECTION_NAME = 'orders'
    
    # Order status constants
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_READY = 'ready'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    
    VALID_STATUSES = [
        STATUS_PENDING, STATUS_CONFIRMED, STATUS_PREPARING,
        STATUS_READY, STATUS_DELIVERED, STATUS_CANCELLED
    ]
    
    # Delivery type constants
    DELIVERY_PICKUP = 'pickup'
    DELIVERY_DELIVERY = 'delivery'
    VALID_DELIVERY_TYPES = [DELIVERY_PICKUP, DELIVERY_DELIVERY]
    
    # Validation constants
    MIN_CUSTOMER_NAME_LENGTH = 2
    MAX_CUSTOMER_NAME_LENGTH = 50
    MAX_SPECIAL_INSTRUCTIONS_LENGTH = 500
    MIN_QUANTITY = 1
    MAX_QUANTITY = 100
    MIN_PRICE = Decimal('0.01')
    MAX_PRICE = Decimal('9999.99')
    
    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize Order object from dictionary data.
        
        Args:
            data (dict): Order data dictionary from MongoDB or form input
        """
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.order_number = data.get('order_number')
        self.customer_phone = data.get('customer_phone')
        self.customer_name = data.get('customer_name')
        self.status = data.get('status', self.STATUS_PENDING)
        self.items = data.get('items', [])
        self.subtotal = self._convert_to_decimal(data.get('subtotal'))
        self.total = self._convert_to_decimal(data.get('total'))
        self.delivery_type = data.get('delivery_type', self.DELIVERY_PICKUP)
        self.delivery_address = data.get('delivery_address')
        self.delivery_phone = data.get('delivery_phone')
        self.requested_time = data.get('requested_time')
        self.special_instructions = data.get('special_instructions')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.confirmed_at = data.get('confirmed_at')
        self.ready_at = data.get('ready_at')
        self.delivered_at = data.get('delivered_at')
    
    @classmethod
    def create(cls, customer_phone: str, customer_name: str, items: List[Dict[str, Any]],
               delivery_type: str = DELIVERY_PICKUP, delivery_address: Dict[str, Any] = None,
               delivery_phone: str = None, requested_time: datetime = None,
               special_instructions: str = None) -> 'Order':
        """
        Create a new order in the database.
        
        Args:
            customer_phone (str): Customer's phone number in E.164 format
            customer_name (str): Customer's full name
            items (list): List of order items
            delivery_type (str): pickup or delivery
            delivery_address (dict): Delivery address (required for delivery)
            delivery_phone (str): Delivery phone (optional)
            requested_time (datetime): Requested pickup/delivery time
            special_instructions (str): Special instructions
            
        Returns:
            Order: Created order instance
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If order creation fails
        """
        try:
            # Validate inputs
            normalized_phone = cls._validate_and_normalize_phone(customer_phone)
            cls._validate_customer_name(customer_name)
            cls._validate_delivery_type(delivery_type)
            validated_items = cls._validate_and_process_items(items)
            
            # Validate delivery-specific requirements
            if delivery_type == cls.DELIVERY_DELIVERY:
                if not delivery_address:
                    raise ValidationError("Delivery address is required for delivery orders")
                delivery_address = cls._validate_delivery_address(delivery_address)
            
            # Validate optional fields
            validated_delivery_phone = None
            if delivery_phone:
                validated_delivery_phone = cls._validate_and_normalize_phone(delivery_phone)
            
            validated_requested_time = None
            if requested_time:
                validated_requested_time = cls._validate_requested_time(requested_time)
            
            validated_instructions = None
            if special_instructions:
                validated_instructions = cls._validate_special_instructions(special_instructions)
            
            # Calculate totals
            subtotal, total = cls._calculate_order_totals(validated_items)
            
            # Generate unique order number
            order_number = cls._generate_unique_order_number()
            
            # Prepare order document
            now = datetime.utcnow()
            order_doc = {
                'order_number': order_number,
                'customer_phone': normalized_phone,
                'customer_name': sanitize_string(customer_name.strip()),
                'status': cls.STATUS_PENDING,
                'items': validated_items,
                'subtotal': subtotal,
                'total': total,
                'delivery_type': delivery_type,
                'created_at': now,
                'updated_at': now
            }
            
            # Add optional fields
            if delivery_address:
                order_doc['delivery_address'] = delivery_address
            if validated_delivery_phone:
                order_doc['delivery_phone'] = validated_delivery_phone
            if validated_requested_time:
                order_doc['requested_time'] = validated_requested_time
            if validated_instructions:
                order_doc['special_instructions'] = validated_instructions
            
            # Insert into database
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            result = collection.insert_one(order_doc)
            order_doc['_id'] = result.inserted_id
            
            # Create and return Order instance
            order = cls(order_doc)
            
            logging.info(f"Order created successfully: {order_number}")
            return order
            
        except DuplicateKeyError as e:
            if 'order_number' in str(e):
                # Retry with new order number
                return cls.create(customer_phone, customer_name, items, delivery_type,
                                delivery_address, delivery_phone, requested_time, special_instructions)
            raise DatabaseError("Order creation failed due to duplicate data", "DB_001")
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error creating order: {str(e)}")
            raise DatabaseError("Failed to create order", "DB_001")
    
    @classmethod
    def find_by_id(cls, order_id: Union[str, ObjectId]) -> Optional['Order']:
        """
        Find order by ObjectId.
        
        Args:
            order_id (str|ObjectId): Order's MongoDB ObjectId
            
        Returns:
            Order: Order instance if found, None otherwise
        """
        try:
            if isinstance(order_id, str):
                order_id = ObjectId(order_id)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            order_doc = collection.find_one({'_id': order_id})
            
            if order_doc:
                return cls(order_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding order by ID: {str(e)}")
            raise DatabaseError("Failed to find order", "DB_001")
    
    @classmethod
    def find_by_order_number(cls, order_number: str) -> Optional['Order']:
        """
        Find order by order number.
        
        Args:
            order_number (str): Order number
            
        Returns:
            Order: Order instance if found, None otherwise
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            order_doc = collection.find_one({'order_number': order_number})
            
            if order_doc:
                return cls(order_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding order by number: {str(e)}")
            raise DatabaseError("Failed to find order", "DB_001")
    
    @classmethod
    def find_by_customer(cls, customer_phone: str, limit: int = None) -> List['Order']:
        """
        Find orders by customer phone number.
        
        Args:
            customer_phone (str): Customer's phone number
            limit (int): Maximum number of orders to return
            
        Returns:
            List[Order]: List of orders for customer
        """
        try:
            normalized_phone = cls._validate_and_normalize_phone(customer_phone)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Find orders sorted by creation date (newest first)
            cursor = collection.find({'customer_phone': normalized_phone}).sort('created_at', -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            orders = []
            for order_doc in cursor:
                orders.append(cls(order_doc))
            
            return orders
            
        except Exception as e:
            logging.error(f"Error finding orders by customer: {str(e)}")
            raise DatabaseError("Failed to find orders", "DB_001")
    
    @classmethod
    def find_by_customer_phone(cls, customer_phone: str, limit: int = None, status_filter: str = None) -> List['Order']:
        """
        Find orders by customer phone number with optional status filtering.
        
        Args:
            customer_phone (str): Customer's phone number
            limit (int): Maximum number of orders to return
            status_filter (str): Optional status filter
            
        Returns:
            List[Order]: List of orders for customer
        """
        try:
            normalized_phone = cls._validate_and_normalize_phone(customer_phone)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Build query
            query = {'customer_phone': normalized_phone}
            if status_filter:
                if status_filter not in cls.VALID_STATUSES:
                    raise ValidationError(f"Invalid status filter: {status_filter}")
                query['status'] = status_filter
            
            # Find orders sorted by creation date (newest first)
            cursor = collection.find(query).sort('created_at', -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            orders = []
            for order_doc in cursor:
                orders.append(cls(order_doc))
            
            return orders
            
        except Exception as e:
            logging.error(f"Error finding orders by customer phone: {str(e)}")
            raise DatabaseError("Failed to find orders", "DB_001")
    
    @classmethod
    def find_by_status(cls, status: str, limit: int = None) -> List['Order']:
        """
        Find orders by status.
        
        Args:
            status (str): Order status
            limit (int): Maximum number of orders to return
            
        Returns:
            List[Order]: List of orders with specified status
        """
        try:
            if status not in cls.VALID_STATUSES:
                raise ValidationError(f"Invalid status: {status}")
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Find orders sorted by creation date (oldest first for processing)
            cursor = collection.find({'status': status}).sort('created_at', 1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            orders = []
            for order_doc in cursor:
                orders.append(cls(order_doc))
            
            return orders
            
        except Exception as e:
            logging.error(f"Error finding orders by status: {str(e)}")
            raise DatabaseError("Failed to find orders", "DB_001")
    
    def update(self, data: Dict[str, Any]) -> bool:
        """
        Update order data in database.
        
        Args:
            data (dict): Dictionary of fields to update
            
        Returns:
            bool: True if update successful
            
        Raises:
            DatabaseError: If update fails
        """
        try:
            if not self._id:
                raise DatabaseError("Cannot update order without ID")
            
            update_data = {}
            
            # Handle specific field updates with validation
            if 'customer_name' in data:
                self._validate_customer_name(data['customer_name'])
                update_data['customer_name'] = sanitize_string(data['customer_name'].strip())
                self.customer_name = update_data['customer_name']
            
            if 'delivery_type' in data:
                self._validate_delivery_type(data['delivery_type'])
                update_data['delivery_type'] = data['delivery_type']
                self.delivery_type = data['delivery_type']
            
            if 'delivery_address' in data:
                if data['delivery_address']:
                    validated_address = self._validate_delivery_address(data['delivery_address'])
                    update_data['delivery_address'] = validated_address
                    self.delivery_address = validated_address
                else:
                    update_data['delivery_address'] = None
                    self.delivery_address = None
            
            if 'delivery_phone' in data:
                if data['delivery_phone']:
                    validated_phone = self._validate_and_normalize_phone(data['delivery_phone'])
                    update_data['delivery_phone'] = validated_phone
                    self.delivery_phone = validated_phone
                else:
                    update_data['delivery_phone'] = None
                    self.delivery_phone = None
            
            if 'requested_time' in data:
                if data['requested_time']:
                    validated_time = self._validate_requested_time(data['requested_time'])
                    update_data['requested_time'] = validated_time
                    self.requested_time = validated_time
                else:
                    update_data['requested_time'] = None
                    self.requested_time = None
            
            if 'special_instructions' in data:
                if data['special_instructions']:
                    validated_instructions = self._validate_special_instructions(data['special_instructions'])
                    update_data['special_instructions'] = validated_instructions
                    self.special_instructions = validated_instructions
                else:
                    update_data['special_instructions'] = None
                    self.special_instructions = None
            
            if 'items' in data:
                validated_items = self._validate_and_process_items(data['items'])
                subtotal, total = self._calculate_order_totals(validated_items)
                update_data['items'] = validated_items
                update_data['subtotal'] = subtotal
                update_data['total'] = total
                self.items = validated_items
                self.subtotal = subtotal
                self.total = total
            
            # Always update timestamp
            update_data['updated_at'] = datetime.utcnow()
            self.updated_at = update_data['updated_at']
            
            # Perform update
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            result = collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logging.info(f"Order updated successfully: {self.order_number}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error updating order: {str(e)}")
            raise DatabaseError("Failed to update order", "DB_001")
    
    def update_status(self, new_status: str) -> bool:
        """
        Update order status with appropriate timestamp.
        
        Args:
            new_status (str): New order status
            
        Returns:
            bool: True if status updated successfully
        """
        try:
            if new_status not in self.VALID_STATUSES:
                raise ValidationError(f"Invalid status: {new_status}")
            
            # Prepare update data
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }
            
            # Add status-specific timestamps
            now = datetime.utcnow()
            if new_status == self.STATUS_CONFIRMED and not self.confirmed_at:
                update_data['confirmed_at'] = now
                self.confirmed_at = now
            elif new_status == self.STATUS_READY and not self.ready_at:
                update_data['ready_at'] = now
                self.ready_at = now
            elif new_status == self.STATUS_DELIVERED and not self.delivered_at:
                update_data['delivered_at'] = now
                self.delivered_at = now
            
            # Update in database
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            result = collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                self.status = new_status
                self.updated_at = update_data['updated_at']
                logging.info(f"Order status updated: {self.order_number} -> {new_status}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logging.error(f"Error updating order status: {str(e)}")
            raise DatabaseError("Failed to update order status", "DB_001")
    
    def calculate_totals(self) -> tuple[Decimal, Decimal]:
        """
        Calculate order subtotal and total.
        
        Returns:
            tuple: (subtotal, total)
        """
        return self._calculate_order_totals(self.items)
    
    def add_item(self, product_id: Union[str, ObjectId], product_name: str,
                 quantity: int, unit_price: Union[str, float, Decimal]) -> bool:
        """
        Add item to order.
        
        Args:
            product_id (str|ObjectId): Product ID
            product_name (str): Product name
            quantity (int): Item quantity
            unit_price (str|float|Decimal): Unit price
            
        Returns:
            bool: True if item added successfully
        """
        try:
            # Validate item data
            validated_product_id = self._validate_object_id(product_id, "product_id")
            validated_quantity = self._validate_quantity(quantity)
            validated_price = self._validate_price(unit_price)
            total_price = validated_price * validated_quantity
            
            # Create item
            item = {
                'product_id': validated_product_id,
                'product_name': sanitize_string(product_name.strip()),
                'quantity': validated_quantity,
                'unit_price': validated_price,
                'total_price': total_price
            }
            
            # Add to items list
            new_items = self.items.copy()
            new_items.append(item)
            
            # Update order with new items
            return self.update({'items': new_items})
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logging.error(f"Error adding item to order: {str(e)}")
            raise DatabaseError("Failed to add item to order", "DB_001")
    
    def to_dict(self, include_internal: bool = False) -> Dict[str, Any]:
        """
        Convert order to dictionary representation.
        
        Args:
            include_internal (bool): Include internal fields
            
        Returns:
            dict: Order data dictionary
        """
        data = {
            'id': str(self._id) if self._id else None,
            'order_number': self.order_number,
            'customer_phone': self.customer_phone,
            'customer_name': self.customer_name,
            'status': self.status,
            'items': self.items,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'total': float(self.total) if self.total else None,
            'delivery_type': self.delivery_type,
            'delivery_address': self.delivery_address,
            'delivery_phone': self.delivery_phone,
            'requested_time': self.requested_time.isoformat() + 'Z' if self.requested_time else None,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'confirmed_at': self.confirmed_at.isoformat() + 'Z' if self.confirmed_at else None,
            'ready_at': self.ready_at.isoformat() + 'Z' if self.ready_at else None,
            'delivered_at': self.delivered_at.isoformat() + 'Z' if self.delivered_at else None
        }
        
        return data
    
    @classmethod
    def _generate_unique_order_number(cls) -> str:
        """
        Generate unique incremental order number starting from 10000.
        Uses OrderService for consistent numbering across the application.
        
        Returns:
            str: Unique order number (e.g., "10001", "10002", etc.)
        """
        from app.services.order_service import OrderService
        order_service = OrderService()
        return order_service._generate_order_number()
    
    @staticmethod
    def _validate_and_normalize_phone(phone: str) -> str:
        """Validate and normalize phone number."""
        if not validate_phone_number(phone):
            raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            else:
                raise ValidationError("Phone number must include country code or be in E.164 format")
        
        return cleaned
    
    @staticmethod
    def _validate_customer_name(name: str) -> None:
        """Validate customer name."""
        if not name or not name.strip():
            raise ValidationError("Customer name is required")
        
        name = name.strip()
        if len(name) < Order.MIN_CUSTOMER_NAME_LENGTH:
            raise ValidationError(f"Customer name must be at least {Order.MIN_CUSTOMER_NAME_LENGTH} characters")
        
        if len(name) > Order.MAX_CUSTOMER_NAME_LENGTH:
            raise ValidationError(f"Customer name must not exceed {Order.MAX_CUSTOMER_NAME_LENGTH} characters")
    
    @staticmethod
    def _validate_delivery_type(delivery_type: str) -> None:
        """Validate delivery type."""
        if delivery_type not in Order.VALID_DELIVERY_TYPES:
            raise ValidationError(f"Delivery type must be one of: {', '.join(Order.VALID_DELIVERY_TYPES)}")
    
    @staticmethod
    def _validate_delivery_address(address: Dict[str, Any]) -> Dict[str, Any]:
        """Validate delivery address."""
        if not isinstance(address, dict):
            raise ValidationError("Delivery address must be an object")
        
        required_fields = ['street', 'city']
        for field in required_fields:
            if field not in address or not address[field]:
                raise ValidationError(f"Delivery address must include {field}")
        
        # Sanitize address fields
        validated_address = {}
        for key, value in address.items():
            if isinstance(value, str):
                validated_address[key] = sanitize_string(value.strip())
            else:
                validated_address[key] = value
        
        return validated_address
    
    @staticmethod
    def _validate_requested_time(requested_time: datetime) -> datetime:
        """Validate requested pickup/delivery time."""
        if not isinstance(requested_time, datetime):
            raise ValidationError("Requested time must be a datetime")
        
        # Check if time is not in the past (allow 1 hour buffer)
        min_time = datetime.utcnow() + timedelta(hours=1)
        if requested_time < min_time:
            raise ValidationError("Requested time must be at least 1 hour from now")
        
        return requested_time
    
    @staticmethod
    def _validate_special_instructions(instructions: str) -> str:
        """Validate special instructions."""
        instructions = instructions.strip()
        if len(instructions) > Order.MAX_SPECIAL_INSTRUCTIONS_LENGTH:
            raise ValidationError(f"Special instructions must not exceed {Order.MAX_SPECIAL_INSTRUCTIONS_LENGTH} characters")
        
        return sanitize_string(instructions)
    
    @staticmethod
    def _validate_and_process_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and process order items."""
        if not items:
            raise ValidationError("Order must have at least one item")
        
        if not isinstance(items, list):
            raise ValidationError("Items must be a list")
        
        validated_items = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValidationError(f"Item {i+1} must be an object")
            
            # Validate required fields
            required_fields = ['product_id', 'product_name', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item:
                    raise ValidationError(f"Item {i+1} missing required field: {field}")
            
            # Validate and convert item data
            validated_item = {
                'product_id': Order._validate_object_id(item['product_id'], f"item {i+1} product_id"),
                'product_name': sanitize_string(str(item['product_name']).strip()),
                'quantity': Order._validate_quantity(item['quantity']),
                'unit_price': Order._validate_price(item['unit_price'])
            }
            
            # Calculate total price
            validated_item['total_price'] = validated_item['unit_price'] * validated_item['quantity']
            
            validated_items.append(validated_item)
        
        return validated_items
    
    @staticmethod
    def _calculate_order_totals(items: List[Dict[str, Any]]) -> tuple[Decimal, Decimal]:
        """Calculate order subtotal and total."""
        subtotal = Decimal('0.00')
        
        for item in items:
            if 'total_price' in item:
                subtotal += Decimal(str(item['total_price']))
        
        # For now, total equals subtotal (no tax/delivery fees)
        total = subtotal
        
        return subtotal, total
    
    @staticmethod
    def _validate_quantity(quantity: Any) -> int:
        """Validate item quantity."""
        try:
            quantity = int(quantity)
            
            if quantity < Order.MIN_QUANTITY:
                raise ValidationError(f"Quantity must be at least {Order.MIN_QUANTITY}")
            
            if quantity > Order.MAX_QUANTITY:
                raise ValidationError(f"Quantity cannot exceed {Order.MAX_QUANTITY}")
            
            return quantity
            
        except (ValueError, TypeError):
            raise ValidationError("Quantity must be an integer")
    
    @staticmethod
    def _validate_price(price: Union[str, float, Decimal]) -> Decimal:
        """Validate and convert price to Decimal."""
        try:
            if isinstance(price, str):
                price = Decimal(price)
            elif isinstance(price, float):
                price = Decimal(str(price))
            elif not isinstance(price, Decimal):
                raise ValidationError("Price must be a number")
            
            # Round to 2 decimal places
            price = price.quantize(Decimal('0.01'))
            
            if price < Order.MIN_PRICE:
                raise ValidationError(f"Price must be at least ${Order.MIN_PRICE}")
            
            if price > Order.MAX_PRICE:
                raise ValidationError(f"Price must not exceed ${Order.MAX_PRICE}")
            
            return price
            
        except (ValueError, TypeError):
            raise ValidationError("Invalid price format")
    
    @staticmethod
    def _validate_object_id(obj_id: Union[str, ObjectId], field_name: str) -> ObjectId:
        """Validate and convert ObjectId."""
        try:
            if isinstance(obj_id, str):
                return ObjectId(obj_id)
            elif isinstance(obj_id, ObjectId):
                return obj_id
            else:
                raise ValidationError(f"{field_name} must be a valid ObjectId")
        except Exception:
            raise ValidationError(f"Invalid {field_name} format")
    
    @staticmethod
    def _convert_to_decimal(value: Any) -> Optional[Decimal]:
        """Convert value to Decimal, handling None."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                return Decimal(value)
            elif isinstance(value, (int, float)):
                return Decimal(str(value))
            elif isinstance(value, Decimal):
                return value
            else:
                return None
        except:
            return None
    
    def __repr__(self) -> str:
        """String representation of Order object."""
        return f"Order(id={self._id}, number={self.order_number}, status={self.status}, total=${self.total})"