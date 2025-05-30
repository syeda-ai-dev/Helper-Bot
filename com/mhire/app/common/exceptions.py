from typing import Optional

class BaseError(Exception):
    """Base exception class for all custom exceptions"""
    def __init__(self, message: str, error_code: int, http_status_code: int):
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        super().__init__(self.message)

class DatabaseError(BaseError):
    """Exception raised for database-related errors"""
    def __init__(self, message: str, error_code: int = 50001, http_status_code: int = 500):
        super().__init__(message, error_code, http_status_code)

class ValidationError(BaseError):
    """Exception raised for validation errors"""
    def __init__(self, message: str, error_code: int = 40001, http_status_code: int = 400):
        super().__init__(message, error_code, http_status_code)

class NotFoundError(BaseError):
    """Exception raised when a resource is not found"""
    def __init__(self, message: str, error_code: int = 40401, http_status_code: int = 404):
        super().__init__(message, error_code, http_status_code)

class ConfigurationError(BaseError):
    """Exception raised for configuration-related errors"""
    def __init__(self, message: str, error_code: int = 50002, http_status_code: int = 500):
        super().__init__(message, error_code, http_status_code)

class ExternalServiceError(BaseError):
    """Exception raised for external service errors (e.g., OpenAI API)"""
    def __init__(self, message: str, error_code: int = 50003, http_status_code: int = 503):
        super().__init__(message, error_code, http_status_code)