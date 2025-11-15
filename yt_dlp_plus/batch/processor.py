"""Batch processor for multiple downloads."""

import asyncio
from typing import Any, Dict, List, Optional

from yt_dlp_plus.async_ops import AsyncDownloader, ProgressCallback
from yt_dlp_plus.batch.queue import DownloadQueue, Priority, QueueItem


class BatchProcessor:
    """Process multiple downloads with queue management."""

    def __init__(
        self,
        max_concurrent: int = 3,
        ydl_opts: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """
        Initialize batch processor.

        Args:
            max_concurrent: Maximum number of concurrent downloads
            ydl_opts: Default options for downloads
            progress_callback: Optional progress callback
        """
        self.queue = DownloadQueue(max_concurrent=max_concurrent)
        self.downloader = AsyncDownloader(
            ydl_opts=ydl_opts, progress_callback=progress_callback
        )
        self._running = False
        self._worker_tasks: List[asyncio.Task] = []

    async def process_urls(
        self,
        urls: List[str],
        priority: Priority = Priority.NORMAL,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process a list of URLs.

        Args:
            urls: List of URLs to download
            priority: Priority for all URLs
            options: Additional options for all downloads

        Returns:
            List of results (one per URL)
        """
        # Add all URLs to queue
        items = []
        for url in urls:
            item = await self.queue.add(
                url=url, priority=priority, options=options
            )
            items.append(item)

        # Start workers if not running
        if not self._running:
            await self.start()

        # Wait for all items to complete
        results = []
        for item in items:
            while True:
                status = await self.queue.get_status()
                if item.url in (await self.queue.get_completed()):
                    completed = await self.queue.get_completed()
                    results.append(completed[item.url].result)
                    break
                elif item.url in (await self.queue.get_failed()):
                    failed = await self.queue.get_failed()
                    results.append(
                        {"url": item.url, "error": failed[item.url].error}
                    )
                    break
                await asyncio.sleep(0.5)

        return results

    async def start(self, num_workers: Optional[int] = None):
        """
        Start worker tasks to process the queue.

        Args:
            num_workers: Number of worker tasks (defaults to max_concurrent)
        """
        if self._running:
            return

        self._running = True
        num_workers = num_workers or self.queue._max_concurrent

        # Start worker tasks
        self._worker_tasks = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(num_workers)
        ]

    async def stop(self):
        """Stop worker tasks."""
        self._running = False
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            self._worker_tasks = []

    async def _worker(self, name: str):
        """Worker task that processes queue items."""
        while self._running:
            try:
                # Get next item from queue
                item = await self.queue.get()
                if item is None:
                    await asyncio.sleep(0.1)
                    continue

                # Acquire download slot
                await self.queue.acquire_slot()
                try:
                    await self.queue.mark_active(item)

                    # Download
                    result = await self.downloader.download(
                        item.url, **item.options
                    )

                    if "error" in result:
                        await self.queue.mark_failed(item, result["error"])
                    else:
                        await self.queue.mark_completed(item, result)
                finally:
                    self.queue.release_slot()

            except Exception as e:
                if item:
                    await self.queue.mark_failed(item, str(e))
                print(f"Worker {name} error: {e}")

            await asyncio.sleep(0.1)

    async def get_status(self) -> Dict[str, Any]:
        """Get processor status."""
        queue_status = await self.queue.get_status()
        return {
            **queue_status,
            "running": self._running,
            "workers": len(self._worker_tasks),
        }

    async def add_url(
        self,
        url: str,
        priority: Priority = Priority.NORMAL,
        options: Optional[Dict[str, Any]] = None,
    ) -> QueueItem:
        """
        Add a single URL to the queue.

        Args:
            url: URL to download
            priority: Download priority
            options: Additional download options

        Returns:
            QueueItem that was added
        """
        if not self._running:
            await self.start()

        return await self.queue.add(
            url=url, priority=priority, options=options
        )

