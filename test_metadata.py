#!/usr/bin/env python3
"""
Test: Check downloader module metadata
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Checking Downloader Classes Metadata")
print("=" * 70)

# Import base
from modules.base import BaseDownloader

# Check YouTube
try:
    from modules.youtube import YouTubeDownloader
    print(f"\n✅ YouTubeDownloader:")
    print(f"   NAME: {YouTubeDownloader.NAME}")
    print(f"   PRIORITY: {YouTubeDownloader.PRIORITY}")
    print(f"   ICON: {YouTubeDownloader.ICON}")
    print(f"   ENABLED: {YouTubeDownloader.ENABLED}")
except Exception as e:
    print(f"\n❌ YouTubeDownloader: {e}")

# Check Instagram
try:
    from modules.instagram import InstagramDownloader
    print(f"\n✅ InstagramDownloader:")
    print(f"   NAME: {InstagramDownloader.NAME}")
    print(f"   PRIORITY: {InstagramDownloader.PRIORITY}")
    print(f"   ICON: {InstagramDownloader.ICON}")
    print(f"   ENABLED: {InstagramDownloader.ENABLED}")
except Exception as e:
    print(f"\n❌ InstagramDownloader: {e}")

# Check Twitter
try:
    from modules.twitter import TwitterDownloader
    print(f"\n✅ TwitterDownloader:")
    print(f"   NAME: {TwitterDownloader.NAME}")
    print(f"   PRIORITY: {TwitterDownloader.PRIORITY}")
    print(f"   ICON: {TwitterDownloader.ICON}")
    print(f"   ENABLED: {TwitterDownloader.ENABLED}")
except Exception as e:
    print(f"\n❌ TwitterDownloader: {e}")

# Check DirectLink
try:
    from modules.direct_link import DirectLinkDownloader
    print(f"\n✅ DirectLinkDownloader:")
    print(f"   NAME: {DirectLinkDownloader.NAME}")
    print(f"   PRIORITY: {DirectLinkDownloader.PRIORITY}")
    print(f"   ICON: {DirectLinkDownloader.ICON}")
    print(f"   ENABLED: {DirectLinkDownloader.ENABLED}")
except Exception as e:
    print(f"\n❌ DirectLinkDownloader: {e}")

print("\n" + "=" * 70)
print("Priority Order (highest to lowest):")
print("=" * 70)

modules = []
try:
    from modules.youtube import YouTubeDownloader
    modules.append(("YouTube", YouTubeDownloader))
except: pass

try:
    from modules.instagram import InstagramDownloader
    modules.append(("Instagram", InstagramDownloader))
except: pass

try:
    from modules.twitter import TwitterDownloader
    modules.append(("Twitter", TwitterDownloader))
except: pass

try:
    from modules.direct_link import DirectLinkDownloader
    modules.append(("DirectLink", DirectLinkDownloader))
except: pass

# Sort by priority
modules_sorted = sorted(modules, key=lambda x: x[1].PRIORITY, reverse=True)

for i, (name, cls) in enumerate(modules_sorted, 1):
    print(f"{i}. {cls.NAME:<20} (priority={cls.PRIORITY})")

print("\nDone!")
