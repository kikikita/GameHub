"""Middleware to send typing action while processing commands."""

import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class TypingMiddleware(BaseMiddleware):
    """Send 'typing' action while handler is processing."""

    def __init__(self, interval: float = 4.0):
        """Initialize middleware."""

        self.interval = interval

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        """Forward update while periodically sending typing status."""
        if not isinstance(event, Message):
            return await handler(event, data)

        stop_event = asyncio.Event()

        async def send_typing() -> None:
            while not stop_event.is_set():
                try:
                    await event.bot.send_chat_action(event.chat.id, "typing")
                    await asyncio.wait_for(
                        stop_event.wait(),
                        timeout=self.interval,
                    )
                except asyncio.TimeoutError:
                    continue

        task = asyncio.create_task(send_typing())
        try:
            return await handler(event, data)
        finally:
            stop_event.set()
            await task
