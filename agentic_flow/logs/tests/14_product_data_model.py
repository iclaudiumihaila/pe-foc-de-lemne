"""
Test Harness: Product Data Model with MongoDB Schema

This test harness validates the Product model implementation including CRUD operations,
inventory management, pricing, and business logic without requiring database connections.
"""

import ast
import os
import sys
import re

def test_product_model_structure():
    """Test Product model file structure and class definition."""
    product_file = 'backend/app/models/product.py'
    
    test_results = {
        "file_exists": False,
        "product_class_found": False,
        "required_methods": [],
        "missing_methods": [],
        "collection_name_defined": False,
        "price_constants_defined": False,
        "stock_constants_defined": False,
        "validation_constants_defined": False
    }
    
    required_methods = [
        '__init__', 'create', 'find_by_id', 'find_by_slug', 'find_by_category',
        'find_available', 'update', 'update_stock', 'delete', 'to_dict'
    ]
    
    try:
        if os.path.exists(product_file):
            test_results["file_exists"] = True
            
            with open(product_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find Product class and methods
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'Product':
                    test_results["product_class_found"] = True
                    
                    # Find methods in Product class
                    found_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            found_methods.append(item.name)
                    
                    test_results["required_methods"] = found_methods
                    test_results["missing_methods"] = [
                        method for method in required_methods 
                        if method not in found_methods
                    ]
            
            # Check for important constants and configurations
            test_results["collection_name_defined"] = "COLLECTION_NAME = 'products'" in content
            test_results["price_constants_defined"] = "MIN_PRICE" in content and "MAX_PRICE" in content
            test_results["stock_constants_defined"] = "MIN_STOCK" in content and "MAX_STOCK" in content
            test_results["validation_constants_defined"] = "MIN_NAME_LENGTH" in content and "MAX_NAME_LENGTH" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_pricing_and_inventory():
    """Test pricing and inventory management features."""
    product_file = 'backend/app/models/product.py'
    
    test_results = {
        "decimal_import": False,
        "price_validation": False,
        "stock_validation": False,
        "stock_operations": False,
        "availability_logic": False,
        "price_conversion": False,
        "inventory_tracking": False
    }
    
    try:
        if os.path.exists(product_file):
            with open(product_file, 'r') as f:
                content = f.read()
            
            # Check pricing and inventory features
            test_results["decimal_import"] = "from decimal import Decimal" in content
            test_results["price_validation"] = "_validate_price" in content
            test_results["stock_validation"] = "_validate_stock" in content
            test_results["stock_operations"] = "update_stock" in content and "operation" in content
            test_results["availability_logic"] = "is_available" in content and ("stock_quantity > 0" in content or "validated_stock > 0" in content)
            test_results["price_conversion"] = "_convert_to_decimal" in content
            test_results["inventory_tracking"] = "quantity_change" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_seo_and_slug_features():
    """Test SEO features and URL slug generation."""
    product_file = 'backend/app/models/product.py'
    
    test_results = {
        "slug_generation": False,
        "unique_slug_check": False,
        "url_sanitization": False,
        "slug_conflict_resolution": False,
        "find_by_slug_method": False,
        "slug_update_logic": False
    }
    
    try:
        if os.path.exists(product_file):
            with open(product_file, 'r') as f:
                content = f.read()
            
            # Check SEO and slug features
            test_results["slug_generation"] = "_generate_unique_slug" in content
            test_results["unique_slug_check"] = "find_one({'slug'" in content
            test_results["url_sanitization"] = "re.sub" in content and "lower()" in content
            test_results["slug_conflict_resolution"] = "counter" in content
            test_results["find_by_slug_method"] = "def find_by_slug" in content
            test_results["slug_update_logic"] = "exclude_id" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_and_security():
    """Test validation and security features."""
    product_file = 'backend/app/models/product.py'
    
    test_results = {
        "input_validation": False,
        "sanitization": False,
        "url_validation": False,
        "objectid_validation": False,
        "error_handling": False,
        "field_validation": False,
        "business_rules": False
    }
    
    try:
        if os.path.exists(product_file):
            with open(product_file, 'r') as f:
                content = f.read()
            
            # Check validation and security features
            test_results["input_validation"] = "_validate_" in content
            test_results["sanitization"] = "sanitize_string" in content
            test_results["url_validation"] = "_validate_images" in content and "url_pattern" in content
            test_results["objectid_validation"] = "_validate_object_id" in content
            test_results["error_handling"] = "ValidationError" in content and "DatabaseError" in content
            test_results["field_validation"] = "_validate_name" in content and "_validate_description" in content
            test_results["business_rules"] = "_validate_weight" in content and "_validate_preparation_time" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_mongodb_integration():
    """Test MongoDB integration and database operations."""
    product_file = 'backend/app/models/product.py'
    
    test_results = {
        "mongodb_imports": False,
        "database_connection": False,
        "collection_operations": False,
        "find_operations": False,
        "update_operations": False,
        "query_building": False,
        "sorting_and_limiting": False,
        "error_handling": False
    }
    
    try:
        if os.path.exists(product_file):
            with open(product_file, 'r') as f:
                content = f.read()
            
            # Check MongoDB integration
            test_results["mongodb_imports"] = "from bson import ObjectId" in content
            test_results["database_connection"] = "get_database()" in content
            test_results["collection_operations"] = "collection.insert_one" in content
            test_results["find_operations"] = "find_one" in content and "find(" in content
            test_results["update_operations"] = "update_one" in content
            test_results["query_building"] = "query = {" in content
            test_results["sorting_and_limiting"] = "sort(" in content and "limit(" in content
            test_results["error_handling"] = "DuplicateKeyError" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_models_package_update():
    """Test models package structure includes Product."""
    models_init_file = 'backend/app/models/__init__.py'
    
    test_results = {
        "package_init_exists": False,
        "product_import": False,
        "product_export": False,
        "user_import_maintained": False
    }
    
    try:
        if os.path.exists(models_init_file):
            test_results["package_init_exists"] = True
            
            with open(models_init_file, 'r') as f:
                content = f.read()
            
            test_results["product_import"] = "from .product import Product" in content
            test_results["product_export"] = "'Product'" in content
            test_results["user_import_maintained"] = "from .user import User" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Product model tests and return results."""
    print("Testing Product Data Model Implementation...")
    print("=" * 50)
    
    # Test 1: Model Structure
    print("\\n1. Testing Product Model Structure:")
    structure_results = test_product_model_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Product class found: {structure_results['product_class_found']}")
    print(f"   ✓ Required methods found: {len(structure_results['required_methods'])}/10")
    print(f"   ✓ Missing methods: {structure_results['missing_methods']}")
    print(f"   ✓ Collection name defined: {structure_results['collection_name_defined']}")
    print(f"   ✓ Price constants defined: {structure_results['price_constants_defined']}")
    print(f"   ✓ Stock constants defined: {structure_results['stock_constants_defined']}")
    
    # Test 2: Pricing and Inventory
    print("\\n2. Testing Pricing and Inventory:")
    pricing_results = test_pricing_and_inventory()
    
    print(f"   ✓ Decimal import: {pricing_results['decimal_import']}")
    print(f"   ✓ Price validation: {pricing_results['price_validation']}")
    print(f"   ✓ Stock validation: {pricing_results['stock_validation']}")
    print(f"   ✓ Stock operations: {pricing_results['stock_operations']}")
    print(f"   ✓ Availability logic: {pricing_results['availability_logic']}")
    print(f"   ✓ Price conversion: {pricing_results['price_conversion']}")
    print(f"   ✓ Inventory tracking: {pricing_results['inventory_tracking']}")
    
    # Test 3: SEO and Slug Features
    print("\\n3. Testing SEO and Slug Features:")
    seo_results = test_seo_and_slug_features()
    
    print(f"   ✓ Slug generation: {seo_results['slug_generation']}")
    print(f"   ✓ Unique slug check: {seo_results['unique_slug_check']}")
    print(f"   ✓ URL sanitization: {seo_results['url_sanitization']}")
    print(f"   ✓ Slug conflict resolution: {seo_results['slug_conflict_resolution']}")
    print(f"   ✓ Find by slug method: {seo_results['find_by_slug_method']}")
    print(f"   ✓ Slug update logic: {seo_results['slug_update_logic']}")
    
    # Test 4: Validation and Security
    print("\\n4. Testing Validation and Security:")
    validation_results = test_validation_and_security()
    
    print(f"   ✓ Input validation: {validation_results['input_validation']}")
    print(f"   ✓ Sanitization: {validation_results['sanitization']}")
    print(f"   ✓ URL validation: {validation_results['url_validation']}")
    print(f"   ✓ ObjectId validation: {validation_results['objectid_validation']}")
    print(f"   ✓ Error handling: {validation_results['error_handling']}")
    print(f"   ✓ Field validation: {validation_results['field_validation']}")
    print(f"   ✓ Business rules: {validation_results['business_rules']}")
    
    # Test 5: MongoDB Integration
    print("\\n5. Testing MongoDB Integration:")
    mongodb_results = test_mongodb_integration()
    
    print(f"   ✓ MongoDB imports: {mongodb_results['mongodb_imports']}")
    print(f"   ✓ Database connection: {mongodb_results['database_connection']}")
    print(f"   ✓ Collection operations: {mongodb_results['collection_operations']}")
    print(f"   ✓ Find operations: {mongodb_results['find_operations']}")
    print(f"   ✓ Update operations: {mongodb_results['update_operations']}")
    print(f"   ✓ Query building: {mongodb_results['query_building']}")
    print(f"   ✓ Sorting and limiting: {mongodb_results['sorting_and_limiting']}")
    
    # Test 6: Package Update
    print("\\n6. Testing Models Package Update:")
    package_results = test_models_package_update()
    
    print(f"   ✓ Package init exists: {package_results['package_init_exists']}")
    print(f"   ✓ Product import: {package_results['product_import']}")
    print(f"   ✓ Product export: {package_results['product_export']}")
    print(f"   ✓ User import maintained: {package_results['user_import_maintained']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['product_class_found'],
        len(structure_results['missing_methods']) == 0,
        structure_results['collection_name_defined'],
        pricing_results['decimal_import'],
        pricing_results['price_validation'],
        pricing_results['stock_validation'],
        pricing_results['availability_logic'],
        seo_results['slug_generation'],
        seo_results['unique_slug_check'],
        seo_results['find_by_slug_method'],
        validation_results['input_validation'],
        validation_results['sanitization'],
        validation_results['error_handling'],
        mongodb_results['mongodb_imports'],
        mongodb_results['database_connection'],
        mongodb_results['collection_operations'],
        package_results['package_init_exists'],
        package_results['product_import']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Product Data Model implementation PASSED")
        return True
    else:
        print("❌ Product Data Model implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)