"""
Test Harness: Products GET All Endpoint

This test harness validates the GET /api/products endpoint implementation
including route definition, query parameter handling, database integration,
and response format without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_products_route_structure():
    """Test products route file structure and endpoint definition."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "list_products_function": False,
        "get_route_decorator": False,
        "imports_complete": False,
        "error_handling_imports": False
    }
    
    try:
        if os.path.exists(products_file):
            test_results["file_exists"] = True
            
            with open(products_file, 'r') as f:
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
            test_results["blueprint_defined"] = "products_bp = Blueprint" in content
            test_results["list_products_function"] = "list_products" in found_functions
            test_results["get_route_decorator"] = "list_products" in route_decorators
            test_results["imports_complete"] = all([
                "from flask import Blueprint" in content,
                "from app.models.product import Product" in content,
                "from app.models.category import Category" in content
            ])
            test_results["error_handling_imports"] = "from app.utils.error_handlers import" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_endpoint_functionality():
    """Test endpoint functionality and query parameter handling."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "route_path_correct": False,
        "http_method_get": False,
        "query_param_parsing": False,
        "pagination_support": False,
        "filtering_support": False,
        "sorting_support": False,
        "database_query": False,
        "aggregation_pipeline": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check route configuration
            test_results["route_path_correct"] = "@products_bp.route('/', methods=['GET'])" in content
            test_results["http_method_get"] = "methods=['GET']" in content
            
            # Check query parameter handling
            test_results["query_param_parsing"] = all([
                "request.args.get('page'" in content,
                "request.args.get('limit'" in content,
                "request.args.get('category_id'" in content
            ])
            
            # Check pagination features
            test_results["pagination_support"] = all([
                "page = max(1" in content,
                "limit = min(" in content,
                "'$skip':" in content,
                "'$limit':" in content
            ])
            
            # Check filtering capabilities
            test_results["filtering_support"] = all([
                "available_only" in content,
                "is_available" in content,
                "stock_quantity" in content,
                "category_id" in content
            ])
            
            # Check sorting capabilities
            test_results["sorting_support"] = all([
                "sort_by" in content,
                "sort_order" in content,
                "'$sort':" in content,
                "sort_direction" in content
            ])
            
            # Check database integration
            test_results["database_query"] = "get_database()" in content
            test_results["aggregation_pipeline"] = "'$facet':" in content and "'$lookup':" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_format():
    """Test API response format and structure."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "success_response_format": False,
        "error_handling": False,
        "json_response": False,
        "pagination_metadata": False,
        "product_to_dict": False,
        "category_lookup": False,
        "status_codes": False,
        "logging": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
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
            
            # Check pagination metadata
            test_results["pagination_metadata"] = all([
                "'pagination':" in content,
                "'total_items':" in content,
                "'total_pages':" in content,
                "'has_next':" in content
            ])
            
            # Check product processing
            test_results["product_to_dict"] = "to_dict()" in content
            test_results["category_lookup"] = "'$lookup':" in content and "'categories'" in content
            
            # Check logging
            test_results["logging"] = "logging.info(" in content and "logging.error(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_query_validation():
    """Test query parameter validation and error handling."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "parameter_validation": False,
        "price_validation": False,
        "category_id_validation": False,
        "sort_field_validation": False,
        "pagination_limits": False,
        "invalid_format_handling": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check parameter validation
            test_results["parameter_validation"] = all([
                "max(1, int(" in content,
                "min(100, max(1" in content
            ])
            
            # Check price validation
            test_results["price_validation"] = all([
                "float(min_price)" in content,
                "float(max_price)" in content,
                "ValueError:" in content
            ])
            
            # Check category ID validation
            test_results["category_id_validation"] = "ObjectId(category_id)" in content
            
            # Check sort field validation
            test_results["sort_field_validation"] = "valid_sort_fields" in content
            
            # Check pagination limits
            test_results["pagination_limits"] = "min(100" in content and "max(1" in content
            
            # Check invalid format handling
            test_results["invalid_format_handling"] = "Invalid" in content and "format" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_integration():
    """Test database integration and MongoDB operations."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "database_import": False,
        "collection_access": False,
        "aggregation_usage": False,
        "product_model_integration": False,
        "category_model_integration": False,
        "document_conversion": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check database integration
            test_results["database_import"] = "from app.database import get_database" in content
            test_results["collection_access"] = "db[Product.COLLECTION_NAME]" in content
            test_results["aggregation_usage"] = "collection.aggregate(pipeline)" in content
            
            # Check model integration
            test_results["product_model_integration"] = "Product(product_doc)" in content
            test_results["category_model_integration"] = "Category(product_doc['category'])" in content
            
            # Check document conversion
            test_results["document_conversion"] = "product.to_dict()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test products blueprint is properly registered."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "routes_init_exists": False,
        "products_import": False,
        "blueprint_registration": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            test_results["routes_init_exists"] = True
            
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["products_import"] = "from .products import products_bp" in content
            test_results["blueprint_registration"] = "api.register_blueprint(products_bp" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Products GET All Endpoint tests and return results."""
    print("Testing Products GET All Endpoint Implementation...")
    print("=" * 60)
    
    # Test 1: Products Route Structure
    print("\\n1. Testing Products Route Structure:")
    structure_results = test_products_route_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {structure_results['blueprint_defined']}")
    print(f"   ✓ List products function: {structure_results['list_products_function']}")
    print(f"   ✓ GET route decorator: {structure_results['get_route_decorator']}")
    print(f"   ✓ Imports complete: {structure_results['imports_complete']}")
    print(f"   ✓ Error handling imports: {structure_results['error_handling_imports']}")
    
    # Test 2: Endpoint Functionality
    print("\\n2. Testing Endpoint Functionality:")
    functionality_results = test_endpoint_functionality()
    
    print(f"   ✓ Route path correct: {functionality_results['route_path_correct']}")
    print(f"   ✓ HTTP method GET: {functionality_results['http_method_get']}")
    print(f"   ✓ Query param parsing: {functionality_results['query_param_parsing']}")
    print(f"   ✓ Pagination support: {functionality_results['pagination_support']}")
    print(f"   ✓ Filtering support: {functionality_results['filtering_support']}")
    print(f"   ✓ Sorting support: {functionality_results['sorting_support']}")
    print(f"   ✓ Database query: {functionality_results['database_query']}")
    print(f"   ✓ Aggregation pipeline: {functionality_results['aggregation_pipeline']}")
    
    # Test 3: Response Format
    print("\\n3. Testing Response Format:")
    response_results = test_response_format()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Error handling: {response_results['error_handling']}")
    print(f"   ✓ JSON response: {response_results['json_response']}")
    print(f"   ✓ Pagination metadata: {response_results['pagination_metadata']}")
    print(f"   ✓ Product to dict: {response_results['product_to_dict']}")
    print(f"   ✓ Category lookup: {response_results['category_lookup']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    print(f"   ✓ Logging: {response_results['logging']}")
    
    # Test 4: Query Validation
    print("\\n4. Testing Query Validation:")
    validation_results = test_query_validation()
    
    print(f"   ✓ Parameter validation: {validation_results['parameter_validation']}")
    print(f"   ✓ Price validation: {validation_results['price_validation']}")
    print(f"   ✓ Category ID validation: {validation_results['category_id_validation']}")
    print(f"   ✓ Sort field validation: {validation_results['sort_field_validation']}")
    print(f"   ✓ Pagination limits: {validation_results['pagination_limits']}")
    print(f"   ✓ Invalid format handling: {validation_results['invalid_format_handling']}")
    
    # Test 5: Database Integration
    print("\\n5. Testing Database Integration:")
    database_results = test_database_integration()
    
    print(f"   ✓ Database import: {database_results['database_import']}")
    print(f"   ✓ Collection access: {database_results['collection_access']}")
    print(f"   ✓ Aggregation usage: {database_results['aggregation_usage']}")
    print(f"   ✓ Product model integration: {database_results['product_model_integration']}")
    print(f"   ✓ Category model integration: {database_results['category_model_integration']}")
    print(f"   ✓ Document conversion: {database_results['document_conversion']}")
    
    # Test 6: Blueprint Registration
    print("\\n6. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Routes init exists: {blueprint_results['routes_init_exists']}")
    print(f"   ✓ Products import: {blueprint_results['products_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['blueprint_defined'],
        structure_results['list_products_function'],
        structure_results['get_route_decorator'],
        structure_results['imports_complete'],
        structure_results['error_handling_imports'],
        functionality_results['route_path_correct'],
        functionality_results['http_method_get'],
        functionality_results['query_param_parsing'],
        functionality_results['pagination_support'],
        functionality_results['filtering_support'],
        functionality_results['sorting_support'],
        functionality_results['database_query'],
        functionality_results['aggregation_pipeline'],
        response_results['success_response_format'],
        response_results['error_handling'],
        response_results['json_response'],
        response_results['pagination_metadata'],
        response_results['product_to_dict'],
        response_results['category_lookup'],
        response_results['status_codes'],
        response_results['logging'],
        validation_results['parameter_validation'],
        validation_results['price_validation'],
        validation_results['category_id_validation'],
        validation_results['sort_field_validation'],
        validation_results['pagination_limits'],
        validation_results['invalid_format_handling'],
        database_results['database_import'],
        database_results['collection_access'],
        database_results['aggregation_usage'],
        database_results['product_model_integration'],
        database_results['category_model_integration'],
        database_results['document_conversion'],
        blueprint_results['routes_init_exists'],
        blueprint_results['products_import'],
        blueprint_results['blueprint_registration']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Products GET All Endpoint implementation PASSED")
        return True
    else:
        print("❌ Products GET All Endpoint implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)