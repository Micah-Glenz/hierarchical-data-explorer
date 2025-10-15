"""
Configuration settings for the Hierarchical Data Explorer.

This module contains application configuration including data paths,
server settings, and other configurable parameters.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """
    Application configuration class.

    Centralizes all configuration settings for the application,
    making it easier to manage different environments.
    """

    def __init__(self) -> None:
        """Initialize default configuration settings."""
        # Data directory configuration
        self.DATA_DIR = Path("data")

        # Server configuration
        self.HOST = "0.0.0.0"
        self.PORT = 8001
        self.DEBUG = False

        # Application settings
        self.APP_TITLE = "Hierarchical Data Explorer API"
        self.APP_DESCRIPTION = "API for managing hierarchical business data"
        self.APP_VERSION = "1.0.0"

        # File serving configuration
        self.STATIC_DIR = Path(".")
        self.STATIC_URL = "/static"

        # CORS settings (if needed for future development)
        self.ALLOWED_ORIGINS = ["*"]
        self.ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.ALLOWED_HEADERS = ["*"]

        # Data file names
        self.CUSTOMERS_FILE = "customers.json"
        self.PROJECTS_FILE = "projects.json"
        self.QUOTES_FILE = "quotes.json"
        self.FREIGHT_REQUESTS_FILE = "freight_requests.json"
        self.VENDORS_FILE = "vendors.json"

        # Validation settings
        self.MAX_NAME_LENGTH = 255
        self.MAX_INDUSTRY_LENGTH = 100
        self.MAX_BUDGET = 999999999.99
        self.MAX_WEIGHT = 999999.99

    def get_data_path(self, filename: str) -> Path:
        """
        Get full path to a data file.

        Args:
            filename: Name of the data file

        Returns:
            Full path to the data file

        Raises:
            FileNotFoundError: If data directory doesn't exist
        """
        if not self.DATA_DIR.exists():
            raise FileNotFoundError(f"Data directory not found: {self.DATA_DIR}")

        return self.DATA_DIR / filename

    def get_available_files(self) -> Dict[str, Path]:
        """
        Get paths to all available data files.

        Returns:
            Dictionary mapping file types to their paths
        """
        return {
            "customers": self.get_data_path(self.CUSTOMERS_FILE),
            "projects": self.get_data_path(self.PROJECTS_FILE),
            "quotes": self.get_data_path(self.QUOTES_FILE),
            "freight_requests": self.get_data_path(self.FREIGHT_REQUESTS_FILE),
            "vendors": self.get_data_path(self.VENDORS_FILE),
        }

    def validate_data_directory(self) -> bool:
        """
        Validate that the data directory exists and is accessible.

        Returns:
            True if data directory is valid, False otherwise
        """
        try:
            return self.DATA_DIR.exists() and self.DATA_DIR.is_dir()
        except Exception:
            return False

    def ensure_data_directory(self) -> bool:
        """
        Ensure the data directory exists.

        Creates the directory if it doesn't exist.

        Returns:
            True if directory exists or was created successfully
        """
        try:
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        The application settings instance
    """
    return settings


def load_env_settings() -> None:
    """
    Load settings from environment variables.

    This function can be called to override default settings
    with values from environment variables.
    """
    # Server settings
    if os.getenv("HOST"):
        settings.HOST = os.getenv("HOST")
    if os.getenv("PORT"):
        settings.PORT = int(os.getenv("PORT"))
    if os.getenv("DEBUG"):
        settings.DEBUG = os.getenv("DEBUG").lower() in ("true", "1", "yes")

    # Data directory
    if os.getenv("DATA_DIR"):
        settings.DATA_DIR = Path(os.getenv("DATA_DIR"))

    # Application settings
    if os.getenv("APP_TITLE"):
        settings.APP_TITLE = os.getenv("APP_TITLE")
    if os.getenv("APP_DESCRIPTION"):
        settings.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION")
    if os.getenv("APP_VERSION"):
        settings.APP_VERSION = os.getenv("APP_VERSION")