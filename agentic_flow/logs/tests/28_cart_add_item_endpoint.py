"""
Test Harness: Cart Add Item Endpoint

This test harness validates the POST /api/cart endpoint implementation
including route definition, cart model integration, validation,
and response format without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_cart_model_structure():
    """Test cart model file structure and class definition."""
    cart_model_file = 'backend/app/models/cart.py'
    
    test_results = {
        "file_exists": False,
        "cart_class_defined": False,
        "cart_item_class_defined": False,
        "required_methods": False,
        "imports_complete": False,
        "database_integration": False
    }
    
    try:
        if os.path.exists(cart_model_file):
            test_results["file_exists"] = True
            
            with open(cart_model_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find classes and methods
            tree = ast.parse(content)
            found_classes = []
            found_methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    found_classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    found_methods.append(node.name)
            
            test_results["cart_class_defined"] = "Cart" in found_classes
            test_results["cart_item_class_defined"] = "CartItem" in found_classes
            test_results["required_methods"] = all([
                "add_item" in found_methods,
                "find_by_session_id" in found_methods,
                "save" in found_methods,
                "to_dict" in found_methods
            ])
            test_results["imports_complete"] = all([
                "from app.database import get_database" in content,
                "from app.models.product import Product" in content,
                "from bson import ObjectId" in content
            ])
            test_results["database_integration"] = "COLLECTION_NAME" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_cart_routes_structure():
    """Test cart routes file structure and endpoint definition."""
    cart_routes_file = 'backend/app/routes/cart.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "add_to_cart_function": False,
        "post_route_decorator": False,
        "validation_decorator": False,
        "imports_complete": False,
        "schema_validation": False
    }
    
    try:
        if os.path.exists(cart_routes_file):
            test_results["file_exists"] = True
            
            with open(cart_routes_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find functions
            tree = ast.parse(content)
            found_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    found_functions.append(node.name)
            
            test_results["blueprint_defined"] = "cart_bp = Blueprint" in content
            test_results["add_to_cart_function"] = "add_to_cart" in found_functions
            test_results["post_route_decorator"] = "@cart_bp.route('/', methods=['POST'])" in content
            test_results["validation_decorator"] = "@validate_json" in content
            test_results["imports_complete"] = all([
                "from flask import Blueprint" in content,
                "from app.models.cart import Cart" in content,
                "from app.models.product import Product" in content,
                "from app.utils.validators import validate_json" in content
            ])
            test_results["schema_validation"] = "CART_ITEM_SCHEMA" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_endpoint_functionality():
    """Test endpoint functionality and validation logic."""
    cart_routes_file = 'backend/app/routes/cart.py'
    
    test_results = {
        "request_validation": False,
        "product_id_validation": False,
        "product_existence_check": False,
        "stock_availability_check": False,
        "cart_session_management": False,
        "cart_save_operation": False,
        "response_format": False,
        "error_handling": False
    }
    
    try:
        if os.path.exists(cart_routes_file):
            with open(cart_routes_file, 'r') as f:
                content = f.read()
            
            test_results["request_validation"] = "request.get_json()" in content
            test_results["product_id_validation"] = "ObjectId(product_id)" in content
            test_results["product_existence_check"] = "Product.find_by_id(product_id)" in content
            test_results["stock_availability_check"] = "product.is_available" in content and "stock_quantity" in content
            test_results["cart_session_management"] = "Cart.find_by_session_id" in content and "Cart()" in content
            test_results["cart_save_operation"] = "cart.save()" in content
            test_results["response_format"] = "success_response(" in content
            test_results["error_handling"] = "create_error_response(" in content and "try:" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_schema():
    """Test request validation schema definition."""
    cart_routes_file = 'backend/app/routes/cart.py'
    
    test_results = {
        "schema_defined": False,
        "product_id_validation": False,
        "quantity_validation": False,
        "session_id_optional": False,
        "required_fields": False,
        "additional_properties": False
    }
    
    try:
        if os.path.exists(cart_routes_file):
            with open(cart_routes_file, 'r') as f:
                content = f.read()
            
            test_results["schema_defined"] = "CART_ITEM_SCHEMA" in content
            test_results["product_id_validation"] = '"pattern": "^[0-9a-fA-F]{24}$"' in content
            test_results["quantity_validation"] = '"minimum": 1' in content and '"maximum": 100' in content
            test_results["session_id_optional"] = '"session_id"' in content and '"required": ["product_id", "quantity"]' in content
            test_results["required_fields"] = '"product_id", "quantity"' in content
            test_results["additional_properties"] = '"additionalProperties": False' in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_error_handling():
    """Test comprehensive error handling scenarios."""
    cart_routes_file = 'backend/app/routes/cart.py'
    
    test_results = {
        "invalid_product_id": False,
        "product_not_found": False,
        "product_unavailable": False,
        "out_of_stock": False,
        "validation_errors": False,
        "database_errors": False,
        "exception_logging": False
    }
    
    try:
        if os.path.exists(cart_routes_file):
            with open(cart_routes_file, 'r') as f:
                content = f.read()
            
            test_results["invalid_product_id"] = "Invalid product ID format" in content
            test_results["product_not_found"] = "Product not found" in content and "NOT_001" in content
            test_results["product_unavailable"] = "not available for purchase" in content
            test_results["out_of_stock"] = "out of stock" in content
            test_results["validation_errors"] = "VAL_" in content and "400" in content
            test_results["database_errors"] = "DB_001" in content and "Failed to save cart" in content
            test_results["exception_logging"] = "logging.error(" in content and "str(e)" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_cart_model_methods():
    """Test cart model method implementation."""
    cart_model_file = 'backend/app/models/cart.py'
    
    test_results = {
        "add_item_method": False,
        "quantity_validation": False,
        "stock_checking": False,
        "existing_item_update": False,
        "cart_limits": False,
        "session_expiry": False,
        "database_operations": False
    }
    
    try:
        if os.path.exists(cart_model_file):
            with open(cart_model_file, 'r') as f:
                content = f.read()
            
            test_results["add_item_method"] = "def add_item(" in content
            test_results["quantity_validation"] = "MAX_QUANTITY_PER_ITEM" in content
            test_results["stock_checking"] = "product.stock_quantity" in content
            test_results["existing_item_update"] = "existing_item.quantity" in content
            test_results["cart_limits"] = "MAX_ITEMS_PER_CART" in content
            test_results["session_expiry"] = "SESSION_EXPIRY_HOURS" in content and "expires_at" in content
            test_results["database_operations"] = "collection.insert_one" in content and "collection.update_one" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test cart blueprint registration in routes."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "routes_init_exists": False,
        "cart_import": False,
        "blueprint_registration": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            test_results["routes_init_exists"] = True
            
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["cart_import"] = "from .cart import cart_bp" in content
            test_results["blueprint_registration"] = "api.register_blueprint(cart_bp" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_additional_endpoints():
    """Test additional cart endpoints implementation."""
    cart_routes_file = 'backend/app/routes/cart.py'
    
    test_results = {
        "get_cart_endpoint": False,
        "update_item_endpoint": False,
        "clear_cart_endpoint": False,
        "session_validation": False,
        "cart_expiry_check": False
    }
    
    try:
        if os.path.exists(cart_routes_file):
            with open(cart_routes_file, 'r') as f:
                content = f.read()
            
            test_results["get_cart_endpoint"] = "get_cart_contents" in content and "methods=['GET']" in content
            test_results["update_item_endpoint"] = "update_cart_item" in content and "methods=['PUT']" in content
            test_results["clear_cart_endpoint"] = "clear_cart" in content and "methods=['DELETE']" in content
            test_results["session_validation"] = "len(session_id) != 24" in content
            test_results["cart_expiry_check"] = "cart.is_expired()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Cart Add Item Endpoint tests and return results."""
    print("Testing Cart Add Item Endpoint Implementation...")
    print("=" * 60)
    
    # Test 1: Cart Model Structure
    print("\\n1. Testing Cart Model Structure:")
    model_results = test_cart_model_structure()
    
    print(f"   ✓ File exists: {model_results['file_exists']}")
    print(f"   ✓ Cart class defined: {model_results['cart_class_defined']}")
    print(f"   ✓ CartItem class defined: {model_results['cart_item_class_defined']}")
    print(f"   ✓ Required methods: {model_results['required_methods']}")
    print(f"   ✓ Imports complete: {model_results['imports_complete']}")
    print(f"   ✓ Database integration: {model_results['database_integration']}")
    
    # Test 2: Cart Routes Structure
    print("\\n2. Testing Cart Routes Structure:")
    routes_results = test_cart_routes_structure()
    
    print(f"   ✓ File exists: {routes_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {routes_results['blueprint_defined']}")
    print(f"   ✓ Add to cart function: {routes_results['add_to_cart_function']}")
    print(f"   ✓ POST route decorator: {routes_results['post_route_decorator']}")
    print(f"   ✓ Validation decorator: {routes_results['validation_decorator']}")
    print(f"   ✓ Imports complete: {routes_results['imports_complete']}")
    print(f"   ✓ Schema validation: {routes_results['schema_validation']}")
    
    # Test 3: Endpoint Functionality
    print("\\n3. Testing Endpoint Functionality:")
    functionality_results = test_endpoint_functionality()
    
    print(f"   ✓ Request validation: {functionality_results['request_validation']}")
    print(f"   ✓ Product ID validation: {functionality_results['product_id_validation']}")
    print(f"   ✓ Product existence check: {functionality_results['product_existence_check']}")
    print(f"   ✓ Stock availability check: {functionality_results['stock_availability_check']}")
    print(f"   ✓ Cart session management: {functionality_results['cart_session_management']}")
    print(f"   ✓ Cart save operation: {functionality_results['cart_save_operation']}")
    print(f"   ✓ Response format: {functionality_results['response_format']}")
    print(f"   ✓ Error handling: {functionality_results['error_handling']}")
    
    # Test 4: Validation Schema
    print("\\n4. Testing Validation Schema:")
    schema_results = test_validation_schema()
    
    print(f"   ✓ Schema defined: {schema_results['schema_defined']}")
    print(f"   ✓ Product ID validation: {schema_results['product_id_validation']}")
    print(f"   ✓ Quantity validation: {schema_results['quantity_validation']}")
    print(f"   ✓ Session ID optional: {schema_results['session_id_optional']}")
    print(f"   ✓ Required fields: {schema_results['required_fields']}")
    print(f"   ✓ Additional properties: {schema_results['additional_properties']}")
    
    # Test 5: Error Handling
    print("\\n5. Testing Error Handling:")
    error_results = test_error_handling()
    
    print(f"   ✓ Invalid product ID: {error_results['invalid_product_id']}")
    print(f"   ✓ Product not found: {error_results['product_not_found']}")
    print(f"   ✓ Product unavailable: {error_results['product_unavailable']}")
    print(f"   ✓ Out of stock: {error_results['out_of_stock']}")
    print(f"   ✓ Validation errors: {error_results['validation_errors']}")
    print(f"   ✓ Database errors: {error_results['database_errors']}")
    print(f"   ✓ Exception logging: {error_results['exception_logging']}")
    
    # Test 6: Cart Model Methods
    print("\\n6. Testing Cart Model Methods:")
    methods_results = test_cart_model_methods()
    
    print(f"   ✓ Add item method: {methods_results['add_item_method']}")
    print(f"   ✓ Quantity validation: {methods_results['quantity_validation']}")
    print(f"   ✓ Stock checking: {methods_results['stock_checking']}")
    print(f"   ✓ Existing item update: {methods_results['existing_item_update']}")
    print(f"   ✓ Cart limits: {methods_results['cart_limits']}")
    print(f"   ✓ Session expiry: {methods_results['session_expiry']}")
    print(f"   ✓ Database operations: {methods_results['database_operations']}")
    
    # Test 7: Blueprint Registration
    print("\\n7. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Routes init exists: {blueprint_results['routes_init_exists']}")
    print(f"   ✓ Cart import: {blueprint_results['cart_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    
    # Test 8: Additional Endpoints
    print("\\n8. Testing Additional Endpoints:")
    additional_results = test_additional_endpoints()
    
    print(f"   ✓ GET cart endpoint: {additional_results['get_cart_endpoint']}")
    print(f"   ✓ Update item endpoint: {additional_results['update_item_endpoint']}")
    print(f"   ✓ Clear cart endpoint: {additional_results['clear_cart_endpoint']}")
    print(f"   ✓ Session validation: {additional_results['session_validation']}")
    print(f"   ✓ Cart expiry check: {additional_results['cart_expiry_check']}")
    
    # Calculate overall success
    all_tests = [
        model_results['file_exists'],
        model_results['cart_class_defined'],
        model_results['cart_item_class_defined'],
        model_results['required_methods'],
        model_results['imports_complete'],
        model_results['database_integration'],
        routes_results['file_exists'],
        routes_results['blueprint_defined'],
        routes_results['add_to_cart_function'],
        routes_results['post_route_decorator'],
        routes_results['validation_decorator'],
        routes_results['imports_complete'],
        routes_results['schema_validation'],
        functionality_results['request_validation'],
        functionality_results['product_id_validation'],
        functionality_results['product_existence_check'],
        functionality_results['stock_availability_check'],
        functionality_results['cart_session_management'],
        functionality_results['cart_save_operation'],
        functionality_results['response_format'],
        functionality_results['error_handling'],
        schema_results['schema_defined'],
        schema_results['product_id_validation'],
        schema_results['quantity_validation'],
        schema_results['session_id_optional'],
        schema_results['required_fields'],
        schema_results['additional_properties'],
        error_results['invalid_product_id'],
        error_results['product_not_found'],
        error_results['product_unavailable'],
        error_results['out_of_stock'],
        error_results['validation_errors'],
        error_results['database_errors'],
        error_results['exception_logging'],
        methods_results['add_item_method'],
        methods_results['quantity_validation'],
        methods_results['stock_checking'],
        methods_results['existing_item_update'],
        methods_results['cart_limits'],
        methods_results['session_expiry'],
        methods_results['database_operations'],
        blueprint_results['routes_init_exists'],
        blueprint_results['cart_import'],
        blueprint_results['blueprint_registration'],
        additional_results['get_cart_endpoint'],
        additional_results['update_item_endpoint'],
        additional_results['clear_cart_endpoint'],
        additional_results['session_validation'],
        additional_results['cart_expiry_check']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Cart Add Item Endpoint implementation PASSED")
        return True
    else:
        print("❌ Cart Add Item Endpoint implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)