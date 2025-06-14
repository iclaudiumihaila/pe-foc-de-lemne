"""
Test Harness: Order Management Endpoints

This test harness validates the order management endpoints implementation including
order creation, status management, customer access, and admin order management 
without requiring actual execution.
"""

import ast
import os
import sys
import re

def test_orders_endpoints_structure():
    """Test orders endpoints file structure and functions."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "file_exists": False,
        "blueprint_defined": False,
        "required_endpoints": [],
        "missing_endpoints": [],
        "admin_decorator": False,
        "order_schema": False
    }
    
    required_endpoints = [
        'create_order', 'get_customer_orders', 'get_order', 'cancel_order',
        'list_orders', 'update_order_status', 'get_order_admin'
    ]
    
    try:
        if os.path.exists(orders_file):
            test_results["file_exists"] = True
            
            with open(orders_file, 'r') as f:
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
            test_results["blueprint_defined"] = "orders_bp = Blueprint" in content
            test_results["admin_decorator"] = "require_admin" in content
            test_results["order_schema"] = "ORDER_SCHEMA" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_customer_order_endpoints():
    """Test customer order endpoints (creation, access, cancellation)."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "create_order_endpoint": False,
        "get_customer_orders_endpoint": False,
        "get_order_endpoint": False,
        "cancel_order_endpoint": False,
        "phone_verification": False,
        "stock_validation": False,
        "sms_integration": False,
        "order_confirmation": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check customer endpoints
            test_results["create_order_endpoint"] = "@orders_bp.route('/', methods=['POST'])" in content
            test_results["get_customer_orders_endpoint"] = "@orders_bp.route('/customer/<phone>', methods=['GET'])" in content
            test_results["get_order_endpoint"] = "@orders_bp.route('/<order_id>', methods=['GET'])" in content
            test_results["cancel_order_endpoint"] = "@orders_bp.route('/<order_id>/cancel', methods=['PUT'])" in content
            
            # Check features
            test_results["phone_verification"] = "validate_recent_code" in content
            test_results["stock_validation"] = "stock_quantity" in content and "update_stock" in content
            test_results["sms_integration"] = "get_sms_service()" in content
            test_results["order_confirmation"] = "Order confirmed" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_admin_order_endpoints():
    """Test admin order management endpoints."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "list_orders_endpoint": False,
        "update_status_endpoint": False,
        "get_order_admin_endpoint": False,
        "admin_authorization": False,
        "status_validation": False,
        "pagination_support": False,
        "filtering_support": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check admin endpoints
            test_results["list_orders_endpoint"] = "def list_orders" in content and "@require_admin" in content
            test_results["update_status_endpoint"] = "@orders_bp.route('/<order_id>/status', methods=['PUT'])" in content
            test_results["get_order_admin_endpoint"] = "@orders_bp.route('/<order_id>/admin', methods=['GET'])" in content
            
            # Check admin features
            test_results["admin_authorization"] = "@require_admin" in content
            test_results["status_validation"] = "VALID_STATUSES" in content
            test_results["pagination_support"] = "page" in content and "limit" in content
            test_results["filtering_support"] = "status_filter" in content and "customer_phone" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_order_creation_workflow():
    """Test order creation workflow and validation."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "phone_verification_required": False,
        "product_validation": False,
        "stock_checking": False,
        "total_calculation": False,
        "order_number_generation": False,
        "stock_deduction": False,
        "sms_confirmation": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check order creation workflow
            test_results["phone_verification_required"] = "verification_code" in content and "validate_recent_code" in content
            test_results["product_validation"] = "Product.find_by_id" in content
            test_results["stock_checking"] = "stock_quantity" in content and "Insufficient stock" in content
            test_results["total_calculation"] = "item_total" in content and "processed_items" in content
            test_results["order_number_generation"] = "Order.create" in content
            test_results["stock_deduction"] = "update_stock" in content and "subtract" in content
            test_results["sms_confirmation"] = "Order confirmed" in content and "send_notification" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_order_lifecycle_management():
    """Test order status management and lifecycle."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "status_transitions": False,
        "status_notifications": False,
        "order_cancellation": False,
        "stock_restoration": False,
        "timestamp_tracking": False,
        "admin_status_update": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check lifecycle management
            test_results["status_transitions"] = "update_status" in content and "new_status" in content
            test_results["status_notifications"] = "status_messages" in content and "send_notification" in content
            test_results["order_cancellation"] = "STATUS_CANCELLED" in content
            test_results["stock_restoration"] = "add" in content and "cancel" in content
            test_results["timestamp_tracking"] = "confirmed_at" in content or "ready_at" in content
            test_results["admin_status_update"] = "update_order_status" in content and "@require_admin" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_and_security():
    """Test input validation and security features."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "json_schema_validation": False,
        "phone_validation": False,
        "admin_role_check": False,
        "object_id_validation": False,
        "order_ownership": False,
        "error_standardization": False,
        "logging_integration": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check validation features
            test_results["json_schema_validation"] = "ORDER_SCHEMA" in content and "@validate_json" in content
            test_results["phone_validation"] = "validate_phone_number" in content
            test_results["admin_role_check"] = "User.ROLE_ADMIN" in content
            test_results["object_id_validation"] = "ObjectId" in content and "re.match" in content
            test_results["order_ownership"] = "customer_phone" in content and "session" in content
            test_results["error_standardization"] = "create_error_response" in content
            test_results["logging_integration"] = "logging.info" in content and "logging.error" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_model_integration():
    """Test integration with models and services."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "order_model_integration": False,
        "product_model_integration": False,
        "user_model_integration": False,
        "sms_service_integration": False,
        "aggregation_usage": False,
        "database_operations": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check model integrations
            test_results["order_model_integration"] = "from app.models.order import Order" in content
            test_results["product_model_integration"] = "from app.models.product import Product" in content
            test_results["user_model_integration"] = "from app.models.user import User" in content
            test_results["sms_service_integration"] = "from app.services.sms_service import get_sms_service" in content
            test_results["aggregation_usage"] = "pipeline" in content and "$facet" in content
            test_results["database_operations"] = "find_by_id" in content and "find_by_customer_phone" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_response_formatting():
    """Test response formatting and API consistency."""
    orders_file = 'backend/app/routes/orders.py'
    
    test_results = {
        "success_response_format": False,
        "pagination_metadata": False,
        "order_dict_conversion": False,
        "status_codes": False,
        "error_handling": False,
        "sms_integration": False
    }
    
    try:
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                content = f.read()
            
            # Check response formatting
            test_results["success_response_format"] = "success_response" in content
            test_results["pagination_metadata"] = "total_pages" in content and "has_next" in content
            test_results["order_dict_conversion"] = "to_dict()" in content
            test_results["status_codes"] = "201" in content and "400" in content and "409" in content
            test_results["error_handling"] = "create_error_response" in content
            test_results["sms_integration"] = "send_notification" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_blueprint_registration():
    """Test blueprint registration in routes/__init__.py."""
    routes_init_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "orders_import": False,
        "blueprint_registration": False,
        "url_prefix": False
    }
    
    try:
        if os.path.exists(routes_init_file):
            with open(routes_init_file, 'r') as f:
                content = f.read()
            
            test_results["orders_import"] = "from .orders import orders_bp" in content
            test_results["blueprint_registration"] = "register_blueprint(orders_bp" in content
            test_results["url_prefix"] = "url_prefix='/orders'" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all order management endpoints tests and return results."""
    print("Testing Order Management Endpoints Implementation...")
    print("=" * 50)
    
    # Test 1: Endpoints Structure
    print("\n1. Testing Orders Endpoints Structure:")
    structure_results = test_orders_endpoints_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Blueprint defined: {structure_results['blueprint_defined']}")
    print(f"   ✓ Required endpoints found: {len(structure_results['required_endpoints'])}/7")
    print(f"   ✓ Missing endpoints: {structure_results['missing_endpoints']}")
    print(f"   ✓ Admin decorator: {structure_results['admin_decorator']}")
    print(f"   ✓ Order schema: {structure_results['order_schema']}")
    
    # Test 2: Customer Order Endpoints
    print("\n2. Testing Customer Order Endpoints:")
    customer_results = test_customer_order_endpoints()
    
    print(f"   ✓ Create order endpoint: {customer_results['create_order_endpoint']}")
    print(f"   ✓ Get customer orders endpoint: {customer_results['get_customer_orders_endpoint']}")
    print(f"   ✓ Get order endpoint: {customer_results['get_order_endpoint']}")
    print(f"   ✓ Cancel order endpoint: {customer_results['cancel_order_endpoint']}")
    print(f"   ✓ Phone verification: {customer_results['phone_verification']}")
    print(f"   ✓ Stock validation: {customer_results['stock_validation']}")
    print(f"   ✓ SMS integration: {customer_results['sms_integration']}")
    print(f"   ✓ Order confirmation: {customer_results['order_confirmation']}")
    
    # Test 3: Admin Order Endpoints
    print("\n3. Testing Admin Order Endpoints:")
    admin_results = test_admin_order_endpoints()
    
    print(f"   ✓ List orders endpoint: {admin_results['list_orders_endpoint']}")
    print(f"   ✓ Update status endpoint: {admin_results['update_status_endpoint']}")
    print(f"   ✓ Get order admin endpoint: {admin_results['get_order_admin_endpoint']}")
    print(f"   ✓ Admin authorization: {admin_results['admin_authorization']}")
    print(f"   ✓ Status validation: {admin_results['status_validation']}")
    print(f"   ✓ Pagination support: {admin_results['pagination_support']}")
    print(f"   ✓ Filtering support: {admin_results['filtering_support']}")
    
    # Test 4: Order Creation Workflow
    print("\n4. Testing Order Creation Workflow:")
    creation_results = test_order_creation_workflow()
    
    print(f"   ✓ Phone verification required: {creation_results['phone_verification_required']}")
    print(f"   ✓ Product validation: {creation_results['product_validation']}")
    print(f"   ✓ Stock checking: {creation_results['stock_checking']}")
    print(f"   ✓ Total calculation: {creation_results['total_calculation']}")
    print(f"   ✓ Order number generation: {creation_results['order_number_generation']}")
    print(f"   ✓ Stock deduction: {creation_results['stock_deduction']}")
    print(f"   ✓ SMS confirmation: {creation_results['sms_confirmation']}")
    
    # Test 5: Order Lifecycle Management
    print("\n5. Testing Order Lifecycle Management:")
    lifecycle_results = test_order_lifecycle_management()
    
    print(f"   ✓ Status transitions: {lifecycle_results['status_transitions']}")
    print(f"   ✓ Status notifications: {lifecycle_results['status_notifications']}")
    print(f"   ✓ Order cancellation: {lifecycle_results['order_cancellation']}")
    print(f"   ✓ Stock restoration: {lifecycle_results['stock_restoration']}")
    print(f"   ✓ Timestamp tracking: {lifecycle_results['timestamp_tracking']}")
    print(f"   ✓ Admin status update: {lifecycle_results['admin_status_update']}")
    
    # Test 6: Validation and Security
    print("\n6. Testing Validation and Security:")
    security_results = test_validation_and_security()
    
    print(f"   ✓ JSON schema validation: {security_results['json_schema_validation']}")
    print(f"   ✓ Phone validation: {security_results['phone_validation']}")
    print(f"   ✓ Admin role check: {security_results['admin_role_check']}")
    print(f"   ✓ ObjectId validation: {security_results['object_id_validation']}")
    print(f"   ✓ Order ownership: {security_results['order_ownership']}")
    print(f"   ✓ Error standardization: {security_results['error_standardization']}")
    print(f"   ✓ Logging integration: {security_results['logging_integration']}")
    
    # Test 7: Model Integration
    print("\n7. Testing Model Integration:")
    model_results = test_model_integration()
    
    print(f"   ✓ Order model integration: {model_results['order_model_integration']}")
    print(f"   ✓ Product model integration: {model_results['product_model_integration']}")
    print(f"   ✓ User model integration: {model_results['user_model_integration']}")
    print(f"   ✓ SMS service integration: {model_results['sms_service_integration']}")
    print(f"   ✓ Aggregation usage: {model_results['aggregation_usage']}")
    print(f"   ✓ Database operations: {model_results['database_operations']}")
    
    # Test 8: Response Formatting
    print("\n8. Testing Response Formatting:")
    response_results = test_response_formatting()
    
    print(f"   ✓ Success response format: {response_results['success_response_format']}")
    print(f"   ✓ Pagination metadata: {response_results['pagination_metadata']}")
    print(f"   ✓ Order dict conversion: {response_results['order_dict_conversion']}")
    print(f"   ✓ Status codes: {response_results['status_codes']}")
    print(f"   ✓ Error handling: {response_results['error_handling']}")
    print(f"   ✓ SMS integration: {response_results['sms_integration']}")
    
    # Test 9: Blueprint Registration
    print("\n9. Testing Blueprint Registration:")
    blueprint_results = test_blueprint_registration()
    
    print(f"   ✓ Orders import: {blueprint_results['orders_import']}")
    print(f"   ✓ Blueprint registration: {blueprint_results['blueprint_registration']}")
    print(f"   ✓ URL prefix: {blueprint_results['url_prefix']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['blueprint_defined'],
        len(structure_results['missing_endpoints']) == 0,
        structure_results['admin_decorator'],
        structure_results['order_schema'],
        customer_results['create_order_endpoint'],
        customer_results['get_customer_orders_endpoint'],
        customer_results['get_order_endpoint'],
        customer_results['cancel_order_endpoint'],
        customer_results['phone_verification'],
        customer_results['stock_validation'],
        admin_results['list_orders_endpoint'],
        admin_results['update_status_endpoint'],
        admin_results['get_order_admin_endpoint'],
        admin_results['admin_authorization'],
        admin_results['pagination_support'],
        creation_results['phone_verification_required'],
        creation_results['product_validation'],
        creation_results['stock_checking'],
        creation_results['total_calculation'],
        creation_results['stock_deduction'],
        lifecycle_results['status_transitions'],
        lifecycle_results['status_notifications'],
        lifecycle_results['order_cancellation'],
        lifecycle_results['stock_restoration'],
        security_results['json_schema_validation'],
        security_results['phone_validation'],
        security_results['admin_role_check'],
        security_results['error_standardization'],
        model_results['order_model_integration'],
        model_results['product_model_integration'],
        model_results['sms_service_integration'],
        response_results['success_response_format'],
        response_results['order_dict_conversion'],
        blueprint_results['orders_import'],
        blueprint_results['blueprint_registration']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ Order Management Endpoints implementation PASSED")
        return True
    else:
        print("❌ Order Management Endpoints implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)