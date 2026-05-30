"""Admin filter for command access control"""
from aiogram.filters import Filter
from aiogram.types import Message
from config_simple import settings


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMIN_IDS_LIST


__all__ = ["IsAdmin"]
