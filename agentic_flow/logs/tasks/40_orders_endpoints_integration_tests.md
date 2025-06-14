# Task 40: Create orders API integration tests

## Task Details
- **ID**: 40_orders_endpoints_integration_tests
- **Title**: Create orders API integration tests
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Orders create endpoint (Task 39)

## Objective
Create comprehensive integration tests for the POST /api/orders endpoint that validate the complete order creation workflow, including OrderService integration, JSON schema validation, error handling, and all business logic scenarios.

## Requirements
1. **Test File**: `backend/tests/test_orders_api.py`
2. **Framework**: pytest with Flask test client
3. **Coverage**: Success scenarios, validation errors, business logic errors
4. **Integration**: OrderService, SMS verification, cart management
5. **Mocking**: Strategic mocking of external dependencies
6. **Assertions**: HTTP status codes, response format, business logic validation

## Technical Implementation

### 1. Test Structure Overview
```python
class TestOrdersAPI:
    """Integration tests for orders API endpoints."""
    
    def setup_method(self):
        """Setup test environment for each test."""
        
    def teardown_method(self):
        """Cleanup after each test."""

class TestOrderCreationSuccess:
    """Test successful order creation scenarios."""
    
class TestOrderCreationValidation:
    """Test request validation scenarios."""
    
class TestOrderCreationBusinessLogic:
    """Test business logic validation scenarios."""
    
class TestOrderCreationIntegration:
    """Test integration points and dependencies."""
```

### 2. Test Framework Configuration
```python
import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app
from app.services.order_service import OrderValidationError, OrderCreationError
from app.models.cart import Cart
from app.models.product import Product
from app.models.order import Order
```

### 3. Success Scenario Tests

#### Complete Order Creation Workflow
```python
def test_create_order_success_complete_workflow(self, app, client):
    """Test complete successful order creation workflow."""
    
    # Mock OrderService response
    mock_order_response = {
        'success': True,
        'message': 'Order ORD-20250113-000001 created successfully',
        'order': {
            'order_number': 'ORD-20250113-000001',
            'status': 'pending',
            'customer_phone': '+1234567890',
            'customer_name': 'John Doe',
            'items': [...],
            'totals': {...}
        }
    }
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.return_value = mock_order_response
        
        # Valid request payload
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com'
            },
            'phone_verification_session_id': 'session_123'
        }
        
        response = client.post('/api/orders', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['order']['order_number'] == 'ORD-20250113-000001'
        
        # Verify OrderService called with correct parameters
        mock_service.return_value.create_order.assert_called_once_with(
            cart_session_id='cart_123',
            customer_info={...},
            phone_verification_session_id='session_123'
        )
```

#### Order Creation with Optional Fields
```python
def test_create_order_success_with_optional_fields(self, app, client):
    """Test order creation with optional customer information."""
    
def test_create_order_success_minimal_payload(self, app, client):
    """Test order creation with only required fields."""
```

### 4. JSON Schema Validation Tests

#### Missing Required Fields
```python
def test_create_order_missing_cart_session_id(self, app, client):
    """Test validation error for missing cart session ID."""
    
    payload = {
        'customer_info': {...},
        'phone_verification_session_id': 'session_123'
    }
    
    response = client.post('/api/orders',
                         data=json.dumps(payload),
                         content_type='application/json')
    
    assert response.status_code == 400
    # Verify JSON schema validation error
    
def test_create_order_missing_customer_info(self, app, client):
    """Test validation error for missing customer info."""
    
def test_create_order_missing_verification_session(self, app, client):
    """Test validation error for missing verification session ID."""
```

#### Invalid Field Formats
```python
def test_create_order_invalid_phone_format(self, app, client):
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
    # Verify phone format validation error

def test_create_order_invalid_email_format(self, app, client):
    """Test validation error for invalid email format."""
    
def test_create_order_customer_name_too_short(self, app, client):
    """Test validation error for customer name too short."""
    
def test_create_order_special_instructions_too_long(self, app, client):
    """Test validation error for special instructions too long."""
```

### 5. OrderService Integration Tests

#### SMS Verification Errors
```python
def test_create_order_invalid_sms_verification(self, app, client):
    """Test order creation with invalid SMS verification session."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.side_effect = OrderValidationError(
            "Invalid or expired phone verification session",
            "ORDER_003",
            {"session_id": "session_123", "suggestion": "Please verify your phone number again"}
        )
        
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {...},
            'phone_verification_session_id': 'invalid_session'
        }
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'ORDER_003'
        assert 'Invalid or expired' in data['error']

def test_create_order_expired_sms_verification(self, app, client):
    """Test order creation with expired SMS verification session."""
    
def test_create_order_phone_mismatch(self, app, client):
    """Test order creation with phone number mismatch."""
    
def test_create_order_sms_session_already_used(self, app, client):
    """Test order creation with already used SMS session."""
```

#### Cart Validation Errors
```python
def test_create_order_cart_not_found(self, app, client):
    """Test order creation with non-existent cart session."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.side_effect = OrderValidationError(
            "Cart session not found",
            "ORDER_008",
            {"cart_session_id": "cart_123", "suggestion": "Please add items to cart again"}
        )
        
        payload = {
            'cart_session_id': 'nonexistent_cart',
            'customer_info': {...},
            'phone_verification_session_id': 'session_123'
        }
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'ORDER_008'

def test_create_order_cart_expired(self, app, client):
    """Test order creation with expired cart session."""
    
def test_create_order_cart_empty(self, app, client):
    """Test order creation with empty cart."""
```

#### Product and Inventory Errors
```python
def test_create_order_product_not_found(self, app, client):
    """Test order creation with non-existent product."""
    
def test_create_order_product_unavailable(self, app, client):
    """Test order creation with unavailable product."""
    
def test_create_order_insufficient_inventory(self, app, client):
    """Test order creation with insufficient inventory."""
```

### 6. Order Creation Error Tests

#### Database Transaction Errors
```python
def test_create_order_database_error(self, app, client):
    """Test order creation with database transaction failure."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.side_effect = OrderCreationError(
            "Failed to create order due to database error",
            "ORDER_020",
            {"operation": "order_insertion"}
        )
        
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {...},
            'phone_verification_session_id': 'session_123'
        }
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error_code'] == 'ORDER_020'

def test_create_order_inventory_update_failure(self, app, client):
    """Test order creation with inventory update failure."""
    
def test_create_order_session_cleanup_failure(self, app, client):
    """Test order creation with session cleanup failure."""
```

#### Unexpected System Errors
```python
def test_create_order_unexpected_error(self, app, client):
    """Test order creation with unexpected system error."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.side_effect = Exception("Unexpected error")
        
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {...},
            'phone_verification_session_id': 'session_123'
        }
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error_code'] == 'ORDER_500'
        assert 'unexpected error' in data['error'].lower()
```

### 7. Request Format Tests

#### Content Type Validation
```python
def test_create_order_invalid_content_type(self, app, client):
    """Test order creation with invalid content type."""
    
    payload = {...}
    
    response = client.post('/api/orders',
                         data=json.dumps(payload),
                         content_type='text/plain')
    
    assert response.status_code == 400

def test_create_order_no_content_type(self, app, client):
    """Test order creation without content type header."""
    
def test_create_order_malformed_json(self, app, client):
    """Test order creation with malformed JSON."""
```

#### HTTP Method Validation
```python
def test_create_order_get_method_not_allowed(self, app, client):
    """Test that GET method is not allowed for order creation."""
    
    response = client.get('/api/orders')
    assert response.status_code == 405

def test_create_order_put_method_not_allowed(self, app, client):
    """Test that PUT method is not allowed for order creation."""
    
def test_create_order_delete_method_not_allowed(self, app, client):
    """Test that DELETE method is not allowed for order creation."""
```

### 8. Response Format Validation Tests

#### Success Response Structure
```python
def test_create_order_success_response_structure(self, app, client):
    """Test that success response has correct structure."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.return_value = {
            'success': True,
            'message': 'Order created successfully',
            'order': {...}
        }
        
        payload = {...}
        
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
```

#### Error Response Structure
```python
def test_create_order_error_response_structure(self, app, client):
    """Test that error response has correct structure."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.side_effect = OrderValidationError(
            "Test error", "ORDER_001", {"field": "test"}
        )
        
        payload = {...}
        
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
```

### 9. Integration Point Tests

#### OrderService Mock Verification
```python
def test_create_order_service_called_with_correct_parameters(self, app, client):
    """Test that OrderService is called with correct parameters."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.return_value = {...}
        
        payload = {
            'cart_session_id': 'cart_123',
            'customer_info': {
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com',
                'special_instructions': 'Handle with care'
            },
            'phone_verification_session_id': 'session_123'
        }
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # Verify service called once with exact parameters
        mock_service.return_value.create_order.assert_called_once_with(
            cart_session_id='cart_123',
            customer_info={
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com',
                'special_instructions': 'Handle with care'
            },
            phone_verification_session_id='session_123'
        )
```

### 10. Error Code Coverage Tests

#### All OrderService Error Codes
```python
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
def test_create_order_all_error_codes(self, app, client, error_code, error_message, expected_status):
    """Test all possible OrderService error codes."""
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        if expected_status == 400:
            mock_service.return_value.create_order.side_effect = OrderValidationError(
                error_message, error_code, {}
            )
        else:
            mock_service.return_value.create_order.side_effect = OrderCreationError(
                error_message, error_code, {}
            )
        
        payload = {...}
        
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == expected_status
        data = response.get_json()
        assert data['error_code'] == error_code
        assert data['success'] is False
```

### 11. Performance and Load Tests

#### Response Time Tests
```python
def test_create_order_response_time(self, app, client):
    """Test that order creation responds within acceptable time."""
    
    import time
    
    with patch('app.services.order_service.get_order_service') as mock_service:
        mock_service.return_value.create_order.return_value = {...}
        
        payload = {...}
        
        start_time = time.time()
        response = client.post('/api/orders',
                             data=json.dumps(payload),
                             content_type='application/json')
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
```

### 12. Test Configuration and Fixtures

#### Flask App Fixture
```python
@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
```

#### Sample Data Fixtures
```python
@pytest.fixture
def valid_order_payload():
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
def mock_order_response():
    """Mock successful order response."""
    return {
        'success': True,
        'message': 'Order ORD-20250113-000001 created successfully',
        'order': {...}
    }
```

## Success Criteria
- Complete test coverage for POST /api/orders endpoint
- All success scenarios tested with proper assertions
- All validation error scenarios covered
- All OrderService error codes tested
- Integration points with OrderService validated
- Request/response format validation
- HTTP method and content type validation
- Performance and response time testing
- Proper mocking of external dependencies
- Clear test organization and maintainable test code