#!/usr/bin/env python3
"""
Test runner script for the Hierarchical Data Explorer project.

This script provides convenient commands for running different types of tests
with appropriate configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print(f"{'='*60}")

    try:
        # Use list form to avoid shell injection - always expect list commands
        if not isinstance(cmd, list):
            raise ValueError("Commands must be provided as lists for security")
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main function to handle test runner arguments."""
    parser = argparse.ArgumentParser(description="Test runner for Hierarchical Data Explorer")
    parser.add_argument("command", choices=[
        "all", "unit", "integration", "api", "projects", "coverage", "lint"
    ], help="Test command to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-k", "--keyword", help="Run tests matching keyword")
    parser.add_argument("--no-cov", action="store_true", help="Don't run with coverage")

    args = parser.parse_args()

    # Base pytest command as list
    base_cmd = ["python", "-m", "pytest"]
    if args.verbose:
        base_cmd.append("-vv")

    # Add keyword filter if specified
    if args.keyword:
        # Validate keyword to allow only safe characters
        import re
        if not re.match(r'^[a-zA-Z0-9_\s-]+$', args.keyword):
            print(f"❌ Invalid keyword '{args.keyword}'. Only alphanumeric characters, underscores, hyphens, and spaces are allowed.")
            sys.exit(1)
        base_cmd.extend(["-k", args.keyword])

    # Add coverage if not disabled
    if not args.no_cov:
        base_cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term-missing"])

    success = True

    if args.command == "all":
        # Run all tests
        cmd = base_cmd + ["tests/"]
        success = run_command(cmd, "All Tests")

    elif args.command == "unit":
        # Run unit tests only
        cmd = base_cmd + ["tests/", "-m", "not integration"]
        success = run_command(cmd, "Unit Tests")

    elif args.command == "integration":
        # Run integration tests only
        cmd = base_cmd + ["tests/", "-m", "integration"]
        success = run_command(cmd, "Integration Tests")

    elif args.command == "api":
        # Run API tests only
        cmd = base_cmd + ["tests/api/"]
        success = run_command(cmd, "API Tests")

    elif args.command == "projects":
        # Run projects tests specifically
        cmd = base_cmd + ["tests/api/test_projects.py"]
        success = run_command(cmd, "Projects API Tests")

    elif args.command == "coverage":
        # Run tests with coverage report
        cmd = ["python", "-m", "pytest", "--cov=src", "--cov-report=html", "--cov-report=term"]
        success = run_command(cmd, "Tests with Coverage")

        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")

    elif args.command == "lint":
        # Run linting (if available)
        print("Running linting checks...")

        # Try black
        try:
            cmd = ["python", "-m", "black", "--check", "src", "tests"]
            run_command(cmd, "Black formatting check")
        except (FileNotFoundError, ModuleNotFoundError, subprocess.CalledProcessError):
            print("⚠️  Black not installed, skipping...")

        # Try flake8
        try:
            cmd = ["python", "-m", "flake8", "src", "tests", "--max-line-length=100"]
            run_command(cmd, "Flake8 linting")
        except (FileNotFoundError, ModuleNotFoundError, subprocess.CalledProcessError):
            print("⚠️  Flake8 not installed, skipping...")

        # Try mypy
        try:
            cmd = ["python", "-m", "mypy", "src", "--ignore-missing-imports"]
            run_command(cmd, "MyPy type checking")
        except (FileNotFoundError, ModuleNotFoundError, subprocess.CalledProcessError):
            print("⚠️  MyPy not installed, skipping...")

    if not success:
        sys.exit(1)
    else:
        print(f"\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    main()