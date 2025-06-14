"""
Cart Model for Local Producer Web Application

This module implements a session-based shopping cart model for managing
cart items and quantities without requiring user authentication.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from bson import ObjectId
from app.database import get_database
from app.models.product import Product


class CartItem:
    """Represents an item in the shopping cart."""
    
    def __init__(self, product_id: str, quantity: int, price: float, product_name: str = None):
        self.product_id = str(product_id)
        self.quantity = int(quantity)
        self.price = float(price)
        self.product_name = product_name or ""
        self.subtotal = self.quantity * self.price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cart item to dictionary format."""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.subtotal
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartItem':
        """Create cart item from dictionary data."""
        return cls(
            product_id=data['product_id'],
            quantity=data['quantity'],
            price=data['price'],
            product_name=data.get('product_name', '')
        )


class Cart:
    """Session-based shopping cart model."""
    
    COLLECTION_NAME = 'cart_sessions'
    MAX_ITEMS_PER_CART = 50
    MAX_QUANTITY_PER_ITEM = 100
    SESSION_EXPIRY_HOURS = 24
    
    def __init__(self, session_data: Dict[str, Any] = None):
        """Initialize cart from session data or create new cart."""
        if session_data:
            self._id = session_data.get('_id')
            self.session_id = session_data.get('session_id')
            self.items = [CartItem.from_dict(item) for item in session_data.get('items', [])]
            self.created_at = session_data.get('created_at', datetime.utcnow())
            self.updated_at = session_data.get('updated_at', datetime.utcnow())
            self.expires_at = session_data.get('expires_at', self._calculate_expiry())
        else:
            self._id = None
            self.session_id = str(ObjectId())
            self.items = []
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            self.expires_at = self._calculate_expiry()
    
    def _calculate_expiry(self) -> datetime:
        """Calculate cart expiry time."""
        return datetime.utcnow() + timedelta(hours=self.SESSION_EXPIRY_HOURS)
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self) -> float:
        """Get total cart amount."""
        return sum(item.subtotal for item in self.items)
    
    def add_item(self, product_id: str, quantity: int) -> bool:
        """
        Add item to cart or update quantity if item already exists.
        
        Args:
            product_id: Product ObjectId string
            quantity: Quantity to add
            
        Returns:
            bool: True if item was added successfully
            
        Raises:
            ValueError: If validation fails
        """
        # Validate quantity
        if quantity <= 0 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Quantity must be between 1 and {self.MAX_QUANTITY_PER_ITEM}")
        
        # Get product information
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_available or product.stock_quantity <= 0:
            raise ValueError("Product is not available")
        
        # Find existing item in cart
        existing_item = None
        for item in self.items:
            if item.product_id == str(product_id):
                existing_item = item
                break
        
        if existing_item:
            # Update existing item quantity
            new_quantity = existing_item.quantity + quantity
            
            # Check stock availability
            if new_quantity > product.stock_quantity:
                raise ValueError(f"Insufficient stock. Available: {product.stock_quantity}")
            
            if new_quantity > self.MAX_QUANTITY_PER_ITEM:
                raise ValueError(f"Maximum quantity per item is {self.MAX_QUANTITY_PER_ITEM}")
            
            existing_item.quantity = new_quantity
            existing_item.subtotal = existing_item.quantity * existing_item.price
        else:
            # Add new item to cart
            if len(self.items) >= self.MAX_ITEMS_PER_CART:
                raise ValueError(f"Maximum {self.MAX_ITEMS_PER_CART} different items allowed in cart")
            
            # Check stock availability
            if quantity > product.stock_quantity:
                raise ValueError(f"Insufficient stock. Available: {product.stock_quantity}")
            
            new_item = CartItem(
                product_id=str(product_id),
                quantity=quantity,
                price=product.price,
                product_name=product.name
            )
            self.items.append(new_item)
        
        self.updated_at = datetime.utcnow()
        return True
    
    def remove_item(self, product_id: str) -> bool:
        """
        Remove item from cart completely.
        
        Args:
            product_id: Product ObjectId string
            
        Returns:
            bool: True if item was removed
        """
        for i, item in enumerate(self.items):
            if item.product_id == str(product_id):
                del self.items[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def update_item_quantity(self, product_id: str, quantity: int) -> bool:
        """
        Update item quantity in cart.
        
        Args:
            product_id: Product ObjectId string
            quantity: New quantity (0 to remove item)
            
        Returns:
            bool: True if item was updated
        """
        if quantity == 0:
            return self.remove_item(product_id)
        
        if quantity < 0 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Quantity must be between 0 and {self.MAX_QUANTITY_PER_ITEM}")
        
        # Get product for stock validation
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if quantity > product.stock_quantity:
            raise ValueError(f"Insufficient stock. Available: {product.stock_quantity}")
        
        for item in self.items:
            if item.product_id == str(product_id):
                item.quantity = quantity
                item.subtotal = item.quantity * item.price
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items = []
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if cart session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cart to dictionary format."""
        return {
            'session_id': self.session_id,
            'items': [item.to_dict() for item in self.items],
            'total_items': self.total_items,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'expires_at': self.expires_at.isoformat() + 'Z'
        }
    
    def save(self) -> bool:
        """Save cart to database."""
        try:
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            cart_data = {
                'session_id': self.session_id,
                'items': [item.to_dict() for item in self.items],
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'expires_at': self.expires_at
            }
            
            if self._id:
                # Update existing cart
                result = collection.update_one(
                    {'_id': self._id},
                    {'$set': cart_data}
                )
                return result.modified_count > 0
            else:
                # Insert new cart
                result = collection.insert_one(cart_data)
                self._id = result.inserted_id
                return bool(result.inserted_id)
                
        except Exception as e:
            logging.error(f"Error saving cart: {str(e)}")
            return False
    
    @classmethod
    def find_by_session_id(cls, session_id: str) -> Optional['Cart']:
        """
        Find cart by session ID.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            Cart instance or None if not found
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            cart_data = collection.find_one({
                'session_id': session_id,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if cart_data:
                return cls(cart_data)
            return None
            
        except Exception as e:
            logging.error(f"Error finding cart by session ID: {str(e)}")
            return None
    
    @classmethod
    def cleanup_expired_carts(cls) -> int:
        """
        Remove expired cart sessions from database.
        
        Returns:
            Number of expired carts removed
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            result = collection.delete_many({
                'expires_at': {'$lt': datetime.utcnow()}
            })
            
            logging.info(f"Cleaned up {result.deleted_count} expired cart sessions")
            return result.deleted_count
            
        except Exception as e:
            logging.error(f"Error cleaning up expired carts: {str(e)}")
            return 0