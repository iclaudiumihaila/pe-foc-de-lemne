# Task 30: Create cart API integration tests

## Task Details
- **ID**: 30_cart_endpoints_integration_tests
- **Title**: Create cart API integration tests
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Cart get contents endpoint

## Objective
Create comprehensive integration tests for the cart API endpoints to ensure they function correctly end-to-end with proper database integration, request/response handling, and error scenarios.

## Requirements
1. **Test File**: `backend/tests/test_cart_api.py`
2. **Test Framework**: pytest with Flask test client
3. **Coverage**: All cart endpoints (POST /api/cart, GET /api/cart/:session, PUT, DELETE)
4. **Test Scenarios**: 
   - Successful requests with valid data
   - Error scenarios (invalid data, not found, validation errors)
   - Database integration validation
   - Response format verification
   - Session management testing
5. **Database**: Use test database with sample data
6. **Mocking**: Mock Product model for validation testing

## Technical Implementation
- **Test Framework**: pytest with Flask-Testing
- **Database**: MongoDB test database with fixtures
- **HTTP Client**: Flask test client for API requests
- **Assertions**: Validate status codes, response structure, and data integrity

## Test Scenarios to Cover

### 1. POST /api/cart Tests
- ✅ Add item to cart successfully (new session)
- ✅ Add item to existing cart session
- ✅ Handle invalid product ID format
- ✅ Handle non-existent product
- ✅ Handle out-of-stock product
- ✅ Handle invalid quantity values
- ✅ Validate response format and session creation

### 2. GET /api/cart/:session Tests
- ✅ Get cart contents successfully
- ✅ Handle invalid session ID format
- ✅ Handle non-existent session
- ✅ Handle expired session
- ✅ Validate response format and cart data

### 3. PUT /api/cart/:session/item/:product Tests
- ✅ Update item quantity successfully
- ✅ Remove item with quantity 0
- ✅ Handle invalid session/product IDs
- ✅ Handle non-existent cart or item
- ✅ Validate stock checking on updates

### 4. DELETE /api/cart/:session Tests
- ✅ Clear cart successfully
- ✅ Handle non-existent session
- ✅ Validate empty cart response

### 5. Error Handling Tests
- ✅ Database connection failures
- ✅ Invalid parameter validation
- ✅ Proper HTTP status codes
- ✅ Error response format consistency

## Expected Test Structure
```python
import pytest
from unittest.mock import patch, MagicMock
from app.models.product import Product
from app.models.cart import Cart

class TestCartAPI:
    def test_add_item_to_cart_success(self):
        # Test successful item addition
        pass
    
    def test_add_item_invalid_product_id(self):
        # Test invalid product ID handling
        pass
    
    def test_get_cart_contents_success(self):
        # Test cart retrieval
        pass
    
    def test_cart_session_management(self):
        # Test session creation and persistence
        pass
```

## Testing Criteria
1. All test cases pass successfully
2. Proper HTTP status code validation (200, 400, 404, 500)
3. Response format matches API specifications
4. Database integration works correctly
5. Error scenarios are handled appropriately
6. Test coverage includes all endpoint variations
7. Cart model integration testing

## Success Criteria
- Complete test file created at `backend/tests/test_cart_api.py`
- All integration tests pass when executed
- Comprehensive coverage of cart API functionality
- Proper test database setup and teardown
- Integration with existing test infrastructure