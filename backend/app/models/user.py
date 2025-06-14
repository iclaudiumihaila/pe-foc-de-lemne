"""
User Data Model for Local Producer Web Application

This module provides the User model class with MongoDB operations,
password management, and phone verification functionality.
"""

import re
import logging
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.utils.error_handlers import DatabaseError, ValidationError
from app.utils.validators import validate_phone_number


class User:
    """
    User model for managing user accounts, authentication, and phone verification.
    
    This class handles user CRUD operations with MongoDB, password hashing,
    phone number validation, and SMS verification workflow.
    """
    
    # Collection name in MongoDB
    COLLECTION_NAME = 'users'
    
    # User roles
    ROLE_CUSTOMER = 'customer'
    ROLE_ADMIN = 'admin'
    VALID_ROLES = [ROLE_CUSTOMER, ROLE_ADMIN]
    
    # Password hashing configuration
    BCRYPT_ROUNDS = 12
    
    # Verification code configuration
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_CODE_EXPIRY_MINUTES = 10
    
    def __init__(self, data: Dict[str, Any] = None):
        """
        Initialize User object from dictionary data.
        
        Args:
            data (dict): User data dictionary from MongoDB or form input
        """
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.phone_number = data.get('phone_number')
        self.name = data.get('name')
        self.role = data.get('role', self.ROLE_CUSTOMER)
        self.password_hash = data.get('password_hash')
        self.is_verified = data.get('is_verified', False)
        self.verification_code = data.get('verification_code')
        self.verification_expires = data.get('verification_expires')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.last_login = data.get('last_login')
    
    @classmethod
    def create(cls, phone_number: str, name: str, password: str, role: str = ROLE_CUSTOMER) -> 'User':
        """
        Create a new user in the database.
        
        Args:
            phone_number (str): User's phone number in E.164 format
            name (str): User's full name
            password (str): Plain text password to be hashed
            role (str): User role (customer or admin)
            
        Returns:
            User: Created user instance
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If user creation fails (e.g., duplicate phone)
        """
        try:
            # Validate inputs
            if not phone_number or not name or not password:
                raise ValidationError("Phone number, name, and password are required")
            
            # Validate and normalize phone number
            normalized_phone = cls._normalize_phone_number(phone_number)
            
            # Validate name length
            if len(name.strip()) < 2 or len(name.strip()) > 50:
                raise ValidationError("Name must be between 2 and 50 characters")
            
            # Validate role
            if role not in cls.VALID_ROLES:
                raise ValidationError(f"Role must be one of: {', '.join(cls.VALID_ROLES)}")
            
            # Validate password strength
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long")
            
            # Hash password
            password_hash = cls._hash_password(password)
            
            # Prepare user document
            now = datetime.utcnow()
            user_doc = {
                'phone_number': normalized_phone,
                'name': name.strip(),
                'role': role,
                'password_hash': password_hash,
                'is_verified': False,
                'created_at': now,
                'updated_at': now
            }
            
            # Insert into database
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            result = collection.insert_one(user_doc)
            user_doc['_id'] = result.inserted_id
            
            # Create and return User instance
            user = cls(user_doc)
            
            logging.info(f"User created successfully: {normalized_phone}")
            return user
            
        except DuplicateKeyError:
            raise DatabaseError(
                "Phone number already registered",
                "DB_001",
                409,
                {"field": "phone_number", "value": phone_number}
            )
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error creating user: {str(e)}")
            raise DatabaseError("Failed to create user", "DB_001")
    
    @classmethod
    def find_by_phone(cls, phone_number: str) -> Optional['User']:
        """
        Find user by phone number.
        
        Args:
            phone_number (str): Phone number to search for
            
        Returns:
            User: User instance if found, None otherwise
        """
        try:
            # Normalize phone number for search
            normalized_phone = cls._normalize_phone_number(phone_number)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            user_doc = collection.find_one({'phone_number': normalized_phone})
            
            if user_doc:
                return cls(user_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding user by phone: {str(e)}")
            raise DatabaseError("Failed to find user", "DB_001")
    
    @classmethod
    def find_by_id(cls, user_id: Union[str, ObjectId]) -> Optional['User']:
        """
        Find user by ObjectId.
        
        Args:
            user_id (str|ObjectId): User's MongoDB ObjectId
            
        Returns:
            User: User instance if found, None otherwise
        """
        try:
            # Convert string to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            user_doc = collection.find_one({'_id': user_id})
            
            if user_doc:
                return cls(user_doc)
            return None
            
        except Exception as e:
            logging.error(f"Error finding user by ID: {str(e)}")
            raise DatabaseError("Failed to find user", "DB_001")
    
    def update(self, data: Dict[str, Any]) -> bool:
        """
        Update user data in database.
        
        Args:
            data (dict): Dictionary of fields to update
            
        Returns:
            bool: True if update successful
            
        Raises:
            DatabaseError: If update fails
        """
        try:
            if not self._id:
                raise DatabaseError("Cannot update user without ID")
            
            # Prepare update data
            update_data = {}
            
            # Handle specific field updates with validation
            if 'name' in data:
                name = data['name'].strip()
                if len(name) < 2 or len(name) > 50:
                    raise ValidationError("Name must be between 2 and 50 characters")
                update_data['name'] = name
                self.name = name
            
            if 'role' in data:
                if data['role'] not in self.VALID_ROLES:
                    raise ValidationError(f"Role must be one of: {', '.join(self.VALID_ROLES)}")
                update_data['role'] = data['role']
                self.role = data['role']
            
            if 'is_verified' in data:
                update_data['is_verified'] = bool(data['is_verified'])
                self.is_verified = bool(data['is_verified'])
            
            if 'last_login' in data:
                update_data['last_login'] = data['last_login']
                self.last_login = data['last_login']
            
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
                logging.info(f"User updated successfully: {self.phone_number}")
                return True
            return False
            
        except Exception as e:
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            logging.error(f"Error updating user: {str(e)}")
            raise DatabaseError("Failed to update user", "DB_001")
    
    def set_password(self, password: str) -> bool:
        """
        Set user password with hashing.
        
        Args:
            password (str): Plain text password
            
        Returns:
            bool: True if password set successfully
        """
        try:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long")
            
            password_hash = self._hash_password(password)
            
            return self.update({'password_hash': password_hash})
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logging.error(f"Error setting password: {str(e)}")
            raise DatabaseError("Failed to set password", "DB_001")
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches
        """
        try:
            if not self.password_hash:
                return False
            
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
            
        except Exception as e:
            logging.error(f"Error verifying password: {str(e)}")
            return False
    
    def set_verification_code(self, code: str) -> bool:
        """
        Set SMS verification code with expiry.
        
        Args:
            code (str): 6-digit verification code
            
        Returns:
            bool: True if code set successfully
        """
        try:
            if not re.match(r'^\d{6}$', code):
                raise ValidationError("Verification code must be 6 digits")
            
            expiry = datetime.utcnow() + timedelta(minutes=self.VERIFICATION_CODE_EXPIRY_MINUTES)
            
            update_data = {
                'verification_code': code,
                'verification_expires': expiry
            }
            
            return self.update(update_data)
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logging.error(f"Error setting verification code: {str(e)}")
            raise DatabaseError("Failed to set verification code", "DB_001")
    
    def verify_phone(self, code: str) -> bool:
        """
        Verify phone with SMS code and mark as verified.
        
        Args:
            code (str): 6-digit verification code
            
        Returns:
            bool: True if verification successful
        """
        try:
            # Check if code matches and hasn't expired
            if not self.verification_code or self.verification_code != code:
                return False
            
            if not self.verification_expires or datetime.utcnow() > self.verification_expires:
                return False
            
            # Mark as verified and clear verification data
            update_data = {
                'is_verified': True,
                'verification_code': None,
                'verification_expires': None
            }
            
            success = self.update(update_data)
            
            if success:
                logging.info(f"Phone verified successfully: {self.phone_number}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error verifying phone: {str(e)}")
            raise DatabaseError("Failed to verify phone", "DB_001")
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Args:
            include_sensitive (bool): Include sensitive fields like password_hash
            
        Returns:
            dict: User data dictionary
        """
        data = {
            'id': str(self._id) if self._id else None,
            'phone_number': self.phone_number,
            'name': self.name,
            'role': self.role,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'last_login': self.last_login.isoformat() + 'Z' if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'password_hash': self.password_hash,
                'verification_code': self.verification_code,
                'verification_expires': self.verification_expires.isoformat() + 'Z' if self.verification_expires else None
            })
        
        return data
    
    @staticmethod
    def _normalize_phone_number(phone_number: str) -> str:
        """
        Normalize phone number to E.164 format.
        
        Args:
            phone_number (str): Phone number to normalize
            
        Returns:
            str: Normalized phone number
            
        Raises:
            ValidationError: If phone number format is invalid
        """
        if not validate_phone_number(phone_number):
            raise ValidationError("Invalid phone number format. Use E.164 format (+1234567890)")
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            else:
                raise ValidationError("Phone number must include country code or be in E.164 format")
        
        return cleaned
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt(rounds=User.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def __repr__(self) -> str:
        """String representation of User object."""
        return f"User(id={self._id}, phone={self.phone_number}, name={self.name}, role={self.role})"