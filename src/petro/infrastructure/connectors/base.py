"""Base connector class for all data sources."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from petro.core import get_logger


class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    def __init__(self, source_name: str, timeout: int = 30, max_retries: int = 3):
        """Initialize connector.

        Args:
            source_name: Human-readable name of data source
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.source_name = source_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(f"{__name__}.{source_name}")

    @abstractmethod
    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch data from source.

        Returns:
            Dictionary with fetched data, or None on failure
        """
        pass

    async def validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate response data.

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        return data is not None and isinstance(data, dict)

    def log_fetch(self, success: bool, message: str = "", **extra):
        """Log fetch operation.

        Args:
            success: Whether fetch was successful
            message: Optional message
            **extra: Extra context to log
        """
        level = "info" if success else "warning"
        log_func = self.logger.info if success else self.logger.warning

        context = {"source": self.source_name, "timestamp": datetime.utcnow().isoformat()}
        context.update(extra)

        log_msg = f"[{self.source_name}] {message}" if message else f"[{self.source_name}] Fetch {'success' if success else 'failed'}"
        log_func(log_msg, extra=context)
