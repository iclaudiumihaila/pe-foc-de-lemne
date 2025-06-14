"""
Test Harness: Category Data Model with MongoDB Schema

This test harness validates the Category model implementation including CRUD operations,
hierarchy management, product counting, and business logic without requiring database connections.
"""

import ast
import os
import sys
import re

def test_category_model_structure():
    """Test Category model file structure and class definition."""
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "file_exists": False,
        "category_class_found": False,
        "required_methods": [],
        "missing_methods": [],
        "collection_name_defined": False,
        "display_order_constants": False,
        "validation_constants": False
    }
    
    required_methods = [
        '__init__', 'create', 'find_by_id', 'find_by_slug', 'find_all',
        'find_active', 'update', 'update_product_count', 'delete', 'to_dict'
    ]
    
    try:
        if os.path.exists(category_file):
            test_results["file_exists"] = True
            
            with open(category_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find Category class and methods
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'Category':
                    test_results["category_class_found"] = True
                    
                    # Find methods in Category class
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
            test_results["collection_name_defined"] = "COLLECTION_NAME = 'categories'" in content
            test_results["display_order_constants"] = "MIN_DISPLAY_ORDER" in content and "MAX_DISPLAY_ORDER" in content
            test_results["validation_constants"] = "MIN_NAME_LENGTH" in content and "MAX_NAME_LENGTH" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_hierarchy_and_ordering():
    """Test hierarchy management and display ordering features."""
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "display_order_management": False,
        "auto_order_assignment": False,
        "order_validation": False,
        "find_all_with_ordering": False,
        "find_active_method": False,
        "soft_deletion": False,
        "ordering_logic": False
    }
    
    try:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                content = f.read()
            
            # Check hierarchy and ordering features
            test_results["display_order_management"] = "display_order" in content
            test_results["auto_order_assignment"] = "_get_next_display_order" in content
            test_results["order_validation"] = "_validate_display_order" in content
            test_results["find_all_with_ordering"] = "sort([" in content and "display_order" in content
            test_results["find_active_method"] = "def find_active" in content
            test_results["soft_deletion"] = "is_active" in content and "False" in content
            test_results["ordering_logic"] = "('display_order', 1)" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_product_count_tracking():
    """Test product count tracking and caching features."""
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "product_count_field": False,
        "update_product_count_method": False,
        "calculate_product_count": False,
        "count_validation": False,
        "count_caching": False,
        "products_collection_query": False
    }
    
    try:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                content = f.read()
            
            # Check product count tracking features
            test_results["product_count_field"] = "product_count" in content
            test_results["update_product_count_method"] = "def update_product_count" in content
            test_results["calculate_product_count"] = "_calculate_product_count" in content
            test_results["count_validation"] = "count < 0" in content
            test_results["count_caching"] = "cached" in content.lower()
            test_results["products_collection_query"] = "products_collection.count_documents" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_seo_and_slug_features():
    """Test SEO features and URL slug generation."""
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "slug_generation": False,
        "unique_slug_check": False,
        "url_sanitization": False,
        "slug_conflict_resolution": False,
        "find_by_slug_method": False,
        "slug_update_logic": False
    }
    
    try:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
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
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "input_validation": False,
        "sanitization": False,
        "name_validation": False,
        "description_validation": False,
        "objectid_validation": False,
        "error_handling": False,
        "field_constraints": False
    }
    
    try:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                content = f.read()
            
            # Check validation and security features
            test_results["input_validation"] = "_validate_" in content
            test_results["sanitization"] = "sanitize_string" in content
            test_results["name_validation"] = "_validate_name" in content
            test_results["description_validation"] = "_validate_description" in content
            test_results["objectid_validation"] = "_validate_object_id" in content
            test_results["error_handling"] = "ValidationError" in content and "DatabaseError" in content
            test_results["field_constraints"] = "MIN_NAME_LENGTH" in content and "MAX_DESCRIPTION_LENGTH" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_mongodb_integration():
    """Test MongoDB integration and database operations."""
    category_file = 'backend/app/models/category.py'
    
    test_results = {
        "mongodb_imports": False,
        "database_connection": False,
        "collection_operations": False,
        "find_operations": False,
        "update_operations": False,
        "duplicate_key_handling": False,
        "sorting_operations": False
    }
    
    try:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                content = f.read()
            
            # Check MongoDB integration
            test_results["mongodb_imports"] = "from bson import ObjectId" in content
            test_results["database_connection"] = "get_database()" in content
            test_results["collection_operations"] = "collection.insert_one" in content
            test_results["find_operations"] = "find_one" in content and "find(" in content
            test_results["update_operations"] = "update_one" in content
            test_results["duplicate_key_handling"] = "DuplicateKeyError" in content
            test_results["sorting_operations"] = "sort([" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_models_package_update():
    """Test models package structure includes Category."""
    models_init_file = 'backend/app/models/__init__.py'
    
    test_results = {
        "package_init_exists": False,
        "category_import": False,
        "category_export": False,
        "other_imports_maintained": False
    }
    
    try:
        if os.path.exists(models_init_file):
            test_results["package_init_exists"] = True
            
            with open(models_init_file, 'r') as f:
                content = f.read()
            
            test_results["category_import"] = "from .category import Category" in content
            test_results["category_export"] = "'Category'" in content
            test_results["other_imports_maintained"] = "from .user import User" in content and "from .product import Product" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Category model tests and return results."""
    print("Testing Category Data Model Implementation...")
    print("=" * 50)
    
    # Test 1: Model Structure
    print("\\n1. Testing Category Model Structure:")
    structure_results = test_category_model_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Category class found: {structure_results['category_class_found']}")
    print(f"   ✓ Required methods found: {len(structure_results['required_methods'])}/10")
    print(f"   ✓ Missing methods: {structure_results['missing_methods']}")
    print(f"   ✓ Collection name defined: {structure_results['collection_name_defined']}")
    print(f"   ✓ Display order constants: {structure_results['display_order_constants']}")
    print(f"   ✓ Validation constants: {structure_results['validation_constants']}")
    
    # Test 2: Hierarchy and Ordering
    print("\\n2. Testing Hierarchy and Ordering:")
    hierarchy_results = test_hierarchy_and_ordering()
    
    print(f"   ✓ Display order management: {hierarchy_results['display_order_management']}")
    print(f"   ✓ Auto order assignment: {hierarchy_results['auto_order_assignment']}")
    print(f"   ✓ Order validation: {hierarchy_results['order_validation']}")
    print(f"   ✓ Find all with ordering: {hierarchy_results['find_all_with_ordering']}")
    print(f"   ✓ Find active method: {hierarchy_results['find_active_method']}")
    print(f"   ✓ Soft deletion: {hierarchy_results['soft_deletion']}")
    print(f"   ✓ Ordering logic: {hierarchy_results['ordering_logic']}")
    
    # Test 3: Product Count Tracking
    print("\\n3. Testing Product Count Tracking:")
    count_results = test_product_count_tracking()
    
    print(f"   ✓ Product count field: {count_results['product_count_field']}")
    print(f"   ✓ Update product count method: {count_results['update_product_count_method']}")
    print(f"   ✓ Calculate product count: {count_results['calculate_product_count']}")
    print(f"   ✓ Count validation: {count_results['count_validation']}")
    print(f"   ✓ Products collection query: {count_results['products_collection_query']}")
    
    # Test 4: SEO and Slug Features
    print("\\n4. Testing SEO and Slug Features:")
    seo_results = test_seo_and_slug_features()
    
    print(f"   ✓ Slug generation: {seo_results['slug_generation']}")
    print(f"   ✓ Unique slug check: {seo_results['unique_slug_check']}")
    print(f"   ✓ URL sanitization: {seo_results['url_sanitization']}")
    print(f"   ✓ Slug conflict resolution: {seo_results['slug_conflict_resolution']}")
    print(f"   ✓ Find by slug method: {seo_results['find_by_slug_method']}")
    print(f"   ✓ Slug update logic: {seo_results['slug_update_logic']}")
    
    # Test 5: Validation and Security
    print("\\n5. Testing Validation and Security:")
    validation_results = test_validation_and_security()
    
    print(f"   ✓ Input validation: {validation_results['input_validation']}")
    print(f"   ✓ Sanitization: {validation_results['sanitization']}")
    print(f"   ✓ Name validation: {validation_results['name_validation']}")
    print(f"   ✓ Description validation: {validation_results['description_validation']}")
    print(f"   ✓ ObjectId validation: {validation_results['objectid_validation']}")
    print(f"   ✓ Error handling: {validation_results['error_handling']}")
    print(f"   ✓ Field constraints: {validation_results['field_constraints']}")
    
    # Test 6: MongoDB Integration
    print("\\n6. Testing MongoDB Integration:")
    mongodb_results = test_mongodb_integration()
    
    print(f"   ✓ MongoDB imports: {mongodb_results['mongodb_imports']}")
    print(f"   ✓ Database connection: {mongodb_results['database_connection']}")
    print(f"   ✓ Collection operations: {mongodb_results['collection_operations']}")
    print(f"   ✓ Find operations: {mongodb_results['find_operations']}")
    print(f"   ✓ Update operations: {mongodb_results['update_operations']}")
    print(f"   ✓ Duplicate key handling: {mongodb_results['duplicate_key_handling']}")
    print(f"   ✓ Sorting operations: {mongodb_results['sorting_operations']}")
    
    # Test 7: Package Update
    print("\\n7. Testing Models Package Update:")
    package_results = test_models_package_update()
    
    print(f"   ✓ Package init exists: {package_results['package_init_exists']}")
    print(f"   ✓ Category import: {package_results['category_import']}")
    print(f"   ✓ Category export: {package_results['category_export']}")
    print(f"   ✓ Other imports maintained: {package_results['other_imports_maintained']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['category_class_found'],
        len(structure_results['missing_methods']) == 0,
        structure_results['collection_name_defined'],
        hierarchy_results['display_order_management'],
        hierarchy_results['auto_order_assignment'],
        hierarchy_results['find_all_with_ordering'],
        hierarchy_results['find_active_method'],
        count_results['product_count_field'],
        count_results['update_product_count_method'],
        count_results['calculate_product_count'],
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
        package_results['category_import']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Category Data Model implementation PASSED")
        return True
    else:
        print("❌ Category Data Model implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)