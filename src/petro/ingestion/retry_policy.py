"""Retry policy for data fetching."""

import asyncio
import random
from typing import Callable, Optional, TypeVar

from petro.core import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RetryPolicy:
    """Configurable retry policy with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry policy.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff calculation
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    async def execute(
        self,
        func: Callable,
        *args,
        on_failure: Optional[Callable] = None,
        **kwargs,
    ) -> Optional[T]:
        """Execute function with automatic retries.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            on_failure: Optional callback on failure (takes exception)
            **kwargs: Keyword arguments for func

        Returns:
            Result of func, or None if all retries exhausted
        """
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Success on attempt {attempt + 1}/{self.max_retries + 1}")
                return result

            except Exception as e:
                if attempt < self.max_retries:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed: {e}"
                    )
                    if on_failure:
                        await on_failure(e) if asyncio.iscoroutinefunction(on_failure) else on_failure(e)
                    return None

        return None


# Common retry policies
DEFAULT_RETRY_POLICY = RetryPolicy(max_retries=3)
AGGRESSIVE_RETRY_POLICY = RetryPolicy(
    max_retries=5,
    initial_delay=0.5,
    max_delay=60.0,
)
CONSERVATIVE_RETRY_POLICY = RetryPolicy(
    max_retries=2,
    initial_delay=2.0,
    max_delay=15.0,
)
