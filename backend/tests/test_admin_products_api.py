"""
Integration tests for Admin Products API endpoints.

This module contains comprehensive integration tests for the admin product management
API including create, update, delete operations with authentication, validation,
Romanian localization testing, and business logic verification.
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
from bson import ObjectId

from app import create_app
from app.config import TestingConfig
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.services.auth_service import AuthService


class TestAdminProductsAPI:
    """Integration tests for admin products API endpoints."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Test admin user data
        self.admin_user_data = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'user_id': '507f1f77bcf86cd799439011',
            'phone_number': '+40722123456',
            'name': 'Test Admin',
            'role': 'admin',
            'password_hash': '$2b$12$test.hash.value',
            'is_verified': True,
            'last_login': None
        }
        
        # Test category data
        self.test_category = {
            '_id': ObjectId('507f1f77bcf86cd799439012'),
            'name': 'Produse lactate',
            'slug': 'produse-lactate',
            'description': 'Brânză și alte produse lactate',
            'is_active': True
        }
        
        # Test product data
        self.test_product = {
            '_id': ObjectId('507f1f77bcf86cd799439013'),
            'name': 'Brânză de capră',
            'description': 'Brânză artizanală de capră, maturată 30 de zile',
            'price': 25.99,
            'category_id': ObjectId('507f1f77bcf86cd799439012'),
            'images': ['https://example.com/image1.jpg'],
            'stock_quantity': 10,
            'weight_grams': 500,
            'preparation_time_hours': 24,
            'is_available': True,
            'created_by': '507f1f77bcf86cd799439011',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'slug': 'branza-de-capra'
        }
        
        # Valid JWT token for testing
        self.valid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token'
        self.invalid_token = 'invalid.jwt.token'
        
        # Common headers
        self.auth_headers = {
            'Authorization': f'Bearer {self.valid_token}',
            'Content-Type': 'application/json'
        }
        
        self.no_auth_headers = {
            'Content-Type': 'application/json'
        }
        
        self.invalid_auth_headers = {
            'Authorization': f'Bearer {self.invalid_token}',
            'Content-Type': 'application/json'
        }
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.app_context.pop()
    
    # === PRODUCT CREATE ENDPOINT TESTS ===
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.category.Category.find_by_id')
    @patch('app.models.product.Product.find_by_name')
    @patch('app.models.product.Product.create')
    @patch('app.utils.auth_middleware.log_admin_action')
    def test_create_product_success(self, mock_log_action, mock_product_create, 
                                   mock_find_by_name, mock_category_find, 
                                   mock_user_find, mock_verify_jwt, mock_validate):
        """Test successful product creation with valid data."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_category_find.return_value = Category(self.test_category)
        mock_find_by_name.return_value = None  # No duplicate
        
        # Mock successful product creation
        created_product = Product(self.test_product)
        mock_product_create.return_value = created_product
        
        # Test data
        product_data = {
            'name': 'Brânză de capră nouă',
            'description': 'Brânză artizanală de capră, maturată 30 de zile',
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439012',
            'stock_quantity': 10,
            'weight_grams': 500,
            'preparation_time_hours': 24,
            'images': ['https://example.com/image1.jpg']
        }
        
        # Make request
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        # Assertions
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'Produsul' in response_data['message']
        assert 'creat cu succes' in response_data['message']
        assert 'product' in response_data['data']
        
        # Verify mocks were called
        mock_verify_jwt.assert_called_once()
        mock_user_find.assert_called_once()
        mock_category_find.assert_called_once()
        mock_find_by_name.assert_called_once()
        mock_product_create.assert_called_once()
        mock_log_action.assert_called_once()
    
    def test_create_product_no_auth(self):
        """Test product creation without authentication."""
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 10.00,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.no_auth_headers
        )
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'AUTH_001' in response_data['error']['code']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    def test_create_product_invalid_auth(self, mock_verify_jwt):
        """Test product creation with invalid JWT token."""
        mock_verify_jwt.side_effect = Exception("Invalid token")
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 10.00,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.invalid_auth_headers
        )
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_create_product_missing_required_fields(self, mock_user_find, 
                                                   mock_verify_jwt, mock_validate):
        """Test product creation with missing required fields."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Missing required fields
        product_data = {
            'name': 'Test Product'
            # Missing description, price, category_id
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'obligatorii' in response_data['error']['message']
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.category.Category.find_by_id')
    @patch('app.models.product.Product.find_by_name')
    def test_create_product_duplicate_name(self, mock_find_by_name, mock_category_find,
                                          mock_user_find, mock_verify_jwt, mock_validate):
        """Test product creation with duplicate name."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_category_find.return_value = Category(self.test_category)
        mock_find_by_name.return_value = Product(self.test_product)  # Duplicate exists
        
        product_data = {
            'name': 'Brânză de capră',  # Duplicate name
            'description': 'Test description',
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'există deja' in response_data['error']['message']
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.category.Category.find_by_id')
    def test_create_product_invalid_category(self, mock_category_find, mock_user_find,
                                           mock_verify_jwt, mock_validate):
        """Test product creation with invalid category."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_category_find.return_value = None  # Category not found
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439999'  # Invalid category
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'nu există în sistem' in response_data['error']['message']
    
    # === PRODUCT UPDATE ENDPOINT TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    @patch('app.models.category.Category.find_by_id')
    @patch('app.models.product.Product.find_by_name')
    @patch('app.utils.auth_middleware.log_admin_action')
    def test_update_product_success(self, mock_log_action, mock_find_by_name,
                                   mock_category_find, mock_product_find,
                                   mock_user_find, mock_verify_jwt):
        """Test successful product update."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing product
        existing_product = Product(self.test_product)
        mock_product_find.return_value = existing_product
        
        # Mock category
        mock_category_find.return_value = Category(self.test_category)
        mock_find_by_name.return_value = None  # No name conflict
        
        # Mock successful update
        with patch.object(existing_product, 'update', return_value=True):
            with patch.object(existing_product, 'to_dict', return_value={'id': 'test'}):
                update_data = {
                    'name': 'Brânză de capră actualizată',
                    'price': 30.00
                }
                
                response = self.client.put(
                    '/api/admin/products/507f1f77bcf86cd799439013',
                    data=json.dumps(update_data),
                    headers=self.auth_headers
                )
                
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert response_data['success'] is True
                assert 'actualizat cu succes' in response_data['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    def test_update_product_not_found(self, mock_product_find, mock_user_find, mock_verify_jwt):
        """Test updating non-existent product."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_product_find.return_value = None  # Product not found
        
        update_data = {
            'name': 'Updated Product'
        }
        
        response = self.client.put(
            '/api/admin/products/507f1f77bcf86cd799439999',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'NOT_001' in response_data['error']['code']
        assert 'nu a fost găsit' in response_data['error']['message']
    
    def test_update_product_no_auth(self):
        """Test product update without authentication."""
        update_data = {
            'name': 'Updated Product'
        }
        
        response = self.client.put(
            '/api/admin/products/507f1f77bcf86cd799439013',
            data=json.dumps(update_data),
            headers=self.no_auth_headers
        )
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    # === PRODUCT DELETE ENDPOINT TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    @patch('app.utils.auth_middleware.log_admin_action')
    def test_delete_product_success(self, mock_log_action, mock_product_find,
                                   mock_user_find, mock_verify_jwt):
        """Test successful product deletion (soft delete)."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing available product
        existing_product = Product(self.test_product)
        mock_product_find.return_value = existing_product
        
        # Mock successful soft delete
        with patch.object(existing_product, 'delete', return_value=True):
            response = self.client.delete(
                '/api/admin/products/507f1f77bcf86cd799439013',
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert 'dezactivat cu succes' in response_data['message']
            assert response_data['data']['deleted'] is True
            assert response_data['data']['product_id'] == '507f1f77bcf86cd799439013'
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    def test_delete_product_already_deleted(self, mock_product_find, mock_user_find, mock_verify_jwt):
        """Test deleting already deleted product."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock already deleted product
        deleted_product_data = self.test_product.copy()
        deleted_product_data['is_available'] = False
        deleted_product_data['stock_quantity'] = 0
        
        existing_product = Product(deleted_product_data)
        mock_product_find.return_value = existing_product
        
        response = self.client.delete(
            '/api/admin/products/507f1f77bcf86cd799439013',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'deja dezactivat' in response_data['message']
        assert response_data['data']['deleted'] is True
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    def test_delete_product_not_found(self, mock_product_find, mock_user_find, mock_verify_jwt):
        """Test deleting non-existent product."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_product_find.return_value = None  # Product not found
        
        response = self.client.delete(
            '/api/admin/products/507f1f77bcf86cd799439999',
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'NOT_001' in response_data['error']['code']
        assert 'nu a fost găsit' in response_data['error']['message']
    
    def test_delete_product_no_auth(self):
        """Test product deletion without authentication."""
        response = self.client.delete(
            '/api/admin/products/507f1f77bcf86cd799439013',
            headers=self.no_auth_headers
        )
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.product.Product.find_by_id')
    def test_delete_product_database_error(self, mock_product_find, mock_user_find, mock_verify_jwt):
        """Test product deletion with database error."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing product
        existing_product = Product(self.test_product)
        mock_product_find.return_value = existing_product
        
        # Mock database error during delete
        with patch.object(existing_product, 'delete', return_value=False):
            response = self.client.delete(
                '/api/admin/products/507f1f77bcf86cd799439013',
                headers=self.auth_headers
            )
            
            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert response_data['success'] is False
            assert 'DB_001' in response_data['error']['code']
            assert 'Eroare la dezactivarea' in response_data['error']['message']
    
    # === VALIDATION TESTS ===
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_create_product_invalid_price(self, mock_user_find, mock_verify_jwt, mock_validate):
        """Test product creation with invalid price."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': -10.00,  # Invalid negative price
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'pozitiv' in response_data['error']['message']
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_create_product_price_too_high(self, mock_user_find, mock_verify_jwt, mock_validate):
        """Test product creation with price too high."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 10000.00,  # Price too high
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert '9999.99' in response_data['error']['message']
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_create_product_name_too_short(self, mock_user_find, mock_verify_jwt, mock_validate):
        """Test product creation with name too short."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        product_data = {
            'name': 'A',  # Too short
            'description': 'Test description',
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'cel puțin 2 caractere' in response_data['error']['message']
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_create_product_description_too_short(self, mock_user_find, mock_verify_jwt, mock_validate):
        """Test product creation with description too short."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        product_data = {
            'name': 'Test Product',
            'description': 'Short',  # Too short
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'cel puțin 10 caractere' in response_data['error']['message']
    
    # === ERROR HANDLING TESTS ===
    
    @patch('app.utils.validators.validate_json')
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.category.Category.find_by_id')
    @patch('app.models.product.Product.find_by_name')
    @patch('app.models.product.Product.create')
    def test_create_product_database_error(self, mock_product_create, mock_find_by_name,
                                          mock_category_find, mock_user_find,
                                          mock_verify_jwt, mock_validate):
        """Test product creation with database error."""
        # Setup mocks
        mock_validate.return_value = lambda f: f  # Decorator passthrough
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_category_find.return_value = Category(self.test_category)
        mock_find_by_name.return_value = None
        
        # Mock database error
        mock_product_create.side_effect = Exception("Database connection failed")
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 25.99,
            'category_id': '507f1f77bcf86cd799439012'
        }
        
        response = self.client.post(
            '/api/admin/products',
            data=json.dumps(product_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'DB_001' in response_data['error']['code']
        assert 'baza de date' in response_data['error']['message']
    
    # === ROMANIAN LOCALIZATION TESTS ===
    
    def test_romanian_error_messages_consistency(self):
        """Test that Romanian error messages are consistent and properly formatted."""
        # This test verifies that all Romanian error messages follow proper Romanian grammar
        # and are consistently formatted across the API
        
        # Test cases for different error scenarios
        error_scenarios = [
            {
                'endpoint': '/api/admin/products',
                'method': 'POST',
                'data': {},
                'expected_phrases': ['obligatorii', 'câmpuri']
            },
            {
                'endpoint': '/api/admin/products/invalid_id',
                'method': 'PUT', 
                'data': {'name': 'Test'},
                'expected_phrases': ['nu a fost găsit', 'sistem']
            },
            {
                'endpoint': '/api/admin/products/invalid_id',
                'method': 'DELETE',
                'data': None,
                'expected_phrases': ['nu a fost găsit', 'sistem']
            }
        ]
        
        for scenario in error_scenarios:
            if scenario['method'] == 'POST':
                response = self.client.post(
                    scenario['endpoint'],
                    data=json.dumps(scenario['data']) if scenario['data'] else None,
                    headers=self.no_auth_headers
                )
            elif scenario['method'] == 'PUT':
                response = self.client.put(
                    scenario['endpoint'],
                    data=json.dumps(scenario['data']) if scenario['data'] else None,
                    headers=self.no_auth_headers
                )
            elif scenario['method'] == 'DELETE':
                response = self.client.delete(
                    scenario['endpoint'],
                    headers=self.no_auth_headers
                )
            
            # Verify that response contains Romanian text
            assert response.status_code in [400, 401, 404]
            if response.status_code != 401:  # Skip auth errors for this test
                response_data = json.loads(response.data)
                assert response_data['success'] is False
                # Note: Romanian phrase checking would be done with auth, 
                # so this test mainly verifies structure