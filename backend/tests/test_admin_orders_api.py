"""
Integration tests for Admin Orders API endpoints.

This module contains comprehensive integration tests for the admin order management
API including order listing, status updates, authentication, validation,
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
from app.models.order import Order
from app.models.user import User
from app.services.auth_service import AuthService


class TestAdminOrdersAPI:
    """Integration tests for admin orders API endpoints."""
    
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
        
        # Test order data
        self.test_orders = [
            {
                '_id': ObjectId('507f1f77bcf86cd799439020'),
                'order_number': 'ORD-2025-001234',
                'customer_name': 'Ion Popescu',
                'customer_phone': '+40722111111',
                'customer_email': 'ion@example.com',
                'status': 'pending',
                'total': 125.50,
                'items': [
                    {
                        'product_id': ObjectId('507f1f77bcf86cd799439030'),
                        'name': 'Brânză de capră',
                        'price': 25.99,
                        'quantity': 2
                    }
                ],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'special_instructions': 'Livrare după ora 18:00'
            },
            {
                '_id': ObjectId('507f1f77bcf86cd799439021'),
                'order_number': 'ORD-2025-001235',
                'customer_name': 'Maria Ionescu',
                'customer_phone': '+40722222222',
                'status': 'confirmed',
                'total': 89.25,
                'items': [
                    {
                        'product_id': ObjectId('507f1f77bcf86cd799439031'),
                        'name': 'Miere de salcâm',
                        'price': 15.50,
                        'quantity': 3
                    }
                ],
                'created_at': datetime.utcnow() - timedelta(days=1),
                'updated_at': datetime.utcnow() - timedelta(hours=2)
            },
            {
                '_id': ObjectId('507f1f77bcf86cd799439022'),
                'order_number': 'ORD-2025-001236',
                'customer_name': 'Andrei Georgescu',
                'customer_phone': '+40722333333',
                'status': 'completed',
                'total': 75.00,
                'items': [],
                'created_at': datetime.utcnow() - timedelta(days=2),
                'updated_at': datetime.utcnow() - timedelta(hours=1)
            }
        ]
        
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
    
    # === AUTHENTICATION TESTS ===
    
    def test_get_orders_no_auth(self):
        """Test order listing without authentication."""
        response = self.client.get('/api/admin/orders', headers=self.no_auth_headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'AUTH_001' in response_data['error']['code']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    def test_get_orders_invalid_auth(self, mock_verify_jwt):
        """Test order listing with invalid JWT token."""
        mock_verify_jwt.side_effect = Exception("Invalid token")
        
        response = self.client.get('/api/admin/orders', headers=self.invalid_auth_headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_update_order_status_no_auth(self):
        """Test order status update without authentication."""
        update_data = {'status': 'confirmed'}
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439020/status',
            data=json.dumps(update_data),
            headers=self.no_auth_headers
        )
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    # === ORDER LISTING TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    @patch('app.utils.auth_middleware.log_admin_action')
    def test_get_orders_success(self, mock_log_action, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test successful order listing with default parameters."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock database collection
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock aggregation result
        mock_collection.aggregate.return_value = [{
            'orders': self.test_orders,
            'total_count': [{'count': 3}],
            'statistics': [{
                'total_revenue': 289.75,
                'avg_order_value': 96.58,
                'status_counts': ['pending', 'confirmed', 'completed']
            }]
        }]
        
        response = self.client.get('/api/admin/orders', headers=self.auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'Au fost găsite' in response_data['message']
        assert 'orders' in response_data['data']
        assert 'pagination' in response_data['data']
        assert 'statistics' in response_data['data']
        
        # Verify mocks were called
        mock_verify_jwt.assert_called_once()
        mock_log_action.assert_called_once()
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    def test_get_orders_with_filters(self, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test order listing with various filters."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock empty result for filtered query
        mock_collection.aggregate.return_value = [{
            'orders': [],
            'total_count': [],
            'statistics': []
        }]
        
        # Test with status filter
        response = self.client.get(
            '/api/admin/orders?status=confirmed&page=1&limit=10',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['filters']['status'] == 'confirmed'
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_get_orders_invalid_status_filter(self, mock_user_find, mock_verify_jwt):
        """Test order listing with invalid status filter."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        response = self.client.get(
            '/api/admin/orders?status=invalid_status',
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'Status invalid' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_get_orders_invalid_date_filter(self, mock_user_find, mock_verify_jwt):
        """Test order listing with invalid date format."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        response = self.client.get(
            '/api/admin/orders?start_date=invalid-date',
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'Data de început invalidă' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_get_orders_invalid_amount_filter(self, mock_user_find, mock_verify_jwt):
        """Test order listing with invalid amount filter."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        response = self.client.get(
            '/api/admin/orders?min_total=-10',
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'nu poate fi negativă' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_get_orders_min_max_total_validation(self, mock_user_find, mock_verify_jwt):
        """Test order listing with min_total > max_total."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        response = self.client.get(
            '/api/admin/orders?min_total=100&max_total=50',
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'nu poate fi mai mare decât' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    def test_get_orders_database_error(self, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test order listing with database error."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock database error
        mock_get_db.side_effect = Exception("Database connection failed")
        
        response = self.client.get('/api/admin/orders', headers=self.auth_headers)
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'DB_001' in response_data['error']['code']
        assert 'Eroare la încărcarea comenzilor' in response_data['error']['message']
    
    # === ORDER STATUS UPDATE TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    @patch('app.services.sms_service.get_sms_service')
    @patch('app.utils.auth_middleware.log_admin_action')
    def test_update_order_status_success(self, mock_log_action, mock_sms_service,
                                        mock_order_find, mock_user_find, mock_verify_jwt):
        """Test successful order status update."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing order
        order_data = self.test_orders[0].copy()
        order_data['status'] = 'pending'
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        # Mock successful status update
        with patch.object(existing_order, 'update_status', return_value=True):
            # Mock SMS service
            mock_sms = Mock()
            mock_sms_service.return_value = mock_sms
            
            update_data = {'status': 'confirmed'}
            
            response = self.client.put(
                '/api/admin/orders/507f1f77bcf86cd799439020/status',
                data=json.dumps(update_data),
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert 'actualizat' in response_data['message']
            assert response_data['data']['old_status'] == 'pending'
            assert response_data['data']['new_status'] == 'confirmed'
            assert response_data['data']['updated'] is True
            
            # Verify SMS was sent
            mock_sms.send_notification.assert_called_once()
            
            # Verify audit logging
            mock_log_action.assert_called_once()
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_update_order_status_missing_data(self, mock_user_find, mock_verify_jwt):
        """Test order status update with missing status data."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Empty request data
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439020/status',
            data=json.dumps({}),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'obligatoriu' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_update_order_status_empty_status(self, mock_user_find, mock_verify_jwt):
        """Test order status update with empty status value."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        update_data = {'status': '   '}  # Whitespace only
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439020/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'nu poate fi gol' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_update_order_status_invalid_status(self, mock_user_find, mock_verify_jwt):
        """Test order status update with invalid status value."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        update_data = {'status': 'invalid_status'}
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439020/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'Status invalid' in response_data['error']['message']
        assert 'în așteptare' in response_data['error']['message']  # Romanian status names
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    def test_update_order_status_not_found(self, mock_order_find, mock_user_find, mock_verify_jwt):
        """Test order status update for non-existent order."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        mock_order_find.return_value = None  # Order not found
        
        update_data = {'status': 'confirmed'}
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439999/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'NOT_001' in response_data['error']['code']
        assert 'nu a fost găsită' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    def test_update_order_status_same_status(self, mock_order_find, mock_user_find, mock_verify_jwt):
        """Test order status update with same status."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock order with confirmed status
        order_data = self.test_orders[1].copy()
        order_data['status'] = 'confirmed'
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        update_data = {'status': 'confirmed'}  # Same as current
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439021/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'deja în statusul' in response_data['message']
        assert response_data['data']['changed'] is False
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    def test_update_order_status_invalid_transition(self, mock_order_find, mock_user_find, mock_verify_jwt):
        """Test order status update with invalid transition."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock completed order (final state)
        order_data = self.test_orders[2].copy()
        order_data['status'] = 'completed'
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        update_data = {'status': 'pending'}  # Invalid transition
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439022/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VAL_001' in response_data['error']['code']
        assert 'nu mai poate fi modificată' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    def test_update_order_status_database_error(self, mock_order_find, mock_user_find, mock_verify_jwt):
        """Test order status update with database error."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing order
        order_data = self.test_orders[0].copy()
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        # Mock database error during update
        with patch.object(existing_order, 'update_status', return_value=False):
            update_data = {'status': 'confirmed'}
            
            response = self.client.put(
                '/api/admin/orders/507f1f77bcf86cd799439020/status',
                data=json.dumps(update_data),
                headers=self.auth_headers
            )
            
            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert response_data['success'] is False
            assert 'DB_001' in response_data['error']['code']
            assert 'Eroare la actualizarea' in response_data['error']['message']
    
    # === SMS NOTIFICATION TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    @patch('app.services.sms_service.get_sms_service')
    def test_update_order_status_sms_success(self, mock_sms_service, mock_order_find, 
                                           mock_user_find, mock_verify_jwt):
        """Test order status update with successful SMS notification."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing order
        order_data = self.test_orders[0].copy()
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        # Mock SMS service
        mock_sms = Mock()
        mock_sms_service.return_value = mock_sms
        
        with patch.object(existing_order, 'update_status', return_value=True):
            update_data = {'status': 'confirmed'}
            
            response = self.client.put(
                '/api/admin/orders/507f1f77bcf86cd799439020/status',
                data=json.dumps(update_data),
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            
            # Verify SMS was sent with Romanian message
            args, kwargs = mock_sms.send_notification.call_args
            phone_number, message = args
            assert phone_number == order_data['customer_phone']
            assert 'confirmată' in message  # Romanian status message
            assert order_data['order_number'] in message
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_id')
    @patch('app.services.sms_service.get_sms_service')
    def test_update_order_status_sms_failure(self, mock_sms_service, mock_order_find,
                                           mock_user_find, mock_verify_jwt):
        """Test order status update with SMS failure (should not fail update)."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing order
        order_data = self.test_orders[0].copy()
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        # Mock SMS service failure
        mock_sms = Mock()
        mock_sms.send_notification.side_effect = Exception("SMS service unavailable")
        mock_sms_service.return_value = mock_sms
        
        with patch.object(existing_order, 'update_status', return_value=True):
            update_data = {'status': 'confirmed'}
            
            response = self.client.put(
                '/api/admin/orders/507f1f77bcf86cd799439020/status',
                data=json.dumps(update_data),
                headers=self.auth_headers
            )
            
            # Status update should still succeed even if SMS fails
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
    
    # === ROMANIAN LOCALIZATION TESTS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    def test_romanian_error_messages_orders_listing(self, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test that Romanian error messages are properly displayed in orders listing."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Test invalid date format
        response = self.client.get(
            '/api/admin/orders?start_date=invalid-date',
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Data de început invalidă' in response_data['error']['message']
        assert 'YYYY-MM-DD' in response_data['error']['message']
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    def test_romanian_error_messages_status_update(self, mock_user_find, mock_verify_jwt):
        """Test that Romanian error messages are properly displayed in status updates."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Test invalid status
        update_data = {'status': 'invalid'}
        
        response = self.client.put(
            '/api/admin/orders/507f1f77bcf86cd799439020/status',
            data=json.dumps(update_data),
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        
        # Should contain Romanian status descriptions
        error_message = response_data['error']['message']
        assert 'în așteptare' in error_message
        assert 'confirmată' in error_message
        assert 'finalizată' in error_message
        assert 'anulată' in error_message
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    def test_romanian_success_messages(self, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test that Romanian success messages are properly displayed."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock database collection
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Mock aggregation result
        mock_collection.aggregate.return_value = [{
            'orders': [],
            'total_count': [{'count': 0}],
            'statistics': []
        }]
        
        response = self.client.get('/api/admin/orders', headers=self.auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'Au fost găsite' in response_data['message']
        assert 'comenzi' in response_data['message']
    
    # === EDGE CASES AND BOUNDARY CONDITIONS ===
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.models.order.Order.find_by_order_number')
    def test_update_order_status_by_order_number(self, mock_order_find, mock_user_find, mock_verify_jwt):
        """Test order status update using order number instead of ObjectId."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        # Mock existing order
        order_data = self.test_orders[0].copy()
        existing_order = Order(order_data)
        mock_order_find.return_value = existing_order
        
        with patch.object(existing_order, 'update_status', return_value=True):
            update_data = {'status': 'confirmed'}
            
            # Use order number instead of ObjectId
            response = self.client.put(
                '/api/admin/orders/ORD-2025-001234/status',
                data=json.dumps(update_data),
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            
            # Verify order was found by order number
            mock_order_find.assert_called_once_with('ORD-2025-001234')
    
    @patch('app.utils.auth_middleware.verify_jwt_token')
    @patch('app.models.user.User.find_by_phone')
    @patch('app.database.get_database')
    def test_get_orders_pagination_edge_cases(self, mock_get_db, mock_user_find, mock_verify_jwt):
        """Test order listing pagination with edge cases."""
        # Setup mocks
        mock_verify_jwt.return_value = self.admin_user_data
        mock_user_find.return_value = User(self.admin_user_data)
        
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        mock_collection.aggregate.return_value = [{
            'orders': [],
            'total_count': [],
            'statistics': []
        }]
        
        # Test with very large page number
        response = self.client.get(
            '/api/admin/orders?page=999999&limit=1',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['data']['pagination']['page'] == 999999
        
        # Test with maximum limit
        response = self.client.get(
            '/api/admin/orders?limit=100',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['data']['pagination']['limit'] == 100
        
        # Test with limit over maximum (should be capped)
        response = self.client.get(
            '/api/admin/orders?limit=200',
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['data']['pagination']['limit'] == 100  # Capped at maximum