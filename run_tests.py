#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API.
Usage:
    python run_tests.py           # Run all tests
    python run_tests.py --cov     # Run tests with coverage
    python run_tests.py --help    # Show help
"""

import subprocess
import sys
import os

def run_tests(with_coverage=False, verbose=True):
    """Run the test suite with optional coverage reporting."""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, ".venv", "bin", "python")
    
    # Build the pytest command
    cmd = [venv_python, "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if with_coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    print("=" * 70)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        
        if with_coverage:
            print("\nCoverage report has been generated in htmlcov/index.html")
        
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for the Mergington High School API")
    parser.add_argument("--cov", "--coverage", action="store_true", 
                       help="Run tests with coverage reporting")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Run tests in quiet mode")
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    exit_code = run_tests(with_coverage=args.cov, verbose=verbose)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()