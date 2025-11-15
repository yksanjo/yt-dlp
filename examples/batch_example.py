"""Example: Batch download with queue management."""

import asyncio
from yt_dlp_plus.batch import BatchProcessor, Priority


async def main():
    """Download multiple videos in batch."""
    processor = BatchProcessor(max_concurrent=2)
    
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
    ]
    
    print(f"Processing {len(urls)} URLs...")
    
    results = await processor.process_urls(
        urls=urls,
        priority=Priority.NORMAL,
        options={"format": "best"},
    )
    
    print("\nResults:")
    for i, result in enumerate(results, 1):
        if "error" in result:
            print(f"{i}. Error: {result['error']}")
        else:
            print(f"{i}. Downloaded: {result.get('filename', 'Unknown')}")


if __name__ == "__main__":
    asyncio.run(main())

