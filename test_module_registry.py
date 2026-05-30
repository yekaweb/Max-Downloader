#!/usr/bin/env python3
"""
Test script for ModuleRegistry - PHASE 2 Item 2.1 Verification
Tests priority-based module selection and discovery
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_discovery():
    """Test that all modules are discovered correctly"""
    print("=" * 70)
    print("TEST 1: Module Discovery")
    print("=" * 70)
    
    from modules import discover_modules
    
    modules = discover_modules()
    
    if not modules:
        print("❌ FAILED: No modules discovered")
        return False
    
    print(f"✅ PASSED: Discovered {len(modules)} modules")
    print("\nDiscovered modules:")
    for i, (priority, cls) in enumerate(sorted(modules, reverse=True), 1):
        print(f"  {i}. {cls.NAME} (priority={priority}, icon={cls.ICON})")
    
    return True

def test_priority_ordering():
    """Test that modules are ordered by priority"""
    print("\n" + "=" * 70)
    print("TEST 2: Priority Ordering")
    print("=" * 70)
    
    from modules import discover_modules
    
    modules = discover_modules()
    sorted_modules = sorted(modules, key=lambda x: x[0], reverse=True)
    
    print("Modules in priority order (highest to lowest):")
    for i, (priority, cls) in enumerate(sorted_modules, 1):
        print(f"  {i}. {cls.NAME:<20} priority={priority:>3}")
    
    # Verify YouTube has highest priority
    if sorted_modules[0][0] == 100:
        print(f"\n✅ PASSED: YouTube has highest priority (100)")
        return True
    else:
        print(f"\n❌ FAILED: YouTube priority is {sorted_modules[0][0]}, expected 100")
        return False

def test_can_handle_urls():
    """Test URL detection for each module"""
    print("\n" + "=" * 70)
    print("TEST 3: URL Detection")
    print("=" * 70)
    
    from modules import get_downloader, discover_modules
    
    test_urls = {
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "YouTube",
        "https://www.instagram.com/p/ABC123/": "Instagram",
        "https://twitter.com/user/status/123": "Twitter",
        "https://example.com/file.mp4": "Direct Link",
    }
    
    all_passed = True
    for url, expected_module in test_urls.items():
        downloader = get_downloader(url)
        if downloader and downloader.__class__.NAME == expected_module:
            print(f"✅ {url[:40]:<40} → {expected_module}")
        else:
            actual = downloader.__class__.NAME if downloader else "None"
            print(f"❌ {url[:40]:<40} → Expected: {expected_module}, Got: {actual}")
            all_passed = False
    
    return all_passed

def test_get_downloader_by_priority():
    """Test priority-based downloader selection"""
    print("\n" + "=" * 70)
    print("TEST 4: get_downloader_by_priority()")
    print("=" * 70)
    
    from modules import get_downloader_by_priority
    
    # Test with YouTube URL - should return YouTubeDownloader
    yt_downloader = get_downloader_by_priority("https://www.youtube.com/watch?v=test")
    if yt_downloader and yt_downloader.__class__.NAME == "YouTube":
        print(f"✅ YouTube URL prioritized correctly: {yt_downloader.__class__.NAME}")
        return True
    else:
        print(f"❌ YouTube URL not prioritized correctly")
        return False

def test_metadata_attributes():
    """Test that all modules have required metadata"""
    print("\n" + "=" * 70)
    print("TEST 5: Module Metadata")
    print("=" * 70)
    
    from modules import discover_modules
    
    modules = discover_modules()
    required_attrs = ['NAME', 'ICON', 'PRIORITY', 'VERSION', 'ENABLED']
    all_passed = True
    
    for priority, cls in sorted(modules, key=lambda x: x[0], reverse=True):
        missing = [attr for attr in required_attrs if not hasattr(cls, attr)]
        if missing:
            print(f"❌ {cls.__name__}: Missing {missing}")
            all_passed = False
        else:
            print(f"✅ {cls.NAME:<20} - All metadata present")
    
    return all_passed

def test_fallback_behavior():
    """Test fallback to DirectLinkDownloader for unknown URLs"""
    print("\n" + "=" * 70)
    print("TEST 6: Fallback Behavior")
    print("=" * 70)
    
    from modules import get_downloader_by_priority
    
    unknown_url = "https://example.com/video.mp4"
    downloader = get_downloader_by_priority(unknown_url)
    
    if downloader and downloader.__class__.NAME == "Direct Link":
        print(f"✅ Unknown URL correctly delegated to Direct Link downloader")
        return True
    else:
        actual = downloader.__class__.NAME if downloader else "None"
        print(f"❌ Unknown URL not delegated correctly. Got: {actual}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("█" * 70)
    print("█  PHASE 2 - ITEM 2.1: ModuleRegistry Test Suite")
    print("█" * 70)
    
    tests = [
        test_module_discovery,
        test_priority_ordering,
        test_can_handle_urls,
        test_get_downloader_by_priority,
        test_metadata_attributes,
        test_fallback_behavior,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - ModuleRegistry implementation is correct!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Please review the output above")
        return 1

if __name__ == "__main__":
    exit(main())
