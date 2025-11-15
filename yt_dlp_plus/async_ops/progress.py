"""Progress tracking for async downloads."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from datetime import datetime


@dataclass
class DownloadProgress:
    """Progress information for a download."""

    url: str
    status: str  # 'downloading', 'processing', 'completed', 'error'
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[float] = None
    eta: Optional[int] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def progress_percent(self) -> Optional[float]:
        """Calculate progress percentage."""
        if self.total_bytes and self.total_bytes > 0:
            return (self.downloaded_bytes / self.total_bytes) * 100
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "status": self.status,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "speed": self.speed,
            "eta": self.eta,
            "filename": self.filename,
            "error": self.error,
            "progress_percent": self.progress_percent,
            "timestamp": self.timestamp.isoformat(),
        }


ProgressCallback = Callable[[DownloadProgress], None]


class ProgressTracker:
    """Track progress for multiple downloads."""

    def __init__(self):
        self._progress: Dict[str, DownloadProgress] = {}
        self._callbacks: list[ProgressCallback] = []
        self._lock = asyncio.Lock()

    async def update(
        self,
        url: str,
        status: str,
        downloaded_bytes: int = 0,
        total_bytes: Optional[int] = None,
        speed: Optional[float] = None,
        eta: Optional[int] = None,
        filename: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """Update progress for a URL."""
        async with self._lock:
            progress = DownloadProgress(
                url=url,
                status=status,
                downloaded_bytes=downloaded_bytes,
                total_bytes=total_bytes,
                speed=speed,
                eta=eta,
                filename=filename,
                error=error,
            )
            self._progress[url] = progress

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(progress)
                    else:
                        callback(progress)
                except Exception as e:
                    print(f"Error in progress callback: {e}")

    def add_callback(self, callback: ProgressCallback):
        """Add a progress callback."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: ProgressCallback):
        """Remove a progress callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def get_progress(self, url: str) -> Optional[DownloadProgress]:
        """Get current progress for a URL."""
        async with self._lock:
            return self._progress.get(url)

    async def get_all_progress(self) -> Dict[str, DownloadProgress]:
        """Get all progress information."""
        async with self._lock:
            return self._progress.copy()

