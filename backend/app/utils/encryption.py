"""
Data Encryption and Cryptographic Utilities for Local Producer Web Application

This module provides comprehensive encryption utilities for protecting sensitive data,
including personal information, payment details, and communications.
"""

import os
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import jwt


class EncryptionManager:
    """Centralized encryption management for the application"""
    
    def __init__(self, master_key: str = None):
        """
        Initialize encryption manager with master key.
        
        Args:
            master_key (str): Master encryption key (from environment variable)
        """
        self.master_key = master_key or os.environ.get('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError("ENCRYPTION_MASTER_KEY environment variable must be set")
        
        # Initialize Fernet cipher for symmetric encryption
        self.fernet = self._initialize_fernet()
        
        # Initialize RSA keys for asymmetric encryption
        self.rsa_private_key, self.rsa_public_key = self._initialize_rsa_keys()
    
    def _initialize_fernet(self) -> Fernet:
        """Initialize Fernet symmetric encryption"""
        # Derive key from master key
        salt = b'romanian_producers_salt'  # In production, use random salt stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def _initialize_rsa_keys(self):
        """Initialize RSA key pair for asymmetric encryption"""
        # In production, load keys from secure storage
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data using Fernet symmetric encryption.
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            str: Base64 encoded encrypted data
        """
        if not data:
            return ""
        
        encrypted_data = self.fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data using Fernet symmetric encryption.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            
        Returns:
            str: Decrypted data
        """
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            raise ValueError("Failed to decrypt data")
    
    def encrypt_phone_number(self, phone_number: str) -> str:
        """
        Encrypt Romanian phone number for storage.
        
        Args:
            phone_number (str): Phone number to encrypt
            
        Returns:
            str: Encrypted phone number
        """
        # Normalize phone number before encryption
        normalized_phone = phone_number.replace('+40', '').replace(' ', '').replace('-', '')
        return self.encrypt_sensitive_data(normalized_phone)
    
    def decrypt_phone_number(self, encrypted_phone: str) -> str:
        """
        Decrypt Romanian phone number.
        
        Args:
            encrypted_phone (str): Encrypted phone number
            
        Returns:
            str: Decrypted phone number in +40 format
        """
        decrypted_phone = self.decrypt_sensitive_data(encrypted_phone)
        if decrypted_phone and not decrypted_phone.startswith('+40'):
            decrypted_phone = '+40' + decrypted_phone
        return decrypted_phone
    
    def encrypt_email(self, email: str) -> str:
        """
        Encrypt email address for storage.
        
        Args:
            email (str): Email address to encrypt
            
        Returns:
            str: Encrypted email
        """
        return self.encrypt_sensitive_data(email.lower().strip())
    
    def decrypt_email(self, encrypted_email: str) -> str:
        """
        Decrypt email address.
        
        Args:
            encrypted_email (str): Encrypted email
            
        Returns:
            str: Decrypted email address
        """
        return self.decrypt_sensitive_data(encrypted_email)
    
    def encrypt_address(self, address_data: Dict[str, str]) -> Dict[str, str]:
        """
        Encrypt address data for storage.
        
        Args:
            address_data (dict): Address data to encrypt
            
        Returns:
            dict: Encrypted address data
        """
        encrypted_address = {}
        sensitive_fields = ['street', 'city', 'county', 'postal_code']
        
        for key, value in address_data.items():
            if key in sensitive_fields and value:
                encrypted_address[key] = self.encrypt_sensitive_data(str(value))
            else:
                encrypted_address[key] = value
        
        return encrypted_address
    
    def decrypt_address(self, encrypted_address: Dict[str, str]) -> Dict[str, str]:
        """
        Decrypt address data.
        
        Args:
            encrypted_address (dict): Encrypted address data
            
        Returns:
            dict: Decrypted address data
        """
        decrypted_address = {}
        sensitive_fields = ['street', 'city', 'county', 'postal_code']
        
        for key, value in encrypted_address.items():
            if key in sensitive_fields and value:
                decrypted_address[key] = self.decrypt_sensitive_data(value)
            else:
                decrypted_address[key] = value
        
        return decrypted_address


class TokenManager:
    """JWT token management for authentication and sessions"""
    
    def __init__(self, secret_key: str = None):
        """
        Initialize token manager.
        
        Args:
            secret_key (str): Secret key for JWT signing
        """
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable must be set")
    
    def generate_admin_token(self, admin_id: str, permissions: list = None) -> str:
        """
        Generate JWT token for admin authentication.
        
        Args:
            admin_id (str): Admin user ID
            permissions (list): Admin permissions
            
        Returns:
            str: JWT token
        """
        payload = {
            'admin_id': admin_id,
            'permissions': permissions or [],
            'type': 'admin',
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=8)  # 8-hour expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def generate_session_token(self, phone_number: str) -> str:
        """
        Generate session token for customer authentication.
        
        Args:
            phone_number (str): Customer phone number
            
        Returns:
            str: Session token
        """
        payload = {
            'phone_number': phone_number,
            'type': 'customer_session',
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)  # 24-hour expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def generate_csrf_token(self, session_id: str) -> str:
        """
        Generate CSRF token for form protection.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            str: CSRF token
        """
        payload = {
            'session_id': session_id,
            'type': 'csrf',
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # 1-hour expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_token(self, token: str, token_type: str = None) -> Dict[str, Any]:
        """
        Validate JWT token.
        
        Args:
            token (str): JWT token to validate
            token_type (str): Expected token type
            
        Returns:
            dict: Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Validate token type if specified
            if token_type and payload.get('type') != token_type:
                return {'valid': False, 'error': 'Invalid token type'}
            
            return {'valid': True, 'payload': payload}
        
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    def refresh_admin_token(self, token: str) -> Optional[str]:
        """
        Refresh admin token if close to expiry.
        
        Args:
            token (str): Current admin token
            
        Returns:
            str: New token if refreshed, None if not needed or invalid
        """
        validation = self.validate_token(token, 'admin')
        if not validation['valid']:
            return None
        
        payload = validation['payload']
        exp_time = datetime.fromtimestamp(payload['exp'], timezone.utc)
        
        # Refresh if token expires within 1 hour
        if exp_time - datetime.now(timezone.utc) < timedelta(hours=1):
            return self.generate_admin_token(
                payload['admin_id'],
                payload.get('permissions', [])
            )
        
        return None


class HashingUtils:
    """Utilities for hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt-style hashing.
        
        Args:
            password (str): Password to hash
            
        Returns:
            str: Hashed password
        """
        # Add salt and multiple rounds for security
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return f"{salt}${base64.b64encode(password_hash).decode('utf-8')}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password (str): Plain text password
            hashed_password (str): Stored password hash
            
        Returns:
            bool: True if password matches
        """
        try:
            salt, stored_hash = hashed_password.split('$')
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            computed_hash = base64.b64encode(password_hash).decode('utf-8')
            
            return secrets.compare_digest(stored_hash, computed_hash)
        except Exception:
            return False
    
    @staticmethod
    def hash_file_content(file_content: bytes) -> str:
        """
        Generate hash of file content for integrity verification.
        
        Args:
            file_content (bytes): File content
            
        Returns:
            str: SHA-256 hash of file
        """
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """
        Generate secure filename with hash component.
        
        Args:
            original_filename (str): Original filename
            
        Returns:
            str: Secure filename
        """
        # Extract extension
        name, ext = os.path.splitext(original_filename)
        
        # Generate secure random component
        secure_component = secrets.token_hex(16)
        
        # Create secure filename
        timestamp = int(datetime.now().timestamp())
        secure_filename = f"{timestamp}_{secure_component}{ext}"
        
        return secure_filename


class DataMasking:
    """Utilities for data masking and anonymization"""
    
    @staticmethod
    def mask_phone_number(phone_number: str) -> str:
        """
        Mask phone number for display purposes.
        
        Args:
            phone_number (str): Phone number to mask
            
        Returns:
            str: Masked phone number
        """
        if not phone_number:
            return ""
        
        # Remove country code and formatting
        clean_phone = phone_number.replace('+40', '').replace(' ', '').replace('-', '')
        
        if len(clean_phone) >= 4:
            return f"+40***{clean_phone[-4:]}"
        else:
            return "+40***"
    
    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address for display purposes.
        
        Args:
            email (str): Email to mask
            
        Returns:
            str: Masked email
        """
        if not email or '@' not in email:
            return "***"
        
        local, domain = email.split('@', 1)
        
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_address(address: str) -> str:
        """
        Mask address for display purposes.
        
        Args:
            address (str): Address to mask
            
        Returns:
            str: Masked address
        """
        if not address:
            return ""
        
        words = address.split()
        if len(words) <= 2:
            return "***"
        
        # Show first and last word, mask middle
        return f"{words[0]} *** {words[-1]}"


# Global encryption manager instance
encryption_manager = None
token_manager = None

def initialize_encryption(master_key: str = None, jwt_secret: str = None):
    """Initialize global encryption managers"""
    global encryption_manager, token_manager
    
    encryption_manager = EncryptionManager(master_key)
    token_manager = TokenManager(jwt_secret)

def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    if encryption_manager is None:
        raise ValueError("Encryption manager not initialized")
    return encryption_manager

def get_token_manager() -> TokenManager:
    """Get global token manager instance"""
    if token_manager is None:
        raise ValueError("Token manager not initialized")
    return token_manager