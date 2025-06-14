"""
Test Harness: User Data Model with MongoDB Schema

This test harness validates the User model implementation including CRUD operations,
security features, and MongoDB schema compliance without requiring database connections.
"""

import ast
import os
import sys
import re

def test_user_model_structure():
    """Test User model file structure and class definition."""
    user_file = 'backend/app/models/user.py'
    
    test_results = {
        "file_exists": False,
        "user_class_found": False,
        "required_methods": [],
        "missing_methods": [],
        "collection_name_defined": False,
        "roles_defined": False,
        "bcrypt_rounds_defined": False
    }
    
    required_methods = [
        '__init__', 'create', 'find_by_phone', 'find_by_id', 'update',
        'set_password', 'verify_password', 'set_verification_code',
        'verify_phone', 'to_dict'
    ]
    
    try:
        if os.path.exists(user_file):
            test_results["file_exists"] = True
            
            with open(user_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find User class and methods
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'User':
                    test_results["user_class_found"] = True
                    
                    # Find methods in User class
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
            test_results["collection_name_defined"] = "COLLECTION_NAME = 'users'" in content
            test_results["roles_defined"] = "ROLE_CUSTOMER" in content and "ROLE_ADMIN" in content
            test_results["bcrypt_rounds_defined"] = "BCRYPT_ROUNDS" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_security_features():
    """Test security-related features in User model."""
    user_file = 'backend/app/models/user.py'
    
    test_results = {
        "bcrypt_import": False,
        "password_hashing": False,
        "password_verification": False,
        "phone_normalization": False,
        "sensitive_data_exclusion": False,
        "verification_code_validation": False,
        "password_strength_validation": False
    }
    
    try:
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                content = f.read()
            
            # Check security features
            test_results["bcrypt_import"] = "import bcrypt" in content
            test_results["password_hashing"] = "bcrypt.hashpw" in content
            test_results["password_verification"] = "bcrypt.checkpw" in content
            test_results["phone_normalization"] = "_normalize_phone_number" in content
            test_results["sensitive_data_exclusion"] = "include_sensitive" in content
            test_results["verification_code_validation"] = "re.match(r'^\\d{6}$'" in content
            test_results["password_strength_validation"] = "len(password) < 8" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_mongodb_integration():
    """Test MongoDB integration and database operations."""
    user_file = 'backend/app/models/user.py'
    
    test_results = {
        "mongodb_imports": False,
        "database_connection": False,
        "objectid_usage": False,
        "collection_operations": False,
        "duplicate_key_handling": False,
        "database_error_handling": False,
        "find_operations": False,
        "update_operations": False
    }
    
    try:
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                content = f.read()
            
            # Check MongoDB integration
            test_results["mongodb_imports"] = "from bson import ObjectId" in content
            test_results["database_connection"] = "get_database()" in content
            test_results["objectid_usage"] = "ObjectId(" in content
            test_results["collection_operations"] = "collection.insert_one" in content
            test_results["duplicate_key_handling"] = "DuplicateKeyError" in content
            test_results["database_error_handling"] = "DatabaseError" in content
            test_results["find_operations"] = "find_one" in content
            test_results["update_operations"] = "update_one" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_validation_integration():
    """Test integration with validation middleware."""
    user_file = 'backend/app/models/user.py'
    
    test_results = {
        "validation_imports": False,
        "phone_validation": False,
        "validation_error_usage": False,
        "field_validation": False,
        "error_code_usage": False
    }
    
    try:
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                content = f.read()
            
            # Check validation integration
            test_results["validation_imports"] = "from app.utils.validators import" in content
            test_results["phone_validation"] = "validate_phone_number" in content
            test_results["validation_error_usage"] = "ValidationError" in content
            test_results["field_validation"] = "len(name.strip())" in content
            test_results["error_code_usage"] = '"DB_001"' in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_models_package():
    """Test models package structure and exports."""
    models_init_file = 'backend/app/models/__init__.py'
    
    test_results = {
        "package_init_exists": False,
        "user_import": False,
        "user_export": False
    }
    
    try:
        if os.path.exists(models_init_file):
            test_results["package_init_exists"] = True
            
            with open(models_init_file, 'r') as f:
                content = f.read()
            
            test_results["user_import"] = "from .user import User" in content
            test_results["user_export"] = "__all__ = ['User']" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all User model tests and return results."""
    print("Testing User Data Model Implementation...")
    print("=" * 50)
    
    # Test 1: Model Structure
    print("\\n1. Testing User Model Structure:")
    structure_results = test_user_model_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ User class found: {structure_results['user_class_found']}")
    print(f"   ✓ Required methods found: {len(structure_results['required_methods'])}/10")
    print(f"   ✓ Missing methods: {structure_results['missing_methods']}")
    print(f"   ✓ Collection name defined: {structure_results['collection_name_defined']}")
    print(f"   ✓ User roles defined: {structure_results['roles_defined']}")
    print(f"   ✓ Bcrypt rounds defined: {structure_results['bcrypt_rounds_defined']}")
    
    # Test 2: Security Features
    print("\\n2. Testing Security Features:")
    security_results = test_security_features()
    
    print(f"   ✓ Bcrypt import: {security_results['bcrypt_import']}")
    print(f"   ✓ Password hashing: {security_results['password_hashing']}")
    print(f"   ✓ Password verification: {security_results['password_verification']}")
    print(f"   ✓ Phone normalization: {security_results['phone_normalization']}")
    print(f"   ✓ Sensitive data exclusion: {security_results['sensitive_data_exclusion']}")
    print(f"   ✓ Verification code validation: {security_results['verification_code_validation']}")
    print(f"   ✓ Password strength validation: {security_results['password_strength_validation']}")
    
    # Test 3: MongoDB Integration
    print("\\n3. Testing MongoDB Integration:")
    mongodb_results = test_mongodb_integration()
    
    print(f"   ✓ MongoDB imports: {mongodb_results['mongodb_imports']}")
    print(f"   ✓ Database connection: {mongodb_results['database_connection']}")
    print(f"   ✓ ObjectId usage: {mongodb_results['objectid_usage']}")
    print(f"   ✓ Collection operations: {mongodb_results['collection_operations']}")
    print(f"   ✓ Duplicate key handling: {mongodb_results['duplicate_key_handling']}")
    print(f"   ✓ Database error handling: {mongodb_results['database_error_handling']}")
    print(f"   ✓ Find operations: {mongodb_results['find_operations']}")
    print(f"   ✓ Update operations: {mongodb_results['update_operations']}")
    
    # Test 4: Validation Integration
    print("\\n4. Testing Validation Integration:")
    validation_results = test_validation_integration()
    
    print(f"   ✓ Validation imports: {validation_results['validation_imports']}")
    print(f"   ✓ Phone validation: {validation_results['phone_validation']}")
    print(f"   ✓ ValidationError usage: {validation_results['validation_error_usage']}")
    print(f"   ✓ Field validation: {validation_results['field_validation']}")
    print(f"   ✓ Error code usage: {validation_results['error_code_usage']}")
    
    # Test 5: Package Structure
    print("\\n5. Testing Models Package:")
    package_results = test_models_package()
    
    print(f"   ✓ Package init exists: {package_results['package_init_exists']}")
    print(f"   ✓ User import: {package_results['user_import']}")
    print(f"   ✓ User export: {package_results['user_export']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['user_class_found'],
        len(structure_results['missing_methods']) == 0,
        structure_results['collection_name_defined'],
        structure_results['roles_defined'],
        security_results['bcrypt_import'],
        security_results['password_hashing'],
        security_results['password_verification'],
        security_results['phone_normalization'],
        mongodb_results['mongodb_imports'],
        mongodb_results['database_connection'],
        mongodb_results['collection_operations'],
        mongodb_results['duplicate_key_handling'],
        validation_results['validation_imports'],
        validation_results['phone_validation'],
        package_results['package_init_exists'],
        package_results['user_import']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ User Data Model implementation PASSED")
        return True
    else:
        print("❌ User Data Model implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)