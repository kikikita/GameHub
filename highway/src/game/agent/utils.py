"""Agent-related utilities."""

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

from src.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retries(
    awaitable_factory: Callable[[], Awaitable[T]],
    retries: int = 2,
    timeout: int = settings.request_timeout,
) -> T:
    """Execute an awaitable with retries and timeout."""
    last_exception = None
    for attempt in range(retries):
        try:
            return await asyncio.wait_for(awaitable_factory(), timeout=timeout)
        except Exception as exc:
            logger.warning(
                "Attempt %s/%s failed with error: %s",
                attempt + 1,
                retries,
                exc,
            )
            last_exception = exc
    raise last_exception
