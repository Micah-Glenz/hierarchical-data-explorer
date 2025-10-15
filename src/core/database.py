"""
Database operations for the Hierarchical Data Explorer.

This module handles all data access operations including reading,
writing, and managing JSON files that store the application data.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from .config import get_settings
from .exceptions import DatabaseOperationError, DataNotFoundError

# Set up logger
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for JSON file operations.

    This class provides a clean interface for all database operations,
    abstracting away the details of JSON file handling and providing
    error handling and validation.
    """

    def __init__(self) -> None:
        """Initialize the database manager."""
        self.settings = get_settings()
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        if not self.settings.ensure_data_directory():
            raise DatabaseOperationError(
                "Failed to create data directory",
                "initialize",
                str(self.settings.DATA_DIR)
            )

    def _get_file_path(self, filename: str) -> Path:
        """
        Get the full path to a data file.

        Args:
            filename: Name of the data file

        Returns:
            Full path to the data file
        """
        return self.settings.get_data_path(filename)

    def _validate_file_exists(self, filepath: Path) -> None:
        """
        Validate that a file exists.

        Args:
            filepath: Path to validate

        Raises:
            DatabaseOperationError: If file doesn't exist
        """
        if not filepath.exists():
            raise DatabaseOperationError(
                f"Data file not found: {filepath}",
                "read",
                filepath.name
            )

    def load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            List of dictionaries representing the data

        Raises:
            DatabaseOperationError: If file cannot be read or parsed
        """
        filepath = self._get_file_path(filename)

        try:
            self._validate_file_exists(filepath)

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise DatabaseOperationError(
                    f"Invalid data format in {filename}: expected list",
                    "read",
                    filename
                )

            return data

        except json.JSONDecodeError as e:
            raise DatabaseOperationError(
                f"Invalid JSON in {filename}: {str(e)}",
                "read",
                filename,
                e
            )
        except Exception as e:
            if isinstance(e, DatabaseOperationError):
                raise
            raise DatabaseOperationError(
                f"Failed to load {filename}: {str(e)}",
                "read",
                filename,
                e
            )

    def save_json_data(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """
        Save data to a JSON file.

        Args:
            filename: Name of the JSON file to save
            data: List of dictionaries to save

        Returns:
            True if successful, False otherwise

        Raises:
            DatabaseOperationError: If file cannot be written
        """
        filepath = self._get_file_path(filename)

        try:
            if not isinstance(data, list):
                raise ValueError("Data must be a list")

            # Create backup before saving
            self._create_backup(filepath)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            raise DatabaseOperationError(
                f"Failed to save {filename}: {str(e)}",
                "write",
                filename,
                e
            )

    def _create_backup(self, filepath: Path) -> None:
        """
        Create a backup of the file before modification.

        Args:
            filepath: Path to the file to backup

        Raises:
            DatabaseOperationError: If backup creation fails and backup is required
        """
        if filepath.exists():
            backup_path = filepath.with_suffix(
                f"{filepath.suffix}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            try:
                import shutil
                shutil.copy2(filepath, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except (OSError, IOError, PermissionError) as e:
                # Log the error with details but don't fail the main operation
                logger.warning(f"Failed to create backup of {filepath}: {str(e)}")
                # Optionally re-raise if backups are critical for your use case
                # raise DatabaseOperationError(
                #     f"Failed to create backup of {filepath}: {str(e)}",
                #     "backup",
                #     filepath.name,
                #     e
                # )

    def get_next_id(self, filename: str) -> int:
        """
        Get the next available ID for a data file.

        Args:
            filename: Name of the data file

        Returns:
            Next available ID (1-based)
        """
        try:
            data = self.load_json_data(filename)
            if not data:
                return 1
            max_id = max(item.get("id", 0) for item in data)
            return max_id + 1
        except DatabaseOperationError:
            # If file doesn't exist or is empty, start with ID 1
            return 1

    def find_by_id(self, filename: str, item_id: int, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """
        Find an item by ID in a data file.

        Args:
            filename: Name of the data file
            item_id: ID of the item to find
            include_deleted: Whether to include soft-deleted items

        Returns:
            Dictionary representing the item, or None if not found
        """
        try:
            data = self.load_json_data(filename)
            for item in data:
                if item.get("id") == item_id:
                    if include_deleted or not item.get("is_deleted", False):
                        return item.copy()
            return None
        except DatabaseOperationError:
            return None

    def find_all(self, filename: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        Find all items in a data file.

        Args:
            filename: Name of the data file
            include_deleted: Whether to include soft-deleted items

        Returns:
            List of dictionaries representing all items
        """
        try:
            data = self.load_json_data(filename)
            if include_deleted:
                return data.copy()
            return [item.copy() for item in data if not item.get("is_deleted", False)]
        except DatabaseOperationError:
            return []

    def filter_by_field(self, filename: str, field: str, value: Any, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        Filter items by a specific field value.

        Args:
            filename: Name of the data file
            field: Field name to filter by
            value: Value to filter for
            include_deleted: Whether to include soft-deleted items

        Returns:
            List of dictionaries representing filtered items
        """
        try:
            data = self.load_json_data(filename)
            filtered_items = []
            for item in data:
                if item.get(field) == value:
                    if include_deleted or not item.get("is_deleted", False):
                        filtered_items.append(item.copy())
            return filtered_items
        except DatabaseOperationError:
            return []

    def soft_delete_by_id(self, filename: str, item_id: int) -> bool:
        """
        Soft delete an item by ID.

        Args:
            filename: Name of the data file
            item_id: ID of the item to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.load_json_data(filename)
            for item in data:
                if item.get("id") == item_id and not item.get("is_deleted", False):
                    item["is_deleted"] = True
                    item["deleted_at"] = datetime.now().isoformat()
                    return self.save_json_data(filename, data)
            return False
        except DatabaseOperationError:
            return False

    def update_by_id(self, filename: str, item_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update an item by ID.

        Args:
            filename: Name of the data file
            item_id: ID of the item to update
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.load_json_data(filename)
            for i, item in enumerate(data):
                if item.get("id") == item_id and not item.get("is_deleted", False):
                    # Update only provided fields
                    for key, value in updates.items():
                        if value is not None:
                            data[i][key] = value
                    return self.save_json_data(filename, data)
            return False
        except DatabaseOperationError:
            return False

    def append_item(self, filename: str, item: Dict[str, Any]) -> bool:
        """
        Append a new item to a data file.

        Args:
            filename: Name of the data file
            item: Dictionary representing the new item

        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.load_json_data(filename)
            data.append(item)
            return self.save_json_data(filename, data)
        except DatabaseOperationError:
            return False

    def get_file_stats(self, filename: str) -> Dict[str, Any]:
        """
        Get statistics about a data file.

        Args:
            filename: Name of the data file

        Returns:
            Dictionary containing file statistics
        """
        try:
            filepath = self._get_file_path(filename)
            stat = filepath.stat()

            data = self.load_json_data(filename)
            total_items = len(data)
            active_items = len([item for item in data if not item.get("is_deleted", False)])
            deleted_items = total_items - active_items

            return {
                "file_path": str(filepath),
                "file_size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "total_items": total_items,
                "active_items": active_items,
                "deleted_items": deleted_items,
                "has_data": total_items > 0
            }
        except DatabaseOperationError:
            return {
                "file_path": str(self._get_file_path(filename)),
                "file_size_bytes": 0,
                "last_modified": None,
                "total_items": 0,
                "active_items": 0,
                "deleted_items": 0,
                "has_data": False
            }


# Global database manager instance
db_manager = DatabaseManager()


def get_database() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        The database manager instance
    """
    return db_manager