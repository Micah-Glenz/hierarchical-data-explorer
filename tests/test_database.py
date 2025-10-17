"""
Test suite for database operations with logging verification.

This module tests DatabaseManager CRUD operations and validates that
proper logging is performed for all operations.
"""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.core.database import DatabaseManager, DatabaseOperationContext
from src.core.exceptions import DatabaseOperationError, DataNotFoundError
from src.core.config import Settings


class TestDatabaseOperationContext:
    """Test DatabaseOperationContext logging functionality."""

    def test_context_initialization(self):
        """Test DatabaseOperationContext initialization."""
        context = DatabaseOperationContext("test_op", "test_file", {"user": "test_user"})

        assert context.operation == "test_op"
        assert context.filename == "test_file"
        assert context.user_context == {"user": "test_user"}
        assert context.start_time > 0
        assert "operation_id" in context.metadata
        assert context.metadata["operation"] == "test_op"
        assert context.metadata["target_filename"] == "test_file"

    def test_context_log_methods(self):
        """Test DatabaseOperationContext logging methods."""
        with patch('src.core.database.logger') as mock_logger:
            context = DatabaseOperationContext("test_op", "test_file")

            # Test log_start
            context.log_start("Starting operation")
            mock_logger.info.assert_called_once()
            assert "test_op" in str(mock_logger.info.call_args)

            # Test log_success
            context.log_success("Operation completed")
            mock_logger.info.assert_called()
            assert "Operation completed" in str(mock_logger.info.call_args)
            assert "duration_seconds" in context.metadata
            assert context.metadata["status"] == "success"

            # Test log_error
            test_error = Exception("Test error")
            context.log_error("Operation failed", test_error)
            mock_logger.error.assert_called_once()
            assert "Operation failed" in str(mock_logger.error.call_args)
            assert "Test error" in str(mock_logger.error.call_args)
            assert context.metadata["status"] == "error"

            # Test log_warning
            context.log_warning("Warning message")
            mock_logger.warning.assert_called_once()
            assert "Warning message" in str(mock_logger.warning.call_args)

            # Test log_debug
            context.log_debug("Debug message")
            mock_logger.debug.assert_called_once()
            assert "Debug message" in str(mock_logger.debug.call_args)


class TestDatabaseManagerBasicOperations:
    """Test basic DatabaseManager operations."""

    def test_initialization(self):
        """Test DatabaseManager initialization."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path("test_data")
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            db_manager = DatabaseManager()
            assert db_manager.settings == mock_settings

    def test_get_file_path(self):
        """Test file path resolution."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path("test_data")
            mock_settings.get_data_path = lambda filename: Path("test_data") / filename
            mock_get_settings.return_value = mock_settings

            db_manager = DatabaseManager()
            file_path = db_manager._get_file_path("test.json")
            assert file_path == Path("test_data/test.json")

    def test_validate_file_exists_valid_file(self):
        """Test file validation with existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            db_manager = DatabaseManager()
            # Should not raise exception for existing file
            db_manager._validate_file_exists(temp_path)

            # Clean up
            temp_path.unlink()

    def test_validate_file_exists_missing_file(self):
        """Test file validation with missing file."""
        missing_path = Path("/nonexistent/file.json")

        db_manager = DatabaseManager()
        with pytest.raises(DatabaseOperationError):
            db_manager._validate_file_exists(missing_path)

    def test_get_next_id_empty_file(self):
        """Test get_next_id with empty/nonexistent file."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path("test_data")
            mock_settings.get_data_path = lambda filename: Path("test_data") / filename
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            db_manager = DatabaseManager()
            next_id = db_manager.get_next_id("nonexistent.json")
            assert next_id == 1

    def test_get_next_id_existing_file(self):
        """Test get_next_id with existing file."""
        test_data = [
            {"id": 1, "name": "Test 1"},
            {"id": 3, "name": "Test 2"},
            {"id": 5, "name": "Test 3"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            with patch('src.core.database.get_settings') as mock_get_settings:
                mock_settings = Mock(spec=Settings)
                mock_settings.DATA_DIR = Path(temp_dir)
                mock_settings.get_data_path = lambda filename: test_file
                mock_settings.ensure_data_directory.return_value = True
                mock_get_settings.return_value = mock_settings

                db_manager = DatabaseManager()
                next_id = db_manager.get_next_id("test.json")
                assert next_id == 6  # Max ID is 5, so next is 6


class TestDatabaseManagerCRUDWithLogging:
    """Test DatabaseManager CRUD operations with logging verification."""

    def setup_database_manager(self, temp_dir):
        """Set up DatabaseManager with temporary directory."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path(temp_dir)
            mock_settings.get_data_path = lambda filename: Path(temp_dir) / filename
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            return DatabaseManager()

    def test_load_json_data_success_logging(self):
        """Test successful JSON data loading with logging."""
        test_data = [
            {"id": 1, "name": "Test Item 1"},
            {"id": 2, "name": "Test Item 2"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                result = db_manager.load_json_data("test.json")

                # Verify data was loaded correctly
                assert len(result) == 2
                assert result[0]["id"] == 1
                assert result[1]["id"] == 2

                # Verify logging was called
                mock_logger.info.assert_called()
                log_calls = [str(call) for call in mock_logger.info.call_args_list]

                # Check for start and success logs
                assert any("Loading data from test.json" in call for call in log_calls)
                assert any("Successfully loaded 2 items from test.json" in call for call in log_calls)
                assert any("operation_id" in call for call in log_calls)

    def test_load_json_data_invalid_json_logging(self):
        """Test JSON data loading with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "invalid.json"
            with open(test_file, 'w') as f:
                f.write("{ invalid json")

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                with pytest.raises(DatabaseOperationError):
                    db_manager.load_json_data("invalid.json")

                # Verify error logging was called
                mock_logger.error.assert_called()
                log_call = str(mock_logger.error.call_args)
                assert "JSON decode failed" in log_call
                assert "operation_id" in log_call

    def test_save_json_data_success_logging(self):
        """Test successful JSON data saving with logging."""
        test_data = [
            {"id": 1, "name": "Test Item 1"},
            {"id": 2, "name": "Test Item 2"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                success = db_manager.save_json_data("test.json", test_data)

                assert success is True

                # Verify file was created
                test_file = Path(temp_dir) / "test.json"
                assert test_file.exists()

                # Verify data was saved correctly
                with open(test_file, 'r') as f:
                    saved_data = json.load(f)
                assert saved_data == test_data

                # Verify logging was called
                mock_logger.info.assert_called()
                log_calls = [str(call) for call in mock_logger.info.call_args_list]

                assert any("Saving data to test.json" in call for call in log_calls)
                assert any("Successfully saved 2 items to test.json" in call for call in log_calls)
                assert any("operation_id" in call for call in log_calls)

    def test_save_json_data_invalid_data_logging(self):
        """Test JSON data saving with invalid data."""
        invalid_data = "not a list"  # Should be a list

        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                with pytest.raises(DatabaseOperationError):
                    db_manager.save_json_data("test.json", invalid_data)

                # Verify error logging was called
                mock_logger.error.assert_called()
                log_call = str(mock_logger.error.call_args)
                assert "Save operation failed" in log_call
                assert "operation_id" in log_call

    def test_find_by_id_success_logging(self):
        """Test successful find_by_id operation with logging."""
        test_data = [
            {"id": 1, "name": "Test Item 1", "is_deleted": False},
            {"id": 2, "name": "Test Item 2", "is_deleted": False},
            {"id": 3, "name": "Deleted Item", "is_deleted": True}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                # Test finding active item
                result = db_manager.find_by_id("test.json", 2, include_deleted=False)
                assert result is not None
                assert result["id"] == 2
                assert result["name"] == "Test Item 2"

                # Test finding deleted item
                result_deleted = db_manager.find_by_id("test.json", 3, include_deleted=False)
                assert result_deleted is None

                # Test finding deleted item with include_deleted=True
                result_with_deleted = db_manager.find_by_id("test.json", 3, include_deleted=True)
                assert result_with_deleted is not None
                assert result_with_deleted["id"] == 3

                # Verify logging was called for find operation
                mock_logger.info.assert_called()
                log_calls = [str(call) for call in mock_logger.info.call_args_list]

                # Check for search and success/failure logs
                assert any("Searching for item 2 in test.json" in call for call in log_calls)
                assert any("operation_id" in call for call in log_calls)

    def test_find_by_id_not_found_logging(self):
        """Test find_by_id operation for non-existent item with logging."""
        test_data = [{"id": 1, "name": "Test Item", "is_deleted": False}]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                result = db_manager.find_by_id("test.json", 999, include_deleted=False)
                assert result is None

                # Verify logging was called
                mock_logger.info.assert_called()
                log_call = str(mock_logger.info.call_args)
                assert "Searching for item 999 in test.json" in log_call
                assert "Item 999 not found" in log_call

    def test_append_item_success_logging(self):
        """Test successful append_item operation with logging."""
        test_data = [
            {"id": 1, "name": "Existing Item"}
        ]
        new_item = {"id": 2, "name": "New Item"}

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                success = db_manager.append_item("test.json", new_item)
                assert success is True

                # Verify item was added
                with open(test_file, 'r') as f:
                    saved_data = json.load(f)
                assert len(saved_data) == 2
                assert saved_data[1]["id"] == 2
                assert saved_data[1]["name"] == "New Item"

                # Verify logging was called
                mock_logger.info.assert_called()
                log_calls = [str(call) for call in mock_logger.info.call_args_list]

                assert any("Appending item 2 to test.json" in call for call in log_calls)
                assert any("Successfully appended item 2 to test.json" in call for call in log_calls)
                assert any("original_count=1" in call for call in log_calls)
                assert any("new_count=2" in call for call in log_calls)

    def test_append_item_duplicate_id_logging(self):
        """Test append_item operation with duplicate ID with warning logging."""
        test_data = [
            {"id": 1, "name": "Existing Item"}
        ]
        duplicate_item = {"id": 1, "name": "Duplicate Item"}

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                success = db_manager.append_item("test.json", duplicate_item)
                assert success is True  # Operation still succeeds

                # Verify warning was logged about duplicate ID
                mock_logger.warning.assert_called()
                warning_call = str(mock_logger.warning.call_args)
                assert "Item with ID 1 already exists" in warning_call

                # Verify both items are in the file
                with open(test_file, 'r') as f:
                    saved_data = json.load(f)
                assert len(saved_data) == 2

    def test_backup_creation_logging(self):
        """Test backup creation with logging."""
        original_data = [{"id": 1, "name": "Original Data"}]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(original_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                # Test successful backup
                db_manager._create_backup(test_file)

                # Verify backup was created
                backup_files = list(Path(temp_dir).glob("test.json.backup.*"))
                assert len(backup_files) == 1

                # Verify backup file has same content
                with open(backup_files[0], 'r') as f:
                    backup_data = json.load(f)
                assert backup_data == original_data

                # Verify logging was called
                mock_logger.info.assert_called()
                log_call = str(mock_logger.info.call_args)
                assert "Created backup:" in log_call
                assert "original_bytes" in log_call
                assert "backup_bytes" in log_call

            # Test backup when file doesn't exist
            non_existent_file = Path(temp_dir) / "nonexistent.json"

            with patch('src.core.database.logger') as mock_logger:
                db_manager._create_backup(non_existent_file)

                # Verify debug logging for non-existent file
                mock_logger.debug.assert_called()
                debug_call = str(mock_logger.debug.call_args)
                assert "No backup needed - file does not exist" in debug_call

    def test_backup_creation_failure_logging(self):
        """Test backup creation failure with warning logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "readonly.json"
            with open(test_file, 'w') as f:
                json.dump([{"id": 1}], f)

            # Make file read-only to cause backup failure
            test_file.chmod(0o444)

            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                with patch('src.core.database.shutil') as mock_shutil:
                    mock_shutil.copy2.side_effect = PermissionError("Permission denied")

                    # Should not raise exception, just log warning
                    db_manager._create_backup(test_file)

                    # Verify warning was logged
                    mock_logger.warning.assert_called()
                    warning_call = str(mock_logger.warning.call_args)
                    assert "Failed to create backup" in warning_call


class TestDatabaseManagerErrorHandling:
    """Test DatabaseManager error handling and edge cases."""

    def setup_database_manager(self, temp_dir):
        """Set up DatabaseManager with temporary directory."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path(temp_dir)
            mock_settings.get_data_path = lambda filename: Path(temp_dir) / filename
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            return DatabaseManager()

    def test_load_json_data_file_not_found(self):
        """Test load_json_data with file not found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            with patch('src.core.database.logger') as mock_logger:
                result = db_manager.load_json_data("nonexistent.json")
                assert result == []  # Should return empty list

                # Verify error was logged
                mock_logger.error.assert_called()
                log_call = str(mock_logger.error.call_args)
                assert "Database error while loading" in log_call

    def test_save_json_data_permission_error(self):
        """Test save_json_data with permission error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            # Create a directory where a file should be
            invalid_path = Path(temp_dir) / "directory.json"
            invalid_path.mkdir()

            with patch('src.core.database.logger') as mock_logger:
                with pytest.raises(DatabaseOperationError):
                    db_manager.save_json_data("directory.json", [{"id": 1}])

                # Verify error was logged
                mock_logger.error.assert_called()
                log_call = str(mock_logger.error.call_args)
                assert "Save operation failed" in log_call

    def test_find_all_with_include_deleted(self):
        """Test find_all with include_deleted parameter."""
        test_data = [
            {"id": 1, "name": "Active Item", "is_deleted": False},
            {"id": 2, "name": "Deleted Item", "is_deleted": True},
            {"id": 3, "name": "Another Active Item", "is_deleted": False}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            # Test without including deleted items
            active_items = db_manager.find_all("test.json", include_deleted=False)
            assert len(active_items) == 2
            assert all(not item.get("is_deleted", False) for item in active_items)

            # Test including deleted items
            all_items = db_manager.find_all("test.json", include_deleted=True)
            assert len(all_items) == 3

    def test_get_file_stats(self):
        """Test get_file_stats method."""
        test_data = [
            {"id": 1, "name": "Test Item", "is_deleted": False},
            {"id": 2, "name": "Deleted Item", "is_deleted": True}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)

            db_manager = self.setup_database_manager(temp_dir)

            stats = db_manager.get_file_stats("test.json")

            assert stats["file_path"] == str(test_file)
            assert stats["file_size_bytes"] > 0
            assert stats["total_items"] == 2
            assert stats["active_items"] == 1
            assert stats["deleted_items"] == 1
            assert stats["has_data"] is True
            assert "last_modified" in stats

    def test_get_file_stats_nonexistent_file(self):
        """Test get_file_stats with non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            stats = db_manager.get_file_stats("nonexistent.json")

            assert stats["file_path"] == str(Path(temp_dir) / "nonexistent.json")
            assert stats["file_size_bytes"] == 0
            assert stats["total_items"] == 0
            assert stats["active_items"] == 0
            assert stats["deleted_items"] == 0
            assert stats["has_data"] is False
            assert stats["last_modified"] is None


class TestDatabaseManagerPerformance:
    """Test DatabaseManager performance and efficiency."""

    def setup_database_manager(self, temp_dir):
        """Set up DatabaseManager with temporary directory."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path(temp_dir)
            mock_settings.get_data_path = lambda filename: Path(temp_dir) / filename
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            return DatabaseManager()

    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        # Create a large dataset (1000 items)
        large_data = [
            {"id": i, "name": f"Item {i}", "is_deleted": i % 10 == 0}
            for i in range(1, 1001)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Time the save operation
            import time
            start_time = time.time()

            db_manager = self.setup_database_manager(temp_dir)
            success = db_manager.save_json_data("large.json", large_data)

            save_time = time.time() - start_time

            assert success is True
            assert save_time < 1.0  # Should complete in less than 1 second

            # Time the load operation
            start_time = time.time()

            loaded_data = db_manager.load_json_data("large.json")

            load_time = time.time() - start_time

            assert len(loaded_data) == 1000
            assert load_time < 0.5  # Should complete in less than 0.5 seconds

    def test_concurrent_operations(self):
        """Test database manager with concurrent operations."""
        import threading
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            results = []
            errors = []

            def worker(worker_id):
                try:
                    # Each worker performs 10 operations
                    for i in range(10):
                        item = {"id": worker_id * 10 + i, "name": f"Worker {worker_id} Item {i}"}
                        success = db_manager.append_item("concurrent.json", item)
                        results.append((worker_id, i, success))
                        time.sleep(0.001)  # Small delay to simulate real work
                except Exception as e:
                    errors.append((worker_id, str(e)))

            # Create 5 worker threads
            threads = []
            for worker_id in range(5):
                thread = threading.Thread(target=worker, args=(worker_id,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=5.0)

            # Verify all operations completed successfully
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 50, f"Expected 50 results, got {len(results)}"
            assert all(success for _, _, success in results), "Some operations failed"

            # Verify all data was saved correctly
            final_data = db_manager.load_json_data("concurrent.json")
            assert len(final_data) == 50


class TestDatabaseManagerIntegration:
    """Test DatabaseManager integration scenarios."""

    def setup_database_manager(self, temp_dir):
        """Set up DatabaseManager with temporary directory."""
        with patch('src.core.database.get_settings') as mock_get_settings:
            mock_settings = Mock(spec=Settings)
            mock_settings.DATA_DIR = Path(temp_dir)
            mock_settings.get_data_path = lambda filename: Path(temp_dir) / filename
            mock_settings.ensure_data_directory.return_value = True
            mock_get_settings.return_value = mock_settings

            return DatabaseManager()

    def test_crud_lifecycle(self):
        """Test complete CRUD lifecycle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            # CREATE: Add initial items
            item1 = {"id": 1, "name": "Item 1", "is_deleted": False}
            item2 = {"id": 2, "name": "Item 2", "is_deleted": False}

            assert db_manager.append_item("lifecycle.json", item1)
            assert db_manager.append_item("lifecycle.json", item2)

            # READ: Find items
            found_item1 = db_manager.find_by_id("lifecycle.json", 1)
            found_item2 = db_manager.find_by_id("lifecycle.json", 2)

            assert found_item1 is not None
            assert found_item1["name"] == "Item 1"
            assert found_item2 is not None
            assert found_item2["name"] == "Item 2"

            # READ: Find all items
            all_items = db_manager.find_all("lifecycle.json")
            assert len(all_items) == 2

            # UPDATE: Modify item (simulate update with append and soft delete)
            update_data = {"id": 1, "name": "Updated Item 1", "is_deleted": False}
            db_manager.append_item("lifecycle.json", update_data)  # This would normally be handled by update logic

            # DELETE: Soft delete item
            assert db_manager.soft_delete_by_id("lifecycle.json", 2)

            # Verify soft delete
            active_items = db_manager.find_all("lifecycle.json", include_deleted=False)
            assert len(active_items) == 2  # Both items still there (original + updated)

            deleted_items = db_manager.find_all("lifecycle.json", include_deleted=True)
            assert len(deleted_items) == 3  # Original + updated + deleted

    def test_relationship_maintenance(self):
        """Test maintaining relationships between entities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_manager = self.setup_database_manager(temp_dir)

            # Create parent data (customers)
            customers = [
                {"id": 1, "name": "Customer A", "is_deleted": False},
                {"id": 2, "name": "Customer B", "is_deleted": False}
            ]
            db_manager.save_json_data("customers.json", customers)

            # Create child data (projects linked to customers)
            projects = [
                {"id": 101, "customer_id": 1, "name": "Project A1", "is_deleted": False},
                {"id": 102, "customer_id": 1, "name": "Project A2", "is_deleted": False},
                {"id": 201, "customer_id": 2, "name": "Project B1", "is_deleted": False}
            ]
            db_manager.save_json_data("projects.json", projects)

            # Test relationship queries
            customer_1_projects = db_manager.filter_by_field("projects.json", "customer_id", 1)
            assert len(customer_1_projects) == 2

            customer_2_projects = db_manager.filter_by_field("projects.json", "customer_id", 2)
            assert len(customer_2_projects) == 1

            # Test cascade delete simulation
            db_manager.soft_delete_by_id("customers.json", 1)

            # Verify customer is deleted
            active_customers = db_manager.find_all("customers.json", include_deleted=False)
            assert len(active_customers) == 1
            assert active_customers[0]["id"] == 2

            # Projects should still exist (in real implementation, cascade delete would be separate)
            all_projects = db_manager.find_all("projects.json", include_deleted=False)
            assert len(all_projects) == 3  # All projects still exist