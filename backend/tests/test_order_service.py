"""
Unit tests for order processing service.

This module contains comprehensive tests for the OrderService class including
validation logic, error handling, pricing calculations, atomic transactions,
and integration with external dependencies.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, call
from bson import ObjectId

from app.services.order_service import (
    OrderService, 
    OrderValidationError, 
    OrderCreationError, 
    get_order_service
)


class TestOrderServiceInitialization:
    """Test OrderService initialization and configuration."""
    
    @patch('app.services.order_service.get_database')
    def test_initialization_success(self, mock_get_database):
        """Test successful OrderService initialization."""
        mock_db = MagicMock()
        mock_get_database.return_value = mock_db
        
        service = OrderService()
        
        assert service.db == mock_db
        assert service.orders_collection == mock_db.orders
        assert service.products_collection == mock_db.products
        assert service.verification_sessions_collection == mock_db.verification_sessions
        assert service.order_sequences_collection == mock_db.order_sequences
        assert service.cart_sessions_collection == mock_db.cart_sessions
    
    def test_service_constants(self):
        """Test service constants are properly configured."""
        service = OrderService()
        
        assert service.TAX_RATE == Decimal('0.08')
        assert service.FREE_DELIVERY_THRESHOLD == Decimal('50.00')
        assert service.DELIVERY_FEE == Decimal('5.00')
        assert service.ORDER_STATUS_PENDING == 'pending'
        assert service.ORDER_STATUS_CONFIRMED == 'confirmed'
        assert service.ORDER_STATUS_CANCELLED == 'cancelled'


class TestSMSVerificationValidation:
    """Test SMS verification session validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
        self.service.verification_sessions_collection = MagicMock()
    
    def test_validate_verification_session_success(self):
        """Test successful verification session validation."""
        # Setup valid session
        valid_session = {
            'session_id': 'session_123',
            'phone_number': '+1234567890',
            'verified': True,
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'used': False
        }
        
        self.service.verification_sessions_collection.find_one.return_value = valid_session
        
        # Should not raise exception
        self.service._validate_verification_session('session_123', '+1234567890')
        
        # Verify database query
        self.service.verification_sessions_collection.find_one.assert_called_once()
        query = self.service.verification_sessions_collection.find_one.call_args[0][0]
        assert query['session_id'] == 'session_123'
        assert query['verified'] is True
        assert '$gt' in query['expires_at']
    
    def test_validate_verification_session_missing_id(self):
        """Test validation with missing session ID."""
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('', '+1234567890')
        
        assert exc_info.value.error_code == 'ORDER_001'
        assert 'Phone verification session ID is required' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'phone_verification_session_id'
    
    def test_validate_verification_session_missing_phone(self):
        """Test validation with missing phone number."""
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('session_123', '')
        
        assert exc_info.value.error_code == 'ORDER_002'
        assert 'Customer phone number is required' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'phone_number'
    
    def test_validate_verification_session_not_found(self):
        """Test validation with session not found."""
        self.service.verification_sessions_collection.find_one.return_value = None
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('session_123', '+1234567890')
        
        assert exc_info.value.error_code == 'ORDER_003'
        assert 'Invalid or expired phone verification session' in str(exc_info.value)
        assert exc_info.value.details['session_id'] == 'session_123'
        assert 'verify your phone number again' in exc_info.value.details['suggestion']
    
    def test_validate_verification_session_phone_mismatch(self):
        """Test validation with phone number mismatch."""
        session_with_different_phone = {
            'session_id': 'session_123',
            'phone_number': '+0987654321',
            'verified': True,
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'used': False
        }
        
        self.service.verification_sessions_collection.find_one.return_value = session_with_different_phone
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('session_123', '+1234567890')
        
        assert exc_info.value.error_code == 'ORDER_004'
        assert 'does not match customer phone number' in str(exc_info.value)
        assert exc_info.value.details['verified_phone'] == '4321'  # Last 4 digits
    
    def test_validate_verification_session_already_used(self):
        """Test validation with already used session."""
        used_session = {
            'session_id': 'session_123',
            'phone_number': '+1234567890',
            'verified': True,
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'used': True
        }
        
        self.service.verification_sessions_collection.find_one.return_value = used_session
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('session_123', '+1234567890')
        
        assert exc_info.value.error_code == 'ORDER_005'
        assert 'already been used' in str(exc_info.value)
        assert 'verify your phone number again' in exc_info.value.details['suggestion']
    
    def test_validate_verification_session_database_error(self):
        """Test validation with database error."""
        self.service.verification_sessions_collection.find_one.side_effect = Exception("DB Error")
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_verification_session('session_123', '+1234567890')
        
        assert exc_info.value.error_code == 'ORDER_006'
        assert 'Unable to validate phone verification' in str(exc_info.value)


class TestCartValidation:
    """Test cart validation logic."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    @patch('app.services.order_service.Cart')
    def test_validate_cart_success(self, mock_cart_class):
        """Test successful cart validation."""
        # Setup valid cart
        mock_cart = MagicMock()
        mock_cart.expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_cart.items = [MagicMock(), MagicMock()]  # Non-empty cart
        
        mock_cart_class.find_by_session_id.return_value = mock_cart
        
        result = self.service._validate_cart('cart_123')
        
        assert result == mock_cart
        mock_cart_class.find_by_session_id.assert_called_once_with('cart_123')
    
    def test_validate_cart_missing_session_id(self):
        """Test validation with missing cart session ID."""
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_cart('')
        
        assert exc_info.value.error_code == 'ORDER_007'
        assert 'Cart session ID is required' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'cart_session_id'
    
    @patch('app.services.order_service.Cart')
    def test_validate_cart_not_found(self, mock_cart_class):
        """Test validation with cart not found."""
        mock_cart_class.find_by_session_id.return_value = None
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_cart('cart_123')
        
        assert exc_info.value.error_code == 'ORDER_008'
        assert 'Cart session not found' in str(exc_info.value)
        assert exc_info.value.details['cart_session_id'] == 'cart_123'
        assert 'add items to cart again' in exc_info.value.details['suggestion']
    
    @patch('app.services.order_service.Cart')
    def test_validate_cart_expired(self, mock_cart_class):
        """Test validation with expired cart."""
        mock_cart = MagicMock()
        mock_cart.expires_at = datetime.utcnow() - timedelta(hours=1)  # Expired
        mock_cart.items = [MagicMock()]
        
        mock_cart_class.find_by_session_id.return_value = mock_cart
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_cart('cart_123')
        
        assert exc_info.value.error_code == 'ORDER_009'
        assert 'Cart session has expired' in str(exc_info.value)
        assert 'expired_at' in exc_info.value.details
        assert 'add items to cart again' in exc_info.value.details['suggestion']
    
    @patch('app.services.order_service.Cart')
    def test_validate_cart_empty(self, mock_cart_class):
        """Test validation with empty cart."""
        mock_cart = MagicMock()
        mock_cart.expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_cart.items = []  # Empty cart
        
        mock_cart_class.find_by_session_id.return_value = mock_cart
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_cart('cart_123')
        
        assert exc_info.value.error_code == 'ORDER_010'
        assert 'Cart is empty' in str(exc_info.value)
        assert 'add items to cart before ordering' in exc_info.value.details['suggestion']
    
    @patch('app.services.order_service.Cart')
    def test_validate_cart_database_error(self, mock_cart_class):
        """Test validation with database error."""
        mock_cart_class.find_by_session_id.side_effect = Exception("DB Error")
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_cart('cart_123')
        
        assert exc_info.value.error_code == 'ORDER_011'
        assert 'Unable to validate cart session' in str(exc_info.value)


class TestCustomerInfoValidation:
    """Test customer information validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    def test_validate_customer_info_success(self):
        """Test successful customer info validation."""
        valid_customer_info = {
            'phone_number': '+1234567890',
            'customer_name': 'John Doe'
        }
        
        # Should not raise exception
        self.service._validate_customer_info(valid_customer_info)
    
    def test_validate_customer_info_missing_phone(self):
        """Test validation with missing phone number."""
        customer_info = {
            'customer_name': 'John Doe'
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_customer_info(customer_info)
        
        assert exc_info.value.error_code == 'ORDER_012'
        assert 'Phone number is required' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'phone_number'
    
    def test_validate_customer_info_missing_name(self):
        """Test validation with missing customer name."""
        customer_info = {
            'phone_number': '+1234567890'
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_customer_info(customer_info)
        
        assert exc_info.value.error_code == 'ORDER_012'
        assert 'Customer name is required' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'customer_name'
    
    def test_validate_customer_info_invalid_phone_format(self):
        """Test validation with invalid phone number format."""
        invalid_phones = [
            '1234567890',  # Missing +
            '+123',        # Too short
            'invalid',     # Non-numeric
            '+',           # Just plus sign
        ]
        
        for invalid_phone in invalid_phones:
            customer_info = {
                'phone_number': invalid_phone,
                'customer_name': 'John Doe'
            }
            
            with pytest.raises(OrderValidationError) as exc_info:
                self.service._validate_customer_info(customer_info)
            
            assert exc_info.value.error_code == 'ORDER_013'
            assert 'Invalid phone number format' in str(exc_info.value)
            assert exc_info.value.details['field'] == 'phone_number'
            assert exc_info.value.details['value'] == invalid_phone
    
    def test_validate_customer_info_short_name(self):
        """Test validation with name too short."""
        customer_info = {
            'phone_number': '+1234567890',
            'customer_name': 'A'  # Too short
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_customer_info(customer_info)
        
        assert exc_info.value.error_code == 'ORDER_014'
        assert 'must be at least 2 characters' in str(exc_info.value)
        assert exc_info.value.details['field'] == 'customer_name'


class TestProductAndInventoryValidation:
    """Test product and inventory validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    @patch('app.services.order_service.Product')
    def test_validate_products_and_inventory_success(self, mock_product_class):
        """Test successful product and inventory validation."""
        # Setup cart items
        cart_item = MagicMock()
        cart_item.product_id = 'product_123'
        cart_item.product_name = 'Organic Apples'
        cart_item.quantity = 2
        cart_item.price = Decimal('4.99')
        
        # Setup product
        mock_product = MagicMock()
        mock_product._id = ObjectId()
        mock_product.name = 'Organic Apples'
        mock_product.price = Decimal('4.99')
        mock_product.stock_quantity = 10
        mock_product.is_available = True
        
        mock_product_class.find_by_id.return_value = mock_product
        
        result = self.service._validate_products_and_inventory([cart_item])
        
        assert len(result) == 1
        validated_item = result[0]
        assert validated_item['product_id'] == str(mock_product._id)
        assert validated_item['product_name'] == 'Organic Apples'
        assert validated_item['quantity'] == 2
        assert validated_item['unit_price'] == 4.99
        assert validated_item['total_price'] == 9.98
        
        mock_product_class.find_by_id.assert_called_once_with('product_123')
    
    @patch('app.services.order_service.Product')
    def test_validate_products_product_not_found(self, mock_product_class):
        """Test validation when product not found."""
        cart_item = MagicMock()
        cart_item.product_id = 'product_123'
        cart_item.product_name = 'Organic Apples'
        
        mock_product_class.find_by_id.return_value = None
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_products_and_inventory([cart_item])
        
        assert exc_info.value.error_code == 'ORDER_015'
        assert 'is no longer available' in str(exc_info.value)
        assert exc_info.value.details['product_id'] == 'product_123'
        assert exc_info.value.details['product_name'] == 'Organic Apples'
    
    @patch('app.services.order_service.Product')
    def test_validate_products_product_unavailable(self, mock_product_class):
        """Test validation when product is unavailable."""
        cart_item = MagicMock()
        cart_item.product_id = 'product_123'
        cart_item.product_name = 'Organic Apples'
        
        mock_product = MagicMock()
        mock_product.name = 'Organic Apples'
        mock_product.is_available = False  # Unavailable
        
        mock_product_class.find_by_id.return_value = mock_product
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_products_and_inventory([cart_item])
        
        assert exc_info.value.error_code == 'ORDER_016'
        assert 'currently unavailable' in str(exc_info.value)
        assert exc_info.value.details['product_name'] == 'Organic Apples'
    
    @patch('app.services.order_service.Product')
    def test_validate_products_insufficient_inventory(self, mock_product_class):
        """Test validation with insufficient inventory."""
        cart_item = MagicMock()
        cart_item.product_id = 'product_123'
        cart_item.product_name = 'Organic Apples'
        cart_item.quantity = 5
        
        mock_product = MagicMock()
        mock_product.name = 'Organic Apples'
        mock_product.stock_quantity = 3  # Insufficient
        mock_product.is_available = True
        
        mock_product_class.find_by_id.return_value = mock_product
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service._validate_products_and_inventory([cart_item])
        
        assert exc_info.value.error_code == 'ORDER_017'
        assert 'Insufficient inventory' in str(exc_info.value)
        assert exc_info.value.details['product_name'] == 'Organic Apples'
        assert exc_info.value.details['available_quantity'] == 3
        assert exc_info.value.details['requested_quantity'] == 5
    
    @patch('app.services.order_service.Product')
    def test_validate_products_price_mismatch(self, mock_product_class):
        """Test validation with price mismatch (uses current price)."""
        cart_item = MagicMock()
        cart_item.product_id = 'product_123'
        cart_item.product_name = 'Organic Apples'
        cart_item.quantity = 2
        cart_item.price = Decimal('4.99')  # Cart price
        
        mock_product = MagicMock()
        mock_product._id = ObjectId()
        mock_product.name = 'Organic Apples'
        mock_product.price = Decimal('5.99')  # Different current price
        mock_product.stock_quantity = 10
        mock_product.is_available = True
        
        mock_product_class.find_by_id.return_value = mock_product
        
        result = self.service._validate_products_and_inventory([cart_item])
        
        # Should use current database price, not cart price
        validated_item = result[0]
        assert validated_item['unit_price'] == 5.99  # Current price
        assert validated_item['total_price'] == 11.98  # 5.99 * 2


class TestPricingCalculations:
    """Test pricing and totals calculations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    def test_calculate_order_totals_standard(self):
        """Test standard pricing calculation."""
        items = [
            {'total_price': 9.98},
            {'total_price': 15.50}
        ]
        
        result = self.service._calculate_order_totals(items)
        
        expected_subtotal = 25.48
        expected_tax = round(25.48 * 0.08, 2)  # 8% tax
        expected_delivery = 5.00  # Under $50 threshold
        expected_total = expected_subtotal + expected_tax + expected_delivery
        
        assert result['subtotal'] == expected_subtotal
        assert result['tax'] == expected_tax
        assert result['delivery_fee'] == expected_delivery
        assert result['total'] == expected_total
        assert result['tax_rate'] == 0.08
        assert result['free_delivery_threshold'] == 50.00
    
    def test_calculate_order_totals_free_delivery(self):
        """Test pricing with free delivery over $50."""
        items = [
            {'total_price': 30.00},
            {'total_price': 25.00}
        ]
        
        result = self.service._calculate_order_totals(items)
        
        expected_subtotal = 55.00
        expected_tax = 4.40  # 8% of 55.00
        expected_delivery = 0.00  # Free delivery over $50
        expected_total = 59.40
        
        assert result['subtotal'] == expected_subtotal
        assert result['tax'] == expected_tax
        assert result['delivery_fee'] == expected_delivery
        assert result['total'] == expected_total
    
    def test_calculate_order_totals_exactly_threshold(self):
        """Test pricing exactly at $50 threshold."""
        items = [
            {'total_price': 50.00}
        ]
        
        result = self.service._calculate_order_totals(items)
        
        assert result['subtotal'] == 50.00
        assert result['delivery_fee'] == 0.00  # Free at exactly $50
    
    def test_calculate_order_totals_rounding(self):
        """Test decimal rounding in calculations."""
        items = [
            {'total_price': 9.996},  # Should round properly
            {'total_price': 15.504}
        ]
        
        result = self.service._calculate_order_totals(items)
        
        # Verify proper decimal handling and rounding
        assert isinstance(result['subtotal'], float)
        assert isinstance(result['tax'], float)
        assert isinstance(result['total'], float)
        
        # Check that rounding is consistent
        assert result['total'] == result['subtotal'] + result['tax'] + result['delivery_fee']


class TestOrderNumberGeneration:
    """Test order number generation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
        self.service.order_sequences_collection = MagicMock()
    
    @patch('app.services.order_service.datetime')
    def test_generate_order_number_success(self, mock_datetime):
        """Test successful order number generation."""
        mock_datetime.utcnow.return_value = datetime(2025, 1, 13, 15, 0, 0)
        
        # Mock sequence generation
        self.service.order_sequences_collection.find_one_and_update.return_value = {
            'sequence': 1
        }
        
        result = self.service._generate_order_number()
        
        assert result == 'ORD-20250113-000001'
        
        # Verify database call
        self.service.order_sequences_collection.find_one_and_update.assert_called_once_with(
            {'date': '20250113'},
            {'$inc': {'sequence': 1}},
            upsert=True,
            return_document=True
        )
    
    @patch('app.services.order_service.datetime')
    def test_generate_order_number_sequence_increment(self, mock_datetime):
        """Test order number sequence incrementing."""
        mock_datetime.utcnow.return_value = datetime(2025, 1, 13, 15, 0, 0)
        
        # Mock sequence generation returning higher number
        self.service.order_sequences_collection.find_one_and_update.return_value = {
            'sequence': 42
        }
        
        result = self.service._generate_order_number()
        
        assert result == 'ORD-20250113-000042'
    
    @patch('app.services.order_service.datetime')
    def test_generate_order_number_fallback(self, mock_datetime):
        """Test fallback order number generation."""
        mock_datetime.utcnow.return_value = datetime(2025, 1, 13, 15, 0, 0)
        
        # Mock database error
        self.service.order_sequences_collection.find_one_and_update.side_effect = Exception("DB Error")
        
        result = self.service._generate_order_number()
        
        # Should return fallback format
        assert result.startswith('ORD-20250113-')
        assert len(result) == 21  # ORD-YYYYMMDD-NNNNNN format


class TestAtomicOrderCreation:
    """Test atomic database transactions."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
        self.mock_db = MagicMock()
        self.service.db = self.mock_db
        
        # Setup collections
        self.service.orders_collection = self.mock_db.orders
        self.service.products_collection = self.mock_db.products
        self.service.verification_sessions_collection = self.mock_db.verification_sessions
        self.service.cart_sessions_collection = self.mock_db.cart_sessions
    
    def test_create_order_atomic_success(self):
        """Test successful atomic order creation."""
        # Setup transaction mocks
        mock_session = MagicMock()
        mock_transaction = MagicMock()
        
        self.mock_db.client.start_session.return_value.__enter__.return_value = mock_session
        mock_session.start_transaction.return_value.__enter__.return_value = mock_transaction
        
        # Setup insert result
        mock_order_id = ObjectId()
        self.service.orders_collection.insert_one.return_value.inserted_id = mock_order_id
        
        # Setup update results
        self.service.products_collection.update_one.return_value.matched_count = 1
        
        # Test data
        items = [
            {'product_id': 'product_123', 'quantity': 2},
            {'product_id': 'product_456', 'quantity': 1}
        ]
        
        result = self.service._create_order_atomic(
            cart_session_id='cart_123',
            customer_info={'phone_number': '+1234567890', 'customer_name': 'John Doe'},
            items=items,
            totals={'subtotal': 25.48, 'total': 32.02},
            order_number='ORD-20250113-000001',
            verification_session_id='session_123'
        )
        
        assert result == mock_order_id
        
        # Verify order creation
        self.service.orders_collection.insert_one.assert_called_once()
        order_data = self.service.orders_collection.insert_one.call_args[0][0]
        assert order_data['order_number'] == 'ORD-20250113-000001'
        assert order_data['customer_phone'] == '+1234567890'
        assert order_data['status'] == 'pending'
        assert len(order_data['items']) == 2
        
        # Verify inventory updates
        assert self.service.products_collection.update_one.call_count == 2
        
        # Verify session cleanup
        self.service.verification_sessions_collection.update_one.assert_called_once()
        self.service.cart_sessions_collection.delete_one.assert_called_once()
        
        # Verify transaction commit
        mock_session.commit_transaction.assert_called_once()
    
    def test_create_order_atomic_rollback_on_failure(self):
        """Test transaction rollback on failure."""
        # Setup transaction mocks
        mock_session = MagicMock()
        mock_transaction = MagicMock()
        
        self.mock_db.client.start_session.return_value.__enter__.return_value = mock_session
        mock_session.start_transaction.return_value.__enter__.return_value = mock_transaction
        
        # Setup order creation success
        mock_order_id = ObjectId()
        self.service.orders_collection.insert_one.return_value.inserted_id = mock_order_id
        
        # Setup inventory update failure
        self.service.products_collection.update_one.return_value.matched_count = 0  # Not found
        
        items = [{'product_id': 'product_123', 'quantity': 2}]
        
        with pytest.raises(OrderCreationError) as exc_info:
            self.service._create_order_atomic(
                cart_session_id='cart_123',
                customer_info={'phone_number': '+1234567890', 'customer_name': 'John Doe'},
                items=items,
                totals={'subtotal': 9.98, 'total': 15.78},
                order_number='ORD-20250113-000001',
                verification_session_id='session_123'
            )
        
        assert exc_info.value.error_code == 'ORDER_019'
        assert 'not found during inventory update' in str(exc_info.value)
        
        # Transaction should be aborted automatically by context manager


class TestOrderManagement:
    """Test order status and cancellation methods."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    @patch('app.services.order_service.Order')
    def test_get_order_status_success(self, mock_order_class):
        """Test successful order status retrieval."""
        mock_order = MagicMock()
        mock_order.to_dict.return_value = {
            'order_number': 'ORD-20250113-000001',
            'status': 'pending'
        }
        
        mock_order_class.find_by_order_number.return_value = mock_order
        
        result = self.service.get_order_status('ORD-20250113-000001')
        
        assert result['success'] is True
        assert result['order']['order_number'] == 'ORD-20250113-000001'
        
        mock_order_class.find_by_order_number.assert_called_once_with('ORD-20250113-000001')
    
    @patch('app.services.order_service.Order')
    def test_get_order_status_not_found(self, mock_order_class):
        """Test order status retrieval when order not found."""
        mock_order_class.find_by_order_number.return_value = None
        
        with pytest.raises(OrderValidationError) as exc_info:
            self.service.get_order_status('ORD-20250113-000001')
        
        assert exc_info.value.error_code == 'ORDER_022'
        assert 'not found' in str(exc_info.value)
        assert exc_info.value.details['order_number'] == 'ORD-20250113-000001'


class TestErrorHandling:
    """Test error scenarios and exception handling."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
    
    def test_order_validation_error_structure(self):
        """Test OrderValidationError structure."""
        error = OrderValidationError(
            "Test error message",
            "ORDER_TEST",
            {"field": "test_field", "value": "test_value"}
        )
        
        assert str(error) == "Test error message"
        assert error.error_code == "ORDER_TEST"
        assert error.details["field"] == "test_field"
        assert error.details["value"] == "test_value"
    
    def test_order_creation_error_structure(self):
        """Test OrderCreationError structure."""
        error = OrderCreationError(
            "Test creation error",
            "ORDER_CREATE_TEST",
            {"operation": "test_operation"}
        )
        
        assert str(error) == "Test creation error"
        assert error.error_code == "ORDER_CREATE_TEST"
        assert error.details["operation"] == "test_operation"
    
    def test_order_creation_error_default_code(self):
        """Test OrderCreationError with default error code."""
        error = OrderCreationError("Test error without code")
        
        assert error.error_code == "ORDER_500"
        assert error.details == {}


class TestGetOrderService:
    """Test global order service instance management."""
    
    def test_get_order_service_singleton(self):
        """Test that get_order_service returns singleton instance."""
        service1 = get_order_service()
        service2 = get_order_service()
        
        assert service1 is service2
        assert isinstance(service1, OrderService)


class TestCompleteOrderCreationWorkflow:
    """Test complete order creation workflow integration."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = OrderService()
        
        # Setup all required mocks
        self.mock_db = MagicMock()
        self.service.db = self.mock_db
        self.service.orders_collection = self.mock_db.orders
        self.service.products_collection = self.mock_db.products
        self.service.verification_sessions_collection = self.mock_db.verification_sessions
        self.service.order_sequences_collection = self.mock_db.order_sequences
        self.service.cart_sessions_collection = self.mock_db.cart_sessions
    
    @patch('app.services.order_service.Order')
    @patch('app.services.order_service.Product')
    @patch('app.services.order_service.Cart')
    @patch('app.services.order_service.datetime')
    def test_create_order_complete_success_workflow(self, mock_datetime, mock_cart_class, 
                                                   mock_product_class, mock_order_class):
        """Test complete successful order creation workflow."""
        # Setup datetime
        mock_datetime.utcnow.return_value = datetime(2025, 1, 13, 15, 0, 0)
        
        # Setup verification session
        valid_session = {
            'session_id': 'session_123',
            'phone_number': '+1234567890',
            'verified': True,
            'expires_at': datetime(2025, 1, 13, 16, 0, 0),
            'used': False
        }
        self.service.verification_sessions_collection.find_one.return_value = valid_session
        
        # Setup cart
        mock_cart = MagicMock()
        mock_cart.expires_at = datetime(2025, 1, 13, 17, 0, 0)
        mock_cart_item = MagicMock()
        mock_cart_item.product_id = 'product_123'
        mock_cart_item.product_name = 'Organic Apples'
        mock_cart_item.quantity = 2
        mock_cart_item.price = Decimal('4.99')
        mock_cart.items = [mock_cart_item]
        mock_cart_class.find_by_session_id.return_value = mock_cart
        
        # Setup product
        mock_product = MagicMock()
        mock_product._id = ObjectId()
        mock_product.name = 'Organic Apples'
        mock_product.price = Decimal('4.99')
        mock_product.stock_quantity = 10
        mock_product.is_available = True
        mock_product_class.find_by_id.return_value = mock_product
        
        # Setup order number generation
        self.service.order_sequences_collection.find_one_and_update.return_value = {
            'sequence': 1
        }
        
        # Setup transaction
        mock_session = MagicMock()
        self.mock_db.client.start_session.return_value.__enter__.return_value = mock_session
        mock_session.start_transaction.return_value.__enter__.return_value = MagicMock()
        
        # Setup order creation
        mock_order_id = ObjectId()
        self.service.orders_collection.insert_one.return_value.inserted_id = mock_order_id
        self.service.products_collection.update_one.return_value.matched_count = 1
        
        # Setup created order
        mock_created_order = MagicMock()
        mock_created_order.to_dict.return_value = {
            'order_number': 'ORD-20250113-000001',
            'status': 'pending',
            'total': 15.78
        }
        mock_order_class.find_by_id.return_value = mock_created_order
        
        # Execute order creation
        result = self.service.create_order(
            cart_session_id='cart_123',
            customer_info={
                'phone_number': '+1234567890',
                'customer_name': 'John Doe',
                'email': 'john@example.com'
            },
            phone_verification_session_id='session_123'
        )
        
        # Verify result
        assert result['success'] is True
        assert result['order']['order_number'] == 'ORD-20250113-000001'
        assert 'Order ORD-20250113-000001 created successfully' in result['message']
        
        # Verify all steps were executed
        self.service.verification_sessions_collection.find_one.assert_called_once()
        mock_cart_class.find_by_session_id.assert_called_once_with('cart_123')
        mock_product_class.find_by_id.assert_called_once_with('product_123')
        self.service.orders_collection.insert_one.assert_called_once()
        self.service.products_collection.update_one.assert_called_once()
        self.service.verification_sessions_collection.update_one.assert_called_once()
        self.service.cart_sessions_collection.delete_one.assert_called_once()
        mock_order_class.find_by_id.assert_called_once_with(mock_order_id)