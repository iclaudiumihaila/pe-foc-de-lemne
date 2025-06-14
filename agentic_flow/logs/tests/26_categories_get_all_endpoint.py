"""
Test Harness: Categories GET All Endpoint

This test harness validates the GET /api/categories endpoint implementation
including route definition, parameter handling, database integration,
and response format without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_categories_route_structure():
    """Test categories route file structure and endpoint definition."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "list_categories_function": False,
        "get_route_decorator": False,
        "imports_complete": False,
        "error_handling_imports": False
    }
    
    try:
        if os.path.exists(categories_file):
            test_results["file_exists"] = True
            
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find functions and decorators
            tree = ast.parse(content)
            found_functions = []
            route_decorators = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    found_functions.append(node.name)
                    # Check for route decorators
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr'):
                            if decorator.func.attr == 'route':
                                route_decorators.append(node.name)
            
            # Check for required elements
            test_results["blueprint_defined"] = "categories_bp = Blueprint" in content
            test_results["list_categories_function"] = "list_categories" in found_functions
            test_results["get_route_decorator"] = "list_categories" in route_decorators
            test_results["imports_complete"] = all([
                "from flask import Blueprint" in content,
                "from app.models.category import Category" in content,
                "from app.models.product import Product" in content
            ])
            test_results["error_handling_imports"] = "from app.utils.error_handlers import" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_endpoint_functionality():
    """Test endpoint functionality and query parameter handling."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "route_path_correct": False,
        "http_method_get": False,
        "query_param_parsing": False,
        "active_only_support": False,
        "include_counts_support": False,
        "database_query": False,
        "category_conversion": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check route configuration
            test_results["route_path_correct"] = "@categories_bp.route('/', methods=['GET'])" in content
            test_results["http_method_get"] = "methods=['GET']" in content
            
            # Check query parameter handling
            test_results["query_param_parsing"] = all([
                "request.args.get('active_only'" in content,
                "request.args.get('include_counts'" in content
            ])
            
            # Check parameter features
            test_results["active_only_support"] = "active_only" in content and "default: true" in content
            test_results["include_counts_support"] = "include_counts" in content and "default: true" in content
            
            # Check database integration
            test_results["database_query"] = "Category.find_all(" in content
            test_results["category_conversion"] = "category.to_dict()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_format():
    """Test API response format and structure."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "success_response_format": False,
        "error_handling": False,
        "json_response": False,
        "categories_array": False,
        "total_count": False,
        "filters_metadata": False,
        "status_codes": False,
        "logging": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check response format
            test_results["success_response_format"] = "success_response(" in content
            test_results["json_response"] = "jsonify(" in content
            test_results["status_codes"] = ", 200" in content
            
            # Check error handling
            test_results["error_handling"] = all([
                "try:" in content,
                "except Exception as e:" in content,
                "create_error_response(" in content
            ])
            
            # Check response structure
            test_results["categories_array"] = "'categories': categories_data" in content
            test_results["total_count"] = "'total_count':" in content
            test_results["filters_metadata"] = "'filters':" in content and "'active_only':" in content
            
            # Check logging
            test_results["logging"] = "logging.info(" in content and "logging.error(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_product_count_integration():
    """Test product count functionality."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "product_count_update": False,
        "conditional_counting": False,
        "count_in_response": False,
        "update_method_call": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check product count features
            test_results["product_count_update"] = "update_product_count()" in content
            test_results["conditional_counting"] = "if include_counts:" in content
            test_results["count_in_response"] = "'product_count'" in content
            test_results["update_method_call"] = "category.update_product_count()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_integration():
    """Test database integration and Category model usage."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "category_model_import": False,
        "find_all_method": False,
        "active_only_parameter": False,
        "model_conversion": False,
        "category_iteration": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check database integration
            test_results["category_model_import"] = "from app.models.category import Category" in content
            test_results["find_all_method"] = "Category.find_all(" in content
            test_results["active_only_parameter"] = "active_only=active_only" in content
            test_results["model_conversion"] = "category.to_dict()" in content
            test_results["category_iteration"] = "for category in categories:" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_error_handling():
    """Test error handling and edge cases."""
    categories_file = 'backend/app/routes/categories.py'
    
    test_results = {
        "try_catch_block": False,
        "server_error": False,
        "error_codes": False,
        "exception_logging": False,
        "error_response_format": False
    }
    
    try:
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read()
            
            # Check error handling
            test_results["try_catch_block"] = "try:" in content and "except Exception as e:" in content
            test_results["server_error"] = "DB_001" in content
            test_results["error_codes"] = "500" in content
            test_results["exception_logging"] = "logging.error(" in content and "str(e)" in content
            test_results["error_response_format"] = "create_error_response(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test categories blueprint is properly registered."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "routes_init_exists": False,
        "categories_import": False,
        "blueprint_registration": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            test_results["routes_init_exists"] = True
            
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["categories_import"] = "from .categories import categories_bp" in content
            test_results["blueprint_registration"] = "api.register_blueprint(categories_bp" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Categories GET All Endpoint tests and return results."""
    print("Testing Categories GET All Endpoint Implementation...")
    print("=" * 60)
    
    # Test 1: Categories Route Structure
    print("\\n1. Testing Categories Route Structure:")
    structure_results = test_categories_route_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {structure_results['blueprint_defined']}")
    print(f"   ✓ List categories function: {structure_results['list_categories_function']}")
    print(f"   ✓ GET route decorator: {structure_results['get_route_decorator']}")
    print(f"   ✓ Imports complete: {structure_results['imports_complete']}")
    print(f"   ✓ Error handling imports: {structure_results['error_handling_imports']}")
    
    # Test 2: Endpoint Functionality
    print("\\n2. Testing Endpoint Functionality:")
    functionality_results = test_endpoint_functionality()
    
    print(f"   ✓ Route path correct: {functionality_results['route_path_correct']}")
    print(f"   ✓ HTTP method GET: {functionality_results['http_method_get']}")
    print(f"   ✓ Query param parsing: {functionality_results['query_param_parsing']}")
    print(f"   ✓ Active only support: {functionality_results['active_only_support']}")
    print(f"   ✓ Include counts support: {functionality_results['include_counts_support']}")
    print(f"   ✓ Database query: {functionality_results['database_query']}")
    print(f"   ✓ Category conversion: {functionality_results['category_conversion']}")
    
    # Test 3: Response Format
    print("\\n3. Testing Response Format:")
    response_results = test_response_format()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Error handling: {response_results['error_handling']}")
    print(f"   ✓ JSON response: {response_results['json_response']}")
    print(f"   ✓ Categories array: {response_results['categories_array']}")
    print(f"   ✓ Total count: {response_results['total_count']}")
    print(f"   ✓ Filters metadata: {response_results['filters_metadata']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    print(f"   ✓ Logging: {response_results['logging']}")
    
    # Test 4: Product Count Integration
    print("\\n4. Testing Product Count Integration:")
    count_results = test_product_count_integration()
    
    print(f"   ✓ Product count update: {count_results['product_count_update']}")
    print(f"   ✓ Conditional counting: {count_results['conditional_counting']}")
    print(f"   ✓ Count in response: {count_results['count_in_response']}")
    print(f"   ✓ Update method call: {count_results['update_method_call']}")
    
    # Test 5: Database Integration
    print("\\n5. Testing Database Integration:")
    database_results = test_database_integration()
    
    print(f"   ✓ Category model import: {database_results['category_model_import']}")
    print(f"   ✓ Find all method: {database_results['find_all_method']}")
    print(f"   ✓ Active only parameter: {database_results['active_only_parameter']}")
    print(f"   ✓ Model conversion: {database_results['model_conversion']}")
    print(f"   ✓ Category iteration: {database_results['category_iteration']}")
    
    # Test 6: Error Handling
    print("\\n6. Testing Error Handling:")
    error_results = test_error_handling()
    
    print(f"   ✓ Try catch block: {error_results['try_catch_block']}")
    print(f"   ✓ Server error: {error_results['server_error']}")
    print(f"   ✓ Error codes: {error_results['error_codes']}")
    print(f"   ✓ Exception logging: {error_results['exception_logging']}")
    print(f"   ✓ Error response format: {error_results['error_response_format']}")
    
    # Test 7: Blueprint Registration
    print("\\n7. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Routes init exists: {blueprint_results['routes_init_exists']}")
    print(f"   ✓ Categories import: {blueprint_results['categories_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['blueprint_defined'],
        structure_results['list_categories_function'],
        structure_results['get_route_decorator'],
        structure_results['imports_complete'],
        structure_results['error_handling_imports'],
        functionality_results['route_path_correct'],
        functionality_results['http_method_get'],
        functionality_results['query_param_parsing'],
        functionality_results['active_only_support'],
        functionality_results['include_counts_support'],
        functionality_results['database_query'],
        functionality_results['category_conversion'],
        response_results['success_response_format'],
        response_results['error_handling'],
        response_results['json_response'],
        response_results['categories_array'],
        response_results['total_count'],
        response_results['filters_metadata'],
        response_results['status_codes'],
        response_results['logging'],
        count_results['product_count_update'],
        count_results['conditional_counting'],
        count_results['count_in_response'],
        count_results['update_method_call'],
        database_results['category_model_import'],
        database_results['find_all_method'],
        database_results['active_only_parameter'],
        database_results['model_conversion'],
        database_results['category_iteration'],
        error_results['try_catch_block'],
        error_results['server_error'],
        error_results['error_codes'],
        error_results['exception_logging'],
        error_results['error_response_format'],
        blueprint_results['routes_init_exists'],
        blueprint_results['categories_import'],
        blueprint_results['blueprint_registration']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Categories GET All Endpoint implementation PASSED")
        return True
    else:
        print("❌ Categories GET All Endpoint implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)