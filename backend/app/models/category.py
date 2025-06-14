"""
Category Data Model for Local Producer Web Application

This module provides the Category model class with MongoDB operations,
product organization, and hierarchy management.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.utils.error_handlers import DatabaseError, ValidationError
from app.utils.validators import sanitize_string


class Category:
    """
    Category model for organizing products into hierarchical categories.
    
    This class handles category CRUD operations with MongoDB, product counting,
    display ordering, and SEO-friendly URL generation.
    """
    
    # Collection name in MongoDB
    COLLECTION_NAME = 'categories'
    
    # Name validation constants
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 50
    
    # Description validation constants
    MAX_DESCRIPTION_LENGTH = 500
    
    # Display order constants
    MIN_DISPLAY_ORDER = 0
    MAX_DISPLAY_ORDER = 10000
    DEFAULT_DISPLAY_ORDER = 0
    
    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize Category object from dictionary data.
        
        Args:
            data (dict): Category data dictionary from MongoDB or form input
        """
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.name = data.get('name')
        self.slug = data.get('slug')
        self.description = data.get('description')
        self.display_order = data.get('display_order', self.DEFAULT_DISPLAY_ORDER)
        self.is_active = data.get('is_active', True)
        self.product_count = data.get('product_count', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.created_by = data.get('created_by')
    
    @classmethod
    def create(cls, name: str, created_by: Union[str, ObjectId], 
               description: str = None, display_order: int = None) -> 'Category':
        """
        Create a new category in the database.
        
        Args:
            name (str): Category name
            created_by (str|ObjectId): User who created the category
            description (str): Optional category description
            display_order (int): Optional display order (auto-assigned if None)
            
        Returns:
            Category: Created category instance
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If category creation fails
        """
        try:
            # Validate inputs
            cls._validate_name(name)
            validated_created_by = cls._validate_object_id(created_by, "created_by")
            
            # Validate optional description
            validated_description = None
            if description is not None:
                validated_description = cls._validate_description(description)
            
            # Auto-assign display order if not provided
            if display_order is None:
                display_order = cls._get_next_display_order()
            else:
                display_order = cls._validate_display_order(display_order)
            
            # Generate unique slug
            slug = cls._generate_unique_slug(name)
            
            # Prepare category document
            now = datetime.utcnow()
            category_doc = {
                'name': sanitize_string(name.strip()),
                'slug': slug,
                'display_order': display_order,
                'is_active': True,
                'product_count': 0,
                'created_at': now,
                'updated_at': now,
                'created_by': validated_created_by
            }
            
            # Add optional description
            if validated_description is not None:
                category_doc['description'] = validated_description
            
            # Insert into database
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            result = collection.insert_one(category_doc)
            category_doc['_id'] = result.inserted_id
            
            # Create and return Category instance
            category = cls(category_doc)
            
            logging.info(f"Category created successfully: {name} (slug: {slug})")
            return category
            
        except DuplicateKeyError as e:
            if 'name' in str(e):
                raise DatabaseError(
                    "Category name already exists",
                    "DB_001",
                    409,
                    {"field": "name", "value": name}
                )
            elif 'slug' in str(e):
                raise DatabaseError(
                    "Category with similar name already exists",
                    "DB_001",
                    409,
                    {"field": "slug", "value": slug}
                )
            raise DatabaseError("Category creation failed due to duplicate data", "DB_001")
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error creating category: {str(e)}")
            raise DatabaseError("Failed to create category", "DB_001")
    
    @classmethod
    def find_by_id(cls, category_id: Union[str, ObjectId]) -> Optional['Category']:
        """
        Find category by ObjectId.
        
        Args:
            category_id (str|ObjectId): Category's MongoDB ObjectId
            
        Returns:
            Category: Category instance if found, None otherwise
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            category_doc = collection.find_one({'_id': category_id})
            
            if category_doc:
                return cls(category_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding category by ID: {str(e)}")
            raise DatabaseError("Failed to find category", "DB_001")
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['Category']:
        """
        Find category by URL slug.
        
        Args:
            slug (str): Category URL slug
            
        Returns:
            Category: Category instance if found, None otherwise
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            category_doc = collection.find_one({'slug': slug})
            
            if category_doc:
                return cls(category_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding category by slug: {str(e)}")
            raise DatabaseError("Failed to find category", "DB_001")
    
    @classmethod
    def find_all(cls, active_only: bool = False) -> List['Category']:
        """
        Find all categories with display ordering.
        
        Args:
            active_only (bool): Only return active categories
            
        Returns:
            List[Category]: List of categories ordered by display_order
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Build query
            query = {}
            if active_only:
                query['is_active'] = True
            
            # Find categories sorted by display order, then name
            cursor = collection.find(query).sort([
                ('display_order', 1),
                ('name', 1)
            ])
            
            categories = []
            for category_doc in cursor:
                categories.append(cls(category_doc))
            
            return categories
            
        except Exception as e:
            logging.error(f"Error finding categories: {str(e)}")
            raise DatabaseError("Failed to find categories", "DB_001")
    
    @classmethod
    def find_active(cls) -> List['Category']:
        """
        Find active categories only.
        
        Returns:
            List[Category]: List of active categories ordered by display_order
        """
        return cls.find_all(active_only=True)
    
    def update(self, data: Dict[str, Any]) -> bool:
        """
        Update category data in database.
        
        Args:
            data (dict): Dictionary of fields to update
            
        Returns:
            bool: True if update successful
            
        Raises:
            DatabaseError: If update fails
        """
        try:
            if not self._id:
                raise DatabaseError("Cannot update category without ID")
            
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
                if data['description'] is not None:
                    validated_description = self._validate_description(data['description'])
                    update_data['description'] = validated_description
                    self.description = validated_description
                else:
                    # Allow clearing description
                    update_data['description'] = None
                    self.description = None
            
            if 'display_order' in data:
                validated_order = self._validate_display_order(data['display_order'])
                update_data['display_order'] = validated_order
                self.display_order = validated_order
            
            if 'is_active' in data:
                update_data['is_active'] = bool(data['is_active'])
                self.is_active = update_data['is_active']
            
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
                logging.info(f"Category updated successfully: {self.name}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error updating category: {str(e)}")
            raise DatabaseError("Failed to update category", "DB_001")
    
    def update_product_count(self, count: int = None) -> bool:
        """
        Update cached product count for category.
        
        Args:
            count (int): New product count, or None to recalculate from database
            
        Returns:
            bool: True if count updated successfully
        """
        try:
            if count is None:
                # Recalculate from products collection
                count = self._calculate_product_count()
            
            # Validate count
            if count < 0:
                count = 0
            
            # Update count in database
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            result = collection.update_one(
                {'_id': self._id},
                {
                    '$set': {
                        'product_count': count,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                self.product_count = count
                self.updated_at = datetime.utcnow()
                logging.info(f"Product count updated for category {self.name}: {count}")
                return True
            return False
            
        except Exception as e:
            logging.error(f"Error updating product count: {str(e)}")
            raise DatabaseError("Failed to update product count", "DB_001")
    
    def delete(self) -> bool:
        """
        Soft delete category by marking as inactive.
        
        Returns:
            bool: True if deletion successful
        """
        try:
            return self.update({'is_active': False})
            
        except Exception as e:
            logging.error(f"Error deleting category: {str(e)}")
            raise DatabaseError("Failed to delete category", "DB_001")
    
    def to_dict(self, include_internal: bool = False) -> Dict[str, Any]:
        """
        Convert category to dictionary representation.
        
        Args:
            include_internal (bool): Include internal fields like created_by
            
        Returns:
            dict: Category data dictionary
        """
        data = {
            'id': str(self._id) if self._id else None,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'product_count': self.product_count,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
        
        # Add internal fields if requested
        if include_internal and self.created_by:
            data['created_by'] = str(self.created_by)
        
        return data
    
    def _calculate_product_count(self) -> int:
        """
        Calculate actual product count from products collection.
        
        Returns:
            int: Number of active products in this category
        """
        try:
            db = get_database()
            products_collection = db['products']
            
            # Count active products in this category
            count = products_collection.count_documents({
                'category_id': self._id,
                'is_available': True
            })
            
            return count
            
        except Exception as e:
            logging.error(f"Error calculating product count: {str(e)}")
            return 0
    
    @classmethod
    def _generate_unique_slug(cls, name: str, exclude_id: ObjectId = None) -> str:
        """
        Generate unique URL slug from category name.
        
        Args:
            name (str): Category name
            exclude_id (ObjectId): ID to exclude from uniqueness check
            
        Returns:
            str: Unique URL slug
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        base_slug = re.sub(r'[^\w\s-]', '', name.lower())
        base_slug = re.sub(r'[\s_-]+', '-', base_slug).strip('-')
        
        # Ensure slug is not empty
        if not base_slug:
            base_slug = 'category'
        
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
    
    @classmethod
    def _get_next_display_order(cls) -> int:
        """
        Get the next display order value for a new category.
        
        Returns:
            int: Next display order value
        """
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Find the highest display order
            result = collection.find_one(
                {},
                sort=[('display_order', -1)]
            )
            
            if result and 'display_order' in result:
                return result['display_order'] + 1
            else:
                return cls.DEFAULT_DISPLAY_ORDER
                
        except Exception as e:
            logging.error(f"Error getting next display order: {str(e)}")
            return cls.DEFAULT_DISPLAY_ORDER
    
    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate category name."""
        if not name or not name.strip():
            raise ValidationError("Category name is required")
        
        name = name.strip()
        if len(name) < Category.MIN_NAME_LENGTH:
            raise ValidationError(f"Category name must be at least {Category.MIN_NAME_LENGTH} characters")
        
        if len(name) > Category.MAX_NAME_LENGTH:
            raise ValidationError(f"Category name must not exceed {Category.MAX_NAME_LENGTH} characters")
    
    @staticmethod
    def _validate_description(description: str) -> str:
        """Validate category description."""
        if description is None:
            return None
        
        description = description.strip()
        if len(description) > Category.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description must not exceed {Category.MAX_DESCRIPTION_LENGTH} characters")
        
        return sanitize_string(description) if description else None
    
    @staticmethod
    def _validate_display_order(display_order: int) -> int:
        """Validate display order."""
        try:
            display_order = int(display_order)
            
            if display_order < Category.MIN_DISPLAY_ORDER:
                raise ValidationError(f"Display order cannot be negative")
            
            if display_order > Category.MAX_DISPLAY_ORDER:
                raise ValidationError(f"Display order cannot exceed {Category.MAX_DISPLAY_ORDER}")
            
            return display_order
            
        except (ValueError, TypeError):
            raise ValidationError("Display order must be an integer")
    
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
    
    def __repr__(self) -> str:
        """String representation of Category object."""
        return f"Category(id={self._id}, name={self.name}, order={self.display_order}, products={self.product_count})"