"""Base downloader module definitions"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class MediaInfo:
    url: str
    title: Optional[str] = None
    duration: Optional[int] = None
    thumbnails: Optional[list] = None
    formats: Optional[list] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseDownloader(ABC):
    """Abstract base class for downloader modules"""
    
    # Module metadata - subclasses should override
    NAME: str = "Unknown"
    ICON: str = "📦"
    SUPPORTED_DOMAINS: list[str] = []
    VERSION: str = "1.0.0"
    ENABLED: bool = True
    PRIORITY: int = 0  # Higher priority = tried first (0-100)

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        """Return True if this module can handle the given URL"""
        raise NotImplementedError

    @abstractmethod
    async def fetch_info(self, url: str) -> MediaInfo:
        """Fetch metadata for the media"""
        raise NotImplementedError

    @abstractmethod
    async def download(self, media_info: MediaInfo, output_path: str) -> str:
        """Download media and return local file path"""
        raise NotImplementedError

__all__ = ["BaseDownloader", "MediaInfo"]
