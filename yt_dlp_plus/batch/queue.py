"""Download queue management."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Priority(Enum):
    """Download priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class QueueItem:
    """Item in the download queue."""

    url: str
    priority: Priority = Priority.NORMAL
    options: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def __lt__(self, other):
        """Compare by priority (higher priority first)."""
        if not isinstance(other, QueueItem):
            return NotImplemented
        return self.priority.value < other.priority.value


class DownloadQueue:
    """Thread-safe download queue with priority support."""

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize download queue.

        Args:
            max_concurrent: Maximum number of concurrent downloads
        """
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active: Dict[str, QueueItem] = {}
        self._completed: Dict[str, QueueItem] = {}
        self._failed: Dict[str, QueueItem] = {}
        self._lock = asyncio.Lock()
        self._max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def add(
        self,
        url: str,
        priority: Priority = Priority.NORMAL,
        options: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> QueueItem:
        """
        Add a URL to the queue.

        Args:
            url: URL to download
            priority: Download priority
            options: Additional download options
            max_retries: Maximum number of retries

        Returns:
            QueueItem that was added
        """
        item = QueueItem(
            url=url,
            priority=priority,
            options=options or {},
            max_retries=max_retries,
        )
        # Use negative priority for max-heap behavior (higher priority first)
        await self._queue.put((priority.value, item))
        return item

    async def get(self) -> Optional[QueueItem]:
        """Get next item from queue."""
        try:
            _, item = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            return item
        except asyncio.TimeoutError:
            return None

    async def mark_active(self, item: QueueItem):
        """Mark an item as active."""
        async with self._lock:
            item.started_at = datetime.now()
            self._active[item.url] = item

    async def mark_completed(self, item: QueueItem, result: Dict[str, Any]):
        """Mark an item as completed."""
        async with self._lock:
            item.completed_at = datetime.now()
            item.result = result
            if item.url in self._active:
                del self._active[item.url]
            self._completed[item.url] = item

    async def mark_failed(self, item: QueueItem, error: str):
        """Mark an item as failed."""
        async with self._lock:
            item.error = error
            item.retry_count += 1
            if item.url in self._active:
                del self._active[item.url]

            if item.retry_count < item.max_retries:
                # Retry with lower priority
                item.priority = Priority(max(item.priority.value - 1, 1))
                await self._queue.put((item.priority.value, item))
            else:
                self._failed[item.url] = item

    async def get_status(self) -> Dict[str, Any]:
        """Get queue status."""
        async with self._lock:
            return {
                "queue_size": self._queue.qsize(),
                "active": len(self._active),
                "completed": len(self._completed),
                "failed": len(self._failed),
                "max_concurrent": self._max_concurrent,
            }

    async def get_active(self) -> Dict[str, QueueItem]:
        """Get all active items."""
        async with self._lock:
            return self._active.copy()

    async def get_completed(self) -> Dict[str, QueueItem]:
        """Get all completed items."""
        async with self._lock:
            return self._completed.copy()

    async def get_failed(self) -> Dict[str, QueueItem]:
        """Get all failed items."""
        async with self._lock:
            return self._failed.copy()

    async def acquire_slot(self):
        """Acquire a download slot."""
        await self._semaphore.acquire()

    def release_slot(self):
        """Release a download slot."""
        self._semaphore.release()

