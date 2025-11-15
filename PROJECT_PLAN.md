# yt-dlp-plus Project Plan

## Overview
Enhanced fork of yt-dlp with async support, REST API, batch processing, and integration with pydub-plus for modern content creator workflows.

## Key Enhancements

### 1. Async Support Wrapper ⚡
- Async wrapper around yt-dlp using aiohttp
- Non-blocking downloads
- Concurrent batch processing
- Progress tracking with async callbacks

### 2. REST API (FastAPI) 🌐
- FastAPI-based REST API server
- Download endpoints
- Batch processing endpoints
- Progress tracking via WebSocket
- Metadata extraction endpoints

### 3. Batch Processing 📦
- Queue management
- Progress tracking
- Retry logic
- Rate limiting
- Priority queues

### 4. Integration with pydub-plus 🎵
- Auto-extract audio after download
- Audio processing workflows
- Format conversion helpers

### 5. Enhanced CLI Tools 🛠️
- Better progress display
- Batch operations
- Queue management commands

## Project Structure

```
yt-dlp-plus/
├── yt_dlp/                    # Original yt-dlp code (preserved)
├── yt_dlp_plus/               # New enhancements
│   ├── __init__.py
│   ├── async_ops/             # Async wrapper
│   │   ├── __init__.py
│   │   ├── async_downloader.py
│   │   └── progress.py
│   ├── api/                   # REST API
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── batch/                 # Batch processing
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   └── queue.py
│   ├── integrations/          # Integrations
│   │   ├── __init__.py
│   │   └── pydub_plus.py
│   └── cli/                   # Enhanced CLI
│       ├── __init__.py
│       └── commands.py
├── examples/                  # Example scripts
├── tests/                     # Tests for new features
├── README.md                  # Updated README
└── pyproject.toml             # Updated dependencies
```

## Implementation Phases

### Phase 1: Async Support (Week 1)
- [x] Create async wrapper structure
- [ ] Implement async downloader
- [ ] Add progress tracking
- [ ] Write tests

### Phase 2: REST API (Week 2)
- [ ] Set up FastAPI server
- [ ] Create download endpoints
- [ ] Add batch processing endpoints
- [ ] WebSocket progress updates
- [ ] API documentation

### Phase 3: Batch Processing (Week 2-3)
- [ ] Queue management system
- [ ] Progress tracking
- [ ] Retry logic
- [ ] Rate limiting

### Phase 4: Integrations (Week 3)
- [ ] pydub-plus integration
- [ ] Audio extraction helpers
- [ ] Workflow examples

### Phase 5: Enhanced CLI (Week 3-4)
- [ ] Better progress display
- [ ] Batch commands
- [ ] Queue management

## Dependencies

### New Dependencies
- `fastapi>=0.104.0` - REST API framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `aiohttp>=3.9.0` - Async HTTP client
- `aiofiles>=23.2.0` - Async file operations
- `websockets>=12.0` - WebSocket support
- `pydantic>=2.0.0` - Data validation

### Optional
- `pydub-plus` - Audio processing integration

## Backward Compatibility

- ✅ All original yt-dlp functionality preserved
- ✅ Original CLI remains unchanged
- ✅ New features are opt-in via new modules
- ✅ Can be used as drop-in replacement

## Usage Examples

### Async Usage
```python
from yt_dlp_plus.async_ops import AsyncDownloader

async def download():
    downloader = AsyncDownloader()
    result = await downloader.download("https://youtube.com/watch?v=...")
    print(f"Downloaded: {result['filename']}")
```

### REST API
```bash
# Start API server
yt-dlp-plus-api --port 8000

# Download via API
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

### Batch Processing
```python
from yt_dlp_plus.batch import BatchProcessor

processor = BatchProcessor()
await processor.process_urls([
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=...",
])
```

## Goals

1. **Maintain Compatibility**: Don't break existing yt-dlp usage
2. **Modern Features**: Add async, API, and batch processing
3. **Easy Integration**: Simple APIs for common use cases
4. **Well Documented**: Clear examples and documentation
5. **Community Value**: Useful enhancements for content creators

