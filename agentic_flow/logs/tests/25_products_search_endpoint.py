"""
Test Harness: Products Search Endpoint

This test harness validates the GET /api/products/search endpoint implementation
including route definition, search functionality, parameter validation,
and response format without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_search_route_structure():
    """Test search route structure and endpoint definition."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "file_exists": False,
        "search_products_function": False,
        "search_route_decorator": False,
        "get_method": False,
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
            test_results["search_products_function"] = "search_products" in found_functions
            test_results["search_route_decorator"] = "@products_bp.route('/search', methods=['GET'])" in content
            test_results["get_method"] = "methods=['GET']" in content
            test_results["imports_complete"] = all([
                "from flask import Blueprint" in content,
                "from app.models.product import Product" in content,
                "from app.models.category import Category" in content
            ])
            test_results["error_handling_imports"] = "from app.utils.error_handlers import" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_search_parameters():
    """Test search parameter handling and validation."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "search_query_extraction": False,
        "query_validation": False,
        "pagination_params": False,
        "category_filtering": False,
        "availability_filtering": False,
        "parameter_defaults": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check parameter handling
            test_results["search_query_extraction"] = "request.args.get('q'" in content
            test_results["query_validation"] = "if not search_query:" in content and "Search query is required" in content
            test_results["pagination_params"] = all([
                "request.args.get('page'" in content,
                "request.args.get('limit'" in content
            ])
            test_results["category_filtering"] = "request.args.get('category_id'" in content
            test_results["availability_filtering"] = "request.args.get('available_only'" in content
            test_results["parameter_defaults"] = "default: 1" in content and "default: 20" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_text_search_implementation():
    """Test MongoDB text search implementation."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "text_search_query": False,
        "search_scoring": False,
        "sort_by_score": False,
        "meta_text_score": False,
        "aggregation_pipeline": False,
        "facet_operation": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check text search implementation
            test_results["text_search_query"] = "query['$text'] = {'$search': search_query}" in content
            test_results["search_scoring"] = "'score': {'$meta': 'textScore'}" in content
            test_results["sort_by_score"] = "'$sort': {'score': {'$meta': 'textScore'}}" in content
            test_results["meta_text_score"] = "'$meta': 'textScore'" in content
            test_results["aggregation_pipeline"] = "pipeline = [" in content
            test_results["facet_operation"] = "'$facet':" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_search_filters():
    """Test search filtering capabilities."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "availability_filter": False,
        "stock_quantity_filter": False,
        "category_filter": False,
        "objectid_validation": False,
        "invalid_category_handling": False,
        "query_building": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check filtering capabilities
            test_results["availability_filter"] = "query['is_available'] = True" in content
            test_results["stock_quantity_filter"] = "query['stock_quantity'] = {'$gt': 0}" in content
            test_results["category_filter"] = "query['category_id'] = category_obj_id" in content
            test_results["objectid_validation"] = "ObjectId(category_id)" in content
            test_results["invalid_category_handling"] = "Invalid category ID format" in content
            test_results["query_building"] = "query = {}" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_format():
    """Test search response format and structure."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "success_response_format": False,
        "search_results_structure": False,
        "search_score_inclusion": False,
        "pagination_metadata": False,
        "search_query_in_response": False,
        "category_enrichment": False,
        "json_response": False,
        "status_codes": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check response format
            test_results["success_response_format"] = "success_response(" in content
            test_results["search_results_structure"] = "'products':" in content
            test_results["search_score_inclusion"] = "'search_score'" in content
            test_results["pagination_metadata"] = "'pagination':" in content and "'total_items':" in content
            test_results["search_query_in_response"] = "'search_query': search_query" in content
            test_results["category_enrichment"] = "'$lookup':" in content and "'categories'" in content
            test_results["json_response"] = "jsonify(" in content
            test_results["status_codes"] = ", 200" in content and "400" in content and "500" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_integration():
    """Test database integration and aggregation."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "database_import": False,
        "collection_access": False,
        "aggregation_execution": False,
        "result_processing": False,
        "product_conversion": False,
        "category_lookup": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check database integration
            test_results["database_import"] = "from app.database import get_database" in content
            test_results["collection_access"] = "db[Product.COLLECTION_NAME]" in content
            test_results["aggregation_execution"] = "collection.aggregate(pipeline)" in content
            test_results["result_processing"] = "result['products']" in content and "result['total_count']" in content
            test_results["product_conversion"] = "Product(product_doc)" in content and "to_dict()" in content
            test_results["category_lookup"] = "'localField': 'category_id'" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_error_handling():
    """Test error handling and validation."""
    products_file = 'backend/app/routes/products.py'
    
    test_results = {
        "try_catch_block": False,
        "query_required_validation": False,
        "category_validation_error": False,
        "server_error_handling": False,
        "error_codes": False,
        "logging": False
    }
    
    try:
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                content = f.read()
            
            # Check error handling
            test_results["try_catch_block"] = "try:" in content and "except Exception as e:" in content
            test_results["query_required_validation"] = "VAL_001" in content and "Search query is required" in content
            test_results["category_validation_error"] = "Invalid category ID format" in content
            test_results["server_error_handling"] = "Product search failed" in content and "DB_001" in content
            test_results["error_codes"] = "400" in content and "500" in content
            test_results["logging"] = "logging.info(" in content and "logging.error(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Products Search Endpoint tests and return results."""
    print("Testing Products Search Endpoint Implementation...")
    print("=" * 60)
    
    # Test 1: Search Route Structure
    print("\\n1. Testing Search Route Structure:")
    structure_results = test_search_route_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Search products function: {structure_results['search_products_function']}")
    print(f"   ✓ Search route decorator: {structure_results['search_route_decorator']}")
    print(f"   ✓ GET method: {structure_results['get_method']}")
    print(f"   ✓ Imports complete: {structure_results['imports_complete']}")
    print(f"   ✓ Error handling imports: {structure_results['error_handling_imports']}")
    
    # Test 2: Search Parameters
    print("\\n2. Testing Search Parameters:")
    parameters_results = test_search_parameters()
    
    print(f"   ✓ Search query extraction: {parameters_results['search_query_extraction']}")
    print(f"   ✓ Query validation: {parameters_results['query_validation']}")
    print(f"   ✓ Pagination params: {parameters_results['pagination_params']}")
    print(f"   ✓ Category filtering: {parameters_results['category_filtering']}")
    print(f"   ✓ Availability filtering: {parameters_results['availability_filtering']}")
    print(f"   ✓ Parameter defaults: {parameters_results['parameter_defaults']}")
    
    # Test 3: Text Search Implementation
    print("\\n3. Testing Text Search Implementation:")
    search_results = test_text_search_implementation()
    
    print(f"   ✓ Text search query: {search_results['text_search_query']}")
    print(f"   ✓ Search scoring: {search_results['search_scoring']}")
    print(f"   ✓ Sort by score: {search_results['sort_by_score']}")
    print(f"   ✓ Meta text score: {search_results['meta_text_score']}")
    print(f"   ✓ Aggregation pipeline: {search_results['aggregation_pipeline']}")
    print(f"   ✓ Facet operation: {search_results['facet_operation']}")
    
    # Test 4: Search Filters
    print("\\n4. Testing Search Filters:")
    filters_results = test_search_filters()
    
    print(f"   ✓ Availability filter: {filters_results['availability_filter']}")
    print(f"   ✓ Stock quantity filter: {filters_results['stock_quantity_filter']}")
    print(f"   ✓ Category filter: {filters_results['category_filter']}")
    print(f"   ✓ ObjectId validation: {filters_results['objectid_validation']}")
    print(f"   ✓ Invalid category handling: {filters_results['invalid_category_handling']}")
    print(f"   ✓ Query building: {filters_results['query_building']}")
    
    # Test 5: Response Format
    print("\\n5. Testing Response Format:")
    response_results = test_response_format()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Search results structure: {response_results['search_results_structure']}")
    print(f"   ✓ Search score inclusion: {response_results['search_score_inclusion']}")
    print(f"   ✓ Pagination metadata: {response_results['pagination_metadata']}")
    print(f"   ✓ Search query in response: {response_results['search_query_in_response']}")
    print(f"   ✓ Category enrichment: {response_results['category_enrichment']}")
    print(f"   ✓ JSON response: {response_results['json_response']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    
    # Test 6: Database Integration
    print("\\n6. Testing Database Integration:")
    database_results = test_database_integration()
    
    print(f"   ✓ Database import: {database_results['database_import']}")
    print(f"   ✓ Collection access: {database_results['collection_access']}")
    print(f"   ✓ Aggregation execution: {database_results['aggregation_execution']}")
    print(f"   ✓ Result processing: {database_results['result_processing']}")
    print(f"   ✓ Product conversion: {database_results['product_conversion']}")
    print(f"   ✓ Category lookup: {database_results['category_lookup']}")
    
    # Test 7: Error Handling
    print("\\n7. Testing Error Handling:")
    error_results = test_error_handling()
    
    print(f"   ✓ Try catch block: {error_results['try_catch_block']}")
    print(f"   ✓ Query required validation: {error_results['query_required_validation']}")
    print(f"   ✓ Category validation error: {error_results['category_validation_error']}")
    print(f"   ✓ Server error handling: {error_results['server_error_handling']}")
    print(f"   ✓ Error codes: {error_results['error_codes']}")
    print(f"   ✓ Logging: {error_results['logging']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['search_products_function'],
        structure_results['search_route_decorator'],
        structure_results['get_method'],
        structure_results['imports_complete'],
        structure_results['error_handling_imports'],
        parameters_results['search_query_extraction'],
        parameters_results['query_validation'],
        parameters_results['pagination_params'],
        parameters_results['category_filtering'],
        parameters_results['availability_filtering'],
        parameters_results['parameter_defaults'],
        search_results['text_search_query'],
        search_results['search_scoring'],
        search_results['sort_by_score'],
        search_results['meta_text_score'],
        search_results['aggregation_pipeline'],
        search_results['facet_operation'],
        filters_results['availability_filter'],
        filters_results['stock_quantity_filter'],
        filters_results['category_filter'],
        filters_results['objectid_validation'],
        filters_results['invalid_category_handling'],
        filters_results['query_building'],
        response_results['success_response_format'],
        response_results['search_results_structure'],
        response_results['search_score_inclusion'],
        response_results['pagination_metadata'],
        response_results['search_query_in_response'],
        response_results['category_enrichment'],
        response_results['json_response'],
        response_results['status_codes'],
        database_results['database_import'],
        database_results['collection_access'],
        database_results['aggregation_execution'],
        database_results['result_processing'],
        database_results['product_conversion'],
        database_results['category_lookup'],
        error_results['try_catch_block'],
        error_results['query_required_validation'],
        error_results['category_validation_error'],
        error_results['server_error_handling'],
        error_results['error_codes'],
        error_results['logging']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Products Search Endpoint implementation PASSED")
        return True
    else:
        print("❌ Products Search Endpoint implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)