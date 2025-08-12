"""Simple async-safe in-process TTL cache.

Avoids external dependencies (no Redis). Suitable for small datasets and
read-heavy endpoints. Values expire after a configurable TTL.
"""

from __future__ import annotations

import time
import asyncio
from collections import OrderedDict
from typing import Any, Callable, Sequence
import inspect
from functools import wraps


class AsyncTTLCache:
    """A lightweight async-safe TTL cache with basic LRU eviction."""

    def __init__(self, max_items: int, ttl_seconds: int) -> None:
        self._max_items = max(1, int(max_items))
        # ttl_seconds == 0 means unlimited TTL (no expiration)
        self._ttl_seconds = max(0, int(ttl_seconds))
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = asyncio.Lock()

    def _now(self) -> float:
        return time.monotonic()

    def _is_expired(self, expires_at: float) -> bool:
        return self._now() >= expires_at

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, value = item
            if self._ttl_seconds > 0 and self._is_expired(expires_at):
                # Drop expired
                self._store.pop(key, None)
                return None
            # Mark as recently used
            self._store.move_to_end(key)
            return value

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            expires_at = self._now() + self._ttl_seconds if self._ttl_seconds > 0 else float("inf")
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            # Evict oldest if over capacity
            while len(self._store) > self._max_items:
                self._store.popitem(last=False)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def delete_prefix(self, prefix: str) -> None:
        async with self._lock:
            keys_to_delete = [k for k in self._store.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
                self._store.pop(k, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()


def _build_key_from_args(
    func: Callable[..., Any], include: Sequence[str] | None, prefix: str | None, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    sig = inspect.signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    parts: list[str] = [prefix or f"{func.__module__}.{func.__qualname__}"]
    if include:
        for name in include:
            parts.append(str(bound.arguments.get(name)))
    return ":".join(parts)


def cached(
    cache_getter: Callable[[], AsyncTTLCache | None],
    *,
    include: Sequence[str] | None = None,
    prefix: str | None = None,
):
    """Decorator to cache async function results in an AsyncTTLCache.

    - cache_getter: function returning the cache instance (or None to disable)
    - include: parameter names to include in the key
    - prefix: key prefix namespace (defaults to module.qualname)
    """

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            cache = cache_getter()
            if cache is None:
                return await func(*args, **kwargs)
            key = _build_key_from_args(func, include, prefix, args, kwargs)
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result

        return wrapper

    return decorator


async def invalidate_prefix(cache_getter: Callable[[], AsyncTTLCache | None], prefix: str) -> None:
    cache = cache_getter()
    if cache:
        await cache.delete_prefix(prefix)


