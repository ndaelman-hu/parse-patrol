#!/usr/bin/env python3
"""
Test runner for NOMAD integration tests.

This script provides an easy way to run the NOMAD integration tests
with proper environment setup and clear output.

Example usage:
    uv run python run_nomad_tests.py [--quick] [--software SOFTWARE]
    
Options:
    --quick: Run only the basic search test (no file downloads)
    --software: Test only a specific software package (Gaussian, ORCA, etc.)
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import pytest
    except ImportError:
        missing_deps.append("pytest")
    
    try:
        from parse_patrol.databases.nomad.utils import nomad_search_entries
    except ImportError:
        missing_deps.append("NOMAD utilities (requests)")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install pytest requests")
        return False
    
    print("✅ All dependencies available")
    return True


def check_parsers():
    """Check which parsers are available."""
    available_parsers = []
    
    try:
        import parse_patrol.parsers.cclib.utils
        available_parsers.append("cclib")
    except ImportError:
        pass
    
    try:
        import parse_patrol.parsers.iodata.utils  
        available_parsers.append("iodata")
    except ImportError:
        pass
    
    try:
        import parse_patrol.parsers.gaussian.utils
        available_parsers.append("gaussian")
    except ImportError:
        pass
    
    print(f"📋 Available parsers: {', '.join(available_parsers) if available_parsers else 'None'}")
    return available_parsers


def run_tests(quick=False, software=None):
    """Run the NOMAD integration tests."""
    
    if not check_dependencies():
        return False
    
    available_parsers = check_parsers()
    if not available_parsers:
        print("⚠️  No parsers available - tests will be limited")
    
    # Build pytest command
    test_file = Path(__file__).parent / "test_nomad_integration.py"
    cmd = ["python", "-m", "pytest", str(test_file), "-v", "-s"]
    
    # Add markers based on options
    if quick:
        cmd.extend(["-m", "'integration and not slow'"])
        print("🚀 Running quick tests only (no file downloads)")
    else:
        print("🐌 Running full integration tests (including downloads)")
    
    if software:
        # Filter to specific software via parametrize
        cmd.extend(["-k", software])
        print(f"🎯 Testing only {software}")
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the tests
    result = os.system(" ".join(cmd))
    
    print("=" * 60)
    if result == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run NOMAD integration tests")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only quick tests (no downloads)")
    parser.add_argument("--software", type=str,
                       help="Test only specific software (Gaussian, ORCA, etc.)")
    
    args = parser.parse_args()
    
    print("🧪 NOMAD Integration Test Runner")
    print("=" * 60)
    
    success = run_tests(quick=args.quick, software=args.software)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()