"""
Integration tests for Categories API endpoints.

This module contains comprehensive integration tests for all categories API endpoints
including successful scenarios, error handling, and edge cases.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime

from app.models.category import Category


class TestCategoriesAPI:
    """Test suite for Categories API endpoints."""
    
    def test_list_categories_success(self, client):
        """Test successful category listing with default parameters."""
        # Mock category data
        mock_categories = [
            {
                '_id': ObjectId('507f1f77bcf86cd799439011'),
                'name': 'Vegetables',
                'slug': 'vegetables',
                'description': 'Fresh organic vegetables',
                'image_url': 'vegetables.jpg',
                'status': 'active',
                'display_order': 1,
                'product_count': 5,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                '_id': ObjectId('507f1f77bcf86cd799439012'),
                'name': 'Fruits',
                'slug': 'fruits',
                'description': 'Fresh seasonal fruits',
                'image_url': 'fruits.jpg',
                'status': 'active',
                'display_order': 2,
                'product_count': 8,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            # Setup mock categories
            mock_category_instances = []
            for cat_data in mock_categories:
                mock_cat = MagicMock(spec=Category)
                mock_cat.to_dict.return_value = {
                    '_id': str(cat_data['_id']),
                    'name': cat_data['name'],
                    'slug': cat_data['slug'],
                    'description': cat_data['description'],
                    'image_url': cat_data['image_url'],
                    'status': cat_data['status'],
                    'display_order': cat_data['display_order'],
                    'created_at': cat_data['created_at'].isoformat() + 'Z',
                    'updated_at': cat_data['updated_at'].isoformat() + 'Z'
                }
                mock_cat.product_count = cat_data['product_count']
                mock_cat.update_product_count.return_value = None
                mock_category_instances.append(mock_cat)
            
            mock_find_all.return_value = mock_category_instances
            
            # Make request
            response = client.get('/api/categories/')
            
            # Assertions
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            assert 'categories' in data['data']
            assert len(data['data']['categories']) == 2
            assert data['data']['total_count'] == 2
            
            # Verify category data
            category = data['data']['categories'][0]
            assert category['name'] == 'Vegetables'
            assert category['slug'] == 'vegetables'
            assert category['product_count'] == 5
            
            # Verify filters in response
            assert data['data']['filters']['active_only'] is True
            assert data['data']['filters']['include_counts'] is True
    
    def test_list_categories_active_only_false(self, client):
        """Test category listing with active_only=false."""
        mock_categories = [
            MagicMock(spec=Category),
            MagicMock(spec=Category)
        ]
        
        # Setup mock return values
        for i, mock_cat in enumerate(mock_categories):
            mock_cat.to_dict.return_value = {
                '_id': f'507f1f77bcf86cd79943901{i}',
                'name': f'Category {i}',
                'status': 'active' if i == 0 else 'inactive'
            }
            mock_cat.product_count = 0
            mock_cat.update_product_count.return_value = None
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.return_value = mock_categories
            
            response = client.get('/api/categories/?active_only=false')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['filters']['active_only'] is False
            
            # Verify find_all was called with active_only=False
            mock_find_all.assert_called_once_with(active_only=False)
    
    def test_list_categories_include_counts_false(self, client):
        """Test category listing with include_counts=false."""
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {
            '_id': '507f1f77bcf86cd799439011',
            'name': 'Test Category'
        }
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.return_value = [mock_category]
            
            response = client.get('/api/categories/?include_counts=false')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['filters']['include_counts'] is False
            
            # Verify update_product_count was not called
            mock_category.update_product_count.assert_not_called()
    
    def test_list_categories_empty_result(self, client):
        """Test category listing when no categories exist."""
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.return_value = []
            
            response = client.get('/api/categories/')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['categories'] == []
            assert data['data']['total_count'] == 0
    
    def test_list_categories_database_error(self, client):
        """Test category listing when database error occurs."""
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.side_effect = Exception("Database connection failed")
            
            response = client.get('/api/categories/')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'DB_001'
            assert 'Failed to retrieve categories' in data['error']['message']
    
    def test_get_category_by_id_success(self, client):
        """Test successful category retrieval by ObjectId."""
        category_id = '507f1f77bcf86cd799439011'
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {
            '_id': category_id,
            'name': 'Test Category',
            'slug': 'test-category',
            'description': 'Test description',
            'status': 'active'
        }
        mock_category.category_id = ObjectId(category_id)
        
        # Mock the sub-category aggregation result
        mock_subcategories = []
        
        with patch('app.models.category.Category.find_by_id') as mock_find_by_id:
            with patch('app.models.category.Category.find_by_slug') as mock_find_by_slug:
                with patch('app.database.get_database') as mock_get_db:
                    # Setup mocks
                    mock_find_by_id.return_value = mock_category
                    mock_find_by_slug.return_value = None
                    
                    # Mock database aggregation for subcategories
                    mock_db = MagicMock()
                    mock_collection = MagicMock()
                    mock_db.__getitem__.return_value = mock_collection
                    mock_collection.aggregate.return_value = [{'subcategories': mock_subcategories}]
                    mock_get_db.return_value = mock_db
                    
                    response = client.get(f'/api/categories/{category_id}')
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert data['data']['category']['name'] == 'Test Category'
                    assert data['data']['category']['slug'] == 'test-category'
    
    def test_get_category_by_slug_success(self, client):
        """Test successful category retrieval by slug."""
        category_slug = 'test-category'
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {
            '_id': '507f1f77bcf86cd799439011',
            'name': 'Test Category',
            'slug': category_slug,
            'description': 'Test description',
            'status': 'active'
        }
        
        with patch('app.models.category.Category.find_by_id') as mock_find_by_id:
            with patch('app.models.category.Category.find_by_slug') as mock_find_by_slug:
                with patch('app.database.get_database') as mock_get_db:
                    # Setup mocks for slug-based lookup
                    mock_find_by_id.return_value = None  # ID lookup fails
                    mock_find_by_slug.return_value = mock_category  # Slug lookup succeeds
                    
                    # Mock database for subcategories
                    mock_db = MagicMock()
                    mock_collection = MagicMock()
                    mock_db.__getitem__.return_value = mock_collection
                    mock_collection.aggregate.return_value = [{'subcategories': []}]
                    mock_get_db.return_value = mock_db
                    
                    response = client.get(f'/api/categories/{category_slug}')
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert data['data']['category']['slug'] == category_slug
    
    def test_get_category_not_found(self, client):
        """Test category retrieval when category doesn't exist."""
        category_id = '507f1f77bcf86cd799439999'
        
        with patch('app.models.category.Category.find_by_id') as mock_find_by_id:
            with patch('app.models.category.Category.find_by_slug') as mock_find_by_slug:
                mock_find_by_id.return_value = None
                mock_find_by_slug.return_value = None
                
                response = client.get(f'/api/categories/{category_id}')
                
                assert response.status_code == 404
                data = json.loads(response.data)
                assert data['success'] is False
                assert data['error']['code'] == 'NOT_001'
                assert 'Category not found' in data['error']['message']
    
    def test_get_category_database_error(self, client):
        """Test category retrieval when database error occurs."""
        category_id = '507f1f77bcf86cd799439011'
        
        with patch('app.models.category.Category.find_by_id') as mock_find_by_id:
            mock_find_by_id.side_effect = Exception("Database connection failed")
            
            response = client.get(f'/api/categories/{category_id}')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error']['code'] == 'DB_001'
    
    def test_response_format_consistency(self, client):
        """Test that all responses follow the standard API format."""
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {'_id': '123', 'name': 'Test'}
        mock_category.product_count = 0
        mock_category.update_product_count.return_value = None
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.return_value = [mock_category]
            
            response = client.get('/api/categories/')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify standard API response format
            assert 'success' in data
            assert 'data' in data
            assert 'message' in data
            assert isinstance(data['success'], bool)
            assert isinstance(data['data'], dict)
            assert isinstance(data['message'], str)
    
    def test_query_parameter_validation(self, client):
        """Test query parameter parsing and validation."""
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {'_id': '123', 'name': 'Test'}
        mock_category.product_count = 0
        mock_category.update_product_count.return_value = None
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            mock_find_all.return_value = [mock_category]
            
            # Test various parameter combinations
            test_cases = [
                ('?active_only=true&include_counts=true', True, True),
                ('?active_only=false&include_counts=false', False, False),
                ('?active_only=1&include_counts=0', True, False),
                ('', True, True)  # Default values
            ]
            
            for query_string, expected_active, expected_counts in test_cases:
                response = client.get(f'/api/categories/{query_string}')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['data']['filters']['active_only'] == expected_active
                assert data['data']['filters']['include_counts'] == expected_counts
    
    def test_logging_integration(self, client):
        """Test that proper logging occurs during API operations."""
        mock_category = MagicMock(spec=Category)
        mock_category.to_dict.return_value = {'_id': '123', 'name': 'Test'}
        mock_category.product_count = 0
        mock_category.update_product_count.return_value = None
        
        with patch('app.models.category.Category.find_all') as mock_find_all:
            with patch('app.routes.categories.logging') as mock_logging:
                mock_find_all.return_value = [mock_category]
                
                response = client.get('/api/categories/')
                
                assert response.status_code == 200
                
                # Verify logging calls were made
                mock_logging.info.assert_called()
                log_call = mock_logging.info.call_args[0][0]
                assert 'Categories listed:' in log_call