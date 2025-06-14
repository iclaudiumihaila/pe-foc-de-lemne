"""
Admin Authentication Service for Local Producer Web Application

This module provides secure admin authentication functionality including
login verification, JWT token management, password hashing, and session handling
with Romanian localization for the local producer marketplace.
"""

import os
import logging
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from jose import jwt, JWTError
from app.models.user import User
from app.utils.error_handlers import AuthenticationError, ValidationError


class AuthService:
    """
    Admin authentication service for secure login and session management.
    
    This service handles admin login verification, JWT token generation and validation,
    password management, and provides Romanian localized error messages for
    authentication operations in the local producer marketplace admin system.
    """
    
    # JWT Configuration
    ALGORITHM = 'HS256'
    TOKEN_EXPIRY_HOURS = 8  # Admin tokens expire after 8 hours
    REFRESH_TOKEN_EXPIRY_DAYS = 7  # Refresh tokens expire after 7 days
    
    # Password Configuration
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    def __init__(self, config=None):
        """
        Initialize AuthService with configuration.
        
        Args:
            config: Application configuration object
        """
        self.config = config or {}
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.login_attempts = {}  # In-memory store for rate limiting
        
        # Validate configuration
        if not self.secret_key or self.secret_key == 'your-secret-key-change-in-production':
            logging.warning("Using default JWT secret key. Change JWT_SECRET_KEY in production!")
    
    def authenticate_admin(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Authenticate admin user with username and password.
        
        Args:
            username (str): Admin username (phone number)
            password (str): Plain text password
            ip_address (str): Client IP address for rate limiting
            
        Returns:
            dict: Authentication result with user data and tokens
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If input validation fails
        """
        try:
            # Validate inputs
            if not username or not password:
                raise ValidationError("Numele de utilizator și parola sunt obligatorii")
            
            # Check rate limiting
            self._check_rate_limit(username, ip_address)
            
            # Find admin user by phone number
            admin_user = User.find_by_phone(username)
            
            if not admin_user:
                self._record_failed_attempt(username, ip_address)
                raise AuthenticationError(
                    "Datele de autentificare sunt incorecte",
                    "AUTH_001"
                )
            
            # Verify admin role
            if admin_user.role != User.ROLE_ADMIN:
                self._record_failed_attempt(username, ip_address)
                raise AuthenticationError(
                    "Acces interzis. Doar administratorii pot accesa acest sistem",
                    "AUTH_002"
                )
            
            # Verify password
            if not admin_user.verify_password(password):
                self._record_failed_attempt(username, ip_address)
                raise AuthenticationError(
                    "Datele de autentificare sunt incorecte",
                    "AUTH_001"
                )
            
            # Check if account is verified
            if not admin_user.is_verified:
                raise AuthenticationError(
                    "Contul nu este verificat. Contactați administratorul sistemului",
                    "AUTH_003"
                )
            
            # Clear failed attempts on successful authentication
            self._clear_failed_attempts(username)
            
            # Update last login
            admin_user.update({'last_login': datetime.utcnow()})
            
            # Generate tokens
            access_token = self.generate_token(admin_user)
            refresh_token = self.generate_refresh_token(admin_user)
            
            # Prepare response
            auth_result = {
                'success': True,
                'message': 'Autentificare reușită',
                'user': {
                    'id': str(admin_user._id),
                    'name': admin_user.name,
                    'phone_number': admin_user.phone_number,
                    'role': admin_user.role,
                    'last_login': admin_user.last_login.isoformat() + 'Z' if admin_user.last_login else None
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': self.TOKEN_EXPIRY_HOURS * 3600  # seconds
                }
            }
            
            logging.info(f"Admin authentication successful: {username}")
            return auth_result
            
        except (AuthenticationError, ValidationError):
            raise
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(
                "Eroare la autentificare. Încercați din nou",
                "AUTH_999"
            )
    
    def generate_token(self, admin_user: User, custom_expiry: timedelta = None) -> str:
        """
        Generate JWT access token for authenticated admin.
        
        Args:
            admin_user (User): Authenticated admin user
            custom_expiry (timedelta): Custom token expiry (optional)
            
        Returns:
            str: JWT access token
        """
        try:
            # Calculate expiry
            if custom_expiry:
                expires_at = datetime.utcnow() + custom_expiry
            else:
                expires_at = datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
            
            # Prepare token payload
            payload = {
                'user_id': str(admin_user._id),
                'phone_number': admin_user.phone_number,
                'name': admin_user.name,
                'role': admin_user.role,
                'iat': datetime.utcnow(),  # Issued at
                'exp': expires_at,  # Expiry
                'iss': 'pe-foc-de-lemne-admin',  # Issuer
                'aud': 'pe-foc-de-lemne-admin-panel'  # Audience
            }
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
            
            logging.info(f"Access token generated for admin: {admin_user.phone_number}")
            return token
            
        except Exception as e:
            logging.error(f"Token generation error: {str(e)}")
            raise AuthenticationError(
                "Eroare la generarea token-ului de autentificare",
                "AUTH_004"
            )
    
    def generate_refresh_token(self, admin_user: User) -> str:
        """
        Generate JWT refresh token for admin session renewal.
        
        Args:
            admin_user (User): Authenticated admin user
            
        Returns:
            str: JWT refresh token
        """
        try:
            # Calculate expiry for refresh token
            expires_at = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRY_DAYS)
            
            # Prepare refresh token payload
            payload = {
                'user_id': str(admin_user._id),
                'phone_number': admin_user.phone_number,
                'role': admin_user.role,
                'token_type': 'refresh',
                'iat': datetime.utcnow(),
                'exp': expires_at,
                'iss': 'pe-foc-de-lemne-admin',
                'aud': 'pe-foc-de-lemne-admin-panel'
            }
            
            # Generate refresh token
            refresh_token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
            
            logging.info(f"Refresh token generated for admin: {admin_user.phone_number}")
            return refresh_token
            
        except Exception as e:
            logging.error(f"Refresh token generation error: {str(e)}")
            raise AuthenticationError(
                "Eroare la generarea token-ului de reînnoire",
                "AUTH_005"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token (str): JWT token to verify
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            if not token:
                raise AuthenticationError(
                    "Token de autentificare lipsește",
                    "AUTH_006"
                )
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM],
                audience='pe-foc-de-lemne-admin-panel',
                issuer='pe-foc-de-lemne-admin'
            )
            
            # Verify admin role
            if payload.get('role') != User.ROLE_ADMIN:
                raise AuthenticationError(
                    "Token invalid pentru admin",
                    "AUTH_007"
                )
            
            # Verify token hasn't expired
            exp = payload.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationError(
                    "Token-ul de autentificare a expirat",
                    "AUTH_008"
                )
            
            logging.debug(f"Token verified successfully for user: {payload.get('phone_number')}")
            return payload
            
        except JWTError as e:
            logging.warning(f"JWT verification failed: {str(e)}")
            if 'expired' in str(e).lower():
                raise AuthenticationError(
                    "Token-ul de autentificare a expirat",
                    "AUTH_008"
                )
            else:
                raise AuthenticationError(
                    "Token de autentificare invalid",
                    "AUTH_009"
                )
        except AuthenticationError:
            raise
        except Exception as e:
            logging.error(f"Token verification error: {str(e)}")
            raise AuthenticationError(
                "Eroare la verificarea token-ului",
                "AUTH_010"
            )
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token (str): Valid refresh token
            
        Returns:
            dict: New access token and refresh token
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token)
            
            # Check if it's a refresh token
            if payload.get('token_type') != 'refresh':
                raise AuthenticationError(
                    "Token de reînnoire invalid",
                    "AUTH_011"
                )
            
            # Get admin user
            admin_user = User.find_by_id(payload.get('user_id'))
            if not admin_user or admin_user.role != User.ROLE_ADMIN:
                raise AuthenticationError(
                    "Utilizator admin negăsit",
                    "AUTH_012"
                )
            
            # Generate new tokens
            new_access_token = self.generate_token(admin_user)
            new_refresh_token = self.generate_refresh_token(admin_user)
            
            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'token_type': 'Bearer',
                'expires_in': self.TOKEN_EXPIRY_HOURS * 3600
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logging.error(f"Token refresh error: {str(e)}")
            raise AuthenticationError(
                "Eroare la reînnoirea token-ului",
                "AUTH_013"
            )
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        try:
            if len(password) < self.MIN_PASSWORD_LENGTH:
                raise ValidationError(
                    f"Parola trebuie să aibă cel puțin {self.MIN_PASSWORD_LENGTH} caractere"
                )
            
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return hashed.decode('utf-8')
            
        except ValidationError:
            raise
        except Exception as e:
            logging.error(f"Password hashing error: {str(e)}")
            raise AuthenticationError(
                "Eroare la criptarea parolei",
                "AUTH_014"
            )
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password (str): Plain text password
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logging.error(f"Password verification error: {str(e)}")
            return False
    
    def logout_admin(self, token: str) -> Dict[str, Any]:
        """
        Logout admin by invalidating token.
        
        Note: In a production environment, you would typically maintain
        a blacklist of invalidated tokens in Redis or database.
        
        Args:
            token (str): JWT token to invalidate
            
        Returns:
            dict: Logout confirmation
        """
        try:
            # Verify token first
            payload = self.verify_token(token)
            
            # In production, add token to blacklist here
            # For now, we just log the logout
            logging.info(f"Admin logged out: {payload.get('phone_number')}")
            
            return {
                'success': True,
                'message': 'Deconectare reușită'
            }
            
        except AuthenticationError:
            # Even if token is invalid, consider logout successful
            return {
                'success': True,
                'message': 'Deconectare reușită'
            }
        except Exception as e:
            logging.error(f"Logout error: {str(e)}")
            return {
                'success': True,
                'message': 'Deconectare reușită'
            }
    
    def _check_rate_limit(self, username: str, ip_address: str = None) -> None:
        """
        Check if user has exceeded login attempts.
        
        Args:
            username (str): Username to check
            ip_address (str): Client IP address
            
        Raises:
            AuthenticationError: If rate limit exceeded
        """
        key = f"{username}:{ip_address}" if ip_address else username
        
        if key in self.login_attempts:
            attempts_data = self.login_attempts[key]
            
            # Check if lockout period has expired
            if attempts_data['locked_until'] > datetime.utcnow():
                remaining_minutes = (attempts_data['locked_until'] - datetime.utcnow()).total_seconds() / 60
                raise AuthenticationError(
                    f"Prea multe încercări de autentificare. Încercați din nou în {int(remaining_minutes)} minute",
                    "AUTH_015"
                )
            
            # Reset if lockout period expired
            if attempts_data['locked_until'] <= datetime.utcnow():
                del self.login_attempts[key]
    
    def _record_failed_attempt(self, username: str, ip_address: str = None) -> None:
        """
        Record failed login attempt for rate limiting.
        
        Args:
            username (str): Username that failed
            ip_address (str): Client IP address
        """
        key = f"{username}:{ip_address}" if ip_address else username
        now = datetime.utcnow()
        
        if key not in self.login_attempts:
            self.login_attempts[key] = {
                'count': 1,
                'first_attempt': now,
                'locked_until': now
            }
        else:
            self.login_attempts[key]['count'] += 1
        
        # Lock account if too many failed attempts
        if self.login_attempts[key]['count'] >= self.MAX_LOGIN_ATTEMPTS:
            self.login_attempts[key]['locked_until'] = now + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            logging.warning(f"Account locked due to failed attempts: {username}")
    
    def _clear_failed_attempts(self, username: str) -> None:
        """
        Clear failed login attempts for successful authentication.
        
        Args:
            username (str): Username to clear attempts for
        """
        # Clear all entries for this username (regardless of IP)
        keys_to_remove = [key for key in self.login_attempts.keys() if key.startswith(username)]
        for key in keys_to_remove:
            del self.login_attempts[key]
    
    def create_initial_admin(self, name: str, phone_number: str, password: str) -> Dict[str, Any]:
        """
        Create initial admin account (for setup purposes).
        
        Args:
            name (str): Admin name
            phone_number (str): Admin phone number
            password (str): Admin password
            
        Returns:
            dict: Created admin user info
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If admin creation fails
        """
        try:
            # Check if any admin already exists
            from app.database import get_database
            db = get_database()
            existing_admin = db[User.COLLECTION_NAME].find_one({'role': User.ROLE_ADMIN})
            
            if existing_admin:
                raise AuthenticationError(
                    "Un administrator există deja în sistem",
                    "AUTH_016"
                )
            
            # Create admin user
            admin_user = User.create(
                phone_number=phone_number,
                name=name,
                password=password,
                role=User.ROLE_ADMIN
            )
            
            # Mark as verified (admin doesn't need SMS verification)
            admin_user.update({'is_verified': True})
            
            logging.info(f"Initial admin created: {phone_number}")
            
            return {
                'success': True,
                'message': 'Administrator creat cu succes',
                'admin': {
                    'id': str(admin_user._id),
                    'name': admin_user.name,
                    'phone_number': admin_user.phone_number,
                    'role': admin_user.role
                }
            }
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            logging.error(f"Admin creation error: {str(e)}")
            raise AuthenticationError(
                "Eroare la crearea administratorului",
                "AUTH_017"
            )