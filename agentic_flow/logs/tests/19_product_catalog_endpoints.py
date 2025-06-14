"""
Test Harness: Product Catalog Endpoints

This test harness validates the product catalog endpoints implementation including
listing, search, details, and admin management without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_products_endpoints_structure():
    """Test products endpoints file structure and functions."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "required_endpoints": [],
        "missing_endpoints": [],
        "admin_decorator": False,
        "product_schema": False
    }
    
    required_endpoints = [
        'list_products', 'search_products', 'get_product', 
        'create_product', 'update_product', 'delete_product'
    ]
    
    try:
        if os.path.exists(products_file):
            test_results["file_exists"] = True
            
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find functions
            tree = ast.parse(content)
            found_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    found_functions.append(node.name)
            
            test_results["required_endpoints"] = [
                endpoint for endpoint in required_endpoints 
                if endpoint in found_functions
            ]
            test_results["missing_endpoints"] = [
                endpoint for endpoint in required_endpoints 
                if endpoint not in found_functions
            ]
            
            # Check for important components
            test_results["blueprint_defined"] = "products_bp = Blueprint" in content
            test_results["admin_decorator"] = "require_admin" in content
            test_results["product_schema"] = "PRODUCT_SCHEMA" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_catalog_endpoints():
    """Test public catalog endpoints (listing, search, details)."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "list_products_endpoint": False,
        "search_products_endpoint": False,
        "get_product_endpoint": False,
        "pagination_support": False,
        "filtering_support": False,
        "sorting_support": False,
        "text_search": False,
        "category_integration": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check catalog endpoints
            test_results["list_products_endpoint"] = "@products_bp.route('/', methods=['GET'])" in content
            test_results["search_products_endpoint"] = "@products_bp.route('/search', methods=['GET'])" in content
            test_results["get_product_endpoint"] = "@products_bp.route('/<product_id>', methods=['GET'])" in content
            
            # Check features
            test_results["pagination_support"] = "page" in content and "limit" in content
            test_results["filtering_support"] = "category_id" in content and "available_only" in content
            test_results["sorting_support"] = "sort_by" in content and "sort_order" in content
            test_results["text_search"] = "$text" in content and "$search" in content
            test_results["category_integration"] = "Category.find_by_id" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_admin_management_endpoints():
    """Test admin product management endpoints."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "create_product_endpoint": False,
        "update_product_endpoint": False,
        "delete_product_endpoint": False,
        "admin_authorization": False,
        "input_validation": False,
        "soft_delete": False,
        "category_validation": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check admin endpoints
            test_results["create_product_endpoint"] = "@products_bp.route('/', methods=['POST'])" in content
            test_results["update_product_endpoint"] = "@products_bp.route('/<product_id>', methods=['PUT'])" in content
            test_results["delete_product_endpoint"] = "@products_bp.route('/<product_id>', methods=['DELETE'])" in content
            
            # Check admin features
            test_results["admin_authorization"] = "@require_admin" in content
            test_results["input_validation"] = "@validate_json(PRODUCT_SCHEMA)" in content
            test_results["soft_delete"] = "product.delete()" in content
            test_results["category_validation"] = "Category.find_by_id" in content and "category" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_integration():
    """Test database and model integration."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "product_model_integration": False,
        "category_model_integration": False,
        "user_model_integration": False,
        "aggregation_pipeline": False,
        "text_index_usage": False,
        "pagination_logic": False,
        "error_handling": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check model integrations
            test_results["product_model_integration"] = "from app.models.product import Product" in content
            test_results["category_model_integration"] = "from app.models.category import Category" in content
            test_results["user_model_integration"] = "from app.models.user import User" in content
            
            # Check database features
            test_results["aggregation_pipeline"] = "pipeline" in content and "$facet" in content
            test_results["text_index_usage"] = "$text" in content and "textScore" in content
            test_results["pagination_logic"] = "skip" in content and "limit" in content
            test_results["error_handling"] = "create_error_response" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_and_security():
    """Test input validation and security features."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "json_schema_validation": False,
        "admin_role_check": False,
        "object_id_validation": False,
        "price_range_validation": False,
        "input_sanitization": False,
        "error_standardization": False,
        "logging_integration": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check validation features
            test_results["json_schema_validation"] = "PRODUCT_SCHEMA" in content and "@validate_json" in content
            test_results["admin_role_check"] = "User.ROLE_ADMIN" in content
            test_results["object_id_validation"] = "ObjectId" in content and "re.match" in content
            test_results["price_range_validation"] = "min_price" in content and "max_price" in content
            test_results["input_sanitization"] = "strip()" in content
            test_results["error_standardization"] = "create_error_response" in content
            test_results["logging_integration"] = "logging.info" in content and "logging.error" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_formatting():
    """Test response formatting and API consistency."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "success_response_format": False,
        "pagination_metadata": False,
        "category_embedding": False,
        "search_scoring": False,
        "product_dict_conversion": False,
        "status_codes": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check response formatting
            test_results["success_response_format"] = "success_response" in content
            test_results["pagination_metadata"] = "total_pages" in content and "has_next" in content
            test_results["category_embedding"] = "category" in content and "lookup" in content
            test_results["search_scoring"] = "search_score" in content and "textScore" in content
            test_results["product_dict_conversion"] = "to_dict()" in content
            test_results["status_codes"] = "200" in content and "201" in content and "404" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test blueprint registration in routes/__init__.py."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "products_import": False,
        "blueprint_registration": False,
        "url_prefix": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["products_import"] = "from .products import products_bp" in content
            test_results["blueprint_registration"] = "register_blueprint(products_bp" in content
            test_results["url_prefix"] = "url_prefix='/products'" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all product catalog endpoints tests and return results."""
    print("Testing Product Catalog Endpoints Implementation...")
    print("=" * 50)
    
    # Test 1: Endpoints Structure
    print("\n1. Testing Products Endpoints Structure:")
    structure_results = test_products_endpoints_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {structure_results['blueprint_defined']}")
    print(f"   ✓ Required endpoints found: {len(structure_results['required_endpoints'])}/6")
    print(f"   ✓ Missing endpoints: {structure_results['missing_endpoints']}")
    print(f"   ✓ Admin decorator: {structure_results['admin_decorator']}")
    print(f"   ✓ Product schema: {structure_results['product_schema']}")
    
    # Test 2: Catalog Endpoints
    print("\n2. Testing Catalog Endpoints:")
    catalog_results = test_catalog_endpoints()
    
    print(f"   ✓ List products endpoint: {catalog_results['list_products_endpoint']}")
    print(f"   ✓ Search products endpoint: {catalog_results['search_products_endpoint']}")
    print(f"   ✓ Get product endpoint: {catalog_results['get_product_endpoint']}")
    print(f"   ✓ Pagination support: {catalog_results['pagination_support']}")
    print(f"   ✓ Filtering support: {catalog_results['filtering_support']}")
    print(f"   ✓ Sorting support: {catalog_results['sorting_support']}")
    print(f"   ✓ Text search: {catalog_results['text_search']}")
    print(f"   ✓ Category integration: {catalog_results['category_integration']}")
    
    # Test 3: Admin Management Endpoints
    print("\n3. Testing Admin Management Endpoints:")
    admin_results = test_admin_management_endpoints()
    
    print(f"   ✓ Create product endpoint: {admin_results['create_product_endpoint']}")
    print(f"   ✓ Update product endpoint: {admin_results['update_product_endpoint']}")
    print(f"   ✓ Delete product endpoint: {admin_results['delete_product_endpoint']}")
    print(f"   ✓ Admin authorization: {admin_results['admin_authorization']}")
    print(f"   ✓ Input validation: {admin_results['input_validation']}")
    print(f"   ✓ Soft delete: {admin_results['soft_delete']}")
    print(f"   ✓ Category validation: {admin_results['category_validation']}")
    
    # Test 4: Database Integration
    print("\n4. Testing Database Integration:")
    db_results = test_database_integration()
    
    print(f"   ✓ Product model integration: {db_results['product_model_integration']}")
    print(f"   ✓ Category model integration: {db_results['category_model_integration']}")
    print(f"   ✓ User model integration: {db_results['user_model_integration']}")
    print(f"   ✓ Aggregation pipeline: {db_results['aggregation_pipeline']}")
    print(f"   ✓ Text index usage: {db_results['text_index_usage']}")
    print(f"   ✓ Pagination logic: {db_results['pagination_logic']}")
    print(f"   ✓ Error handling: {db_results['error_handling']}")
    
    # Test 5: Validation and Security
    print("\n5. Testing Validation and Security:")
    security_results = test_validation_and_security()
    
    print(f"   ✓ JSON schema validation: {security_results['json_schema_validation']}")
    print(f"   ✓ Admin role check: {security_results['admin_role_check']}")
    print(f"   ✓ ObjectId validation: {security_results['object_id_validation']}")
    print(f"   ✓ Price range validation: {security_results['price_range_validation']}")
    print(f"   ✓ Input sanitization: {security_results['input_sanitization']}")
    print(f"   ✓ Error standardization: {security_results['error_standardization']}")
    print(f"   ✓ Logging integration: {security_results['logging_integration']}")
    
    # Test 6: Response Formatting
    print("\n6. Testing Response Formatting:")
    response_results = test_response_formatting()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Pagination metadata: {response_results['pagination_metadata']}")
    print(f"   ✓ Category embedding: {response_results['category_embedding']}")
    print(f"   ✓ Search scoring: {response_results['search_scoring']}")
    print(f"   ✓ Product dict conversion: {response_results['product_dict_conversion']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    
    # Test 7: Blueprint Registration
    print("\n7. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Products import: {blueprint_results['products_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    print(f"   ✓ URL prefix: {blueprint_results['url_prefix']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['blueprint_defined'],
        len(structure_results['missing_endpoints']) == 0,
        structure_results['admin_decorator'],
        structure_results['product_schema'],
        catalog_results['list_products_endpoint'],
        catalog_results['search_products_endpoint'],
        catalog_results['get_product_endpoint'],
        catalog_results['pagination_support'],
        catalog_results['filtering_support'],
        catalog_results['text_search'],
        admin_results['create_product_endpoint'],
        admin_results['update_product_endpoint'],
        admin_results['delete_product_endpoint'],
        admin_results['admin_authorization'],
        admin_results['input_validation'],
        db_results['product_model_integration'],
        db_results['category_model_integration'],
        db_results['aggregation_pipeline'],
        db_results['text_index_usage'],
        security_results['json_schema_validation'],
        security_results['admin_role_check'],
        security_results['object_id_validation'],
        security_results['error_standardization'],
        response_results['success_response_format'],
        response_results['pagination_metadata'],
        response_results['product_dict_conversion'],
        blueprint_results['products_import'],
        blueprint_results['blueprint_registration']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Product Catalog Endpoints implementation PASSED")
        return True
    else:
        print("❌ Product Catalog Endpoints implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)