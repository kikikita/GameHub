"""Agent-related utilities."""

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

from config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retries(
    awaitable_factory: Callable[[], Awaitable[T]],
    retries: int = 3,
    timeout: int = settings.request_timeout,
) -> T:
    """Execute an awaitable with retries and timeout.

    :param awaitable_factory: A function that returns an awaitable.
    :param retries: Maximum number of retries.
    :param timeout: Timeout in seconds for each attempt.
    :return: The result of the awaitable.
    """
    last_exception = None
    for attempt in range(retries):
        try:
            return await asyncio.wait_for(awaitable_factory(), timeout=timeout)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed with error: {str(e)}")
            last_exception = e
    raise last_exception from last_exception 