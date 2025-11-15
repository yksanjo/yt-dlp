"""Example: Async download with progress tracking."""

import asyncio
from yt_dlp_plus.async_ops import AsyncDownloader
from yt_dlp_plus.async_ops.progress import DownloadProgress


async def progress_callback(progress: DownloadProgress):
    """Print progress updates."""
    if progress.progress_percent:
        print(f"{progress.url}: {progress.progress_percent:.1f}% - {progress.status}")
    else:
        print(f"{progress.url}: {progress.status}")


async def main():
    """Download a video asynchronously."""
    downloader = AsyncDownloader(progress_callback=progress_callback)
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"Downloading {url}...")
    result = await downloader.download(url)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Downloaded: {result.get('filename')}")
        print(f"Title: {result.get('title')}")


if __name__ == "__main__":
    asyncio.run(main())

