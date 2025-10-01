#!/usr/bin/env python3
"""
Test runner script for the Task Manager API
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite"""
    print("🧪 Running Task Manager API Tests...")
    print("=" * 50)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run pytest with coverage
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test_app.py', 
            '--verbose',
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing'
        ], check=True)
        
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest pytest-cov")
        sys.exit(1)

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"🧪 Running test: {test_name}")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pytest', 
            f'test_app.py::{test_name}',
            '--verbose'
        ], check=True)
        print(f"\n✅ Test {test_name} passed!")
    except subprocess.CalledProcessError:
        print(f"\n❌ Test {test_name} failed!")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_specific_test(sys.argv[1])
    else:
        run_tests()

