"""
Test Harness: SMS Verification Service with Twilio

This test harness validates the SMS verification service implementation including
Twilio integration, rate limiting, and mock mode without requiring actual SMS sending.
"""

import ast
import os
import sys
import re

def test_sms_service_structure():
    """Test SMS service file structure and class definition."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "file_exists": False,
        "sms_service_class_found": False,
        "required_methods": [],
        "missing_methods": [],
        "singleton_function": False,
        "constants_defined": False,
        "rate_limit_constants": False
    }
    
    required_methods = [
        '__init__', 'send_verification_code', 'generate_verification_code',
        'validate_verification_code', 'is_rate_limited', 'get_rate_limit_info'
    ]
    
    try:
        if os.path.exists(sms_file):
            test_results["file_exists"] = True
            
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find SMSService class and methods
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == 'SMSService':
                    test_results["sms_service_class_found"] = True
                    
                    # Find methods in SMSService class
                    found_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            found_methods.append(item.name)
                    
                    test_results["required_methods"] = found_methods
                    test_results["missing_methods"] = [
                        method for method in required_methods 
                        if method not in found_methods
                    ]
                elif isinstance(node, ast.FunctionDef) and node.name == 'get_sms_service':
                    test_results["singleton_function"] = True
            
            # Check for important constants
            test_results["constants_defined"] = "VERIFICATION_CODE_LENGTH" in content and "VERIFICATION_CODE_EXPIRY_MINUTES" in content
            test_results["rate_limit_constants"] = "DEFAULT_RATE_LIMIT_PER_PHONE" in content and "DEFAULT_RATE_LIMIT_WINDOW" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_twilio_integration():
    """Test Twilio integration and API features."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "twilio_import": False,
        "twilio_client_init": False,
        "send_twilio_sms": False,
        "twilio_error_handling": False,
        "configuration_integration": False,
        "phone_number_validation": False
    }
    
    try:
        if os.path.exists(sms_file):
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Check Twilio integration features
            test_results["twilio_import"] = "from twilio.rest import Client" in content
            test_results["twilio_client_init"] = "_twilio_client" in content
            test_results["send_twilio_sms"] = "_send_twilio_sms" in content
            test_results["twilio_error_handling"] = "SMSError" in content and "twilio" in content.lower()
            test_results["configuration_integration"] = "TWILIO_ACCOUNT_SID" in content and "current_app.config" in content
            test_results["phone_number_validation"] = "validate_phone_number" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_rate_limiting_features():
    """Test rate limiting and abuse prevention features."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "rate_limit_checking": False,
        "rate_limit_tracking": False,
        "rate_limit_info": False,
        "rate_limit_storage": False,
        "rate_limit_cleanup": False,
        "rate_limit_error": False
    }
    
    try:
        if os.path.exists(sms_file):
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Check rate limiting features
            test_results["rate_limit_checking"] = "is_rate_limited" in content
            test_results["rate_limit_tracking"] = "_track_sms_attempt" in content
            test_results["rate_limit_info"] = "get_rate_limit_info" in content
            test_results["rate_limit_storage"] = "_rate_limit_storage" in content
            test_results["rate_limit_cleanup"] = "_cleanup_rate_limit_storage" in content
            test_results["rate_limit_error"] = "Rate limit exceeded" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_verification_code_management():
    """Test verification code generation and validation."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "code_generation": False,
        "code_validation": False,
        "code_expiry_check": False,
        "code_format_validation": False,
        "message_formatting": False,
        "logging_integration": False
    }
    
    try:
        if os.path.exists(sms_file):
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Check verification code features
            test_results["code_generation"] = "generate_verification_code" in content and "random.randint" in content
            test_results["code_validation"] = "validate_verification_code" in content
            test_results["code_expiry_check"] = "code_expires" in content and "datetime.utcnow()" in content
            test_results["code_format_validation"] = "re.match(r'^\\d{6}$'" in content
            test_results["message_formatting"] = "_format_message" in content and "VERIFICATION_MESSAGE_TEMPLATE" in content
            test_results["logging_integration"] = "_log_verification_attempt" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_mock_mode_and_testing():
    """Test mock mode and testing support features."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "mock_mode_support": False,
        "send_mock_sms": False,
        "mock_configuration": False,
        "mock_responses": False,
        "test_logging": False,
        "fallback_mechanism": False
    }
    
    try:
        if os.path.exists(sms_file):
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Check mock mode features
            test_results["mock_mode_support"] = "_mock_mode" in content
            test_results["send_mock_sms"] = "_send_mock_sms" in content
            test_results["mock_configuration"] = "SMS_MOCK_MODE" in content
            test_results["mock_responses"] = "mock_sid" in content and "uuid" in content
            test_results["test_logging"] = "MOCK SMS" in content
            test_results["fallback_mechanism"] = "mock mode" in content.lower() and "fallback" in content.lower()
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_phone_number_handling():
    """Test phone number validation and normalization."""
    sms_file = 'backend/app/services/sms_service.py'
    
    test_results = {
        "phone_normalization": False,
        "e164_validation": False,
        "phone_privacy": False,
        "us_number_support": False,
        "phone_format_error": False
    }
    
    try:
        if os.path.exists(sms_file):
            with open(sms_file, 'r') as f:
                content = f.read()
            
            # Check phone number handling
            test_results["phone_normalization"] = "_normalize_phone_number" in content
            test_results["e164_validation"] = "E.164" in content
            test_results["phone_privacy"] = "[-4:]" in content  # Last 4 digits logging
            test_results["us_number_support"] = "+1" in content and "len(cleaned) == 10" in content
            test_results["phone_format_error"] = "Invalid phone number format" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_services_package():
    """Test services package structure and exports."""
    services_init_file = 'backend/app/services/__init__.py'
    
    test_results = {
        "package_init_exists": False,
        "sms_service_import": False,
        "sms_service_export": False
    }
    
    try:
        if os.path.exists(services_init_file):
            test_results["package_init_exists"] = True
            
            with open(services_init_file, 'r') as f:
                content = f.read()
            
            test_results["sms_service_import"] = "from .sms_service import SMSService" in content
            test_results["sms_service_export"] = "__all__ = ['SMSService']" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all SMS service tests and return results."""
    print("Testing SMS Verification Service Implementation...")
    print("=" * 50)
    
    # Test 1: Service Structure
    print("\\n1. Testing SMS Service Structure:")
    structure_results = test_sms_service_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ SMSService class found: {structure_results['sms_service_class_found']}")
    print(f"   ✓ Required methods found: {len(structure_results['required_methods'])}/6")
    print(f"   ✓ Missing methods: {structure_results['missing_methods']}")
    print(f"   ✓ Singleton function: {structure_results['singleton_function']}")
    print(f"   ✓ Constants defined: {structure_results['constants_defined']}")
    print(f"   ✓ Rate limit constants: {structure_results['rate_limit_constants']}")
    
    # Test 2: Twilio Integration
    print("\\n2. Testing Twilio Integration:")
    twilio_results = test_twilio_integration()
    
    print(f"   ✓ Twilio import: {twilio_results['twilio_import']}")
    print(f"   ✓ Twilio client init: {twilio_results['twilio_client_init']}")
    print(f"   ✓ Send Twilio SMS: {twilio_results['send_twilio_sms']}")
    print(f"   ✓ Twilio error handling: {twilio_results['twilio_error_handling']}")
    print(f"   ✓ Configuration integration: {twilio_results['configuration_integration']}")
    print(f"   ✓ Phone number validation: {twilio_results['phone_number_validation']}")
    
    # Test 3: Rate Limiting Features
    print("\\n3. Testing Rate Limiting Features:")
    rate_limit_results = test_rate_limiting_features()
    
    print(f"   ✓ Rate limit checking: {rate_limit_results['rate_limit_checking']}")
    print(f"   ✓ Rate limit tracking: {rate_limit_results['rate_limit_tracking']}")
    print(f"   ✓ Rate limit info: {rate_limit_results['rate_limit_info']}")
    print(f"   ✓ Rate limit storage: {rate_limit_results['rate_limit_storage']}")
    print(f"   ✓ Rate limit cleanup: {rate_limit_results['rate_limit_cleanup']}")
    print(f"   ✓ Rate limit error: {rate_limit_results['rate_limit_error']}")
    
    # Test 4: Verification Code Management
    print("\\n4. Testing Verification Code Management:")
    code_results = test_verification_code_management()
    
    print(f"   ✓ Code generation: {code_results['code_generation']}")
    print(f"   ✓ Code validation: {code_results['code_validation']}")
    print(f"   ✓ Code expiry check: {code_results['code_expiry_check']}")
    print(f"   ✓ Code format validation: {code_results['code_format_validation']}")
    print(f"   ✓ Message formatting: {code_results['message_formatting']}")
    print(f"   ✓ Logging integration: {code_results['logging_integration']}")
    
    # Test 5: Mock Mode and Testing
    print("\\n5. Testing Mock Mode and Testing:")
    mock_results = test_mock_mode_and_testing()
    
    print(f"   ✓ Mock mode support: {mock_results['mock_mode_support']}")
    print(f"   ✓ Send mock SMS: {mock_results['send_mock_sms']}")
    print(f"   ✓ Mock configuration: {mock_results['mock_configuration']}")
    print(f"   ✓ Mock responses: {mock_results['mock_responses']}")
    print(f"   ✓ Test logging: {mock_results['test_logging']}")
    
    # Test 6: Phone Number Handling
    print("\\n6. Testing Phone Number Handling:")
    phone_results = test_phone_number_handling()
    
    print(f"   ✓ Phone normalization: {phone_results['phone_normalization']}")
    print(f"   ✓ E164 validation: {phone_results['e164_validation']}")
    print(f"   ✓ Phone privacy: {phone_results['phone_privacy']}")
    print(f"   ✓ US number support: {phone_results['us_number_support']}")
    print(f"   ✓ Phone format error: {phone_results['phone_format_error']}")
    
    # Test 7: Services Package
    print("\\n7. Testing Services Package:")
    package_results = test_services_package()
    
    print(f"   ✓ Package init exists: {package_results['package_init_exists']}")
    print(f"   ✓ SMS service import: {package_results['sms_service_import']}")
    print(f"   ✓ SMS service export: {package_results['sms_service_export']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['sms_service_class_found'],
        len(structure_results['missing_methods']) == 0,
        structure_results['singleton_function'],
        structure_results['constants_defined'],
        twilio_results['twilio_client_init'],
        twilio_results['send_twilio_sms'],
        twilio_results['configuration_integration'],
        twilio_results['phone_number_validation'],
        rate_limit_results['rate_limit_checking'],
        rate_limit_results['rate_limit_tracking'],
        rate_limit_results['rate_limit_info'],
        code_results['code_generation'],
        code_results['code_validation'],
        code_results['code_expiry_check'],
        code_results['message_formatting'],
        mock_results['mock_mode_support'],
        mock_results['send_mock_sms'],
        phone_results['phone_normalization'],
        phone_results['e164_validation'],
        phone_results['phone_privacy'],
        package_results['package_init_exists'],
        package_results['sms_service_import']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\\n{'='*50}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ SMS Verification Service implementation PASSED")
        return True
    else:
        print("❌ SMS Verification Service implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)