"""
Test Harness: Category Management Endpoints

This test harness validates the category management endpoints implementation including
listing, details, product relationships, and admin management without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_categories_endpoints_structure():
    """Test categories endpoints file structure and functions."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "required_endpoints": [],
        "missing_endpoints": [],
        "admin_decorator": False,
        "category_schema": False
    }
    
    required_endpoints = [
        'list_categories', 'get_category', 'get_category_products',
        'create_category', 'update_category', 'delete_category'
    ]
    
    try:
        if os.path.exists(categories_file):
            test_results["file_exists"] = True
            
            with open(categories_file, 'r') as f:
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
            test_results["blueprint_defined"] = "categories_bp = Blueprint" in content
            test_results["admin_decorator"] = "require_admin" in content
            test_results["category_schema"] = "CATEGORY_SCHEMA" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_public_category_endpoints():
    """Test public category endpoints (listing, details, products)."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "list_categories_endpoint": False,
        "get_category_endpoint": False,
        "get_category_products_endpoint": False,
        "product_count_support": False,
        "pagination_support": False,
        "slug_support": False,
        "category_model_integration": False,
        "product_model_integration": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check public endpoints
            test_results["list_categories_endpoint"] = "@categories_bp.route('/', methods=['GET'])" in content
            test_results["get_category_endpoint"] = "@categories_bp.route('/<category_id>', methods=['GET'])" in content
            test_results["get_category_products_endpoint"] = "@categories_bp.route('/<category_id>/products', methods=['GET'])" in content
            
            # Check features
            test_results["product_count_support"] = "update_product_count" in content
            test_results["pagination_support"] = "page" in content and "limit" in content
            test_results["slug_support"] = "find_by_slug" in content
            test_results["category_model_integration"] = "Category.find_by_id" in content
            test_results["product_model_integration"] = "Product(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_admin_management_endpoints():
    """Test admin category management endpoints."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "create_category_endpoint": False,
        "update_category_endpoint": False,
        "delete_category_endpoint": False,
        "admin_authorization": False,
        "input_validation": False,
        "product_relationship_check": False,
        "soft_delete": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check admin endpoints
            test_results["create_category_endpoint"] = "@categories_bp.route('/', methods=['POST'])" in content
            test_results["update_category_endpoint"] = "@categories_bp.route('/<category_id>', methods=['PUT'])" in content
            test_results["delete_category_endpoint"] = "@categories_bp.route('/<category_id>', methods=['DELETE'])" in content
            
            # Check admin features
            test_results["admin_authorization"] = "@require_admin" in content
            test_results["input_validation"] = "@validate_json(CATEGORY_SCHEMA)" in content
            test_results["product_relationship_check"] = "product_count" in content and "Cannot delete category" in content
            test_results["soft_delete"] = "category.delete()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_product_relationship_handling():
    """Test category-product relationship handling."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "product_count_calculation": False,
        "category_products_listing": False,
        "deletion_constraint": False,
        "aggregation_pipeline": False,
        "product_embedding": False,
        "relationship_validation": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check relationship handling
            test_results["product_count_calculation"] = "update_product_count" in content
            test_results["category_products_listing"] = "get_category_products" in content
            test_results["deletion_constraint"] = "product_count > 0" in content and "409" in content
            test_results["aggregation_pipeline"] = "pipeline" in content and "$facet" in content
            test_results["product_embedding"] = "category" in content and "products" in content
            test_results["relationship_validation"] = "category_id" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_and_security():
    """Test input validation and security features."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "json_schema_validation": False,
        "admin_role_check": False,
        "object_id_validation": False,
        "slug_validation": False,
        "input_sanitization": False,
        "error_standardization": False,
        "logging_integration": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check validation features
            test_results["json_schema_validation"] = "CATEGORY_SCHEMA" in content and "@validate_json" in content
            test_results["admin_role_check"] = "User.ROLE_ADMIN" in content
            test_results["object_id_validation"] = "ObjectId" in content and "re.match" in content
            test_results["slug_validation"] = "find_by_slug" in content
            test_results["input_sanitization"] = "strip()" in content
            test_results["error_standardization"] = "create_error_response" in content
            test_results["logging_integration"] = "logging.info" in content and "logging.error" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_formatting():
    """Test response formatting and API consistency."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "success_response_format": False,
        "pagination_metadata": False,
        "category_dict_conversion": False,
        "product_embedding": False,
        "status_codes": False,
        "error_handling": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check response formatting
            test_results["success_response_format"] = "success_response" in content
            test_results["pagination_metadata"] = "total_pages" in content and "has_next" in content
            test_results["category_dict_conversion"] = "to_dict()" in content
            test_results["product_embedding"] = "category" in content and "products" in content
            test_results["status_codes"] = "200" in content and "201" in content and "404" in content and "409" in content
            test_results["error_handling"] = "create_error_response" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test blueprint registration in routes/__init__.py."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "categories_import": False,
        "blueprint_registration": False,
        "url_prefix": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["categories_import"] = "from .categories import categories_bp" in content
            test_results["blueprint_registration"] = "register_blueprint(categories_bp" in content
            test_results["url_prefix"] = "url_prefix='/categories'" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_additional_features():
    """Test additional features like product count refresh."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "product_count_refresh": False,
        "maintenance_endpoint": False,
        "admin_maintenance": False,
        "count_synchronization": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check additional features
            test_results["product_count_refresh"] = "refresh_category_product_count" in content
            test_results["maintenance_endpoint"] = "product-count" in content and "POST" in content
            test_results["admin_maintenance"] = "@require_admin" in content and "refresh" in content
            test_results["count_synchronization"] = "old_count" in content and "new_count" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all category management endpoints tests and return results."""
    print("Testing Category Management Endpoints Implementation...")
    print("=" * 50)
    
    # Test 1: Endpoints Structure
    print("\n1. Testing Categories Endpoints Structure:")
    structure_results = test_categories_endpoints_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {structure_results['blueprint_defined']}")
    print(f"   ✓ Required endpoints found: {len(structure_results['required_endpoints'])}/6")
    print(f"   ✓ Missing endpoints: {structure_results['missing_endpoints']}")
    print(f"   ✓ Admin decorator: {structure_results['admin_decorator']}")
    print(f"   ✓ Category schema: {structure_results['category_schema']}")
    
    # Test 2: Public Category Endpoints
    print("\n2. Testing Public Category Endpoints:")
    public_results = test_public_category_endpoints()
    
    print(f"   ✓ List categories endpoint: {public_results['list_categories_endpoint']}")
    print(f"   ✓ Get category endpoint: {public_results['get_category_endpoint']}")
    print(f"   ✓ Get category products endpoint: {public_results['get_category_products_endpoint']}")
    print(f"   ✓ Product count support: {public_results['product_count_support']}")
    print(f"   ✓ Pagination support: {public_results['pagination_support']}")
    print(f"   ✓ Slug support: {public_results['slug_support']}")
    print(f"   ✓ Category model integration: {public_results['category_model_integration']}")
    print(f"   ✓ Product model integration: {public_results['product_model_integration']}")
    
    # Test 3: Admin Management Endpoints
    print("\n3. Testing Admin Management Endpoints:")
    admin_results = test_admin_management_endpoints()
    
    print(f"   ✓ Create category endpoint: {admin_results['create_category_endpoint']}")
    print(f"   ✓ Update category endpoint: {admin_results['update_category_endpoint']}")
    print(f"   ✓ Delete category endpoint: {admin_results['delete_category_endpoint']}")
    print(f"   ✓ Admin authorization: {admin_results['admin_authorization']}")
    print(f"   ✓ Input validation: {admin_results['input_validation']}")
    print(f"   ✓ Product relationship check: {admin_results['product_relationship_check']}")
    print(f"   ✓ Soft delete: {admin_results['soft_delete']}")
    
    # Test 4: Product Relationship Handling
    print("\n4. Testing Product Relationship Handling:")
    relationship_results = test_product_relationship_handling()
    
    print(f"   ✓ Product count calculation: {relationship_results['product_count_calculation']}")
    print(f"   ✓ Category products listing: {relationship_results['category_products_listing']}")
    print(f"   ✓ Deletion constraint: {relationship_results['deletion_constraint']}")
    print(f"   ✓ Aggregation pipeline: {relationship_results['aggregation_pipeline']}")
    print(f"   ✓ Product embedding: {relationship_results['product_embedding']}")
    print(f"   ✓ Relationship validation: {relationship_results['relationship_validation']}")
    
    # Test 5: Validation and Security
    print("\n5. Testing Validation and Security:")
    security_results = test_validation_and_security()
    
    print(f"   ✓ JSON schema validation: {security_results['json_schema_validation']}")
    print(f"   ✓ Admin role check: {security_results['admin_role_check']}")
    print(f"   ✓ ObjectId validation: {security_results['object_id_validation']}")
    print(f"   ✓ Slug validation: {security_results['slug_validation']}")
    print(f"   ✓ Input sanitization: {security_results['input_sanitization']}")
    print(f"   ✓ Error standardization: {security_results['error_standardization']}")
    print(f"   ✓ Logging integration: {security_results['logging_integration']}")
    
    # Test 6: Response Formatting
    print("\n6. Testing Response Formatting:")
    response_results = test_response_formatting()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Pagination metadata: {response_results['pagination_metadata']}")
    print(f"   ✓ Category dict conversion: {response_results['category_dict_conversion']}")
    print(f"   ✓ Product embedding: {response_results['product_embedding']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    print(f"   ✓ Error handling: {response_results['error_handling']}")
    
    # Test 7: Blueprint Registration
    print("\n7. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Categories import: {blueprint_results['categories_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    print(f"   ✓ URL prefix: {blueprint_results['url_prefix']}")
    
    # Test 8: Additional Features
    print("\n8. Testing Additional Features:")
    features_results = test_additional_features()
    
    print(f"   ✓ Product count refresh: {features_results['product_count_refresh']}")
    print(f"   ✓ Maintenance endpoint: {features_results['maintenance_endpoint']}")
    print(f"   ✓ Admin maintenance: {features_results['admin_maintenance']}")
    print(f"   ✓ Count synchronization: {features_results['count_synchronization']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['blueprint_defined'],
        len(structure_results['missing_endpoints']) == 0,
        structure_results['admin_decorator'],
        structure_results['category_schema'],
        public_results['list_categories_endpoint'],
        public_results['get_category_endpoint'],
        public_results['get_category_products_endpoint'],
        public_results['product_count_support'],
        public_results['pagination_support'],
        public_results['slug_support'],
        admin_results['create_category_endpoint'],
        admin_results['update_category_endpoint'],
        admin_results['delete_category_endpoint'],
        admin_results['admin_authorization'],
        admin_results['input_validation'],
        admin_results['product_relationship_check'],
        relationship_results['product_count_calculation'],
        relationship_results['category_products_listing'],
        relationship_results['deletion_constraint'],
        relationship_results['aggregation_pipeline'],
        security_results['json_schema_validation'],
        security_results['admin_role_check'],
        security_results['object_id_validation'],
        security_results['error_standardization'],
        response_results['success_response_format'],
        response_results['pagination_metadata'],
        response_results['category_dict_conversion'],
        response_results['status_codes'],
        blueprint_results['categories_import'],
        blueprint_results['blueprint_registration'],
        features_results['product_count_refresh']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Category Management Endpoints implementation PASSED")
        return True
    else:
        print("❌ Category Management Endpoints implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)