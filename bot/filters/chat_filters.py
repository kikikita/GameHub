"""Custom filters for chat types and admin access."""

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message
from settings import settings


class ChatTypeFilter(BaseFilter):
    """Filter messages by allowed chat types."""

    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        """Return ``True`` if message chat type matches filter."""

        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        return message.chat.type in self.chat_type


class AdminFilter(BaseFilter):
    """Allow only admin user to pass."""

    async def __call__(self, message: Message) -> bool:
        """Check if message is from configured admin."""

        return message.from_user.id in settings.bots.admin_id
