"""
Integration tests for orders API endpoints.

This module contains comprehensive integration tests for the orders API,
testing the complete order creation workflow, validation, error handling,
and integration with OrderService.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app.services.order_service import OrderValidationError, OrderCreationError


class TestOrdersAPIBasic:
    """Basic integration tests for orders API endpoints."""

    def test_orders_endpoint_exists(self, client):
        """Test that orders endpoint exists and responds."""
        # Test with invalid JSON to get a quick response
        response = client.post('/api/orders')
        # Should get a 400 for missing content, not 404
        assert response.status_code != 404

    def test_orders_endpoint_requires_post(self, client):
        """Test that orders endpoint only accepts POST method."""
        response = client.get('/api/orders')
        assert response.status_code == 405

        response = client.put('/api/orders')
        assert response.status_code == 405

        response = client.delete('/api/orders')
        assert response.status_code == 405


class TestOrderCreationSuccess:
    """Test successful order creation scenarios."""

    @pytest.fixture
    def valid_order_payload(self):
        """Valid order creation payload."""
        return {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com'
            },
            'phone_verification_session_id': 'session_123'
        }

    @pytest.fixture
    def mock_order_response(self):
        """Mock successful order response."""
        return {
            'success': True,
            'message': 'Order ORD-20250113-000001 created successfully. You will receive SMS confirmation shortly.',
            'order': {
                'order_number': 'ORD-20250113-000001',
                'status': 'pending',
                'customer_phone': '+1234567890',
                'customer_name': 'John Doe',
                'items': [
                    {
                        'product_id': '507f1f77bcf86cd799439011',
                        'product_name': 'Organic Apples',
                        'quantity': 2,
                        'unit_price': 4.99,
                        'total_price': 9.98
                    }
                ],
                'totals': {
                    'subtotal': 9.98,
                    'tax': 0.80,
                    'delivery_fee': 5.00,
                    'total': 15.78,
                    'tax_rate': 0.08,
                    'free_delivery_threshold': 50.00
                },
                'created_at': '2025-01-13T15:30:00Z'
            }
        }

    @patch('app.routes.orders.get_order_service')
    def test_create_order_success_complete_workflow(self, mock_get_service, client, valid_order_payload, mock_order_response):
        """Test complete successful order creation workflow."""
        # Setup mock
        mock_service = MagicMock()
        mock_service.create_order.return_value = mock_order_response
        mock_get_service.return_value = mock_service

        # Make request
        response = client.post('/api/orders',
                             data=json.dumps(valid_order_payload),
                             content_type='application/json')

        # Verify response
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['order']['order_number'] == 'ORD-20250113-000001'
        assert data['order']['status'] == 'pending'
        assert data['order']['customer_phone'] == '+1234567890'

        # Verify OrderService called with correct parameters
        mock_service.create_order.assert_called_once_with(
            cart_session_id='cart_123',
            customer_info={
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com'
            },
            phone_verification_session_id='session_123'
        )

    @patch('app.routes.orders.get_order_service')
    def test_create_order_success_minimal_payload(self, mock_get_service, client, mock_order_response):
        """Test order creation with only required fields."""
        mock_service = MagicMock()
        mock_service.create_order.return_value = mock_order_response
        mock_get_service.return_value = mock_service

        minimal_payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(minimal_payload),
                             content_type='application/json')

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

        # Verify service called with minimal data
        mock_service.create_order.assert_called_once_with(
            cart_session_id='cart_123',
            customer_info={
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            phone_verification_session_id='session_123'
        )

    @patch('app.routes.orders.get_order_service')
    def test_create_order_success_with_special_instructions(self, mock_get_service, client, mock_order_response):
        """Test order creation with special instructions."""
        mock_service = MagicMock()
        mock_service.create_order.return_value = mock_order_response
        mock_get_service.return_value = mock_service

        payload_with_instructions = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'special_instructions': 'Please handle with care'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload_with_instructions),
                             content_type='application/json')

        assert response.status_code == 201
        mock_service.create_order.assert_called_once()
        call_args = mock_service.create_order.call_args[1]
        assert call_args['customer_info']['special_instructions'] == 'Please handle with care'


class TestOrderCreationValidation:
    """Test request validation scenarios."""

    def test_create_order_missing_cart_session_id(self, client):
        """Test validation error for missing cart session ID."""
        payload = {
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400
        # JSON schema validation should reject this

    def test_create_order_missing_customer_info(self, client):
        """Test validation error for missing customer info."""
        payload = {
            'cart_session_id': 'cart_123',
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_missing_verification_session(self, client):
        """Test validation error for missing verification session ID."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            }
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_invalid_phone_format(self, client):
        """Test validation error for invalid phone number format."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '1234567890',  # Missing +
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_invalid_email_format(self, client):
        """Test validation error for invalid email format."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'invalid-email'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_customer_name_too_short(self, client):
        """Test validation error for customer name too short."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'A'  # Too short
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_special_instructions_too_long(self, client):
        """Test validation error for special instructions too long."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'special_instructions': 'A' * 501  # Too long
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400


class TestOrderCreationBusinessLogic:
    """Test business logic validation scenarios."""

    @pytest.fixture
    def valid_payload(self):
        """Valid payload for business logic tests."""
        return {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

    @patch('app.routes.orders.get_order_service')
    def test_create_order_invalid_sms_verification(self, mock_get_service, client, valid_payload):
        """Test order creation with invalid SMS verification session."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Invalid or expired phone verification session",
            "ORDER_003",
            {"session_id": "session_123", "suggestion": "Please verify your phone number again"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'ORDER_003'
        assert 'Invalid or expired' in data['error']
        assert 'details' in data

    @patch('app.routes.orders.get_order_service')
    def test_create_order_phone_mismatch(self, mock_get_service, client, valid_payload):
        """Test order creation with phone number mismatch."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Phone verification session does not match customer phone number",
            "ORDER_004",
            {"verified_phone": "4321", "customer_phone": "7890"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_004'
        assert 'does not match' in data['error']

    @patch('app.routes.orders.get_order_service')
    def test_create_order_cart_not_found(self, mock_get_service, client, valid_payload):
        """Test order creation with non-existent cart session."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Cart session not found",
            "ORDER_008",
            {"cart_session_id": "cart_123", "suggestion": "Please add items to cart again"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_008'
        assert 'Cart session not found' in data['error']

    @patch('app.routes.orders.get_order_service')
    def test_create_order_cart_expired(self, mock_get_service, client, valid_payload):
        """Test order creation with expired cart session."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Cart session has expired",
            "ORDER_009",
            {"cart_session_id": "cart_123", "expired_at": "2025-01-13T12:00:00Z"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_009'

    @patch('app.routes.orders.get_order_service')
    def test_create_order_cart_empty(self, mock_get_service, client, valid_payload):
        """Test order creation with empty cart."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Cart is empty",
            "ORDER_010",
            {"suggestion": "Please add items to cart before ordering"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_010'

    @patch('app.routes.orders.get_order_service')
    def test_create_order_product_not_found(self, mock_get_service, client, valid_payload):
        """Test order creation with non-existent product."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Product 'Organic Apples' is no longer available",
            "ORDER_015",
            {"product_id": "product_123", "product_name": "Organic Apples"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_015'

    @patch('app.routes.orders.get_order_service')
    def test_create_order_insufficient_inventory(self, mock_get_service, client, valid_payload):
        """Test order creation with insufficient inventory."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Insufficient inventory for 'Organic Apples'",
            "ORDER_017",
            {"product_name": "Organic Apples", "available_quantity": 3, "requested_quantity": 5}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_017'


class TestOrderCreationErrors:
    """Test order creation error scenarios."""

    @pytest.fixture
    def valid_payload(self):
        """Valid payload for error tests."""
        return {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

    @patch('app.routes.orders.get_order_service')
    def test_create_order_database_error(self, mock_get_service, client, valid_payload):
        """Test order creation with database transaction failure."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderCreationError(
            "Failed to create order due to database error",
            "ORDER_020",
            {"operation": "order_insertion"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'ORDER_020'

    @patch('app.routes.orders.get_order_service')
    def test_create_order_inventory_update_failure(self, mock_get_service, client, valid_payload):
        """Test order creation with inventory update failure."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderCreationError(
            "Product not found during inventory update",
            "ORDER_019",
            {"product_id": "product_123", "operation": "inventory_update"}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 500
        data = response.get_json()
        assert data['error_code'] == 'ORDER_019'

    @patch('app.routes.orders.get_order_service')
    def test_create_order_unexpected_error(self, mock_get_service, client, valid_payload):
        """Test order creation with unexpected system error."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = Exception("Unexpected database connection error")
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'ORDER_500'
        assert 'unexpected error' in data['error'].lower()


class TestRequestFormat:
    """Test request format validation."""

    def test_create_order_invalid_content_type(self, client):
        """Test order creation with invalid content type."""
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='text/plain')

        assert response.status_code == 400

    def test_create_order_malformed_json(self, client):
        """Test order creation with malformed JSON."""
        malformed_json = '{"cart_session_id": "cart_123", "customer_info": {'

        response = client.post('/api/orders',
                             data=malformed_json,
                             content_type='application/json')

        assert response.status_code == 400

    def test_create_order_empty_payload(self, client):
        """Test order creation with empty payload."""
        response = client.post('/api/orders',
                             data='{}',
                             content_type='application/json')

        assert response.status_code == 400


class TestResponseFormat:
    """Test response format validation."""

    @patch('app.routes.orders.get_order_service')
    def test_create_order_success_response_structure(self, mock_get_service, client):
        """Test that success response has correct structure."""
        mock_service = MagicMock()
        mock_service.create_order.return_value = {
            'success': True,
            'message': 'Order created successfully',
            'order': {
                'order_number': 'ORD-20250113-000001',
                'status': 'pending'
            }
        }
        mock_get_service.return_value = mock_service

        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 201
        data = response.get_json()

        # Validate response structure
        assert 'success' in data
        assert 'message' in data
        assert 'order' in data
        assert data['success'] is True
        assert isinstance(data['order'], dict)

    @patch('app.routes.orders.get_order_service')
    def test_create_order_error_response_structure(self, mock_get_service, client):
        """Test that error response has correct structure."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            "Test error", "ORDER_001", {"field": "test"}
        )
        mock_get_service.return_value = mock_service

        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()

        # Validate error response structure
        assert 'success' in data
        assert 'error' in data
        assert 'error_code' in data
        assert 'details' in data
        assert data['success'] is False


class TestErrorCodeCoverage:
    """Test all possible OrderService error codes."""

    @pytest.fixture
    def valid_payload(self):
        """Valid payload for error code tests."""
        return {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

    @pytest.mark.parametrize("error_code,error_message,expected_status", [
        ("ORDER_001", "Phone verification session ID is required", 400),
        ("ORDER_002", "Customer phone number is required", 400),
        ("ORDER_003", "Invalid or expired phone verification session", 400),
        ("ORDER_004", "Phone verification session does not match customer phone", 400),
        ("ORDER_005", "Phone verification session has already been used", 400),
        ("ORDER_006", "Unable to validate phone verification", 400),
        ("ORDER_007", "Cart session ID is required", 400),
        ("ORDER_008", "Cart session not found", 400),
        ("ORDER_009", "Cart session has expired", 400),
        ("ORDER_010", "Cart is empty", 400),
        ("ORDER_011", "Unable to validate cart session", 400),
        ("ORDER_012", "Phone number is required", 400),
        ("ORDER_013", "Invalid phone number format", 400),
        ("ORDER_014", "Customer name must be at least 2 characters", 400),
        ("ORDER_015", "Product is no longer available", 400),
        ("ORDER_016", "Product is currently unavailable", 400),
        ("ORDER_017", "Insufficient inventory", 400),
        ("ORDER_018", "Unable to validate product inventory", 400),
    ])
    @patch('app.routes.orders.get_order_service')
    def test_create_order_validation_error_codes(self, mock_get_service, client, valid_payload, 
                                                error_code, error_message, expected_status):
        """Test all validation error codes."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderValidationError(
            error_message, error_code, {}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == expected_status
        data = response.get_json()
        assert data['error_code'] == error_code
        assert data['success'] is False

    @pytest.mark.parametrize("error_code,error_message,expected_status", [
        ("ORDER_019", "Product not found during inventory update", 500),
        ("ORDER_020", "Failed to create order", 500),
        ("ORDER_021", "Failed to update inventory", 500),
        ("ORDER_022", "Order not found", 500),
        ("ORDER_023", "Failed to mark verification session as used", 500),
        ("ORDER_024", "Failed to delete cart session", 500),
        ("ORDER_025", "Failed to generate order number", 500),
        ("ORDER_026", "Failed to calculate order totals", 500),
        ("ORDER_027", "Database transaction failed", 500)
    ])
    @patch('app.routes.orders.get_order_service')
    def test_create_order_creation_error_codes(self, mock_get_service, client, valid_payload,
                                             error_code, error_message, expected_status):
        """Test all creation error codes."""
        mock_service = MagicMock()
        mock_service.create_order.side_effect = OrderCreationError(
            error_message, error_code, {}
        )
        mock_get_service.return_value = mock_service

        response = client.post('/api/orders',
                             data=json.dumps(valid_payload),
                             content_type='application/json')

        assert response.status_code == expected_status
        data = response.get_json()
        assert data['error_code'] == error_code
        assert data['success'] is False


class TestPerformanceAndIntegration:
    """Test performance and integration aspects."""

    @patch('app.routes.orders.get_order_service')
    def test_create_order_service_parameters_exact_match(self, mock_get_service, client):
        """Test that OrderService is called with exact parameters."""
        mock_service = MagicMock()
        mock_service.create_order.return_value = {
            'success': True,
            'message': 'Order created',
            'order': {}
        }
        mock_get_service.return_value = mock_service

        payload = {
            'cart_session_id': 'cart_abc123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'Jane Smith',
                'email': 'jane@example.com',
                'special_instructions': 'Handle with extreme care'
            },
            'phone_verification_session_id': 'verify_xyz789'
        }

        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')

        assert response.status_code == 201

        # Verify service called once with exact parameters
        mock_service.create_order.assert_called_once_with(
            cart_session_id='cart_abc123',
            customer_info={
                'phone_number': '+1234567890',
                'customer_name': 'Jane Smith',
                'email': 'jane@example.com',
                'special_instructions': 'Handle with extreme care'
            },
            phone_verification_session_id='verify_xyz789'
        )

    @patch('app.routes.orders.get_order_service')
    def test_create_order_response_time_reasonable(self, mock_get_service, client):
        """Test that order creation responds within reasonable time."""
        import time

        mock_service = MagicMock()
        mock_service.create_order.return_value = {
            'success': True,
            'message': 'Order created',
            'order': {}
        }
        mock_get_service.return_value = mock_service

        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe'
            },
            'phone_verification_session_id': 'session_123'
        }

        start_time = time.time()
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        end_time = time.time()

        assert response.status_code == 201
        # Should respond within 1 second (with mocking this should be much faster)
        assert (end_time - start_time) < 1.0