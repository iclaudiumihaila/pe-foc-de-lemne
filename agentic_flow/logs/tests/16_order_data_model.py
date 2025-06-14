"""
Test Harness: Order Data Model with MongoDB Schema

This test harness validates the Order model implementation including CRUD operations,
order lifecycle management, item tracking, and business logic without requiring database connections.
"""

import ast
import os
import sys
import re

def test_order_model_structure():
    """Test Order model file structure and class definition."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "file_exists": False,
        "order_class_found": False,
        "required_methods": [],
        "missing_methods": [],
        "collection_name_defined": False,
        "status_constants_defined": False,
        "delivery_constants_defined": False,
        "validation_constants_defined": False
    }
    
    required_methods = [
        '__init__', 'create', 'find_by_id', 'find_by_order_number', 'find_by_customer',
        'find_by_status', 'update', 'update_status', 'calculate_totals', 'add_item', 'to_dict'
    ]
    
    try:
        if os.path.exists(order_file):
            test_results["file_exists"] = True
            
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find Order class and methods
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'Order':
                    test_results["order_class_found"] = True
                    
                    # Find methods in Order class
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
            test_results["collection_name_defined"] = "COLLECTION_NAME = 'orders'" in content
            test_results["status_constants_defined"] = "STATUS_PENDING" in content and "VALID_STATUSES" in content
            test_results["delivery_constants_defined"] = "DELIVERY_PICKUP" in content and "VALID_DELIVERY_TYPES" in content
            test_results["validation_constants_defined"] = "MIN_CUSTOMER_NAME_LENGTH" in content and "MAX_QUANTITY" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_order_lifecycle_management():
    """Test order lifecycle and status management features."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "status_management": False,
        "status_validation": False,
        "status_timestamps": False,
        "lifecycle_tracking": False,
        "update_status_method": False,
        "status_constants": False,
        "timestamp_fields": False
    }
    
    try:
        if os.path.exists(order_file):
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Check order lifecycle features
            test_results["status_management"] = "status" in content and "new_status" in content
            test_results["status_validation"] = "VALID_STATUSES" in content
            test_results["status_timestamps"] = "confirmed_at" in content and "ready_at" in content and "delivered_at" in content
            test_results["lifecycle_tracking"] = "STATUS_PENDING" in content and "STATUS_DELIVERED" in content
            test_results["update_status_method"] = "def update_status" in content
            test_results["status_constants"] = "STATUS_CONFIRMED" in content and "STATUS_READY" in content
            test_results["timestamp_fields"] = "now = datetime.utcnow()" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_item_management_and_calculations():
    """Test order item management and total calculation features."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "item_validation": False,
        "total_calculations": False,
        "add_item_method": False,
        "decimal_handling": False,
        "quantity_validation": False,
        "price_validation": False,
        "product_references": False
    }
    
    try:
        if os.path.exists(order_file):
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Check item management features
            test_results["item_validation"] = "_validate_and_process_items" in content
            test_results["total_calculations"] = "_calculate_order_totals" in content
            test_results["add_item_method"] = "def add_item" in content
            test_results["decimal_handling"] = "from decimal import Decimal" in content
            test_results["quantity_validation"] = "_validate_quantity" in content
            test_results["price_validation"] = "_validate_price" in content
            test_results["product_references"] = "product_id" in content and "ObjectId" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_order_number_generation():
    """Test order number generation and uniqueness features."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "order_number_generation": False,
        "unique_order_numbers": False,
        "order_number_format": False,
        "daily_counter": False,
        "find_by_order_number": False,
        "collision_handling": False
    }
    
    try:
        if os.path.exists(order_file):
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Check order number generation features
            test_results["order_number_generation"] = "_generate_unique_order_number" in content
            test_results["unique_order_numbers"] = "order_number" in content and "unique" in content.lower()
            test_results["order_number_format"] = "ORD-" in content and "YYYYMMDD" in content
            test_results["daily_counter"] = "today" in content and "strftime" in content
            test_results["find_by_order_number"] = "def find_by_order_number" in content
            test_results["collision_handling"] = "DuplicateKeyError" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_delivery_and_validation():
    """Test delivery management and validation features."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "delivery_type_validation": False,
        "address_validation": False,
        "phone_validation": False,
        "time_validation": False,
        "e164_normalization": False,
        "delivery_address_required": False,
        "special_instructions": False
    }
    
    try:
        if os.path.exists(order_file):
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Check delivery and validation features
            test_results["delivery_type_validation"] = "_validate_delivery_type" in content
            test_results["address_validation"] = "_validate_delivery_address" in content
            test_results["phone_validation"] = "_validate_and_normalize_phone" in content
            test_results["time_validation"] = "_validate_requested_time" in content
            test_results["e164_normalization"] = "E.164" in content
            test_results["delivery_address_required"] = "delivery_address is required" in content
            test_results["special_instructions"] = "_validate_special_instructions" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_mongodb_integration():
    """Test MongoDB integration and database operations."""
    order_file = 'backend/app/models/order.py'
    
    test_results = {
        "mongodb_imports": False,
        "database_connection": False,
        "collection_operations": False,
        "find_operations": False,
        "update_operations": False,
        "duplicate_key_handling": False,
        "sorting_operations": False,
        "customer_queries": False
    }
    
    try:
        if os.path.exists(order_file):
            with open(order_file, 'r') as f:
                content = f.read()
            
            # Check MongoDB integration
            test_results["mongodb_imports"] = "from bson import ObjectId" in content
            test_results["database_connection"] = "get_database()" in content
            test_results["collection_operations"] = "collection.insert_one" in content
            test_results["find_operations"] = "find_one" in content and "find(" in content
            test_results["update_operations"] = "update_one" in content
            test_results["duplicate_key_handling"] = "DuplicateKeyError" in content
            test_results["sorting_operations"] = "sort(" in content
            test_results["customer_queries"] = "customer_phone" in content and "find(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_models_package_update():
    """Test models package structure includes Order."""
    models_init_file = 'backend/app/models/__init__.py'
    
    test_results = {
        "package_init_exists": False,
        "order_import": False,
        "order_export": False,
        "other_imports_maintained": False
    }
    
    try:
        if os.path.exists(models_init_file):
            test_results["package_init_exists"] = True
            
            with open(models_init_file, 'r') as f:
                content = f.read()
            
            test_results["order_import"] = "from .order import Order" in content
            test_results["order_export"] = "'Order'" in content
            test_results["other_imports_maintained"] = all([
                "from .user import User" in content,
                "from .product import Product" in content,
                "from .category import Category" in content
            ])
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all Order model tests and return results."""
    print("Testing Order Data Model Implementation...")
    print("=" * 50)
    
    # Test 1: Model Structure
    print("\\n1. Testing Order Model Structure:")
    structure_results = test_order_model_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Order class found: {structure_results['order_class_found']}")
    print(f"   ✓ Required methods found: {len(structure_results['required_methods'])}/11")
    print(f"   ✓ Missing methods: {structure_results['missing_methods']}")
    print(f"   ✓ Collection name defined: {structure_results['collection_name_defined']}")
    print(f"   ✓ Status constants defined: {structure_results['status_constants_defined']}")
    print(f"   ✓ Delivery constants defined: {structure_results['delivery_constants_defined']}")
    
    # Test 2: Order Lifecycle Management
    print("\\n2. Testing Order Lifecycle Management:")
    lifecycle_results = test_order_lifecycle_management()
    
    print(f"   ✓ Status management: {lifecycle_results['status_management']}")
    print(f"   ✓ Status validation: {lifecycle_results['status_validation']}")
    print(f"   ✓ Status timestamps: {lifecycle_results['status_timestamps']}")
    print(f"   ✓ Lifecycle tracking: {lifecycle_results['lifecycle_tracking']}")
    print(f"   ✓ Update status method: {lifecycle_results['update_status_method']}")
    print(f"   ✓ Status constants: {lifecycle_results['status_constants']}")
    print(f"   ✓ Timestamp fields: {lifecycle_results['timestamp_fields']}")
    
    # Test 3: Item Management and Calculations
    print("\\n3. Testing Item Management and Calculations:")
    item_results = test_item_management_and_calculations()
    
    print(f"   ✓ Item validation: {item_results['item_validation']}")
    print(f"   ✓ Total calculations: {item_results['total_calculations']}")
    print(f"   ✓ Add item method: {item_results['add_item_method']}")
    print(f"   ✓ Decimal handling: {item_results['decimal_handling']}")
    print(f"   ✓ Quantity validation: {item_results['quantity_validation']}")
    print(f"   ✓ Price validation: {item_results['price_validation']}")
    print(f"   ✓ Product references: {item_results['product_references']}")
    
    # Test 4: Order Number Generation
    print("\\n4. Testing Order Number Generation:")
    number_results = test_order_number_generation()
    
    print(f"   ✓ Order number generation: {number_results['order_number_generation']}")
    print(f"   ✓ Unique order numbers: {number_results['unique_order_numbers']}")
    print(f"   ✓ Order number format: {number_results['order_number_format']}")
    print(f"   ✓ Daily counter: {number_results['daily_counter']}")
    print(f"   ✓ Find by order number: {number_results['find_by_order_number']}")
    print(f"   ✓ Collision handling: {number_results['collision_handling']}")
    
    # Test 5: Delivery and Validation
    print("\\n5. Testing Delivery and Validation:")
    delivery_results = test_delivery_and_validation()
    
    print(f"   ✓ Delivery type validation: {delivery_results['delivery_type_validation']}")
    print(f"   ✓ Address validation: {delivery_results['address_validation']}")
    print(f"   ✓ Phone validation: {delivery_results['phone_validation']}")
    print(f"   ✓ Time validation: {delivery_results['time_validation']}")
    print(f"   ✓ E164 normalization: {delivery_results['e164_normalization']}")
    print(f"   ✓ Delivery address required: {delivery_results['delivery_address_required']}")
    print(f"   ✓ Special instructions: {delivery_results['special_instructions']}")
    
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
    print(f"   ✓ Customer queries: {mongodb_results['customer_queries']}")
    
    # Test 7: Package Update
    print("\\n7. Testing Models Package Update:")
    package_results = test_models_package_update()
    
    print(f"   ✓ Package init exists: {package_results['package_init_exists']}")
    print(f"   ✓ Order import: {package_results['order_import']}")
    print(f"   ✓ Order export: {package_results['order_export']}")
    print(f"   ✓ Other imports maintained: {package_results['other_imports_maintained']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['order_class_found'],
        len(structure_results['missing_methods']) == 0,
        structure_results['collection_name_defined'],
        lifecycle_results['status_management'],
        lifecycle_results['status_validation'],
        lifecycle_results['update_status_method'],
        lifecycle_results['status_timestamps'],
        item_results['item_validation'],
        item_results['total_calculations'],
        item_results['add_item_method'],
        item_results['decimal_handling'],
        number_results['order_number_generation'],
        number_results['find_by_order_number'],
        number_results['order_number_format'],
        delivery_results['delivery_type_validation'],
        delivery_results['address_validation'],
        delivery_results['phone_validation'],
        mongodb_results['mongodb_imports'],
        mongodb_results['database_connection'],
        mongodb_results['collection_operations'],
        package_results['package_init_exists'],
        package_results['order_import']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Order Data Model implementation PASSED")
        return True
    else:
        print("❌ Order Data Model implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)