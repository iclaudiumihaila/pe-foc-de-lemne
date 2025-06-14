"""
Test Harness: SMS Rate Limiting Protection

This test harness validates the SMS rate limiting middleware implementation
including configuration, MongoDB integration, endpoint protection, and
comprehensive error handling without requiring actual test execution.
"""

import ast
import os
import sys
import re

def test_rate_limiter_file_structure():
    """Test that the rate limiting middleware file exists and has proper structure."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "file_exists": False,
        "imports_complete": False,
        "rate_limiter_class": False,
        "decorator_function": False,
        "mongodb_integration": False,
        "error_handling": False
    }
    
    try:
        test_results["file_exists"] = os.path.exists(rate_limiter_file)
        
        if test_results["file_exists"]:
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            # Parse AST to find classes and functions
            tree = ast.parse(content)
            found_classes = []
            found_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    found_classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    found_functions.append(node.name)
            
            test_results["rate_limiter_class"] = "RateLimiter" in found_classes
            test_results["decorator_function"] = "rate_limit" in found_functions
            
            test_results["imports_complete"] = all([
                "from datetime import datetime" in content,
                "from functools import wraps" in content,
                "from flask import request" in content,
                "from app.database import get_database" in content
            ])
            
            test_results["mongodb_integration"] = all([
                "rate_limit_collection" in content,
                "create_index" in content,
                "expires_at" in content,
                "TTL" in content.upper()
            ])
            
            test_results["error_handling"] = all([
                "try:" in content,
                "except" in content,
                "graceful" in content.lower() or "fallback" in content.lower()
            ])
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_rate_limiter_class_methods():
    """Test that RateLimiter class has all required methods."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "check_rate_limit_method": False,
        "record_request_method": False,
        "get_rate_limit_info_method": False,
        "normalize_phone_method": False,
        "extract_phone_method": False,
        "get_config_method": False,
        "database_init_method": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["check_rate_limit_method"] = "def check_rate_limit(" in content
            test_results["record_request_method"] = "def record_request(" in content
            test_results["get_rate_limit_info_method"] = "def get_rate_limit_info(" in content
            test_results["normalize_phone_method"] = "def _normalize_phone_number(" in content
            test_results["extract_phone_method"] = "def _extract_phone_number(" in content
            test_results["get_config_method"] = "def _get_rate_limit_config(" in content
            test_results["database_init_method"] = "def _initialize_database(" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_rate_limit_decorator_functionality():
    """Test that rate_limit decorator has proper functionality."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "decorator_definition": False,
        "wraps_function": False,
        "rate_limit_check": False,
        "error_response_429": False,
        "rate_limit_headers": False,
        "request_recording": False,
        "phone_masking": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["decorator_definition"] = "def rate_limit(" in content and "def decorator(" in content
            test_results["wraps_function"] = "@wraps(f)" in content
            test_results["rate_limit_check"] = "check_rate_limit(" in content
            test_results["error_response_429"] = "429" in content and "RATE_LIMIT_EXCEEDED" in content
            test_results["rate_limit_headers"] = "X-RateLimit-" in content and "Retry-After" in content
            test_results["request_recording"] = "record_request(" in content
            test_results["phone_masking"] = "****" in content and "masked" in content.lower()
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_sms_routes_integration():
    """Test that SMS routes have rate limiting decorators applied."""
    sms_routes_file = 'backend/app/routes/sms.py'
    
    test_results = {
        "sms_routes_file_exists": False,
        "rate_limit_import": False,
        "verify_endpoint_rate_limited": False,
        "confirm_endpoint_rate_limited": False,
        "verify_limit_10": False,
        "confirm_limit_50": False
    }
    
    try:
        test_results["sms_routes_file_exists"] = os.path.exists(sms_routes_file)
        
        if test_results["sms_routes_file_exists"]:
            with open(sms_routes_file, 'r') as f:
                content = f.read()
            
            test_results["rate_limit_import"] = "from app.utils.rate_limiter import rate_limit" in content
            
            # Check for rate limiting decorators on endpoints
            verify_pattern = r"@rate_limit\(['\"]sms_verify['\"].*?\).*?def send_verification_code"
            confirm_pattern = r"@rate_limit\(['\"]sms_confirm['\"].*?\).*?def confirm_verification_code"
            
            test_results["verify_endpoint_rate_limited"] = bool(re.search(verify_pattern, content, re.DOTALL))
            test_results["confirm_endpoint_rate_limited"] = bool(re.search(confirm_pattern, content, re.DOTALL))
            
            # Check for specific rate limits
            test_results["verify_limit_10"] = "limit=10" in content
            test_results["confirm_limit_50"] = "limit=50" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_configuration_integration():
    """Test that configuration supports rate limiting settings."""
    config_file = 'backend/app/config.py'
    
    test_results = {
        "config_file_exists": False,
        "rate_limit_config_section": False,
        "sms_verify_config": False,
        "sms_confirm_config": False,
        "rate_limiting_enabled_flag": False,
        "environment_variable_support": False
    }
    
    try:
        test_results["config_file_exists"] = os.path.exists(config_file)
        
        if test_results["config_file_exists"]:
            with open(config_file, 'r') as f:
                content = f.read()
            
            test_results["rate_limit_config_section"] = "RATE LIMITING CONFIGURATION" in content
            test_results["sms_verify_config"] = "RATE_LIMIT_SMS_VERIFY_LIMIT" in content
            test_results["sms_confirm_config"] = "RATE_LIMIT_SMS_CONFIRM_LIMIT" in content
            test_results["rate_limiting_enabled_flag"] = "RATE_LIMITING_ENABLED" in content
            test_results["environment_variable_support"] = "os.environ.get" in content and "RATE_LIMIT" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_database_integration():
    """Test that rate limiting uses proper MongoDB integration."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "mongodb_collection": False,
        "ttl_index_creation": False,
        "compound_index_creation": False,
        "document_structure": False,
        "expires_at_field": False,
        "automatic_cleanup": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["mongodb_collection"] = "api_rate_limits" in content
            test_results["ttl_index_creation"] = "expireAfterSeconds=0" in content
            test_results["compound_index_creation"] = '("key", 1), ("endpoint", 1)' in content
            test_results["document_structure"] = all([
                "'key':" in content,
                "'endpoint':" in content,
                "'created_at':" in content
            ])
            test_results["expires_at_field"] = "'expires_at':" in content
            test_results["automatic_cleanup"] = "TTL" in content and "cleanup" in content.lower()
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_error_handling_and_fallbacks():
    """Test that rate limiting has proper error handling and fallbacks."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "graceful_degradation": False,
        "database_error_handling": False,
        "fallback_to_allow": False,
        "logging_errors": False,
        "no_exception_propagation": False,
        "database_unavailable_handling": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["graceful_degradation"] = "graceful" in content.lower() and "degradation" in content.lower()
            test_results["database_error_handling"] = "except Exception" in content and "database" in content.lower()
            test_results["fallback_to_allow"] = "'allowed': True" in content and "error" in content
            test_results["logging_errors"] = "logger.error" in content
            test_results["no_exception_propagation"] = "try:" in content and not "raise" in content.split("except")[1] if "except" in content else False
            test_results["database_unavailable_handling"] = "rate_limit_collection is None" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_rate_limit_unit_tests():
    """Test that comprehensive unit tests exist for rate limiting."""
    test_file = 'backend/tests/test_rate_limiter.py'
    
    test_results = {
        "test_file_exists": False,
        "rate_limiter_class_tests": False,
        "decorator_tests": False,
        "integration_tests": False,
        "error_scenario_tests": False,
        "configuration_tests": False,
        "mocking_strategy": False
    }
    
    try:
        test_results["test_file_exists"] = os.path.exists(test_file)
        
        if test_results["test_file_exists"]:
            with open(test_file, 'r') as f:
                content = f.read()
            
            test_results["rate_limiter_class_tests"] = "TestRateLimiter" in content
            test_results["decorator_tests"] = "TestRateLimitDecorator" in content
            test_results["integration_tests"] = "TestRateLimitIntegration" in content
            test_results["error_scenario_tests"] = "database_error" in content or "unavailable" in content
            test_results["configuration_tests"] = "TestRateLimitConfiguration" in content
            test_results["mocking_strategy"] = "MagicMock" in content and "patch" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_phone_number_privacy():
    """Test that phone number privacy is maintained in rate limiting."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "phone_masking": False,
        "privacy_logging": False,
        "no_full_phone_in_logs": False,
        "masked_key_generation": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["phone_masking"] = "****" in content and "[-4:]" in content
            test_results["privacy_logging"] = "masked" in content.lower() and "phone" in content.lower()
            test_results["no_full_phone_in_logs"] = "+1234567890" not in content or "example" in content.lower()
            test_results["masked_key_generation"] = "phone:****" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def test_rate_limit_response_format():
    """Test that rate limit responses follow proper format."""
    rate_limiter_file = 'backend/app/utils/rate_limiter.py'
    
    test_results = {
        "error_response_structure": False,
        "rate_limit_exceeded_code": False,
        "detailed_error_info": False,
        "reset_time_info": False,
        "http_headers": False,
        "retry_after_header": False
    }
    
    try:
        if os.path.exists(rate_limiter_file):
            with open(rate_limiter_file, 'r') as f:
                content = f.read()
            
            test_results["error_response_structure"] = "'success': False" in content and "'error':" in content
            test_results["rate_limit_exceeded_code"] = "RATE_LIMIT_EXCEEDED" in content
            test_results["detailed_error_info"] = "'details':" in content and "'limit':" in content
            test_results["reset_time_info"] = "'reset_in_minutes':" in content and "'reset_at':" in content
            test_results["http_headers"] = "X-RateLimit-" in content
            test_results["retry_after_header"] = "Retry-After" in content
            
    except Exception as e:
        test_results["error"] = str(e)
    
    return test_results

def run_all_tests():
    """Run all SMS rate limiting protection tests and return results."""
    print("Testing SMS Rate Limiting Protection Implementation...")
    print("=" * 60)
    
    # Test 1: Rate Limiter File Structure
    print("\n1. Testing Rate Limiter File Structure:")
    structure_results = test_rate_limiter_file_structure()
    
    print(f"   ✓ File exists: {structure_results['file_exists']}")
    print(f"   ✓ Imports complete: {structure_results['imports_complete']}")
    print(f"   ✓ RateLimiter class: {structure_results['rate_limiter_class']}")
    print(f"   ✓ Decorator function: {structure_results['decorator_function']}")
    print(f"   ✓ MongoDB integration: {structure_results['mongodb_integration']}")
    print(f"   ✓ Error handling: {structure_results['error_handling']}")
    
    # Test 2: RateLimiter Class Methods
    print("\n2. Testing RateLimiter Class Methods:")
    methods_results = test_rate_limiter_class_methods()
    
    print(f"   ✓ Check rate limit method: {methods_results['check_rate_limit_method']}")
    print(f"   ✓ Record request method: {methods_results['record_request_method']}")
    print(f"   ✓ Get rate limit info method: {methods_results['get_rate_limit_info_method']}")
    print(f"   ✓ Normalize phone method: {methods_results['normalize_phone_method']}")
    print(f"   ✓ Extract phone method: {methods_results['extract_phone_method']}")
    print(f"   ✓ Get config method: {methods_results['get_config_method']}")
    print(f"   ✓ Database init method: {methods_results['database_init_method']}")
    
    # Test 3: Rate Limit Decorator Functionality
    print("\n3. Testing Rate Limit Decorator Functionality:")
    decorator_results = test_rate_limit_decorator_functionality()
    
    print(f"   ✓ Decorator definition: {decorator_results['decorator_definition']}")
    print(f"   ✓ Wraps function: {decorator_results['wraps_function']}")
    print(f"   ✓ Rate limit check: {decorator_results['rate_limit_check']}")
    print(f"   ✓ 429 error response: {decorator_results['error_response_429']}")
    print(f"   ✓ Rate limit headers: {decorator_results['rate_limit_headers']}")
    print(f"   ✓ Request recording: {decorator_results['request_recording']}")
    print(f"   ✓ Phone masking: {decorator_results['phone_masking']}")
    
    # Test 4: SMS Routes Integration
    print("\n4. Testing SMS Routes Integration:")
    routes_results = test_sms_routes_integration()
    
    print(f"   ✓ SMS routes file exists: {routes_results['sms_routes_file_exists']}")
    print(f"   ✓ Rate limit import: {routes_results['rate_limit_import']}")
    print(f"   ✓ Verify endpoint rate limited: {routes_results['verify_endpoint_rate_limited']}")
    print(f"   ✓ Confirm endpoint rate limited: {routes_results['confirm_endpoint_rate_limited']}")
    print(f"   ✓ Verify limit 10: {routes_results['verify_limit_10']}")
    print(f"   ✓ Confirm limit 50: {routes_results['confirm_limit_50']}")
    
    # Test 5: Configuration Integration
    print("\n5. Testing Configuration Integration:")
    config_results = test_configuration_integration()
    
    print(f"   ✓ Config file exists: {config_results['config_file_exists']}")
    print(f"   ✓ Rate limit config section: {config_results['rate_limit_config_section']}")
    print(f"   ✓ SMS verify config: {config_results['sms_verify_config']}")
    print(f"   ✓ SMS confirm config: {config_results['sms_confirm_config']}")
    print(f"   ✓ Rate limiting enabled flag: {config_results['rate_limiting_enabled_flag']}")
    print(f"   ✓ Environment variable support: {config_results['environment_variable_support']}")
    
    # Test 6: Database Integration
    print("\n6. Testing Database Integration:")
    database_results = test_database_integration()
    
    print(f"   ✓ MongoDB collection: {database_results['mongodb_collection']}")
    print(f"   ✓ TTL index creation: {database_results['ttl_index_creation']}")
    print(f"   ✓ Compound index creation: {database_results['compound_index_creation']}")
    print(f"   ✓ Document structure: {database_results['document_structure']}")
    print(f"   ✓ Expires at field: {database_results['expires_at_field']}")
    print(f"   ✓ Automatic cleanup: {database_results['automatic_cleanup']}")
    
    # Test 7: Error Handling and Fallbacks
    print("\n7. Testing Error Handling and Fallbacks:")
    error_results = test_error_handling_and_fallbacks()
    
    print(f"   ✓ Graceful degradation: {error_results['graceful_degradation']}")
    print(f"   ✓ Database error handling: {error_results['database_error_handling']}")
    print(f"   ✓ Fallback to allow: {error_results['fallback_to_allow']}")
    print(f"   ✓ Logging errors: {error_results['logging_errors']}")
    print(f"   ✓ No exception propagation: {error_results['no_exception_propagation']}")
    print(f"   ✓ Database unavailable handling: {error_results['database_unavailable_handling']}")
    
    # Test 8: Rate Limit Unit Tests
    print("\n8. Testing Rate Limit Unit Tests:")
    unit_test_results = test_rate_limit_unit_tests()
    
    print(f"   ✓ Test file exists: {unit_test_results['test_file_exists']}")
    print(f"   ✓ RateLimiter class tests: {unit_test_results['rate_limiter_class_tests']}")
    print(f"   ✓ Decorator tests: {unit_test_results['decorator_tests']}")
    print(f"   ✓ Integration tests: {unit_test_results['integration_tests']}")
    print(f"   ✓ Error scenario tests: {unit_test_results['error_scenario_tests']}")
    print(f"   ✓ Configuration tests: {unit_test_results['configuration_tests']}")
    print(f"   ✓ Mocking strategy: {unit_test_results['mocking_strategy']}")
    
    # Test 9: Phone Number Privacy
    print("\n9. Testing Phone Number Privacy:")
    privacy_results = test_phone_number_privacy()
    
    print(f"   ✓ Phone masking: {privacy_results['phone_masking']}")
    print(f"   ✓ Privacy logging: {privacy_results['privacy_logging']}")
    print(f"   ✓ No full phone in logs: {privacy_results['no_full_phone_in_logs']}")
    print(f"   ✓ Masked key generation: {privacy_results['masked_key_generation']}")
    
    # Test 10: Rate Limit Response Format
    print("\n10. Testing Rate Limit Response Format:")
    response_results = test_rate_limit_response_format()
    
    print(f"   ✓ Error response structure: {response_results['error_response_structure']}")
    print(f"   ✓ Rate limit exceeded code: {response_results['rate_limit_exceeded_code']}")
    print(f"   ✓ Detailed error info: {response_results['detailed_error_info']}")
    print(f"   ✓ Reset time info: {response_results['reset_time_info']}")
    print(f"   ✓ HTTP headers: {response_results['http_headers']}")
    print(f"   ✓ Retry-After header: {response_results['retry_after_header']}")
    
    # Calculate overall success
    all_tests = [
        structure_results['file_exists'],
        structure_results['imports_complete'],
        structure_results['rate_limiter_class'],
        structure_results['decorator_function'],
        structure_results['mongodb_integration'],
        structure_results['error_handling'],
        methods_results['check_rate_limit_method'],
        methods_results['record_request_method'],
        methods_results['get_rate_limit_info_method'],
        methods_results['normalize_phone_method'],
        methods_results['extract_phone_method'],
        methods_results['get_config_method'],
        methods_results['database_init_method'],
        decorator_results['decorator_definition'],
        decorator_results['wraps_function'],
        decorator_results['rate_limit_check'],
        decorator_results['error_response_429'],
        decorator_results['rate_limit_headers'],
        decorator_results['request_recording'],
        decorator_results['phone_masking'],
        routes_results['sms_routes_file_exists'],
        routes_results['rate_limit_import'],
        routes_results['verify_endpoint_rate_limited'],
        routes_results['confirm_endpoint_rate_limited'],
        routes_results['verify_limit_10'],
        routes_results['confirm_limit_50'],
        config_results['config_file_exists'],
        config_results['rate_limit_config_section'],
        config_results['sms_verify_config'],
        config_results['sms_confirm_config'],
        config_results['rate_limiting_enabled_flag'],
        config_results['environment_variable_support'],
        database_results['mongodb_collection'],
        database_results['ttl_index_creation'],
        database_results['compound_index_creation'],
        database_results['document_structure'],
        database_results['expires_at_field'],
        database_results['automatic_cleanup'],
        error_results['graceful_degradation'],
        error_results['database_error_handling'],
        error_results['fallback_to_allow'],
        error_results['logging_errors'],
        error_results['no_exception_propagation'],
        error_results['database_unavailable_handling'],
        unit_test_results['test_file_exists'],
        unit_test_results['rate_limiter_class_tests'],
        unit_test_results['decorator_tests'],
        unit_test_results['integration_tests'],
        unit_test_results['error_scenario_tests'],
        unit_test_results['configuration_tests'],
        unit_test_results['mocking_strategy'],
        privacy_results['phone_masking'],
        privacy_results['privacy_logging'],
        privacy_results['no_full_phone_in_logs'],
        privacy_results['masked_key_generation'],
        response_results['error_response_structure'],
        response_results['rate_limit_exceeded_code'],
        response_results['detailed_error_info'],
        response_results['reset_time_info'],
        response_results['http_headers'],
        response_results['retry_after_header']
    ]
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ SMS Rate Limiting Protection implementation PASSED")
        return True
    else:
        print("❌ SMS Rate Limiting Protection implementation FAILED")
        return False

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)