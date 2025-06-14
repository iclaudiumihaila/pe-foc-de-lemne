"""
Integration tests for Cart API endpoints.

This module contains comprehensive integration tests for all cart API endpoints
including successful scenarios, error handling, and edge cases.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime, timedelta

from app.models.cart import Cart, CartItem
from app.models.product import Product


class TestCartAPI:
    """Test suite for Cart API endpoints."""
    
    def test_add_item_to_cart_success_new_session(self, client):
        """Test successful item addition to new cart session."""
        product_id = '507f1f77bcf86cd799439011'
        
        # Mock product
        mock_product = MagicMock(spec=Product)
        mock_product._id = ObjectId(product_id)
        mock_product.name = 'Test Product'
        mock_product.price = 29.99
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        # Mock cart operations
        mock_cart = MagicMock(spec=Cart)
        mock_cart.session_id = '507f1f77bcf86cd799439012'
        mock_cart.add_item.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {
            'session_id': '507f1f77bcf86cd799439012',
            'items': [
                {
                    'product_id': product_id,
                    'product_name': 'Test Product',
                    'quantity': 2,
                    'price': 29.99,
                    'subtotal': 59.98
                }
            ],
            'total_items': 2,
            'total_amount': 59.98,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                with patch('app.models.cart.Cart') as mock_cart_class:
                    # Setup mocks
                    mock_find_product.return_value = mock_product
                    mock_find_cart.return_value = None  # No existing session
                    mock_cart_class.return_value = mock_cart
                    
                    # Make request
                    response = client.post('/api/cart/', 
                        json={
                            'product_id': product_id,
                            'quantity': 2
                        },
                        content_type='application/json'
                    )
                    
                    # Assertions
                    assert response.status_code == 200
                    
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert 'data' in data
                    assert 'session_id' in data['data']
                    assert 'cart' in data['data']
                    assert data['data']['cart']['total_items'] == 2
                    assert data['data']['cart']['total_amount'] == 59.98
                    
                    # Verify cart operations
                    mock_cart.add_item.assert_called_once_with(product_id, 2)
                    mock_cart.save.assert_called_once()
    
    def test_add_item_to_existing_cart(self, client):
        """Test adding item to existing cart session."""
        product_id = '507f1f77bcf86cd799439011'
        session_id = '507f1f77bcf86cd799439012'
        
        # Mock product
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        # Mock existing cart
        mock_cart = MagicMock(spec=Cart)
        mock_cart.session_id = session_id
        mock_cart.add_item.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {
            'session_id': session_id,
            'items': [],
            'total_items': 1,
            'total_amount': 29.99
        }
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                mock_find_product.return_value = mock_product
                mock_find_cart.return_value = mock_cart
                
                response = client.post('/api/cart/', 
                    json={
                        'product_id': product_id,
                        'quantity': 1,
                        'session_id': session_id
                    },
                    content_type='application/json'
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['data']['session_id'] == session_id
    
    def test_add_item_invalid_product_id(self, client):
        """Test adding item with invalid product ID format."""
        response = client.post('/api/cart/', 
            json={
                'product_id': 'invalid_id',
                'quantity': 1
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert 'Invalid product ID format' in data['error']['message']
    
    def test_add_item_product_not_found(self, client):
        """Test adding non-existent product to cart."""
        product_id = '507f1f77bcf86cd799439999'
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            mock_find_product.return_value = None
            
            response = client.post('/api/cart/', 
                json={
                    'product_id': product_id,
                    'quantity': 1
                },
                content_type='application/json'
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_001'
            assert 'Product not found' in data['error']['message']
    
    def test_add_item_product_unavailable(self, client):
        """Test adding unavailable product to cart."""
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = False
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            mock_find_product.return_value = mock_product
            
            response = client.post('/api/cart/', 
                json={
                    'product_id': product_id,
                    'quantity': 1
                },
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'VAL_002'
            assert 'not available for purchase' in data['error']['message']
    
    def test_add_item_out_of_stock(self, client):
        """Test adding out-of-stock product to cart."""
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 0
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            mock_find_product.return_value = mock_product
            
            response = client.post('/api/cart/', 
                json={
                    'product_id': product_id,
                    'quantity': 1
                },
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'VAL_003'
            assert 'out of stock' in data['error']['message']
    
    def test_add_item_validation_error(self, client):
        """Test cart validation errors (quantity limits, etc.)."""
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.add_item.side_effect = ValueError("Quantity must be between 1 and 100")
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                with patch('app.models.cart.Cart') as mock_cart_class:
                    mock_find_product.return_value = mock_product
                    mock_find_cart.return_value = None
                    mock_cart_class.return_value = mock_cart
                    
                    response = client.post('/api/cart/', 
                        json={
                            'product_id': product_id,
                            'quantity': 1
                        },
                        content_type='application/json'
                    )
                    
                    assert response.status_code == 400
                    data = json.loads(response.data)
                    assert data['success'] is False
                    assert data['error']['code'] == 'VAL_004'
    
    def test_get_cart_contents_success(self, client):
        """Test successful cart contents retrieval."""
        session_id = '507f1f77bcf86cd799439011'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.is_expired.return_value = False
        mock_cart.total_items = 2
        mock_cart.to_dict.return_value = {
            'session_id': session_id,
            'items': [
                {
                    'product_id': '507f1f77bcf86cd799439012',
                    'product_name': 'Test Product',
                    'quantity': 2,
                    'price': 29.99,
                    'subtotal': 59.98
                }
            ],
            'total_items': 2,
            'total_amount': 59.98
        }
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.get(f'/api/cart/{session_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['session_id'] == session_id
            assert data['data']['total_items'] == 2
    
    def test_get_cart_invalid_session_format(self, client):
        """Test cart retrieval with invalid session ID format."""
        response = client.get('/api/cart/invalid_session')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'VAL_001'
        assert 'Invalid session ID format' in data['error']['message']
    
    def test_get_cart_session_not_found(self, client):
        """Test cart retrieval for non-existent session."""
        session_id = '507f1f77bcf86cd799439999'
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = None
            
            response = client.get(f'/api/cart/{session_id}')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_002'
            assert 'Cart session not found' in data['error']['message']
    
    def test_get_cart_session_expired(self, client):
        """Test cart retrieval for expired session."""
        session_id = '507f1f77bcf86cd799439011'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.is_expired.return_value = True
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.get(f'/api/cart/{session_id}')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'CART_002'
            assert 'expired' in data['error']['message']
    
    def test_update_cart_item_success(self, client):
        """Test successful cart item quantity update."""
        session_id = '507f1f77bcf86cd799439011'
        product_id = '507f1f77bcf86cd799439012'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.update_item_quantity.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {
            'session_id': session_id,
            'items': [],
            'total_items': 3,
            'total_amount': 89.97
        }
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.put(f'/api/cart/{session_id}/item/{product_id}',
                json={'quantity': 3},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'quantity updated successfully' in data['message']
            
            mock_cart.update_item_quantity.assert_called_once_with(product_id, 3)
    
    def test_remove_cart_item_with_zero_quantity(self, client):
        """Test removing item by setting quantity to zero."""
        session_id = '507f1f77bcf86cd799439011'
        product_id = '507f1f77bcf86cd799439012'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.remove_item.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {
            'session_id': session_id,
            'items': [],
            'total_items': 0,
            'total_amount': 0
        }
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.put(f'/api/cart/{session_id}/item/{product_id}',
                json={'quantity': 0},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'removed from cart' in data['message']
            
            mock_cart.remove_item.assert_called_once_with(product_id)
    
    def test_update_cart_item_not_found(self, client):
        """Test updating non-existent cart item."""
        session_id = '507f1f77bcf86cd799439011'
        product_id = '507f1f77bcf86cd799439999'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.update_item_quantity.return_value = False
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.put(f'/api/cart/{session_id}/item/{product_id}',
                json={'quantity': 1},
                content_type='application/json'
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_003'
            assert 'Item not found in cart' in data['error']['message']
    
    def test_clear_cart_success(self, client):
        """Test successful cart clearing."""
        session_id = '507f1f77bcf86cd799439011'
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.clear.return_value = None
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {
            'session_id': session_id,
            'items': [],
            'total_items': 0,
            'total_amount': 0
        }
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = mock_cart
            
            response = client.delete(f'/api/cart/{session_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Cart cleared successfully' in data['message']
            assert data['data']['total_items'] == 0
            
            mock_cart.clear.assert_called_once()
    
    def test_clear_cart_not_found(self, client):
        """Test clearing non-existent cart."""
        session_id = '507f1f77bcf86cd799439999'
        
        with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
            mock_find_cart.return_value = None
            
            response = client.delete(f'/api/cart/{session_id}')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'NOT_002'
    
    def test_cart_save_failure(self, client):
        """Test cart save failure handling."""
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.add_item.return_value = True
        mock_cart.save.return_value = False  # Save fails
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                with patch('app.models.cart.Cart') as mock_cart_class:
                    mock_find_product.return_value = mock_product
                    mock_find_cart.return_value = None
                    mock_cart_class.return_value = mock_cart
                    
                    response = client.post('/api/cart/', 
                        json={
                            'product_id': product_id,
                            'quantity': 1
                        },
                        content_type='application/json'
                    )
                    
                    assert response.status_code == 500
                    data = json.loads(response.data)
                    assert data['success'] is False
                    assert data['error']['code'] == 'DB_001'
                    assert 'Failed to save cart' in data['error']['message']
    
    def test_response_format_consistency(self, client):
        """Test that all responses follow the standard API format."""
        # Test success response format
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.session_id = '507f1f77bcf86cd799439012'
        mock_cart.add_item.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {'session_id': '507f1f77bcf86cd799439012'}
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                with patch('app.models.cart.Cart') as mock_cart_class:
                    mock_find_product.return_value = mock_product
                    mock_find_cart.return_value = None
                    mock_cart_class.return_value = mock_cart
                    
                    response = client.post('/api/cart/', 
                        json={
                            'product_id': product_id,
                            'quantity': 1
                        },
                        content_type='application/json'
                    )
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    
                    # Verify standard API response format
                    assert 'success' in data
                    assert 'data' in data
                    assert 'message' in data
                    assert isinstance(data['success'], bool)
                    assert isinstance(data['data'], dict)
                    assert isinstance(data['message'], str)
    
    def test_request_validation_schema(self, client):
        """Test request validation against JSON schema."""
        # Test missing required fields
        response = client.post('/api/cart/', 
            json={'quantity': 1},  # Missing product_id
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        # Test invalid quantity type
        response = client.post('/api/cart/', 
            json={
                'product_id': '507f1f77bcf86cd799439011',
                'quantity': 'invalid'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_logging_integration(self, client):
        """Test that proper logging occurs during cart operations."""
        product_id = '507f1f77bcf86cd799439011'
        
        mock_product = MagicMock(spec=Product)
        mock_product.is_available = True
        mock_product.stock_quantity = 10
        
        mock_cart = MagicMock(spec=Cart)
        mock_cart.session_id = '507f1f77bcf86cd799439012'
        mock_cart.add_item.return_value = True
        mock_cart.save.return_value = True
        mock_cart.to_dict.return_value = {'session_id': '507f1f77bcf86cd799439012'}
        
        with patch('app.models.product.Product.find_by_id') as mock_find_product:
            with patch('app.models.cart.Cart.find_by_session_id') as mock_find_cart:
                with patch('app.models.cart.Cart') as mock_cart_class:
                    with patch('app.routes.cart.logging') as mock_logging:
                        mock_find_product.return_value = mock_product
                        mock_find_cart.return_value = None
                        mock_cart_class.return_value = mock_cart
                        
                        response = client.post('/api/cart/', 
                            json={
                                'product_id': product_id,
                                'quantity': 1
                            },
                            content_type='application/json'
                        )
                        
                        assert response.status_code == 200
                        
                        # Verify logging calls were made
                        mock_logging.info.assert_called()
                        log_call = mock_logging.info.call_args[0][0]
                        assert 'Item added to cart:' in log_call