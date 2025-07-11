#!/usr/bin/env python3
"""
Test script to verify ReconAI installation and dependencies
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test if required Python packages are installed"""
    print("\nTesting Python dependencies...")
    
    required_packages = [
        'openai',
        'requests', 
        'rich',
        'dotenv',
        'pandas',
        'beautifulsoup4'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - Missing")
            all_good = False
    
    return all_good

def test_external_tools():
    """Test if external reconnaissance tools are available"""
    print("\nTesting external tools...")
    
    tools = {
        'bbot': ['bbot', '--version'],
        'nmap': ['nmap', '--version']
    }
    
    results = {}
    for tool_name, command in tools.items():
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✓ {tool_name} - {version_line}")
                results[tool_name] = True
            else:
                print(f"✗ {tool_name} - Command failed")
                results[tool_name] = False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"✗ {tool_name} - Not found in PATH")
            results[tool_name] = False
    
    return results

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file found")
        
        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("✓ OPENAI_API_KEY configured")
        else:
            print("⚠ OPENAI_API_KEY not set (AI analysis will be disabled)")
    else:
        print("⚠ .env file not found (copy .env.example to .env and configure)")
    
    # Check output directories
    output_dir = Path('output')
    if output_dir.exists():
        print("✓ Output directory exists")
    else:
        print("⚠ Output directory will be created automatically")

def test_cli_structure():
    """Test CLI module structure"""
    print("\nTesting CLI module structure...")
    
    required_files = [
        'cli/__init__.py',
        'cli/core/orchestrator.py',
        'cli/tools/bbot_wrapper.py',
        'cli/ai/analyzer.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - Missing")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("=== ReconAI Installation Test ===\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("External Tools", test_external_tools),
        ("Environment", test_environment),
        ("CLI Structure", test_cli_structure)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} - Error: {e}")
            results[test_name] = False
    
    print("\n=== Test Summary ===")
    all_passed = True
    for test_name, passed in results.items():
        if isinstance(passed, dict):
            # For external tools, check if at least one tool is available
            passed = any(passed.values()) if passed else False
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
        
        if not passed:
            all_passed = False
    
    print(f"\nOverall Status: {'✓ READY' if all_passed else '⚠ ISSUES FOUND'}")
    
    if not all_passed:
        print("\nTo fix issues:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Install Bbot: pip install bbot")
        print("3. Copy .env.example to .env and configure API keys")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())