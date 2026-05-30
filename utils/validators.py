"""URL validators"""
import re


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    return bool(url_pattern.match(url))


def is_youtube_url(url: str) -> bool:
    """Check if URL is YouTube"""
    return bool(re.search(r"youtube\.com|youtu\.be", url))


def is_instagram_url(url: str) -> bool:
    """Check if URL is Instagram"""
    return bool(re.search(r"instagram\.com", url))


def is_twitter_url(url: str) -> bool:
    """Check if URL is Twitter"""
    return bool(re.search(r"twitter\.com|x\.com", url))


__all__ = ["is_valid_url", "is_youtube_url", "is_instagram_url", "is_twitter_url"]
