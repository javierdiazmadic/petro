"""Custom exceptions for Petro application."""


class PetroException(Exception):
    """Base exception for Petro."""

    def __init__(self, message: str, code: str = "PETRO_ERROR", status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class DataFetchError(PetroException):
    """Raised when data fetching fails."""

    def __init__(self, message: str, source: str = "unknown") -> None:
        super().__init__(
            message=f"Failed to fetch data from {source}: {message}",
            code="DATA_FETCH_ERROR",
            status_code=502,
        )


class DatabaseError(PetroException):
    """Raised when database operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Database error: {message}",
            code="DATABASE_ERROR",
            status_code=500,
        )


class ModelError(PetroException):
    """Raised when model operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Model error: {message}",
            code="MODEL_ERROR",
            status_code=500,
        )


class ValidationError(PetroException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = "unknown") -> None:
        super().__init__(
            message=f"Validation error in {field}: {message}",
            code="VALIDATION_ERROR",
            status_code=400,
        )


class NotFoundError(PetroException):
    """Raised when resource is not found."""

    def __init__(self, resource: str, identifier: str = "") -> None:
        msg = f"{resource} not found"
        if identifier:
            msg += f": {identifier}"
        super().__init__(
            message=msg,
            code="NOT_FOUND",
            status_code=404,
        )


class ConfigurationError(PetroException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Configuration error: {message}",
            code="CONFIG_ERROR",
            status_code=500,
        )
