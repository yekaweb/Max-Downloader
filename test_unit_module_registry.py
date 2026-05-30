"""Unit tests for ModuleRegistry system"""
import pytest
from modules import discover_modules, get_downloader_by_priority
from modules.base import BaseDownloader


@pytest.mark.unit
class TestModuleDiscovery:
    """Test module discovery and registry"""
    
    def test_discover_modules_returns_list(self):
        """Test that discover_modules returns a list of tuples"""
        modules = discover_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0
    
    def test_module_tuple_structure(self):
        """Test that each module tuple has correct structure"""
        modules = discover_modules()
        for priority, module_class in modules:
            assert isinstance(priority, int)
            assert isinstance(module_class, type)
            assert issubclass(module_class, BaseDownloader)
    
    def test_priority_ordering(self):
        """Test that modules are sorted by priority (highest first)"""
        modules = discover_modules()
        priorities = [p for p, _ in modules]
        
        # Check descending order
        assert priorities == sorted(priorities, reverse=True)
    
    def test_youtube_highest_priority(self):
        """Test that YouTube has highest priority"""
        modules = discover_modules()
        if modules:
            highest_priority, highest_class = modules[0]
            assert highest_class.NAME == "YouTube"
            assert highest_priority == 100
    
    def test_all_modules_have_metadata(self):
        """Test that all modules have required metadata"""
        modules = discover_modules()
        required_attrs = ['NAME', 'ICON', 'PRIORITY', 'VERSION', 'ENABLED']
        
        for _, module_class in modules:
            for attr in required_attrs:
                assert hasattr(module_class, attr), f"Module {module_class.__name__} missing {attr}"


@pytest.mark.unit
class TestDownloaderByPriority:
    """Test priority-based downloader selection"""
    
    def test_youtube_url_returns_youtube(self):
        """Test that YouTube URL returns YouTubeDownloader"""
        url = "https://www.youtube.com/watch?v=test"
        downloader = get_downloader_by_priority(url)
        
        assert downloader is not None
        assert downloader.__class__.NAME == "YouTube"
    
    def test_instagram_url_returns_instagram(self):
        """Test that Instagram URL returns InstagramDownloader"""
        url = "https://www.instagram.com/p/ABC123/"
        downloader = get_downloader_by_priority(url)
        
        assert downloader is not None
        assert downloader.__class__.NAME == "Instagram"
    
    def test_unknown_url_returns_directlink(self):
        """Test that unknown URL returns DirectLinkDownloader"""
        url = "https://example.com/video.mp4"
        downloader = get_downloader_by_priority(url)
        
        assert downloader is not None
        assert downloader.__class__.NAME == "Direct Link"
    
    def test_invalid_url_returns_none(self):
        """Test that invalid URL handling"""
        url = "not a url"
        downloader = get_downloader_by_priority(url)
        
        # Should either return None or fallback downloader
        assert downloader is None or isinstance(downloader, BaseDownloader)
