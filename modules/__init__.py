"""Modules Package - Auto-discovery and registry for downloader modules with Priority-based selection"""
import importlib
import pkgutil
from pathlib import Path
from typing import Optional, Dict, Type
from loguru import logger

from .base import BaseDownloader

# Module registry - stores all registered downloader modules with priority
MODULE_REGISTRY: Dict[str, BaseDownloader] = {}
_MODULE_CLASSES: list[tuple[int, Type[BaseDownloader]]] = []  # (priority, class)


def register_module(name: str, downloader: BaseDownloader, priority: int = 0) -> None:
    """
    Register a downloader module in the global registry with priority support.

    Args:
        name: Unique module name (e.g., 'youtube', 'instagram')
        downloader: Instance of BaseDownloader subclass
        priority: Priority level (0-100, higher = tried first)
    """
    if name in MODULE_REGISTRY:
        raise ValueError(f"Module '{name}' is already registered")

    MODULE_REGISTRY[name] = downloader
    _MODULE_CLASSES.append((priority, downloader.__class__))
    
    # Sort by priority descending (higher priority first)
    _MODULE_CLASSES.sort(key=lambda x: x[0], reverse=True)
    logger.info(f"✅ Registered module '{name}' with priority {priority}")


def get_downloader(url: str) -> Optional[BaseDownloader]:
    """
    Find a downloader capable of handling the given URL.
    Uses priority-based selection - tries higher priority modules first.

    Args:
        url: URL to download from

    Returns:
        Appropriate downloader instance or None if not found
    """
    # Try modules in priority order
    for priority, module_class in _MODULE_CLASSES:
        for downloader in MODULE_REGISTRY.values():
            if downloader.__class__ == module_class and downloader.can_handle(url):
                logger.debug(f"✓ Found handler for URL: {module_class.NAME} (priority {priority})")
                return downloader
    
    logger.warning(f"⚠️ No downloader found for URL: {url}")
    return None


def get_downloader_by_priority(url: str) -> Optional[BaseDownloader]:
    """
    Get downloader respecting priority order - best for unknown URLs with fallback.
    
    Returns the FIRST module that can handle the URL (highest priority first).
    """
    for priority, module_class in _MODULE_CLASSES:
        for downloader in MODULE_REGISTRY.values():
            if downloader.__class__ == module_class and downloader.ENABLED and downloader.can_handle(url):
                return downloader
    return None


def get_all_downloaders() -> Dict[str, BaseDownloader]:
    """Get all registered downloaders"""
    return MODULE_REGISTRY.copy()


def discover_modules() -> list[tuple[int, Type[BaseDownloader]]]:
    """
    Auto-discover downloader modules from subdirectories and return them sorted by priority.
    This enables dynamic module loading without manual registration.
    
    Returns:
        List of (priority, module_class) tuples sorted by priority (highest first)
    """
    modules_path = Path(__file__).parent
    discovered = []
    
    for finder, name, ispkg in pkgutil.iter_modules([str(modules_path)]):
        if ispkg and name not in ('__pycache__', '.'):
            try:
                module = importlib.import_module(f".{name}", package=__name__)
                logger.debug(f"Loaded module package: {name}")
                
                # Look for BaseDownloader subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseDownloader) and 
                        attr is not BaseDownloader and
                        hasattr(attr, 'PRIORITY')):
                        priority = attr.PRIORITY
                        discovered.append((priority, attr))
                        logger.info(f"✅ Discovered module: {attr.NAME} (priority={priority})")
            except Exception as e:
                logger.error(f"❌ Failed to load module {name}: {e}")
    
    # Return sorted by priority (highest first)
    return sorted(discovered, key=lambda x: x[0], reverse=True)


# Auto-discover and import modules to trigger auto-registration
discover_modules()

# Fallback: Import modules explicitly to ensure registration
try:
    from .youtube import YouTubeDownloader
except ImportError as e:
    logger.debug(f"YouTube module not available: {e}")

try:
    from .instagram import InstagramDownloader
except ImportError as e:
    logger.debug(f"Instagram module not available: {e}")

try:
    from .twitter import TwitterDownloader
except ImportError as e:
    logger.debug(f"Twitter module not available: {e}")

try:
    from .tiktok import TikTokDownloader
except ImportError as e:
    logger.debug(f"TikTok module not available: {e}")

try:
    from .direct_link import DirectLinkDownloader
except ImportError as e:
    logger.debug(f"Direct Link module not available: {e}")

__all__ = ["MODULE_REGISTRY", "register_module", "get_downloader", "get_downloader_by_priority", "get_all_downloaders", "discover_modules"]
