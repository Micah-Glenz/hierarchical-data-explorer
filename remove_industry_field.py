#!/usr/bin/env python3
"""
Database cleanup script to remove the industry field from customer records.

This script will:
1. Create a backup of the current customer data
2. Remove the industry field from all customer records
3. Validate the data integrity after cleanup
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

def create_backup(file_path):
    """Create a timestamped backup of the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup.{timestamp}"

    print(f"Creating backup: {backup_path}")
    shutil.copy2(file_path, backup_path)
    return backup_path

def load_customers(file_path):
    """Load customer data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return None

def validate_customers(customers):
    """Validate customer data structure."""
    if not isinstance(customers, list):
        print("Error: Customers data should be a list")
        return False

    required_fields = ['id', 'name', 'status', 'created_date']
    optional_fields = ['address', 'city', 'state', 'zip', 'sales_rep_name', 'sales_rep_email',
                      'created_at', 'updated_at', 'is_deleted', 'deleted_at']

    errors = []

    for i, customer in enumerate(customers):
        if not isinstance(customer, dict):
            errors.append(f"Customer {i}: Not a dictionary")
            continue

        # Check required fields
        for field in required_fields:
            if field not in customer:
                errors.append(f"Customer {i}: Missing required field '{field}'")

        # Check for unexpected fields (excluding industry which we're removing)
        unexpected_fields = set(customer.keys()) - set(required_fields + optional_fields)
        if unexpected_fields and 'industry' not in unexpected_fields:
            errors.append(f"Customer {i}: Unexpected fields: {unexpected_fields}")

        # Check that industry field is not present
        if 'industry' in customer:
            errors.append(f"Customer {i}: Still contains industry field")

    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True

def remove_industry_field(customers):
    """Remove the industry field from all customer records."""
    cleaned_customers = []
    removed_count = 0

    for customer in customers:
        customer_copy = customer.copy()

        if 'industry' in customer_copy:
            del customer_copy['industry']
            removed_count += 1
            print(f"Removed industry from customer {customer_copy['id']}: {customer_copy['name']}")

        cleaned_customers.append(customer_copy)

    return cleaned_customers, removed_count

def save_customers(customers, file_path):
    """Save customer data to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(customers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def main():
    """Main cleanup function."""
    # File paths
    data_dir = Path("data")
    customers_file = data_dir / "customers.json"

    print("=== Customer Industry Field Cleanup ===")
    print(f"Processing: {customers_file}")

    # Check if file exists
    if not customers_file.exists():
        print(f"Error: {customers_file} does not exist")
        return False

    # Create backup
    backup_path = create_backup(customers_file)

    # Load current data
    customers = load_customers(customers_file)
    if customers is None:
        print("Failed to load customer data")
        return False

    print(f"Loaded {len(customers)} customer records")

    # Count current industry fields
    industry_count = sum(1 for c in customers if 'industry' in c)
    print(f"Found {industry_count} customers with industry field")

    # Remove industry field
    cleaned_customers, removed_count = remove_industry_field(customers)

    if removed_count == 0:
        print("No industry fields to remove")
        print("Cleanup completed successfully")
        return True

    # Validate cleaned data
    print("\nValidating cleaned data...")
    if not validate_customers(cleaned_customers):
        print("Validation failed. Restoring backup...")
        shutil.copy2(backup_path, customers_file)
        print(f"Backup restored from: {backup_path}")
        return False

    # Save cleaned data
    print("\nSaving cleaned data...")
    if save_customers(cleaned_customers, customers_file):
        print(f"Successfully removed industry field from {removed_count} customers")
        print(f"Backup saved as: {backup_path}")
        return True
    else:
        print("Failed to save cleaned data. Restoring backup...")
        shutil.copy2(backup_path, customers_file)
        print(f"Backup restored from: {backup_path}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Cleanup completed successfully!")
    else:
        print("\n❌ Cleanup failed!")
        exit(1)