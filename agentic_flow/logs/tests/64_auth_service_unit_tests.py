"""
Test harness for admin authentication service unit tests.

This script runs the comprehensive unit test suite for the AuthService class
and validates all authentication functionality including Romanian localization.
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def run_auth_service_tests():
    """
    Run the auth service unit tests and capture results.
    
    Returns:
        dict: Test execution results with pass/fail counts and details
    """
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')
        os.chdir(backend_dir)
        
        # Run pytest with detailed output
        result = subprocess.run([
            'python', '-m', 'pytest',
            'tests/test_auth_service.py',
            '-v',  # Verbose output
            '--tb=short',  # Short traceback format
            '--json-report',  # Generate JSON report
            '--json-report-file=test_results.json'
        ], capture_output=True, text=True)
        
        # Parse test results
        test_results = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
        
        # Try to load JSON report if available
        try:
            with open('test_results.json', 'r') as f:
                json_report = json.load(f)
                test_results['detailed_results'] = json_report
        except FileNotFoundError:
            test_results['detailed_results'] = None
        
        return test_results
        
    except Exception as e:
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'success': False,
            'error': str(e),
            'exit_code': -1
        }

if __name__ == '__main__':
    results = run_auth_service_tests()
    
    print("=== AUTH SERVICE UNIT TESTS RESULTS ===")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Success: {results['success']}")
    print(f"Exit Code: {results['exit_code']}")
    
    if results.get('stdout'):
        print("\n=== STDOUT ===")
        print(results['stdout'])
    
    if results.get('stderr'):
        print("\n=== STDERR ===")
        print(results['stderr'])
    
    if results.get('error'):
        print(f"\n=== ERROR ===")
        print(results['error'])
    
    # Exit with same code as tests
    sys.exit(results['exit_code'])