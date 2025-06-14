"""
Product Data Model for Local Producer Web Application

This module provides the Product model class with MongoDB operations,
inventory management, and catalog functionality.
"""

import re
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.utils.error_handlers import DatabaseError, ValidationError
from app.utils.validators import sanitize_string


class Product:
    """
    Product model for managing product catalog, inventory, and pricing.
    
    This class handles product CRUD operations with MongoDB, inventory tracking,
    category relationships, and SEO-friendly URL generation.
    """
    
    # Collection name in MongoDB
    COLLECTION_NAME = 'products'
    
    # Price validation constants
    MIN_PRICE = Decimal('0.01')
    MAX_PRICE = Decimal('9999.99')
    PRICE_DECIMAL_PLACES = 2
    
    # Stock validation constants
    MIN_STOCK = 0
    MAX_STOCK = 10000
    
    # Name and description validation
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 1000
    
    # Weight validation (grams)
    MIN_WEIGHT = 1
    MAX_WEIGHT = 50000  # 50kg max
    
    # Preparation time validation (hours)
    MIN_PREP_TIME = 1
    MAX_PREP_TIME = 168  # 1 week max
    DEFAULT_PREP_TIME = 24
    
    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize Product object from dictionary data.
        
        Args:
            data (dict): Product data dictionary from MongoDB or form input
        """
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.name = data.get('name')
        self.slug = data.get('slug')
        self.description = data.get('description')
        self.price = self._convert_to_decimal(data.get('price'))
        self.category_id = data.get('category_id')
        self.images = data.get('images', [])
        self.stock_quantity = data.get('stock_quantity', 0)
        self.is_available = data.get('is_available', True)
        self.weight_grams = data.get('weight_grams')
        self.preparation_time_hours = data.get('preparation_time_hours', self.DEFAULT_PREP_TIME)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.created_by = data.get('created_by')
    
    @classmethod
    def create(cls, name: str, description: str, price: Union[str, float, Decimal], 
               category_id: Union[str, ObjectId], created_by: Union[str, ObjectId],
               images: List[str] = None, stock_quantity: int = 0, 
               weight_grams: int = None, preparation_time_hours: int = None) -> 'Product':
        """
        Create a new product in the database.
        
        Args:
            name (str): Product name
            description (str): Product description
            price (str|float|Decimal): Product price
            category_id (str|ObjectId): Category reference
            created_by (str|ObjectId): User who created the product
            images (list): List of image URLs
            stock_quantity (int): Initial stock quantity
            weight_grams (int): Product weight in grams
            preparation_time_hours (int): Preparation time in hours
            
        Returns:
            Product: Created product instance
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If product creation fails
        """
        try:
            # Validate inputs
            cls._validate_name(name)
            cls._validate_description(description)
            validated_price = cls._validate_price(price)
            validated_category_id = cls._validate_object_id(category_id, "category_id")
            validated_created_by = cls._validate_object_id(created_by, "created_by")
            validated_stock = cls._validate_stock(stock_quantity)
            validated_images = cls._validate_images(images or [])
            
            # Validate optional fields
            validated_weight = None
            if weight_grams is not None:
                validated_weight = cls._validate_weight(weight_grams)
            
            validated_prep_time = cls._validate_preparation_time(
                preparation_time_hours or cls.DEFAULT_PREP_TIME
            )
            
            # Generate unique slug
            slug = cls._generate_unique_slug(name)
            
            # Prepare product document
            now = datetime.utcnow()
            product_doc = {
                'name': sanitize_string(name.strip()),
                'slug': slug,
                'description': sanitize_string(description.strip()),
                'price': validated_price,
                'category_id': validated_category_id,
                'images': validated_images,
                'stock_quantity': validated_stock,
                'is_available': validated_stock > 0,  # Auto-set based on stock
                'preparation_time_hours': validated_prep_time,
                'created_at': now,
                'updated_at': now,
                'created_by': validated_created_by
            }
            
            # Add optional weight
            if validated_weight is not None:
                product_doc['weight_grams'] = validated_weight
            
            # Insert into database
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            result = collection.insert_one(product_doc)
            product_doc['_id'] = result.inserted_id
            
            # Create and return Product instance
            product = cls(product_doc)
            
            logging.info(f"Product created successfully: {name} (slug: {slug})")
            return product
            
        except DuplicateKeyError as e:
            if 'slug' in str(e):
                raise DatabaseError(
                    "Product with similar name already exists",
                    "DB_001",
                    409,
                    {"field": "slug", "value": slug}
                )
            raise DatabaseError("Product creation failed due to duplicate data", "DB_001")
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error creating product: {str(e)}")
            raise DatabaseError("Failed to create product", "DB_001")
    
    @classmethod
    def find_by_id(cls, product_id: Union[str, ObjectId]) -> Optional['Product']:
        """
        Find product by ObjectId.
        
        Args:
            product_id (str|ObjectId): Product's MongoDB ObjectId
            
        Returns:
            Product: Product instance if found, None otherwise
        """
        try:
            if isinstance(product_id, str):
                product_id = ObjectId(product_id)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            product_doc = collection.find_one({'_id': product_id})
            
            if product_doc:
                return cls(product_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding product by ID: {str(e)}")
            raise DatabaseError("Failed to find product", "DB_001")
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['Product']:
        """
        Find product by URL slug.
        
        Args:
            slug (str): Product URL slug
            
        Returns:
            Product: Product instance if found, None otherwise
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            product_doc = collection.find_one({'slug': slug})
            
            if product_doc:
                return cls(product_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding product by slug: {str(e)}")
            raise DatabaseError("Failed to find product", "DB_001")
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Product']:
        """
        Find product by exact name (case-insensitive).
        
        Args:
            name (str): Product name to search for
            
        Returns:
            Product: Product instance if found, None otherwise
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Case-insensitive exact name match
            product_doc = collection.find_one({
                'name': {'$regex': f'^{re.escape(name)}$', '$options': 'i'}
            })
            
            if product_doc:
                return cls(product_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding product by name: {str(e)}")
            raise DatabaseError("Failed to find product", "DB_001")
    
    @classmethod
    def find_by_category(cls, category_id: Union[str, ObjectId], 
                        available_only: bool = True) -> List['Product']:
        """
        Find products by category.
        
        Args:
            category_id (str|ObjectId): Category ID to filter by
            available_only (bool): Only return available products
            
        Returns:
            List[Product]: List of products in category
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Build query
            query = {'category_id': category_id}
            if available_only:
                query['is_available'] = True
                query['stock_quantity'] = {'$gt': 0}
            
            # Find products sorted by name
            cursor = collection.find(query).sort('name', 1)
            
            products = []
            for product_doc in cursor:
                products.append(cls(product_doc))
            
            return products
            
        except Exception as e:
            logging.error(f"Error finding products by category: {str(e)}")
            raise DatabaseError("Failed to find products", "DB_001")
    
    @classmethod
    def find_available(cls, limit: int = None) -> List['Product']:
        """
        Find available products with stock.
        
        Args:
            limit (int): Maximum number of products to return
            
        Returns:
            List[Product]: List of available products
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Query for available products with stock
            query = {
                'is_available': True,
                'stock_quantity': {'$gt': 0}
            }
            
            # Build cursor with sorting
            cursor = collection.find(query).sort('name', 1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            products = []
            for product_doc in cursor:
                products.append(cls(product_doc))
            
            return products
            
        except Exception as e:
            logging.error(f"Error finding available products: {str(e)}")
            raise DatabaseError("Failed to find products", "DB_001")
    
    def update(self, data: Dict[str, Any]) -> bool:
        """
        Update product data in database.
        
        Args:
            data (dict): Dictionary of fields to update
            
        Returns:
            bool: True if update successful
            
        Raises:
            DatabaseError: If update fails
        """
        try:
            if not self._id:
                raise DatabaseError("Cannot update product without ID")
            
            update_data = {}
            
            # Handle specific field updates with validation
            if 'name' in data:
                self._validate_name(data['name'])
                update_data['name'] = sanitize_string(data['name'].strip())
                self.name = update_data['name']
                
                # Regenerate slug if name changed
                update_data['slug'] = self._generate_unique_slug(data['name'], exclude_id=self._id)
                self.slug = update_data['slug']
            
            if 'description' in data:
                self._validate_description(data['description'])
                update_data['description'] = sanitize_string(data['description'].strip())
                self.description = update_data['description']
            
            if 'price' in data:
                validated_price = self._validate_price(data['price'])
                update_data['price'] = validated_price
                self.price = validated_price
            
            if 'stock_quantity' in data:
                validated_stock = self._validate_stock(data['stock_quantity'])
                update_data['stock_quantity'] = validated_stock
                update_data['is_available'] = validated_stock > 0
                self.stock_quantity = validated_stock
                self.is_available = update_data['is_available']
            
            if 'images' in data:
                validated_images = self._validate_images(data['images'])
                update_data['images'] = validated_images
                self.images = validated_images
            
            if 'weight_grams' in data and data['weight_grams'] is not None:
                validated_weight = self._validate_weight(data['weight_grams'])
                update_data['weight_grams'] = validated_weight
                self.weight_grams = validated_weight
            
            if 'preparation_time_hours' in data:
                validated_prep_time = self._validate_preparation_time(data['preparation_time_hours'])
                update_data['preparation_time_hours'] = validated_prep_time
                self.preparation_time_hours = validated_prep_time
            
            if 'is_available' in data:
                update_data['is_available'] = bool(data['is_available'])
                self.is_available = update_data['is_available']
            
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
                logging.info(f"Product updated successfully: {self.name}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error updating product: {str(e)}")
            raise DatabaseError("Failed to update product", "DB_001")
    
    def update_stock(self, quantity_change: int, operation: str = 'set') -> bool:
        """
        Update product stock quantity.
        
        Args:
            quantity_change (int): Quantity to add/subtract or new quantity
            operation (str): 'add', 'subtract', or 'set'
            
        Returns:
            bool: True if stock updated successfully
        """
        try:
            if operation == 'set':
                new_stock = quantity_change
            elif operation == 'add':
                new_stock = self.stock_quantity + quantity_change
            elif operation == 'subtract':
                new_stock = self.stock_quantity - quantity_change
            else:
                raise ValidationError("Operation must be 'set', 'add', or 'subtract'")
            
            # Validate new stock level
            validated_stock = self._validate_stock(new_stock)
            
            # Update stock and availability
            update_data = {
                'stock_quantity': validated_stock,
                'is_available': validated_stock > 0,
                'updated_at': datetime.utcnow()
            }
            
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            result = collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                self.stock_quantity = validated_stock
                self.is_available = validated_stock > 0
                self.updated_at = update_data['updated_at']
                
                logging.info(f"Stock updated for product {self.name}: {self.stock_quantity}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logging.error(f"Error updating stock: {str(e)}")
            raise DatabaseError("Failed to update stock", "DB_001")
    
    def delete(self) -> bool:
        """
        Soft delete product by marking as unavailable.
        
        Returns:
            bool: True if deletion successful
        """
        try:
            return self.update({
                'is_available': False,
                'stock_quantity': 0
            })
            
        except Exception as e:
            logging.error(f"Error deleting product: {str(e)}")
            raise DatabaseError("Failed to delete product", "DB_001")
    
    def to_dict(self, include_internal: bool = False) -> Dict[str, Any]:
        """
        Convert product to dictionary representation.
        
        Args:
            include_internal (bool): Include internal fields like created_by
            
        Returns:
            dict: Product data dictionary
        """
        data = {
            'id': str(self._id) if self._id else None,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'images': self.images,
            'stock_quantity': self.stock_quantity,
            'is_available': self.is_available,
            'preparation_time_hours': self.preparation_time_hours,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
        
        # Add category_id if present
        if self.category_id:
            data['category_id'] = str(self.category_id)
        
        # Add weight if present
        if self.weight_grams is not None:
            data['weight_grams'] = self.weight_grams
        
        # Add internal fields if requested
        if include_internal and self.created_by:
            data['created_by'] = str(self.created_by)
        
        return data
    
    @classmethod
    def _generate_unique_slug(cls, name: str, exclude_id: ObjectId = None) -> str:
        """
        Generate unique URL slug from product name.
        
        Args:
            name (str): Product name
            exclude_id (ObjectId): ID to exclude from uniqueness check
            
        Returns:
            str: Unique URL slug
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        base_slug = re.sub(r'[^\w\s-]', '', name.lower())
        base_slug = re.sub(r'[\s_-]+', '-', base_slug).strip('-')
        
        # Ensure slug is not empty
        if not base_slug:
            base_slug = 'product'
        
        # Check for uniqueness
        db = get_database()
        collection = db[cls.COLLECTION_NAME]
        
        slug = base_slug
        counter = 1
        
        while True:
            # Build query to check uniqueness
            query = {'slug': slug}
            if exclude_id:
                query['_id'] = {'$ne': exclude_id}
            
            if not collection.find_one(query):
                break
            
            # Try with counter suffix
            slug = f"{base_slug}-{counter}"
            counter += 1
            
            # Prevent infinite loops
            if counter > 1000:
                slug = f"{base_slug}-{ObjectId()}"
                break
        
        return slug
    
    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate product name."""
        if not name or not name.strip():
            raise ValidationError("Product name is required")
        
        name = name.strip()
        if len(name) < Product.MIN_NAME_LENGTH:
            raise ValidationError(f"Product name must be at least {Product.MIN_NAME_LENGTH} characters")
        
        if len(name) > Product.MAX_NAME_LENGTH:
            raise ValidationError(f"Product name must not exceed {Product.MAX_NAME_LENGTH} characters")
    
    @staticmethod
    def _validate_description(description: str) -> None:
        """Validate product description."""
        if not description or not description.strip():
            raise ValidationError("Product description is required")
        
        description = description.strip()
        if len(description) < Product.MIN_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description must be at least {Product.MIN_DESCRIPTION_LENGTH} characters")
        
        if len(description) > Product.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description must not exceed {Product.MAX_DESCRIPTION_LENGTH} characters")
    
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
            
            if price < Product.MIN_PRICE:
                raise ValidationError(f"Price must be at least ${Product.MIN_PRICE}")
            
            if price > Product.MAX_PRICE:
                raise ValidationError(f"Price must not exceed ${Product.MAX_PRICE}")
            
            return price
            
        except (ValueError, TypeError):
            raise ValidationError("Invalid price format")
    
    @staticmethod
    def _validate_stock(stock: int) -> int:
        """Validate stock quantity."""
        try:
            stock = int(stock)
            
            if stock < Product.MIN_STOCK:
                raise ValidationError(f"Stock quantity cannot be negative")
            
            if stock > Product.MAX_STOCK:
                raise ValidationError(f"Stock quantity cannot exceed {Product.MAX_STOCK}")
            
            return stock
            
        except (ValueError, TypeError):
            raise ValidationError("Stock quantity must be an integer")
    
    @staticmethod
    def _validate_weight(weight: int) -> int:
        """Validate product weight in grams."""
        try:
            weight = int(weight)
            
            if weight < Product.MIN_WEIGHT:
                raise ValidationError(f"Weight must be at least {Product.MIN_WEIGHT} grams")
            
            if weight > Product.MAX_WEIGHT:
                raise ValidationError(f"Weight cannot exceed {Product.MAX_WEIGHT} grams")
            
            return weight
            
        except (ValueError, TypeError):
            raise ValidationError("Weight must be an integer")
    
    @staticmethod
    def _validate_preparation_time(prep_time: int) -> int:
        """Validate preparation time in hours."""
        try:
            prep_time = int(prep_time)
            
            if prep_time < Product.MIN_PREP_TIME:
                raise ValidationError(f"Preparation time must be at least {Product.MIN_PREP_TIME} hour")
            
            if prep_time > Product.MAX_PREP_TIME:
                raise ValidationError(f"Preparation time cannot exceed {Product.MAX_PREP_TIME} hours")
            
            return prep_time
            
        except (ValueError, TypeError):
            raise ValidationError("Preparation time must be an integer")
    
    @staticmethod
    def _validate_images(images: List[str]) -> List[str]:
        """Validate image URLs."""
        if not isinstance(images, list):
            raise ValidationError("Images must be a list")
        
        validated_images = []
        url_pattern = re.compile(
            r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        )
        
        for image_url in images:
            if not isinstance(image_url, str):
                raise ValidationError("Each image URL must be a string")
            
            image_url = image_url.strip()
            if image_url and not url_pattern.match(image_url):
                raise ValidationError(f"Invalid image URL format: {image_url}")
            
            if image_url:  # Only add non-empty URLs
                validated_images.append(image_url)
        
        return validated_images
    
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
        """String representation of Product object."""
        return f"Product(id={self._id}, name={self.name}, price=${self.price}, stock={self.stock_quantity})"