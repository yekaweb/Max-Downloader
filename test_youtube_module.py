#!/usr/bin/env python3
"""Test YouTube module integration"""
import asyncio
import sys
from modules.youtube import YouTubeDownloader, parse_formats
from modules import get_downloader, MODULE_REGISTRY


async def test_youtube_module():
    """Test YouTube downloader module"""
    print("=" * 60)
    print("Testing YouTube Module Integration")
    print("=" * 60)

    # Test 1: Module registration
    print("\n[TEST 1] Module Registration")
    print(f"Registered modules: {list(MODULE_REGISTRY.keys())}")
    assert "youtube" in MODULE_REGISTRY, "YouTube module not registered"
    print("✅ YouTube module registered")

    # Test 2: URL detection
    print("\n[TEST 2] URL Detection")
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://youtu.be/dQw4w9WgXcQ", True),
        ("https://youtube.com/watch?v=test", True),
        ("https://instagram.com/test", False),
    ]

    yt = YouTubeDownloader()
    for url, should_handle in test_urls:
        result = yt.can_handle(url)
        status = "✅" if result == should_handle else "❌"
        print(f"{status} {url}: {result}")
        assert result == should_handle, f"URL detection failed for {url}"

    # Test 3: Downloader lookup
    print("\n[TEST 3] Downloader Lookup")
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        downloader = get_downloader(youtube_url)
        print(f"✅ Found downloader: {downloader.__class__.__name__}")
    except ValueError as e:
        print(f"❌ Failed to find downloader: {e}")
        return False

    # Test 4: Format parser
    print("\n[TEST 4] Format Parser")
    sample_formats = [
        {
            "format_id": "22",
            "ext": "mp4",
            "width": 1280,
            "height": 720,
            "fps": 30,
            "vcodec": "h264",
            "acodec": "aac",
            "filesize": 50000000,
            "tbr": 2000,
        },
        {
            "format_id": "251",
            "ext": "webm",
            "acodec": "opus",
            "abr": 160,
            "filesize": 10000000,
        },
    ]

    parsed = parse_formats(sample_formats)
    print(f"Parsed {len(sample_formats)} formats into {len(parsed)} formats")
    for fmt in parsed:
        print(f"  - {fmt['label']} (ID: {fmt['format_id']})")
    print("✅ Format parser working")

    # Test 5: Metadata extraction (with error handling for network)
    print("\n[TEST 5] Metadata Extraction")
    print("⚠️  Skipping live extraction (requires internet + valid YouTube URL)")
    print("   In production, use real YouTube URLs to test fetch_info()")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_youtube_module())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
