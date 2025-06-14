"""
Integration tests for Admin Authentication API endpoints.

This module contains comprehensive integration tests for the admin authentication
API including login, logout, token refresh, token verification, and admin setup
endpoints with request/response validation and Romanian localization testing.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from flask import Flask

from app import create_app
from app.config import TestingConfig
from app.models.user import User
from app.services.auth_service import AuthService


class TestAdminAuthAPI:
    """Integration tests for admin authentication API endpoints."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Test admin user data
        self.admin_credentials = {
            'username': '+40722123456',
            'password': 'admin_password_123'
        }
        
        self.admin_user_data = {
            '_id': '507f1f77bcf86cd799439011',
            'phone_number': '+40722123456',
            'name': 'Test Admin',
            'role': 'admin',
            'password_hash': '$2b$12$test.hash.value',
            'is_verified': True,
            'last_login': None
        }
        
        # Valid JWT token for testing
        self.valid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token'
        self.expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token'
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    def create_auth_headers(self, token=None):
        """Create Authorization headers for requests."""
        if token is None:
            token = self.valid_token
        return {'Authorization': f'Bearer {token}'}


class TestAdminLogin:
    """Test admin login endpoint functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.authenticate_admin')
    def test_admin_login_success(self, mock_authenticate):
        """Test successful admin login with valid credentials."""
        # Mock successful authentication response
        mock_authenticate.return_value = {
            'success': True,
            'message': 'Autentificare reușită',
            'user': {
                'id': '507f1f77bcf86cd799439011',
                'name': 'Test Admin',
                'phone_number': '+40722123456',
                'role': 'admin',
                'last_login': '2025-01-14T22:40:00Z'
            },
            'tokens': {
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'token_type': 'Bearer',
                'expires_in': 28800
            }
        }
        
        # Test successful login
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '+40722123456',
                'password': 'admin_password_123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Autentificare reușită'
        assert 'user' in data['data']
        assert 'tokens' in data['data']
        assert data['data']['user']['role'] == 'admin'
        assert data['data']['tokens']['token_type'] == 'Bearer'
        
        # Verify AuthService was called with correct parameters
        mock_authenticate.assert_called_once()
        args, kwargs = mock_authenticate.call_args
        assert kwargs['username'] == '+40722123456'
        assert kwargs['password'] == 'admin_password_123'
        assert 'ip_address' in kwargs
    
    def test_admin_login_missing_json(self):
        """Test admin login with missing JSON content type."""
        response = self.client.post('/api/auth/admin/login')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert data['error']['message'] == 'Cererea trebuie să fie în format JSON'
    
    def test_admin_login_invalid_json(self):
        """Test admin login with invalid JSON payload."""
        response = self.client.post(
            '/api/auth/admin/login',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert data['error']['message'] == 'Date JSON invalide sau lipsă'
    
    def test_admin_login_missing_fields(self):
        """Test admin login with missing required fields."""
        # Missing username
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({'password': 'password123'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert data['error']['message'] == 'Numele de utilizator și parola sunt obligatorii'
        
        # Missing password
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({'username': '+40722123456'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Numele de utilizator și parola sunt obligatorii'
    
    def test_admin_login_empty_fields(self):
        """Test admin login with empty field values."""
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '   ',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['message'] == 'Numele de utilizator și parola nu pot fi goale'
    
    @patch('app.routes.auth.admin_auth_service.authenticate_admin')
    def test_admin_login_invalid_credentials(self, mock_authenticate):
        """Test admin login with invalid credentials."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock authentication failure
        mock_authenticate.side_effect = AuthenticationError(
            "Datele de autentificare sunt incorecte",
            "AUTH_001"
        )
        
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '+40722123456',
                'password': 'wrong_password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_001'
        assert data['error']['message'] == 'Datele de autentificare sunt incorecte'
    
    @patch('app.routes.auth.admin_auth_service.authenticate_admin')
    def test_admin_login_non_admin_role(self, mock_authenticate):
        """Test admin login with non-admin user."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock non-admin role error
        mock_authenticate.side_effect = AuthenticationError(
            "Acces interzis. Doar administratorii pot accesa acest sistem",
            "AUTH_002"
        )
        
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '+40722123456',
                'password': 'user_password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_002'
        assert data['error']['message'] == 'Acces interzis. Doar administratorii pot accesa acest sistem'
    
    @patch('app.routes.auth.admin_auth_service.authenticate_admin')
    def test_admin_login_rate_limited(self, mock_authenticate):
        """Test admin login with rate limiting."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock rate limiting error
        mock_authenticate.side_effect = AuthenticationError(
            "Prea multe încercări de autentificare. Încercați din nou în 15 minute",
            "AUTH_015"
        )
        
        response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '+40722123456',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_015'
        assert 'Prea multe încercări' in data['error']['message']


class TestAdminLogout:
    """Test admin logout endpoint functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.logout_admin')
    def test_admin_logout_success(self, mock_logout):
        """Test successful admin logout."""
        # Mock successful logout response
        mock_logout.return_value = {
            'success': True,
            'message': 'Deconectare reușită'
        }
        
        response = self.client.post(
            '/api/auth/admin/logout',
            headers={'Authorization': 'Bearer test_token_123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Deconectare reușită'
        
        # Verify logout was called with token
        mock_logout.assert_called_once_with('test_token_123')
    
    def test_admin_logout_missing_token(self):
        """Test admin logout without Authorization header."""
        response = self.client.post('/api/auth/admin/logout')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_006'
        assert data['error']['message'] == 'Token de autentificare lipsește din header'
    
    def test_admin_logout_invalid_header_format(self):
        """Test admin logout with invalid Authorization header format."""
        response = self.client.post(
            '/api/auth/admin/logout',
            headers={'Authorization': 'Invalid token_123'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_009'
        assert data['error']['message'] == 'Format token invalid. Utilizați \'Bearer token\''
    
    def test_admin_logout_always_succeeds(self):
        """Test admin logout always returns success even on error."""
        # Even with invalid token, logout should succeed for security
        response = self.client.post(
            '/api/auth/admin/logout',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        # Should still return 200 for security reasons
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Deconectare reușită'


class TestTokenRefresh:
    """Test token refresh endpoint functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.refresh_access_token')
    def test_token_refresh_success(self, mock_refresh):
        """Test successful token refresh."""
        # Mock successful refresh response
        mock_refresh.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'token_type': 'Bearer',
            'expires_in': 28800
        }
        
        response = self.client.post(
            '/api/auth/admin/refresh',
            data=json.dumps({
                'refresh_token': 'valid_refresh_token'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Token reînnoit cu succes'
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['token_type'] == 'Bearer'
        
        # Verify refresh was called with correct token
        mock_refresh.assert_called_once_with('valid_refresh_token')
    
    def test_token_refresh_missing_json(self):
        """Test token refresh with missing JSON content type."""
        response = self.client.post('/api/auth/admin/refresh')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Cererea trebuie să fie în format JSON'
    
    def test_token_refresh_missing_token(self):
        """Test token refresh with missing refresh token."""
        response = self.client.post(
            '/api/auth/admin/refresh',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Token de reînnoire este obligatoriu'
    
    def test_token_refresh_empty_token(self):
        """Test token refresh with empty refresh token."""
        response = self.client.post(
            '/api/auth/admin/refresh',
            data=json.dumps({'refresh_token': '   '}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Token de reînnoire nu poate fi gol'
    
    @patch('app.routes.auth.admin_auth_service.refresh_access_token')
    def test_token_refresh_invalid_token(self, mock_refresh):
        """Test token refresh with invalid refresh token."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock invalid refresh token error
        mock_refresh.side_effect = AuthenticationError(
            "Token de reînnoire invalid",
            "AUTH_011"
        )
        
        response = self.client.post(
            '/api/auth/admin/refresh',
            data=json.dumps({
                'refresh_token': 'invalid_refresh_token'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_011'
        assert data['error']['message'] == 'Token de reînnoire invalid'


class TestTokenVerification:
    """Test token verification endpoint functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.verify_token')
    def test_token_verification_success(self, mock_verify):
        """Test successful token verification."""
        # Mock successful verification response
        mock_verify.return_value = {
            'user_id': '507f1f77bcf86cd799439011',
            'phone_number': '+40722123456',
            'name': 'Test Admin',
            'role': 'admin',
            'iat': 1705267200,
            'exp': 1705296000
        }
        
        response = self.client.post(
            '/api/auth/admin/verify',
            headers={'Authorization': 'Bearer valid_token_123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Token valid'
        assert data['data']['valid'] is True
        assert 'user' in data['data']
        assert data['data']['user']['role'] == 'admin'
        
        # Verify token was verified
        mock_verify.assert_called_once_with('valid_token_123')
    
    def test_token_verification_missing_header(self):
        """Test token verification without Authorization header."""
        response = self.client.post('/api/auth/admin/verify')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['message'] == 'Token de autentificare lipsește din header'
    
    def test_token_verification_invalid_format(self):
        """Test token verification with invalid header format."""
        response = self.client.post(
            '/api/auth/admin/verify',
            headers={'Authorization': 'Token invalid_format'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['message'] == 'Format token invalid. Utilizați \'Bearer token\''
    
    @patch('app.routes.auth.admin_auth_service.verify_token')
    def test_token_verification_expired_token(self, mock_verify):
        """Test token verification with expired token."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock expired token error
        mock_verify.side_effect = AuthenticationError(
            "Token-ul de autentificare a expirat",
            "AUTH_008"
        )
        
        response = self.client.post(
            '/api/auth/admin/verify',
            headers={'Authorization': 'Bearer expired_token'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_008'
        assert data['error']['message'] == 'Token-ul de autentificare a expirat'


class TestAdminSetup:
    """Test initial admin setup endpoint functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.create_initial_admin')
    def test_admin_setup_success(self, mock_create):
        """Test successful initial admin creation."""
        # Mock successful admin creation response
        mock_create.return_value = {
            'success': True,
            'message': 'Administrator creat cu succes',
            'admin': {
                'id': '507f1f77bcf86cd799439011',
                'name': 'Initial Admin',
                'phone_number': '+40722123456',
                'role': 'admin'
            }
        }
        
        response = self.client.post(
            '/api/auth/admin/setup',
            data=json.dumps({
                'name': 'Initial Admin',
                'phone_number': '+40722123456',
                'password': 'secure_admin_password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Administrator creat cu succes'
        assert 'admin' in data['data']
        assert data['data']['admin']['role'] == 'admin'
        
        # Verify admin creation was called
        mock_create.assert_called_once_with(
            name='Initial Admin',
            phone_number='+40722123456',
            password='secure_admin_password'
        )
    
    def test_admin_setup_missing_fields(self):
        """Test admin setup with missing required fields."""
        response = self.client.post(
            '/api/auth/admin/setup',
            data=json.dumps({
                'name': 'Admin Name'
                # Missing phone_number and password
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Numele, numărul de telefon și parola sunt obligatorii'
    
    def test_admin_setup_empty_fields(self):
        """Test admin setup with empty field values."""
        response = self.client.post(
            '/api/auth/admin/setup',
            data=json.dumps({
                'name': '   ',
                'phone_number': '+40722123456',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error']['message'] == 'Numele, numărul de telefon și parola nu pot fi goale'
    
    @patch('app.routes.auth.admin_auth_service.create_initial_admin')
    def test_admin_setup_admin_exists(self, mock_create):
        """Test admin setup when admin already exists."""
        from app.utils.error_handlers import AuthenticationError
        
        # Mock admin already exists error
        mock_create.side_effect = AuthenticationError(
            "Un administrator există deja în sistem",
            "AUTH_016"
        )
        
        response = self.client.post(
            '/api/auth/admin/setup',
            data=json.dumps({
                'name': 'Second Admin',
                'phone_number': '+40722123457',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error']['code'] == 'AUTH_016'
        assert data['error']['message'] == 'Un administrator există deja în sistem'


class TestCompleteAuthenticationFlow:
    """Test complete authentication flows and edge cases."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    @patch('app.routes.auth.admin_auth_service.authenticate_admin')
    @patch('app.routes.auth.admin_auth_service.verify_token')
    @patch('app.routes.auth.admin_auth_service.refresh_access_token')
    @patch('app.routes.auth.admin_auth_service.logout_admin')
    def test_complete_authentication_cycle(self, mock_logout, mock_refresh, mock_verify, mock_authenticate):
        """Test complete authentication cycle: login -> verify -> refresh -> logout."""
        
        # Mock login response
        mock_authenticate.return_value = {
            'success': True,
            'message': 'Autentificare reușită',
            'user': {
                'id': '507f1f77bcf86cd799439011',
                'name': 'Test Admin',
                'phone_number': '+40722123456',
                'role': 'admin'
            },
            'tokens': {
                'access_token': 'access_token_123',
                'refresh_token': 'refresh_token_123',
                'token_type': 'Bearer',
                'expires_in': 28800
            }
        }
        
        # Mock token verification
        mock_verify.return_value = {
            'user_id': '507f1f77bcf86cd799439011',
            'phone_number': '+40722123456',
            'name': 'Test Admin',
            'role': 'admin'
        }
        
        # Mock token refresh
        mock_refresh.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'token_type': 'Bearer',
            'expires_in': 28800
        }
        
        # Mock logout
        mock_logout.return_value = {
            'success': True,
            'message': 'Deconectare reușită'
        }
        
        # Step 1: Login
        login_response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': '+40722123456',
                'password': 'admin_password'
            }),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['tokens']['access_token']
        refresh_token = login_data['data']['tokens']['refresh_token']
        
        # Step 2: Verify token
        verify_response = self.client.post(
            '/api/auth/admin/verify',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert verify_response.status_code == 200
        verify_data = json.loads(verify_response.data)
        assert verify_data['data']['valid'] is True
        
        # Step 3: Refresh token
        refresh_response = self.client.post(
            '/api/auth/admin/refresh',
            data=json.dumps({'refresh_token': refresh_token}),
            content_type='application/json'
        )
        
        assert refresh_response.status_code == 200
        refresh_data = json.loads(refresh_response.data)
        new_access_token = refresh_data['data']['access_token']
        
        # Step 4: Logout
        logout_response = self.client.post(
            '/api/auth/admin/logout',
            headers={'Authorization': f'Bearer {new_access_token}'}
        )
        
        assert logout_response.status_code == 200
        logout_data = json.loads(logout_response.data)
        assert logout_data['success'] is True
    
    def test_api_response_format_consistency(self):
        """Test that all endpoints return consistent API response format."""
        # Test login endpoint response format
        login_response = self.client.post(
            '/api/auth/admin/login',
            data=json.dumps({
                'username': 'invalid',
                'password': 'invalid'
            }),
            content_type='application/json'
        )
        
        login_data = json.loads(login_response.data)
        assert 'success' in login_data
        assert 'error' in login_data or 'data' in login_data
        if 'error' in login_data:
            assert 'code' in login_data['error']
            assert 'message' in login_data['error']
    
    def test_romanian_error_messages_consistency(self):
        """Test that Romanian error messages are consistent across endpoints."""
        # Test various endpoints for Romanian error messages
        endpoints_and_errors = [
            ('/api/auth/admin/login', {}, 'Cererea trebuie să fie în format JSON'),
            ('/api/auth/admin/logout', {}, 'Token de autentificare lipsește din header'),
            ('/api/auth/admin/refresh', {}, 'Cererea trebuie să fie în format JSON'),
            ('/api/auth/admin/verify', {}, 'Token de autentificare lipsește din header'),
            ('/api/auth/admin/setup', {}, 'Cererea trebuie să fie în format JSON')
        ]
        
        for endpoint, headers, expected_message in endpoints_and_errors:
            response = self.client.post(endpoint, headers=headers)
            data = json.loads(response.data)
            
            # Verify Romanian error message format
            assert 'error' in data
            assert 'message' in data['error']
            # Check that message is in Romanian (contains Romanian characters or specific terms)
            message = data['error']['message']
            romanian_indicators = ['trebuie', 'lipsește', 'obligatorii', 'invalid', 'format']
            assert any(indicator in message for indicator in romanian_indicators)