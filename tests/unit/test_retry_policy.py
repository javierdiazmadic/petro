"""Unit tests for retry policy."""

import pytest

from petro.ingestion.retry_policy import (
    AGGRESSIVE_RETRY_POLICY,
    CONSERVATIVE_RETRY_POLICY,
    DEFAULT_RETRY_POLICY,
    RetryPolicy,
)


def test_retry_policy_delay_calculation():
    """Test delay calculation with exponential backoff."""
    policy = RetryPolicy(
        max_retries=3,
        initial_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=False,
    )

    # Delays: 1.0, 2.0, 4.0
    assert policy.get_delay(0) == 1.0
    assert policy.get_delay(1) == 2.0
    assert policy.get_delay(2) == 4.0
    assert policy.get_delay(3) == 8.0


def test_retry_policy_max_delay():
    """Test that delays don't exceed max_delay."""
    policy = RetryPolicy(
        max_retries=10,
        initial_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=False,
    )

    # Exponential would be 512, but should be capped at 10
    assert policy.get_delay(10) == 10.0


def test_retry_policy_jitter():
    """Test that jitter adds randomness."""
    policy = RetryPolicy(
        max_retries=3,
        initial_delay=10.0,
        max_delay=100.0,
        exponential_base=2.0,
        jitter=True,
    )

    # Get multiple samples and check they're different
    delays = [policy.get_delay(0) for _ in range(5)]
    assert len(set(delays)) > 1  # Should have variation


@pytest.mark.asyncio
async def test_retry_policy_success_on_first_attempt():
    """Test successful execution on first attempt."""

    async def successful_func():
        return "success"

    policy = RetryPolicy(max_retries=3)
    result = await policy.execute(successful_func)

    assert result == "success"


@pytest.mark.asyncio
async def test_retry_policy_success_after_retries():
    """Test successful execution after some failures."""
    attempt_count = 0

    async def sometimes_fails():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError(f"Attempt {attempt_count} failed")
        return "success"

    policy = RetryPolicy(max_retries=5, initial_delay=0.01)
    result = await policy.execute(sometimes_fails)

    assert result == "success"
    assert attempt_count == 3


@pytest.mark.asyncio
async def test_retry_policy_exhaustion():
    """Test retry exhaustion after max attempts."""
    attempt_count = 0

    async def always_fails():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("Always fails")

    policy = RetryPolicy(max_retries=2, initial_delay=0.01)
    result = await policy.execute(always_fails)

    assert result is None
    assert attempt_count == 3  # initial + 2 retries


@pytest.mark.asyncio
async def test_retry_policy_callback_on_failure():
    """Test callback is called on final failure."""
    failures = []

    async def handle_failure(exc):
        failures.append(str(exc))

    async def always_fails():
        raise ValueError("Test error")

    policy = RetryPolicy(max_retries=1, initial_delay=0.01)
    result = await policy.execute(always_fails, on_failure=handle_failure)

    assert result is None
    assert len(failures) == 1
    assert "Test error" in failures[0]


def test_default_retry_policy():
    """Test default retry policy configuration."""
    assert DEFAULT_RETRY_POLICY.max_retries == 3


def test_aggressive_retry_policy():
    """Test aggressive retry policy configuration."""
    assert AGGRESSIVE_RETRY_POLICY.max_retries == 5


def test_conservative_retry_policy():
    """Test conservative retry policy configuration."""
    assert CONSERVATIVE_RETRY_POLICY.max_retries == 2
