"""
Test Harness: Products GET Single Endpoint

This test harness validates the GET /api/products/:id endpoint implementation
including route definition, parameter validation, database lookup,
and response format without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_single_product_route_structure():
    """Test single product route structure and endpoint definition."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "file_exists": False,
        "get_product_function": False,
        "get_route_with_param": False,
        "parameter_extraction": False,
        "imports_complete": False,
        "error_handling_imports": False
    }
    
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
            
            # Check for required elements
            test_results["get_product_function"] = "get_product" in found_functions
            test_results["get_route_with_param"] = "@products_bp.route('/<product_id>', methods=['GET'])" in content
            test_results["parameter_extraction"] = "def get_product(product_id)" in content
            test_results["imports_complete"] = all([
                "from flask import Blueprint" in content,
                "from app.models.product import Product" in content,
                "from app.models.category import Category" in content
            ])
            test_results["error_handling_imports"] = "from app.utils.error_handlers import" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_parameter_validation():
    """Test parameter validation and ID format checking."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "objectid_validation": False,
        "regex_pattern_check": False,
        "slug_fallback": False,
        "id_format_check": False,
        "parameter_type_handling": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check parameter validation features
            test_results["objectid_validation"] = "re.match(" in content and "24" in content
            test_results["regex_pattern_check"] = "[0-9a-fA-F]{24}" in content
            test_results["slug_fallback"] = "find_by_slug" in content
            test_results["id_format_check"] = "find_by_id" in content
            test_results["parameter_type_handling"] = "product_id" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_lookup():
    """Test database lookup and product retrieval."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "product_find_by_id": False,
        "product_find_by_slug": False,
        "category_lookup": False,
        "not_found_handling": False,
        "product_to_dict": False,
        "category_information": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check database lookup features
            test_results["product_find_by_id"] = "Product.find_by_id(" in content
            test_results["product_find_by_slug"] = "Product.find_by_slug(" in content
            test_results["category_lookup"] = "Category.find_by_id(" in content
            test_results["not_found_handling"] = "Product not found" in content
            test_results["product_to_dict"] = "product.to_dict()" in content
            test_results["category_information"] = "'category':" in content and "'name':" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_format():
    """Test API response format and structure."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "success_response_format": False,
        "error_response_format": False,
        "json_response": False,
        "status_codes": False,
        "product_wrapper": False,
        "category_details": False,
        "logging": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check response format
            test_results["success_response_format"] = "success_response(" in content
            test_results["error_response_format"] = "create_error_response(" in content
            test_results["json_response"] = "jsonify(" in content
            test_results["status_codes"] = ", 200" in content and "404" in content and "500" in content
            test_results["product_wrapper"] = "'product':" in content
            test_results["category_details"] = "'slug':" in content and "'description':" in content
            test_results["logging"] = "logging.info(" in content and "logging.error(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_error_handling():
    """Test error handling and edge cases."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "try_catch_block": False,
        "not_found_error": False,
        "server_error": False,
        "error_codes": False,
        "exception_logging": False,
        "multiple_lookup_attempts": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check error handling
            test_results["try_catch_block"] = "try:" in content and "except Exception as e:" in content
            test_results["not_found_error"] = "NOT_001" in content
            test_results["server_error"] = "DB_001" in content
            test_results["error_codes"] = "404" in content and "500" in content
            test_results["exception_logging"] = "logging.error(" in content and "str(e)" in content
            test_results["multiple_lookup_attempts"] = "if not product:" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_advanced_features():
    """Test advanced features and enhancements."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "dual_lookup_support": False,
        "category_enrichment": False,
        "response_message": False,
        "detailed_category_info": False,
        "flexible_identifier": False,
        "comprehensive_logging": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check advanced features
            test_results["dual_lookup_support"] = "find_by_id" in content and "find_by_slug" in content
            test_results["category_enrichment"] = "if product.category_id:" in content
            test_results["response_message"] = "Product retrieved successfully" in content
            test_results["detailed_category_info"] = "'description':" in content
            test_results["flexible_identifier"] = "ObjectId or URL slug" in content
            test_results["comprehensive_logging"] = "Product retrieved:" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Products GET Single Endpoint tests and return results."""
    print("Testing Products GET Single Endpoint Implementation...")
    print("=" * 60)
    
    # Test 1: Single Product Route Structure
    print("\\n1. Testing Single Product Route Structure:")
    structure_results = test_single_product_route_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Get product function: {structure_results['get_product_function']}")
    print(f"   ✓ GET route with param: {structure_results['get_route_with_param']}")
    print(f"   ✓ Parameter extraction: {structure_results['parameter_extraction']}")
    print(f"   ✓ Imports complete: {structure_results['imports_complete']}")
    print(f"   ✓ Error handling imports: {structure_results['error_handling_imports']}")
    
    # Test 2: Parameter Validation
    print("\\n2. Testing Parameter Validation:")
    validation_results = test_parameter_validation()
    
    print(f"   ✓ ObjectId validation: {validation_results['objectid_validation']}")
    print(f"   ✓ Regex pattern check: {validation_results['regex_pattern_check']}")
    print(f"   ✓ Slug fallback: {validation_results['slug_fallback']}")
    print(f"   ✓ ID format check: {validation_results['id_format_check']}")
    print(f"   ✓ Parameter type handling: {validation_results['parameter_type_handling']}")
    
    # Test 3: Database Lookup
    print("\\n3. Testing Database Lookup:")
    lookup_results = test_database_lookup()
    
    print(f"   ✓ Product find by ID: {lookup_results['product_find_by_id']}")
    print(f"   ✓ Product find by slug: {lookup_results['product_find_by_slug']}")
    print(f"   ✓ Category lookup: {lookup_results['category_lookup']}")
    print(f"   ✓ Not found handling: {lookup_results['not_found_handling']}")
    print(f"   ✓ Product to dict: {lookup_results['product_to_dict']}")
    print(f"   ✓ Category information: {lookup_results['category_information']}")
    
    # Test 4: Response Format
    print("\\n4. Testing Response Format:")
    response_results = test_response_format()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Error response format: {response_results['error_response_format']}")
    print(f"   ✓ JSON response: {response_results['json_response']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    print(f"   ✓ Product wrapper: {response_results['product_wrapper']}")
    print(f"   ✓ Category details: {response_results['category_details']}")
    print(f"   ✓ Logging: {response_results['logging']}")
    
    # Test 5: Error Handling
    print("\\n5. Testing Error Handling:")
    error_results = test_error_handling()
    
    print(f"   ✓ Try catch block: {error_results['try_catch_block']}")
    print(f"   ✓ Not found error: {error_results['not_found_error']}")
    print(f"   ✓ Server error: {error_results['server_error']}")
    print(f"   ✓ Error codes: {error_results['error_codes']}")
    print(f"   ✓ Exception logging: {error_results['exception_logging']}")
    print(f"   ✓ Multiple lookup attempts: {error_results['multiple_lookup_attempts']}")
    
    # Test 6: Advanced Features
    print("\\n6. Testing Advanced Features:")
    advanced_results = test_advanced_features()
    
    print(f"   ✓ Dual lookup support: {advanced_results['dual_lookup_support']}")
    print(f"   ✓ Category enrichment: {advanced_results['category_enrichment']}")
    print(f"   ✓ Response message: {advanced_results['response_message']}")
    print(f"   ✓ Detailed category info: {advanced_results['detailed_category_info']}")
    print(f"   ✓ Flexible identifier: {advanced_results['flexible_identifier']}")
    print(f"   ✓ Comprehensive logging: {advanced_results['comprehensive_logging']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['get_product_function'],
        structure_results['get_route_with_param'],
        structure_results['parameter_extraction'],
        structure_results['imports_complete'],
        structure_results['error_handling_imports'],
        validation_results['objectid_validation'],
        validation_results['regex_pattern_check'],
        validation_results['slug_fallback'],
        validation_results['id_format_check'],
        validation_results['parameter_type_handling'],
        lookup_results['product_find_by_id'],
        lookup_results['product_find_by_slug'],
        lookup_results['category_lookup'],
        lookup_results['not_found_handling'],
        lookup_results['product_to_dict'],
        lookup_results['category_information'],
        response_results['success_response_format'],
        response_results['error_response_format'],
        response_results['json_response'],
        response_results['status_codes'],
        response_results['product_wrapper'],
        response_results['category_details'],
        response_results['logging'],
        error_results['try_catch_block'],
        error_results['not_found_error'],
        error_results['server_error'],
        error_results['error_codes'],
        error_results['exception_logging'],
        error_results['multiple_lookup_attempts'],
        advanced_results['dual_lookup_support'],
        advanced_results['category_enrichment'],
        advanced_results['response_message'],
        advanced_results['detailed_category_info'],
        advanced_results['flexible_identifier'],
        advanced_results['comprehensive_logging']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Products GET Single Endpoint implementation PASSED")
        return True
    else:
        print("❌ Products GET Single Endpoint implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)