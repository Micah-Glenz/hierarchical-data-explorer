"""
Custom exceptions for the Hierarchical Data Explorer.

This module defines custom exceptions that provide specific error handling
for different types of application errors.
"""

from typing import Optional, Dict, Any


class DataExplorerException(Exception):
    """
    Base exception for all Data Explorer errors.

    This class provides a foundation for all custom exceptions in the application,
    ensuring consistent error handling and reporting.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ) -> None:
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message
            details: Additional error details (optional)
            error_code: Machine-readable error code (optional)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "error_code": self.error_code,
        }


class DataValidationError(DataExplorerException):
    """
    Exception raised for data validation errors.

    This exception is used when input data fails validation rules,
    such as missing required fields, invalid formats, or business rule violations.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rule: Optional[str] = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Validation error message
            field: Name of the field that failed validation (optional)
            value: The invalid value (optional)
            validation_rule: Description of the validation rule that failed (optional)
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if validation_rule:
            details["validation_rule"] = validation_rule

        super().__init__(message, details, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.validation_rule = validation_rule


class DataNotFoundError(DataExplorerException):
    """
    Exception raised when requested data is not found.

    This exception is used when a lookup operation fails to find
    the requested data, such as a customer, project, or quote.
    """

    def __init__(self, message: str, resource_type: str, resource_id: Optional[Any] = None) -> None:
        """
        Initialize not found error.

        Args:
            message: Error message
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found (optional)
        """
        details = {"resource_type": resource_type}
        if resource_id is not None:
            details["resource_id"] = resource_id

        super().__init__(message, details, "NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class DatabaseOperationError(DataExplorerException):
    """
    Exception raised for database operation errors.

    This exception is used when file system operations fail,
    such as reading, writing, or updating JSON data files.
    """

    def __init__(
        self,
        message: str,
        operation: str,
        filename: Optional[str] = None,
        original_error: Optional[Exception] = None
    ) -> None:
        """
        Initialize database operation error.

        Args:
            message: Error message
            operation: Type of operation that failed (read, write, update, delete)
            filename: Name of the file being operated on (optional)
            original_error: The original exception that caused this error (optional)
        """
        details = {"operation": operation}
        if filename:
            details["filename"] = filename
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message, details, "DATABASE_ERROR")
        self.operation = operation
        self.filename = filename
        self.original_error = original_error


class BusinessRuleViolationError(DataExplorerException):
    """
    Exception raised for business rule violations.

    This exception is used when an operation violates business logic,
    such as trying to delete a customer with active projects.
    """

    def __init__(
        self,
        message: str,
        rule: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize business rule violation error.

        Args:
            message: Error message
            rule: Description of the business rule that was violated
            context: Additional context about the violation (optional)
        """
        # Sanitize context by removing any conflicting "rule" key
        sanitized_context = {}
        if context:
            sanitized_context = {k: v for k, v in context.items() if k != "rule"}

        details = {"rule": rule}
        details.update(sanitized_context)

        super().__init__(message, details, "BUSINESS_RULE_VIOLATION")
        self.rule = rule
        self.context = sanitized_context


class InvalidStateError(DataExplorerException):
    """
    Exception raised for invalid application state.

    This exception is used when the application is in an invalid state
    for the requested operation, such as trying to create a project
    without selecting a customer.
    """

    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        required_state: Optional[str] = None
    ) -> None:
        """
        Initialize invalid state error.

        Args:
            message: Error message
            current_state: Description of the current state (optional)
            required_state: Description of the required state (optional)
        """
        details = {}
        if current_state:
            details["current_state"] = current_state
        if required_state:
            details["required_state"] = required_state

        super().__init__(message, details, "INVALID_STATE")
        self.current_state = current_state
        self.required_state = required_state


class ExternalServiceError(DataExplorerException):
    """
    Exception raised for external service errors.

    This exception is used when external services (if any) fail,
    such as third-party APIs or external data sources.
    """

    def __init__(
        self,
        message: str,
        service: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize external service error.

        Args:
            message: Error message
            service: Name of the external service
            status_code: HTTP status code (optional)
            response_data: Response data from the service (optional)
        """
        details = {"service": service}
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data

        super().__init__(message, details, "EXTERNAL_SERVICE_ERROR")
        self.service = service
        self.status_code = status_code
        self.response_data = response_data or {}


def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a standardized error response.

    This function provides a consistent way to convert exceptions
    into error responses that can be returned to clients.

    Args:
        exc: The exception to handle

    Returns:
        Standardized error dictionary
    """
    if isinstance(exc, DataExplorerException):
        return exc.to_dict()
    else:
        # Handle unexpected exceptions
        return {
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"original_error": str(exc)},
            "error_code": "INTERNAL_SERVER_ERROR"
        }