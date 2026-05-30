#!/usr/bin/env python3
"""
Simple test for ModuleRegistry discovery
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("=" * 70)
    print("Testing Module Discovery")
    print("=" * 70)
    
    from modules import discover_modules, get_downloader_by_priority
    
    # Test discovery
    print("\n1. Discovering modules...")
    modules = discover_modules()
    
    if modules:
        print(f"✅ Successfully discovered {len(modules)} modules:\n")
        for i, (priority, cls) in enumerate(modules, 1):
            print(f"   {i}. {cls.NAME:<20} | Priority: {priority:>3} | Icon: {cls.ICON}")
    else:
        print("❌ No modules discovered!")
        sys.exit(1)
    
    # Test URL handling
    print("\n2. Testing URL detection:\n")
    
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YouTube"),
        ("https://www.instagram.com/p/ABC123/", "Instagram"),
        ("https://twitter.com/user/status/123", "Twitter"),
        ("https://example.com/file.mp4", "Direct Link"),
    ]
    
    passed = 0
    for url, expected in test_cases:
        downloader = get_downloader_by_priority(url)
        if downloader:
            actual = downloader.__class__.NAME
            if actual == expected:
                print(f"   ✅ {url[:40]:<40} → {actual}")
                passed += 1
            else:
                print(f"   ❌ {url[:40]:<40} → Expected: {expected}, Got: {actual}")
        else:
            print(f"   ❌ {url[:40]:<40} → None (expected: {expected})")
    
    print(f"\n3. Results: {passed}/{len(test_cases)} tests passed")
    
    if passed == len(test_cases):
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {len(test_cases) - passed} tests failed")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
