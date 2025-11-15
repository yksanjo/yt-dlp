# yt-dlp-plus 🚀

> Enhanced yt-dlp with async support, REST API, batch processing, and modern tooling

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](LICENSE)

**yt-dlp-plus** is an enhanced fork of [yt-dlp](https://github.com/yt-dlp/yt-dlp) that adds modern features while maintaining full backward compatibility with the original yt-dlp.

## ✨ New Features

### 1. ⚡ Async Support
- Non-blocking downloads using asyncio
- Concurrent batch processing
- Real-time progress tracking
- Perfect for async applications

### 2. 🌐 REST API
- FastAPI-based REST API server
- Download endpoints
- Batch processing endpoints
- Progress tracking
- Auto-generated API documentation

### 3. 📦 Batch Processing
- Queue management with priority support
- Concurrent downloads with rate limiting
- Automatic retry logic
- Progress tracking for all downloads

### 4. 🛠️ Enhanced CLI
- Modern CLI with typer
- Batch operations
- Progress display
- API server command

## 🚀 Quick Start

### Installation

```bash
# Install with all features
pip install yt-dlp-plus[all]

# Or install specific features
pip install yt-dlp-plus[api]      # REST API
pip install yt-dlp-plus[async]    # Async support
pip install yt-dlp-plus[cli]      # Enhanced CLI
```

### Basic Usage (Same as yt-dlp)

```bash
# All original yt-dlp commands work exactly the same
yt-dlp "https://youtube.com/watch?v=..."
```

### Async Usage

```python
import asyncio
from yt_dlp_plus.async_ops import AsyncDownloader

async def main():
    downloader = AsyncDownloader()
    result = await downloader.download("https://youtube.com/watch?v=...")
    print(f"Downloaded: {result['filename']}")

asyncio.run(main())
```

### REST API

```bash
# Start the API server
yt-dlp-plus-api --port 8000

# Or use the CLI
yt-dlp-plus api --port 8000
```

Then visit `http://localhost:8000/docs` for interactive API documentation.

**Download via API:**
```bash
curl -X POST "http://localhost:8000/api/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=...",
    "extract_audio": true,
    "audio_format": "mp3"
  }'
```

### Batch Processing

```python
import asyncio
from yt_dlp_plus.batch import BatchProcessor, Priority

async def main():
    processor = BatchProcessor(max_concurrent=3)
    
    urls = [
        "https://youtube.com/watch?v=...",
        "https://youtube.com/watch?v=...",
        "https://youtube.com/watch?v=...",
    ]
    
    results = await processor.process_urls(urls, priority=Priority.NORMAL)
    
    for result in results:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Downloaded: {result['filename']}")

asyncio.run(main())
```

### Enhanced CLI

```bash
# Download single URL
yt-dlp-plus download "https://youtube.com/watch?v=..." --extract-audio

# Batch download
yt-dlp-plus batch "url1" "url2" "url3" --max-concurrent 3

# Get info without downloading
yt-dlp-plus info "https://youtube.com/watch?v=..."

# Start API server
yt-dlp-plus api --port 8000
```

## 📚 Documentation

### Async Downloader

```python
from yt_dlp_plus.async_ops import AsyncDownloader, ProgressCallback
from yt_dlp_plus.async_ops.progress import DownloadProgress

async def progress_callback(progress: DownloadProgress):
    print(f"{progress.url}: {progress.progress_percent}%")

downloader = AsyncDownloader(progress_callback=progress_callback)

# Download single URL
result = await downloader.download("https://youtube.com/watch?v=...")

# Download multiple URLs concurrently
results = await downloader.download_multiple([
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=...",
])

# Extract info without downloading
info = await downloader.extract_info("https://youtube.com/watch?v=...")

# Get progress
progress = await downloader.get_progress("https://youtube.com/watch?v=...")
```

### Batch Processor

```python
from yt_dlp_plus.batch import BatchProcessor, Priority

processor = BatchProcessor(
    max_concurrent=3,  # Max concurrent downloads
    ydl_opts={"format": "best"},  # Default options
)

# Process multiple URLs
results = await processor.process_urls(
    urls=["url1", "url2", "url3"],
    priority=Priority.HIGH,
    options={"format": "bestaudio"},
)

# Add single URL to queue
item = await processor.add_url(
    url="https://youtube.com/watch?v=...",
    priority=Priority.URGENT,
)

# Get status
status = await processor.get_status()
print(f"Active: {status['active']}, Completed: {status['completed']}")
```

### REST API Endpoints

- `POST /api/download` - Download a single URL
- `POST /api/batch` - Start a batch download job
- `GET /api/batch/{job_id}/status` - Get batch job status
- `GET /api/progress/{url}` - Get progress for a URL
- `GET /api/progress` - Get all progress
- `POST /api/info` - Extract info without downloading
- `GET /api/health` - Health check

See `/docs` endpoint for full API documentation.

## 🔧 Configuration

All original yt-dlp options are supported. You can pass options to the async downloader or batch processor:

```python
downloader = AsyncDownloader(ydl_opts={
    "format": "bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
    }],
})
```

## 🎯 Use Cases

- **Web Applications**: Use the REST API to integrate downloads into your app
- **Content Creators**: Batch download playlists with progress tracking
- **Async Applications**: Non-blocking downloads in async Python apps
- **Automation**: Queue management and priority-based downloads
- **Backward Compatibility**: Drop-in replacement for yt-dlp

## 🤝 Contributing

Contributions welcome! This project extends yt-dlp while maintaining compatibility.

## 📄 License

Same as yt-dlp - Unlicense

## 🙏 Credits

- Original [yt-dlp](https://github.com/yt-dlp/yt-dlp) by the yt-dlp team
- Enhanced with modern features for async and API workflows

## 🔗 Links

- [Original yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Documentation](https://github.com/yt-dlp/yt-dlp#readme)
- [Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

