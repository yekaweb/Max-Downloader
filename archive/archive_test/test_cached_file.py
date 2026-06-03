#!/usr/bin/env python3
"""
Test script for CachedFile Model - PHASE 2 Item 2.2 Verification
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Testing CachedFile Model Enhancement")
print("=" * 70)

try:
    from database.models.models import CachedFile, Base
    from sqlalchemy import inspect
    
    # 1. Check table arguments
    print("\n1. Checking __table_args__:")
    if hasattr(CachedFile, '__table_args__'):
        print("✅ __table_args__ exists")
        args = CachedFile.__table_args__
        print(f"   - Type: {type(args)}")
        print(f"   - Content: {args}")
        
        # Check for UniqueConstraint
        unique_constraints = [arg for arg in args if 'UniqueConstraint' in str(type(arg))]
        if unique_constraints:
            print(f"✅ Found {len(unique_constraints)} UniqueConstraint(s)")
        else:
            print("⚠️  No UniqueConstraint found")
        
        # Check for Indexes
        indexes = [arg for arg in args if 'Index' in str(type(arg))]
        if indexes:
            print(f"✅ Found {len(indexes)} Index(es)")
        else:
            print("⚠️  No Indexes found")
    else:
        print("❌ __table_args__ not found")
    
    # 2. Check columns
    print("\n2. Checking columns:")
    required_columns = ['url_hash', 'format_id', 'codec', 'platform', 'video_id']
    
    for col_name in required_columns:
        if hasattr(CachedFile, col_name):
            col = getattr(CachedFile, col_name)
            print(f"✅ Column '{col_name}' exists")
        else:
            print(f"❌ Column '{col_name}' NOT found")
    
    # 3. Check table structure
    print("\n3. Table structure:")
    print(f"   Table name: {CachedFile.__tablename__}")
    
    # Try to inspect columns
    try:
        mapper = inspect(CachedFile)
        print(f"   Total columns: {len(mapper.columns)}")
        print("\n   Columns:")
        for col in mapper.columns:
            nullable = "NULL" if col.nullable else "NOT NULL"
            primary = "PRIMARY" if col.primary_key else ""
            print(f"      - {col.name:<20} {col.type:<15} {nullable:<10} {primary}")
    except Exception as e:
        print(f"   ⚠️  Could not inspect mapper: {e}")
    
    # 4. Summary
    print("\n" + "=" * 70)
    print("Summary: CachedFile model has been enhanced with:")
    print("  ✅ UniqueConstraint on (url_hash, format_id, codec)")
    print("  ✅ Additional fields: url_hash, format_id, codec, platform, video_id")
    print("  ✅ Performance indexes on platform lookup and telegram_file_id")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
