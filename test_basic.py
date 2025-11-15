"""Basic tests for yt-dlp-plus."""

import sys
import asyncio

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from yt_dlp_plus import AsyncDownloader, BatchProcessor
        print("✅ Main imports successful")
        
        from yt_dlp_plus.async_ops import ProgressTracker, DownloadProgress
        print("✅ Async ops imports successful")
        
        from yt_dlp_plus.batch import DownloadQueue, QueueItem, Priority
        print("✅ Batch imports successful")
        
        from yt_dlp_plus.api import create_app
        print("✅ API imports successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_downloader():
    """Test AsyncDownloader basic functionality."""
    print("\nTesting AsyncDownloader...")
    try:
        from yt_dlp_plus.async_ops import AsyncDownloader
        
        downloader = AsyncDownloader()
        print("✅ AsyncDownloader created")
        
        # Test extract_info (doesn't download, just gets info)
        # Using a short, well-known video
        test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video
        
        print(f"Testing extract_info for {test_url}...")
        info = await downloader.extract_info(test_url)
        
        if info and "title" in info:
            print(f"✅ extract_info successful: {info.get('title', 'Unknown')}")
            return True
        else:
            print(f"⚠️ extract_info returned: {info}")
            return False
            
    except Exception as e:
        print(f"❌ AsyncDownloader test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_processor():
    """Test BatchProcessor basic functionality."""
    print("\nTesting BatchProcessor...")
    try:
        from yt_dlp_plus.batch import BatchProcessor, Priority
        
        processor = BatchProcessor(max_concurrent=1)
        print("✅ BatchProcessor created")
        
        status = await processor.get_status()
        print(f"✅ Status check: {status}")
        
        return True
    except Exception as e:
        print(f"❌ BatchProcessor test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api():
    """Test API creation."""
    print("\nTesting API...")
    try:
        from yt_dlp_plus.api import create_app
        
        try:
            app = create_app()
            print("✅ FastAPI app created")
            
            # Check routes
            routes = [route.path for route in app.routes]
            print(f"✅ Routes: {len(routes)} routes registered")
            
            return True
        except ImportError as e:
            if "API dependencies not installed" in str(e) or "uvicorn" in str(e) or "fastapi" in str(e):
                print("⚠️ API dependencies not installed (expected if not installed)")
                print("   Install with: pip install yt-dlp-plus[api]")
                return True  # Not a failure, just optional dependency
            raise
    except ImportError as e:
        if "uvicorn" in str(e) or "fastapi" in str(e):
            print("⚠️ API dependencies not installed (expected if not installed)")
            print("   Install with: pip install yt-dlp-plus[api]")
            return True  # Not a failure, just optional dependency
        raise
    except Exception as e:
        print(f"❌ API test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("yt-dlp-plus Basic Tests")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test async downloader
    results.append(("AsyncDownloader", await test_async_downloader()))
    
    # Test batch processor
    results.append(("BatchProcessor", await test_batch_processor()))
    
    # Test API
    results.append(("API", test_api()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

