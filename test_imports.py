#!/usr/bin/env python3
"""Test script to check for import errors"""

try:
    print("Testing imports...")
    print("1. Importing database models...")
    from database.models import User, Download
    print("   ✓ Database models OK")
    
    print("2. Importing repositories...")
    from database.repositories import UserRepository
    print("   ✓ Repositories OK")
    
    print("3. Importing services...")
    from services.cache_service import get_redis
    print("   ✓ Cache service OK")
    
    print("4. Importing parallel download...")
    from services.parallel_download_service import ParallelDownloadManager
    print("   ✓ Parallel download OK")
    
    print("5. Importing compression service...")
    from services.compression_service import CompressionService
    print("   ✓ Compression service OK")
    
    print("6. Importing queue service...")
    from services.queue_service import UnifiedDownloadOrchestrator
    print("   ✓ Queue service OK")
    
    print("7. Importing stream upload...")
    from services.stream_upload_service import StreamUploadService
    print("   ✓ Stream upload OK")
    
    print("8. Importing phases integration...")
    from services.phases_integration import get_phases_manager
    print("   ✓ Phases integration OK")
    
    print("9. Importing bot loader...")
    from bot.loader_professional_enhanced import start_download
    print("   ✓ Bot loader OK")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
