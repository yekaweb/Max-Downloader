"""URL detection filter"""
from aiogram.filters import Filter
from aiogram.types import Message
import re


class URLFilter(Filter):
    URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return bool(self.URL_REGEX.search(message.text))


__all__ = ["URLFilter"]
