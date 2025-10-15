#!/usr/bin/env python3
"""
Test structure validation script.

This script validates that the test suite structure is correct
and all necessary files are present.
"""

import os
import sys
from pathlib import Path


def validate_test_structure():
    """Validate the test directory structure."""
    base_dir = Path(".")
    tests_dir = base_dir / "tests"

    print("🔍 Validating test structure...")

    # Check main directories
    required_dirs = [
        "tests",
        "tests/api",
        "tests/frontend",
        "tests/integration"
    ]

    for dir_path in required_dirs:
        if (base_dir / dir_path).exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            return False

    # Check required files
    required_files = [
        "tests/__init__.py",
        "tests/api/__init__.py",
        "tests/api/conftest.py",
        "tests/api/test_projects.py",
        "tests/README.md",
        "pytest.ini",
        "run_tests.py",
        "requirements-test.txt"
    ]

    for file_path in required_files:
        if (base_dir / file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False

    # Validate test file content
    projects_test = base_dir / "tests/api/test_projects.py"
    if projects_test.exists():
        with open(projects_test, 'r') as f:
            content = f.read()

        # Check for key test components
        checks = [
            ("class TestProjectsAPI", "Main test class"),
            ("def test_get_projects_success", "GET test"),
            ("def test_create_project_success", "POST test"),
            ("def test_update_project_success", "PUT test"),
            ("def test_delete_project_success", "DELETE test"),
            ("class TestProjectsAPIEdgeCases", "Edge cases"),
            ("class TestProjectsAPIIntegration", "Integration tests")
        ]

        for check, description in checks:
            if check in content:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} missing")
                return False

    print("\n📊 Test Statistics:")

    # Count test functions
    if projects_test.exists():
        with open(projects_test, 'r') as f:
            content = f.read()

        test_functions = len([line for line in content.split('\n') if line.strip().startswith('def test_')])
        test_classes = len([line for line in content.split('\n') if line.strip().startswith('class Test')])

        print(f"   - Test classes: {test_classes}")
        print(f"   - Test functions: {test_functions}")

    # Check conftest content
    conftest_file = base_dir / "tests/api/conftest.py"
    if conftest_file.exists():
        with open(conftest_file, 'r') as f:
            content = f.read()

        fixtures = len([line for line in content.split('\n') if line.strip().startswith('@pytest.fixture')])
        print(f"   - Test fixtures: {fixtures}")

    return True


def validate_pytest_config():
    """Validate pytest configuration."""
    print("\n🔧 Validating pytest configuration...")

    pytest_ini = Path("pytest.ini")
    if pytest_ini.exists():
        with open(pytest_ini, 'r') as f:
            content = f.read()

        required_sections = ["[tool:pytest]", "[coverage:run]", "[coverage:report]"]
        for section in required_sections:
            if section in content:
                print(f"✅ {section} configured")
            else:
                print(f"❌ {section} missing")
                return False
    else:
        print("❌ pytest.ini missing")
        return False

    return True


def validate_test_runner():
    """Validate test runner script."""
    print("\n🚀 Validating test runner...")

    runner_script = Path("run_tests.py")
    if runner_script.exists():
        with open(runner_script, 'r') as f:
            content = f.read()

        commands = ["all", "unit", "integration", "api", "projects", "coverage"]
        for cmd in commands:
            if f'"{cmd}"' in content:
                print(f"✅ {cmd} command available")
            else:
                print(f"❌ {cmd} command missing")
                return False

        # Check if script is executable
        if os.access(runner_script, os.X_OK):
            print("✅ Test runner is executable")
        else:
            print("⚠️  Test runner not executable (run: chmod +x run_tests.py)")
    else:
        print("❌ run_tests.py missing")
        return False

    return True


def main():
    """Main validation function."""
    print("🧪 Hierarchical Data Explorer Test Suite Validation")
    print("=" * 60)

    all_valid = True

    # Validate structure
    if not validate_test_structure():
        all_valid = False

    # Validate pytest config
    if not validate_pytest_config():
        all_valid = False

    # Validate test runner
    if not validate_test_runner():
        all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("🎉 All validations passed! Test suite is ready to use.")
        print("\n📋 Next steps:")
        print("1. Install test dependencies: pip install -r requirements-test.txt")
        print("2. Run tests: python run_tests.py projects")
        print("3. View coverage: python run_tests.py coverage")
        print("4. Read documentation: tests/README.md")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())