"""
Unit tests for Admin Authentication Service functionality.

This module contains comprehensive unit tests for the admin authentication service
including admin login, JWT token management, password security, rate limiting,
and Romanian localization. All external dependencies are mocked for isolated testing.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
from jose import jwt

from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.error_handlers import AuthenticationError, ValidationError


class TestAuthServiceInitialization:
    """Test auth service initialization and configuration."""
    
    def test_initialization_with_default_config(self):
        """Test auth service initialization with default configuration."""
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test-secret-key'}):
            service = AuthService()
            
            assert service.secret_key == 'test-secret-key'
            assert service.login_attempts == {}
            assert service.TOKEN_EXPIRY_HOURS == 8
            assert service.REFRESH_TOKEN_EXPIRY_DAYS == 7
            assert service.MAX_LOGIN_ATTEMPTS == 5
    
    def test_initialization_with_custom_config(self):
        """Test auth service initialization with custom configuration."""
        config = {'custom_setting': 'test_value'}
        service = AuthService(config)
        
        assert service.config == config
    
    def test_initialization_with_default_secret_key_warning(self):
        """Test warning when using default JWT secret key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('app.services.auth_service.logging.warning') as mock_warning:
                service = AuthService()
                
                assert service.secret_key == 'your-secret-key-change-in-production'
                mock_warning.assert_called_once()


class TestAdminAuthentication:
    """Test admin authentication functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.secret_key = 'test-secret-key'
        self.auth_service.login_attempts = {}
        
        # Test admin user data
        self.admin_data = {
            '_id': '507f1f77bcf86cd799439011',
            'phone_number': '+40722123456',
            'name': 'Test Admin',
            'role': User.ROLE_ADMIN,
            'password_hash': '$2b$12$test.hash.value',
            'is_verified': True,
            'last_login': None
        }
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_authenticate_admin_success(self, mock_find_by_phone):
        """Test successful admin authentication."""
        # Setup mock admin user
        mock_admin = Mock()
        mock_admin._id = self.admin_data['_id']
        mock_admin.phone_number = self.admin_data['phone_number']
        mock_admin.name = self.admin_data['name']
        mock_admin.role = self.admin_data['role']
        mock_admin.is_verified = True
        mock_admin.last_login = None
        mock_admin.verify_password.return_value = True
        mock_admin.update.return_value = True
        
        mock_find_by_phone.return_value = mock_admin
        
        # Test authentication
        result = self.auth_service.authenticate_admin('+40722123456', 'correct_password', '192.168.1.1')
        
        # Assertions
        assert result['success'] is True
        assert result['message'] == 'Autentificare reușită'
        assert result['user']['name'] == 'Test Admin'
        assert result['user']['role'] == User.ROLE_ADMIN
        assert 'access_token' in result['tokens']
        assert 'refresh_token' in result['tokens']
        assert result['tokens']['token_type'] == 'Bearer'
        
        mock_admin.verify_password.assert_called_once_with('correct_password')
        mock_admin.update.assert_called_once()
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_authenticate_admin_invalid_credentials_user_not_found(self, mock_find_by_phone):
        """Test authentication with non-existent user."""
        mock_find_by_phone.return_value = None
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.authenticate_admin('+40722123456', 'any_password')
        
        assert exc_info.value.message == "Datele de autentificare sunt incorecte"
        assert exc_info.value.error_code == "AUTH_001"
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_authenticate_admin_invalid_credentials_wrong_password(self, mock_find_by_phone):
        """Test authentication with wrong password."""
        mock_admin = Mock()
        mock_admin.role = User.ROLE_ADMIN
        mock_admin.verify_password.return_value = False
        
        mock_find_by_phone.return_value = mock_admin
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.authenticate_admin('+40722123456', 'wrong_password')
        
        assert exc_info.value.message == "Datele de autentificare sunt incorecte"
        assert exc_info.value.error_code == "AUTH_001"
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_authenticate_admin_non_admin_role(self, mock_find_by_phone):
        """Test authentication with customer role user."""
        mock_user = Mock()
        mock_user.role = User.ROLE_CUSTOMER
        
        mock_find_by_phone.return_value = mock_user
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.authenticate_admin('+40722123456', 'any_password')
        
        assert exc_info.value.message == "Acces interzis. Doar administratorii pot accesa acest sistem"
        assert exc_info.value.error_code == "AUTH_002"
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_authenticate_admin_unverified_account(self, mock_find_by_phone):
        """Test authentication with unverified admin account."""
        mock_admin = Mock()
        mock_admin.role = User.ROLE_ADMIN
        mock_admin.verify_password.return_value = True
        mock_admin.is_verified = False
        
        mock_find_by_phone.return_value = mock_admin
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.authenticate_admin('+40722123456', 'correct_password')
        
        assert exc_info.value.message == "Contul nu este verificat. Contactați administratorul sistemului"
        assert exc_info.value.error_code == "AUTH_003"
    
    def test_authenticate_admin_missing_credentials(self):
        """Test authentication with missing username or password."""
        with pytest.raises(ValidationError) as exc_info:
            self.auth_service.authenticate_admin('', 'password')
        
        assert exc_info.value.message == "Numele de utilizator și parola sunt obligatorii"
        
        with pytest.raises(ValidationError) as exc_info:
            self.auth_service.authenticate_admin('username', '')
        
        assert exc_info.value.message == "Numele de utilizator și parola sunt obligatorii"


class TestJWTTokenManagement:
    """Test JWT token generation and verification."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.secret_key = 'test-secret-key-for-jwt'
        
        # Test admin user
        self.mock_admin = Mock()
        self.mock_admin._id = '507f1f77bcf86cd799439011'
        self.mock_admin.phone_number = '+40722123456'
        self.mock_admin.name = 'Test Admin'
        self.mock_admin.role = User.ROLE_ADMIN
    
    def test_generate_token_success(self):
        """Test successful JWT token generation."""
        token = self.auth_service.generate_token(self.mock_admin)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify structure
        payload = jwt.decode(
            token,
            self.auth_service.secret_key,
            algorithms=[self.auth_service.ALGORITHM],
            options={"verify_aud": False, "verify_iss": False}
        )
        
        assert payload['user_id'] == '507f1f77bcf86cd799439011'
        assert payload['phone_number'] == '+40722123456'
        assert payload['name'] == 'Test Admin'
        assert payload['role'] == User.ROLE_ADMIN
        assert payload['iss'] == 'pe-foc-de-lemne-admin'
        assert payload['aud'] == 'pe-foc-de-lemne-admin-panel'
    
    def test_generate_refresh_token_success(self):
        """Test successful refresh token generation."""
        refresh_token = self.auth_service.generate_refresh_token(self.mock_admin)
        
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        
        # Decode token to verify structure
        payload = jwt.decode(
            refresh_token,
            self.auth_service.secret_key,
            algorithms=[self.auth_service.ALGORITHM],
            options={"verify_aud": False, "verify_iss": False}
        )
        
        assert payload['user_id'] == '507f1f77bcf86cd799439011'
        assert payload['phone_number'] == '+40722123456'
        assert payload['role'] == User.ROLE_ADMIN
        assert payload['token_type'] == 'refresh'
        assert payload['iss'] == 'pe-foc-de-lemne-admin'
        assert payload['aud'] == 'pe-foc-de-lemne-admin-panel'
    
    def test_verify_token_success(self):
        """Test successful token verification."""
        # Generate token
        token = self.auth_service.generate_token(self.mock_admin)
        
        # Verify token
        payload = self.auth_service.verify_token(token)
        
        assert payload['user_id'] == '507f1f77bcf86cd799439011'
        assert payload['phone_number'] == '+40722123456'
        assert payload['name'] == 'Test Admin'
        assert payload['role'] == User.ROLE_ADMIN
    
    def test_verify_token_with_bearer_prefix(self):
        """Test token verification with Bearer prefix."""
        token = self.auth_service.generate_token(self.mock_admin)
        bearer_token = f'Bearer {token}'
        
        payload = self.auth_service.verify_token(bearer_token)
        
        assert payload['user_id'] == '507f1f77bcf86cd799439011'
        assert payload['role'] == User.ROLE_ADMIN
    
    def test_verify_token_missing_token(self):
        """Test token verification with missing token."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.verify_token('')
        
        assert exc_info.value.message == "Token de autentificare lipsește"
        assert exc_info.value.error_code == "AUTH_006"
    
    def test_verify_token_invalid_token(self):
        """Test token verification with invalid token."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.verify_token('invalid.token.string')
        
        assert exc_info.value.message == "Token de autentificare invalid"
        assert exc_info.value.error_code == "AUTH_009"
    
    def test_verify_token_expired_token(self):
        """Test token verification with expired token."""
        # Generate token with past expiry
        past_expiry = timedelta(hours=-1)
        expired_token = self.auth_service.generate_token(self.mock_admin, past_expiry)
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.verify_token(expired_token)
        
        assert exc_info.value.message == "Token-ul de autentificare a expirat"
        assert exc_info.value.error_code == "AUTH_008"
    
    def test_verify_token_non_admin_role(self):
        """Test token verification with non-admin role."""
        # Create token with customer role
        self.mock_admin.role = User.ROLE_CUSTOMER
        token = self.auth_service.generate_token(self.mock_admin)
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.verify_token(token)
        
        assert exc_info.value.message == "Token invalid pentru admin"
        assert exc_info.value.error_code == "AUTH_007"


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.secret_key = 'test-secret-key-for-jwt'
        
        self.mock_admin = Mock()
        self.mock_admin._id = '507f1f77bcf86cd799439011'
        self.mock_admin.phone_number = '+40722123456'
        self.mock_admin.name = 'Test Admin'
        self.mock_admin.role = User.ROLE_ADMIN
    
    @patch('app.services.auth_service.User.find_by_id')
    def test_refresh_access_token_success(self, mock_find_by_id):
        """Test successful token refresh."""
        mock_find_by_id.return_value = self.mock_admin
        
        # Generate refresh token
        refresh_token = self.auth_service.generate_refresh_token(self.mock_admin)
        
        # Refresh access token
        result = self.auth_service.refresh_access_token(refresh_token)
        
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == self.auth_service.TOKEN_EXPIRY_HOURS * 3600
    
    @patch('app.services.auth_service.User.find_by_id')
    def test_refresh_access_token_invalid_refresh_token(self, mock_find_by_id):
        """Test token refresh with access token instead of refresh token."""
        mock_find_by_id.return_value = self.mock_admin
        
        # Generate access token (not refresh token)
        access_token = self.auth_service.generate_token(self.mock_admin)
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.refresh_access_token(access_token)
        
        assert exc_info.value.message == "Token de reînnoire invalid"
        assert exc_info.value.error_code == "AUTH_011"
    
    @patch('app.services.auth_service.User.find_by_id')
    def test_refresh_access_token_user_not_found(self, mock_find_by_id):
        """Test token refresh with non-existent user."""
        mock_find_by_id.return_value = None
        
        refresh_token = self.auth_service.generate_refresh_token(self.mock_admin)
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.refresh_access_token(refresh_token)
        
        assert exc_info.value.message == "Utilizator admin negăsit"
        assert exc_info.value.error_code == "AUTH_012"


class TestPasswordSecurity:
    """Test password hashing and verification."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
    
    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = 'test_password_123'
        hashed = self.auth_service.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Ensure it's actually hashed
        assert hashed.startswith('$2b$')  # bcrypt format
    
    def test_hash_password_too_short(self):
        """Test password hashing with too short password."""
        with pytest.raises(ValidationError) as exc_info:
            self.auth_service.hash_password('short')
        
        assert exc_info.value.message == f"Parola trebuie să aibă cel puțin {self.auth_service.MIN_PASSWORD_LENGTH} caractere"
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        password = 'test_password_123'
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password(password, hashed)
        assert result is True
    
    def test_verify_password_failure(self):
        """Test password verification with wrong password."""
        correct_password = 'correct_password'
        wrong_password = 'wrong_password'
        hashed = self.auth_service.hash_password(correct_password)
        
        result = self.auth_service.verify_password(wrong_password, hashed)
        assert result is False


class TestRateLimiting:
    """Test rate limiting and brute force protection."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.login_attempts = {}
    
    def test_record_failed_attempt(self):
        """Test recording failed login attempts."""
        username = '+40722123456'
        ip_address = '192.168.1.1'
        
        self.auth_service._record_failed_attempt(username, ip_address)
        
        key = f"{username}:{ip_address}"
        assert key in self.auth_service.login_attempts
        assert self.auth_service.login_attempts[key]['count'] == 1
    
    def test_multiple_failed_attempts_lockout(self):
        """Test account lockout after multiple failed attempts."""
        username = '+40722123456'
        ip_address = '192.168.1.1'
        
        # Record maximum allowed failed attempts
        for _ in range(self.auth_service.MAX_LOGIN_ATTEMPTS):
            self.auth_service._record_failed_attempt(username, ip_address)
        
        # Next check should raise rate limit error
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service._check_rate_limit(username, ip_address)
        
        assert "Prea multe încercări de autentificare" in exc_info.value.message
        assert exc_info.value.error_code == "AUTH_015"
    
    def test_clear_failed_attempts(self):
        """Test clearing failed attempts after successful authentication."""
        username = '+40722123456'
        ip_address = '192.168.1.1'
        
        # Record some failed attempts
        self.auth_service._record_failed_attempt(username, ip_address)
        self.auth_service._record_failed_attempt(username, '192.168.1.2')
        
        # Clear attempts
        self.auth_service._clear_failed_attempts(username)
        
        # All attempts for this username should be cleared
        remaining_keys = [key for key in self.auth_service.login_attempts.keys() if key.startswith(username)]
        assert len(remaining_keys) == 0


class TestLogoutFunctionality:
    """Test admin logout functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.secret_key = 'test-secret-key'
        
        self.mock_admin = Mock()
        self.mock_admin._id = '507f1f77bcf86cd799439011'
        self.mock_admin.phone_number = '+40722123456'
        self.mock_admin.name = 'Test Admin'
        self.mock_admin.role = User.ROLE_ADMIN
    
    def test_logout_admin_success(self):
        """Test successful admin logout."""
        token = self.auth_service.generate_token(self.mock_admin)
        
        result = self.auth_service.logout_admin(token)
        
        assert result['success'] is True
        assert result['message'] == 'Deconectare reușită'
    
    def test_logout_admin_invalid_token(self):
        """Test logout with invalid token still succeeds."""
        result = self.auth_service.logout_admin('invalid.token.string')
        
        assert result['success'] is True
        assert result['message'] == 'Deconectare reușită'


class TestInitialAdminCreation:
    """Test initial admin account creation."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
    
    @patch('app.services.auth_service.get_database')
    @patch('app.services.auth_service.User.create')
    def test_create_initial_admin_success(self, mock_user_create, mock_get_database):
        """Test successful initial admin creation."""
        # Mock database to show no existing admin
        mock_db = Mock()
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_db.__getitem__.return_value = mock_collection
        mock_get_database.return_value = mock_db
        
        # Mock user creation
        mock_admin = Mock()
        mock_admin._id = '507f1f77bcf86cd799439011'
        mock_admin.name = 'Initial Admin'
        mock_admin.phone_number = '+40722123456'
        mock_admin.role = User.ROLE_ADMIN
        mock_admin.update.return_value = True
        mock_user_create.return_value = mock_admin
        
        result = self.auth_service.create_initial_admin(
            'Initial Admin',
            '+40722123456',
            'secure_password'
        )
        
        assert result['success'] is True
        assert result['message'] == 'Administrator creat cu succes'
        assert result['admin']['name'] == 'Initial Admin'
        assert result['admin']['role'] == User.ROLE_ADMIN
        
        mock_user_create.assert_called_once_with(
            phone_number='+40722123456',
            name='Initial Admin',
            password='secure_password',
            role=User.ROLE_ADMIN
        )
        mock_admin.update.assert_called_once_with({'is_verified': True})
    
    @patch('app.services.auth_service.get_database')
    def test_create_initial_admin_admin_already_exists(self, mock_get_database):
        """Test initial admin creation when admin already exists."""
        # Mock database to show existing admin
        mock_db = Mock()
        mock_collection = Mock()
        mock_collection.find_one.return_value = {'role': User.ROLE_ADMIN}
        mock_db.__getitem__.return_value = mock_collection
        mock_get_database.return_value = mock_db
        
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.create_initial_admin(
                'Initial Admin',
                '+40722123456',
                'secure_password'
            )
        
        assert exc_info.value.message == "Un administrator există deja în sistem"
        assert exc_info.value.error_code == "AUTH_016"


class TestRomanianLocalization:
    """Test Romanian error messages and localization."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
    
    def test_romanian_validation_messages(self):
        """Test Romanian validation error messages."""
        with pytest.raises(ValidationError) as exc_info:
            self.auth_service.authenticate_admin('', 'password')
        
        assert exc_info.value.message == "Numele de utilizator și parola sunt obligatorii"
    
    def test_romanian_authentication_messages(self):
        """Test Romanian authentication error messages."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.auth_service.verify_token('')
        
        assert exc_info.value.message == "Token de autentificare lipsește"
    
    def test_romanian_password_validation_messages(self):
        """Test Romanian password validation messages."""
        with pytest.raises(ValidationError) as exc_info:
            self.auth_service.hash_password('short')
        
        expected_message = f"Parola trebuie să aibă cel puțin {self.auth_service.MIN_PASSWORD_LENGTH} caractere"
        assert exc_info.value.message == expected_message
    
    @patch('app.services.auth_service.User.find_by_phone')
    def test_romanian_success_messages(self, mock_find_by_phone):
        """Test Romanian success messages."""
        mock_admin = Mock()
        mock_admin._id = '507f1f77bcf86cd799439011'
        mock_admin.phone_number = '+40722123456'
        mock_admin.name = 'Test Admin'
        mock_admin.role = User.ROLE_ADMIN
        mock_admin.is_verified = True
        mock_admin.last_login = None
        mock_admin.verify_password.return_value = True
        mock_admin.update.return_value = True
        
        mock_find_by_phone.return_value = mock_admin
        
        result = self.auth_service.authenticate_admin('+40722123456', 'correct_password')
        
        assert result['message'] == 'Autentificare reușită'
    
    def test_logout_romanian_message(self):
        """Test Romanian logout message."""
        result = self.auth_service.logout_admin('any_token')
        assert result['message'] == 'Deconectare reușită'


# Integration test for complete authentication flow
class TestAuthenticationIntegration:
    """Integration tests for complete authentication flows."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.auth_service = AuthService()
        self.auth_service.secret_key = 'test-secret-key-integration'
    
    @patch('app.services.auth_service.User.find_by_phone')
    @patch('app.services.auth_service.User.find_by_id')
    def test_complete_authentication_flow(self, mock_find_by_id, mock_find_by_phone):
        """Test complete authentication flow from login to token refresh."""
        # Setup mock admin
        mock_admin = Mock()
        mock_admin._id = '507f1f77bcf86cd799439011'
        mock_admin.phone_number = '+40722123456'
        mock_admin.name = 'Test Admin'
        mock_admin.role = User.ROLE_ADMIN
        mock_admin.is_verified = True
        mock_admin.last_login = None
        mock_admin.verify_password.return_value = True
        mock_admin.update.return_value = True
        
        mock_find_by_phone.return_value = mock_admin
        mock_find_by_id.return_value = mock_admin
        
        # Step 1: Authenticate admin
        auth_result = self.auth_service.authenticate_admin('+40722123456', 'correct_password')
        
        assert auth_result['success'] is True
        access_token = auth_result['tokens']['access_token']
        refresh_token = auth_result['tokens']['refresh_token']
        
        # Step 2: Verify access token
        payload = self.auth_service.verify_token(access_token)
        assert payload['user_id'] == '507f1f77bcf86cd799439011'
        
        # Step 3: Refresh token
        refresh_result = self.auth_service.refresh_access_token(refresh_token)
        new_access_token = refresh_result['access_token']
        
        # Step 4: Verify new access token
        new_payload = self.auth_service.verify_token(new_access_token)
        assert new_payload['user_id'] == '507f1f77bcf86cd799439011'
        
        # Step 5: Logout
        logout_result = self.auth_service.logout_admin(new_access_token)
        assert logout_result['success'] is True