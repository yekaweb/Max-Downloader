"""
Hash Service for Pro Cache
سرویس تولید hash یکتا برای URL ها
"""

import hashlib
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class PlatformNormalizer(ABC):
    """کلاس abstract برای نرمال‌سازی URL های پلتفرم‌های مختلف"""
    
    @abstractmethod
    def normalize(self, url: str) -> str:
        """نرمال‌سازی URL برای پلتفرم خاص"""
        pass
    
    @abstractmethod
    def extract_id(self, url: str) -> Optional[str]:
        """استخراج ID محتوا از URL"""
        pass


class YouTubeNormalizer(PlatformNormalizer):
    """نرمال‌سازی URL های یوتیوب"""
    
    def normalize(self, url: str) -> str:
        """
        نرمال‌سازی URL یوتیوب
        - تبدیل youtu.be به youtube.com
        - حذف پارامترهای غیرضروری
        - حفظ فقط video ID
        """
        video_id = self.extract_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    def extract_id(self, url: str) -> Optional[str]:
        """استخراج video ID از URL یوتیوب"""
        # Pattern برای انواع URL یوتیوب
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class InstagramNormalizer(PlatformNormalizer):
    """نرمال‌سازی URL های اینستاگرام"""
    
    def normalize(self, url: str) -> str:
        """نرمال‌سازی URL اینستاگرام"""
        # حذف query parameters
        parsed = urlparse(url)
        clean_url = urlunparse(parsed._replace(query='', fragment=''))
        
        # حذف trailing slash
        clean_url = clean_url.rstrip('/')
        
        return clean_url
    
    def extract_id(self, url: str) -> Optional[str]:
        """استخراج post/reel ID از URL اینستاگرام"""
        patterns = [
            r'instagram\.com\/p\/([a-zA-Z0-9_-]+)',
            r'instagram\.com\/reel\/([a-zA-Z0-9_-]+)',
            r'instagram\.com\/reels\/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class TikTokNormalizer(PlatformNormalizer):
    """نرمال‌سازی URL های تیک‌تاک"""
    
    def normalize(self, url: str) -> str:
        """نرمال‌سازی URL تیک‌تاک"""
        video_id = self.extract_id(url)
        if video_id:
            return f"https://www.tiktok.com/@user/video/{video_id}"
        return url
    
    def extract_id(self, url: str) -> Optional[str]:
        """استخراج video ID از URL تیک‌تاک"""
        patterns = [
            r'tiktok\.com\/@[\w.-]+\/video\/(\d+)',
            r'vm\.tiktok\.com\/(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class TwitterNormalizer(PlatformNormalizer):
    """نرمال‌سازی URL های توییتر/X"""
    
    def normalize(self, url: str) -> str:
        """نرمال‌سازی URL توییتر"""
        # تبدیل x.com به twitter.com
        url = url.replace('x.com', 'twitter.com')
        
        tweet_id = self.extract_id(url)
        if tweet_id:
            return f"https://twitter.com/i/status/{tweet_id}"
        return url
    
    def extract_id(self, url: str) -> Optional[str]:
        """استخراج tweet ID از URL توییتر"""
        pattern = r'(?:twitter|x)\.com\/\w+\/status\/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None


class HashService:
    """
    سرویس اصلی تولید hash برای URL ها
    """
    
    def __init__(self):
        self.normalizers: Dict[str, PlatformNormalizer] = {
            'youtube': YouTubeNormalizer(),
            'instagram': InstagramNormalizer(),
            'tiktok': TikTokNormalizer(),
            'twitter': TwitterNormalizer(),
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """تشخیص پلتفرم از روی URL"""
        url_lower = url.lower()
        
        platform_patterns = {
            'youtube': ['youtube.com', 'youtu.be', 'youtube-nocookie.com'],
            'instagram': ['instagram.com', 'instagr.am'],
            'tiktok': ['tiktok.com', 'vm.tiktok.com'],
            'twitter': ['twitter.com', 'x.com'],
        }
        
        for platform, patterns in platform_patterns.items():
            if any(pattern in url_lower for pattern in patterns):
                return platform
        
        return None
    
    def normalize_url(self, url: str) -> str:
        """
        نرمال‌سازی URL بر اساس پلتفرم
        """
        # پاک کردن فضاهای خالی
        url = url.strip()
        
        # اضافه کردن protocol اگر نداشت
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # تشخیص پلتفرم
        platform = self.detect_platform(url)
        
        if platform and platform in self.normalizers:
            return self.normalizers[platform].normalize(url)
        
        # برای URL های غیر پلتفرمی، فقط query parameters را حذف کن
        parsed = urlparse(url)
        return urlunparse(parsed._replace(query='', fragment=''))
    
    def generate_url_hash(self, url: str) -> str:
        """
        تولید hash یکتا برای URL
        
        Args:
            url: آدرس URL ورودی
            
        Returns:
            رشته 64 کاراکتری SHA-256 hash
        """
        # نرمال‌سازی URL
        normalized_url = self.normalize_url(url)
        
        # تولید SHA-256 hash
        hash_object = hashlib.sha256(normalized_url.encode('utf-8'))
        return hash_object.hexdigest()
    
    def get_url_info(self, url: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات کامل URL
        
        Returns:
            دیکشنری شامل:
            - original_url: URL اصلی
            - normalized_url: URL نرمال شده
            - hash: hash تولید شده
            - platform: پلتفرم تشخیص داده شده
            - content_id: ID محتوا (در صورت وجود)
        """
        normalized_url = self.normalize_url(url)
        platform = self.detect_platform(url)
        content_id = None
        
        if platform and platform in self.normalizers:
            content_id = self.normalizers[platform].extract_id(url)
        
        return {
            'original_url': url,
            'normalized_url': normalized_url,
            'hash': self.generate_url_hash(url),
            'platform': platform,
            'content_id': content_id
        }


# تست سرویس
if __name__ == "__main__":
    service = HashService()
    
    # تست URL های مختلف
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.instagram.com/p/CzM_Hs-MCwB/?utm_source=ig_web",
        "https://www.tiktok.com/@user/video/7123456789012345678",
        "https://twitter.com/jack/status/20",
        "https://x.com/jack/status/20",
    ]
    
    for url in test_urls:
        info = service.get_url_info(url)
        print(f"\nURL: {url}")
        print(f"Normalized: {info['normalized_url']}")
        print(f"Hash: {info['hash'][:16]}...")
        print(f"Platform: {info['platform']}")
        print(f"Content ID: {info['content_id']}")