"""
Phase 3 Module Testing - Instagram, TikTok, Twitter
Tests URL detection, module registration, and auto-discovery
"""

import pytest
from modules import get_downloader, get_all_downloaders, MODULE_REGISTRY
from modules.instagram import InstagramDownloader
from modules.twitter import TwitterDownloader


class TestInstagramModule:
    """Test Instagram downloader module"""
    
    def test_instagram_module_exists(self):
        """Verify Instagram module is registered"""
        assert "instagram" in MODULE_REGISTRY
        assert isinstance(MODULE_REGISTRY["instagram"], InstagramDownloader)
    
    def test_instagram_url_detection(self):
        """Test Instagram URL pattern detection"""
        test_urls = [
            "https://instagram.com/p/ABC123/",
            "https://www.instagram.com/p/XYZ789/",
            "https://instagram.com/reel/ABC123/",
            "https://www.instagram.com/reel/XYZ789/",
            "https://instagram.com/stories/username/12345/",
            "https://instagram.com/tv/ABC123/",
            "instagram.com/p/ABC123/",  # without https
        ]
        
        for url in test_urls:
            assert InstagramDownloader.can_handle(url), f"Failed to detect: {url}"
    
    def test_instagram_invalid_urls(self):
        """Test Instagram rejects non-Instagram URLs"""
        test_urls = [
            "https://youtube.com/watch?v=ABC",
            "https://twitter.com/user/status/123",
            "https://tiktok.com/@user/video/123",
            "https://github.com/user/repo",
        ]
        
        for url in test_urls:
            assert not InstagramDownloader.can_handle(url), f"Incorrectly detected: {url}"
    
    def test_instagram_media_id_extraction(self):
        """Test Instagram media ID extraction"""
        test_cases = [
            ("https://instagram.com/p/ABC123/", "ABC123"),
            ("https://instagram.com/reel/XYZ789/", "XYZ789"),
            ("https://instagram.com/tv/DEF456/", "DEF456"),
        ]
        
        for url, expected_id in test_cases:
            extracted_id = InstagramDownloader._extract_media_id(url)
            assert extracted_id == expected_id, f"Expected {expected_id}, got {extracted_id}"


class TestTikTokModule:
    """Test TikTok downloader module (skeleton exists, directory pending)"""
    
    def test_tiktok_module_in_requirements(self):
        """Verify yt-dlp is in requirements.txt"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "yt-dlp" in content, "yt-dlp not in requirements"
    
    def test_tiktok_url_detection_ready(self):
        """Test TikTok URL patterns would be detected"""
        test_urls = [
            "https://www.tiktok.com/@username/video/123456",
            "https://vm.tiktok.com/ABC123/",
            "https://vt.tiktok.com/XYZ789/",
            "tiktok.com/video/123456",
        ]
        
        # These patterns show what TikTok module should detect
        tiktok_patterns = [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@[^/]+/video/\d+',
            r'(?:https?://)?(?:www\.)?tiktok\.com/video/\d+',
            r'(?:https?://)?(?:vm|vt)\.tiktok\.com/[A-Za-z0-9]+',
        ]
        
        import re
        for url in test_urls:
            matches = any(re.search(p, url, re.IGNORECASE) for p in tiktok_patterns)
            assert matches, f"Pattern should match: {url}"


class TestTwitterModule:
    """Test Twitter/X downloader module"""
    
    def test_twitter_module_exists(self):
        """Verify Twitter module is registered"""
        assert "twitter" in MODULE_REGISTRY
        assert isinstance(MODULE_REGISTRY["twitter"], TwitterDownloader)
    
    def test_twitter_url_detection(self):
        """Test Twitter URL pattern detection"""
        test_urls = [
            "https://twitter.com/username/status/123456789",
            "https://x.com/username/status/987654321",
            "https://twitter.com/user/status/123",
            "twitter.com/user/status/123",  # without https
        ]
        
        for url in test_urls:
            assert TwitterDownloader.can_handle(url), f"Failed to detect: {url}"
    
    def test_twitter_invalid_urls(self):
        """Test Twitter rejects non-Twitter URLs"""
        test_urls = [
            "https://instagram.com/p/ABC123/",
            "https://youtube.com/watch?v=ABC",
            "https://tiktok.com/@user/video/123",
        ]
        
        for url in test_urls:
            assert not TwitterDownloader.can_handle(url), f"Incorrectly detected: {url}"
    
    def test_twitter_tweet_id_extraction(self):
        """Test Twitter tweet ID extraction"""
        test_cases = [
            ("https://twitter.com/user/status/123456789", "123456789"),
            ("https://x.com/user/status/987654321", "987654321"),
        ]
        
        for url, expected_id in test_cases:
            extracted_id = TwitterDownloader._extract_tweet_id(url)
            assert extracted_id == expected_id, f"Expected {expected_id}, got {extracted_id}"


class TestModuleRegistry:
    """Test module discovery and registration"""
    
    def test_all_downloaders_registered(self):
        """Verify all downloaders are in registry"""
        downloaders = get_all_downloaders()
        assert "youtube" in downloaders, "YouTube not registered"
        assert "instagram" in downloaders, "Instagram not registered"
        assert "twitter" in downloaders, "Twitter not registered"
    
    def test_get_downloader_instagram(self):
        """Test get_downloader returns Instagram for Instagram URLs"""
        url = "https://instagram.com/p/ABC123/"
        downloader = get_downloader(url)
        assert isinstance(downloader, InstagramDownloader)
    
    def test_get_downloader_twitter(self):
        """Test get_downloader returns Twitter for Twitter URLs"""
        url = "https://twitter.com/user/status/123"
        downloader = get_downloader(url)
        assert isinstance(downloader, TwitterDownloader)
    
    def test_get_downloader_invalid_url(self):
        """Test get_downloader raises error for unsupported URLs"""
        url = "https://example.com/video"
        with pytest.raises(ValueError):
            get_downloader(url)


class TestModuleIntegration:
    """Test module integration and auto-discovery"""
    
    def test_modules_import_without_error(self):
        """Verify all modules can be imported"""
        try:
            from modules.instagram import InstagramDownloader
            from modules.twitter import TwitterDownloader
            from modules.youtube import YouTubeDownloader
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import modules: {e}")
    
    def test_module_registry_count(self):
        """Verify expected number of modules are registered"""
        downloaders = get_all_downloaders()
        # At minimum: YouTube, Instagram, Twitter
        assert len(downloaders) >= 3, f"Expected at least 3 modules, got {len(downloaders)}"
    
    def test_all_modules_have_can_handle(self):
        """Verify all modules implement can_handle method"""
        downloaders = get_all_downloaders()
        for name, downloader in downloaders.items():
            assert hasattr(downloader, 'can_handle'), f"{name} missing can_handle"
            assert callable(downloader.can_handle), f"{name}.can_handle not callable"


class TestURLNormalization:
    """Test URL normalization across modules"""
    
    def test_instagram_url_normalization(self):
        """Test Instagram URL normalization"""
        urls = [
            ("instagram.com/p/ABC123", "https://instagram.com/p/ABC123"),
            ("instagram.com/p/ABC123/", "https://instagram.com/p/ABC123"),
            ("https://instagram.com/p/ABC123?key=value", "https://instagram.com/p/ABC123"),
        ]
        
        for input_url, expected in urls:
            normalized = InstagramDownloader._normalize_url(input_url)
            assert normalized == expected, f"Expected {expected}, got {normalized}"
    
    def test_twitter_url_normalization(self):
        """Test Twitter URL normalization"""
        urls = [
            ("twitter.com/user/status/123", "https://twitter.com/user/status/123"),
            ("x.com/user/status/123", "https://twitter.com/user/status/123"),  # Converts x.com
            ("https://x.com/user/status/123/", "https://twitter.com/user/status/123"),  # Both
        ]
        
        for input_url, expected in urls:
            normalized = TwitterDownloader._normalize_url(input_url)
            assert normalized == expected, f"Expected {expected}, got {normalized}"


class TestRequirements:
    """Test that all required dependencies are in requirements.txt"""
    
    def test_instagrapi_in_requirements(self):
        """Verify instagrapi is listed"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "instagrapi" in content, "instagrapi not in requirements"
    
    def test_tweepy_in_requirements(self):
        """Verify tweepy is listed"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "tweepy" in content, "tweepy not in requirements"
    
    def test_ytdlp_in_requirements(self):
        """Verify yt-dlp is listed"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "yt-dlp" in content, "yt-dlp not in requirements"


# Test execution
if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
