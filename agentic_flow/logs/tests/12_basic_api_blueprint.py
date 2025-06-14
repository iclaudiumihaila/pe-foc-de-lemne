"""
Test Harness: Basic API Blueprint with Health Check

This test harness validates the API blueprint implementation and health check endpoint
without requiring external dependencies or actual Flask server execution.
"""

import ast
import os
import sys

def test_api_blueprint_structure():
    """Test API blueprint file structure and components."""
    routes_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "file_exists": False,
        "functions_found": [],
        "health_check_function": False,
        "register_routes_function": False,
        "api_blueprint_defined": False,
        "health_route_endpoint": False,
        "import_statements": []
    }
    
    try:
        # Check if file exists
        if os.path.exists(routes_file):
            test_results["file_exists"] = True
            
            # Read and parse file content
            with open(routes_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find components
            tree = ast.parse(content)
            
            # Find functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    test_results["functions_found"].append(node.name)
                    
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        test_results["import_statements"].append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        test_results["import_statements"].append(f"{module}.{alias.name}")
            
            # Check specific requirements
            test_results["health_check_function"] = 'health_check' in test_results["functions_found"]
            test_results["register_routes_function"] = 'register_routes' in test_results["functions_found"]
            test_results["api_blueprint_defined"] = 'api = Blueprint' in content
            test_results["health_route_endpoint"] = '/health' in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_flask_app_integration():
    """Test Flask app factory integration with routes."""
    app_file = 'backend/app/__init__.py'
    
    test_results = {
        "file_exists": False,
        "imports_routes": False,
        "calls_register_routes": False,
        "imports_error_handlers": False,
        "imports_database": False,
        "create_app_function": False
    }
    
    try:
        # Check if file exists
        if os.path.exists(app_file):
            test_results["file_exists"] = True
            
            # Read file content
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Check integration requirements
            test_results["imports_routes"] = 'from app.routes import register_routes' in content
            test_results["calls_register_routes"] = 'register_routes(app)' in content
            test_results["imports_error_handlers"] = 'from app.utils.error_handlers import register_error_handlers' in content
            test_results["imports_database"] = 'from app.database import init_mongodb' in content
            test_results["create_app_function"] = 'def create_app(' in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_health_endpoint_specification():
    """Test health endpoint specification compliance."""
    routes_file = 'backend/app/routes/__init__.py'
    
    test_results = {
        "health_route_method": False,
        "database_ping_test": False,
        "success_response_format": False,
        "error_response_format": False,
        "logging_integration": False,
        "version_included": False,
        "timestamp_included": False
    }
    
    try:
        if os.path.exists(routes_file):
            with open(routes_file, 'r') as f:
                content = f.read()
            
            # Check endpoint specifications
            test_results["health_route_method"] = "@api.route('/health', methods=['GET'])" in content
            test_results["database_ping_test"] = "db.command('ping')" in content
            test_results["success_response_format"] = "success_response(" in content
            test_results["error_response_format"] = "create_error_response(" in content
            test_results["logging_integration"] = "logging.info(" in content or "logging.error(" in content
            test_results["version_included"] = '"version": "1.0.0"' in content
            test_results["timestamp_included"] = 'datetime.utcnow().isoformat()' in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all API blueprint tests and return results."""
    print("Testing API Blueprint Implementation...")
    print("=" * 50)
    
    # Test 1: Blueprint Structure
    print("\n1. Testing API Blueprint Structure:")
    structure_results = test_api_blueprint_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Functions found: {structure_results['functions_found']}")
    print(f"   ✓ Health check function: {structure_results['health_check_function']}")
    print(f"   ✓ Register routes function: {structure_results['register_routes_function']}")
    print(f"   ✓ API blueprint defined: {structure_results['api_blueprint_defined']}")
    print(f"   ✓ Health route endpoint: {structure_results['health_route_endpoint']}")
    
    # Test 2: Flask Integration
    print("\n2. Testing Flask App Integration:")
    integration_results = test_flask_app_integration()
    
    print(f"   ✓ App factory file exists: {integration_results['file_exists']}")
    print(f"   ✓ Imports routes module: {integration_results['imports_routes']}")
    print(f"   ✓ Calls register_routes: {integration_results['calls_register_routes']}")
    print(f"   ✓ Imports error handlers: {integration_results['imports_error_handlers']}")
    print(f"   ✓ Imports database module: {integration_results['imports_database']}")
    print(f"   ✓ Create app function exists: {integration_results['create_app_function']}")
    
    # Test 3: Health Endpoint Specification
    print("\n3. Testing Health Endpoint Specification:")
    endpoint_results = test_health_endpoint_specification()
    
    print(f"   ✓ GET method route: {endpoint_results['health_route_method']}")
    print(f"   ✓ Database ping test: {endpoint_results['database_ping_test']}")
    print(f"   ✓ Success response format: {endpoint_results['success_response_format']}")
    print(f"   ✓ Error response format: {endpoint_results['error_response_format']}")
    print(f"   ✓ Logging integration: {endpoint_results['logging_integration']}")
    print(f"   ✓ Version included: {endpoint_results['version_included']}")
    print(f"   ✓ Timestamp included: {endpoint_results['timestamp_included']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['health_check_function'],
        structure_results['register_routes_function'],
        structure_results['api_blueprint_defined'],
        structure_results['health_route_endpoint'],
        integration_results['file_exists'],
        integration_results['imports_routes'],
        integration_results['calls_register_routes'],
        integration_results['imports_error_handlers'],
        integration_results['imports_database'],
        endpoint_results['health_route_method'],
        endpoint_results['database_ping_test'],
        endpoint_results['success_response_format'],
        endpoint_results['error_response_format'],
        endpoint_results['logging_integration']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ API Blueprint with Health Check implementation PASSED")
        return True
    else:
        print("❌ API Blueprint with Health Check implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)