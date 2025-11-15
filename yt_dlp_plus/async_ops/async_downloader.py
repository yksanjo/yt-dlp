"""Async wrapper for yt-dlp downloads."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from yt_dlp_plus.async_ops.progress import ProgressTracker, ProgressCallback


class AsyncDownloader:
    """Async wrapper for yt-dlp downloads."""

    def __init__(
        self,
        ydl_opts: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """
        Initialize async downloader.

        Args:
            ydl_opts: Options to pass to YoutubeDL
            progress_callback: Optional callback for progress updates
        """
        self.ydl_opts = ydl_opts or {}
        self.progress_tracker = ProgressTracker()
        if progress_callback:
            self.progress_tracker.add_callback(progress_callback)

    async def download(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Download a video/audio asynchronously.

        Args:
            url: URL to download
            **kwargs: Additional options to merge with ydl_opts

        Returns:
            Dictionary with download information
        """
        return await self.download_multiple([url], **kwargs)[0]

    async def download_multiple(
        self, urls: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Download multiple URLs concurrently.

        Args:
            urls: List of URLs to download
            **kwargs: Additional options to merge with ydl_opts

        Returns:
            List of dictionaries with download information
        """
        tasks = [self._download_single(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def extract_info(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Extract information about a URL without downloading.

        Args:
            url: URL to extract info from
            **kwargs: Additional options to merge with ydl_opts

        Returns:
            Dictionary with video/audio information
        """
        opts = {**self.ydl_opts, **kwargs}
        opts["quiet"] = True
        opts["no_warnings"] = True

        def _extract():
            with YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract)

    async def _download_single(
        self, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Download a single URL."""
        opts = {**self.ydl_opts, **kwargs}

        # Add progress hook
        original_hook = opts.get("progress_hooks", [])

        def progress_hook(d: Dict[str, Any]):
            """Progress hook for async updates (sync wrapper)."""
            status = d.get("status", "downloading")
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            speed = d.get("speed")
            eta = d.get("eta")

            # Schedule async update
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    self.progress_tracker.update(
                        url=url,
                        status=status,
                        downloaded_bytes=downloaded,
                        total_bytes=total,
                        speed=speed,
                        eta=eta,
                        filename=d.get("filename"),
                        error=d.get("error"),
                    )
                )
            else:
                loop.run_until_complete(
                    self.progress_tracker.update(
                        url=url,
                        status=status,
                        downloaded_bytes=downloaded,
                        total_bytes=total,
                        speed=speed,
                        eta=eta,
                        filename=d.get("filename"),
                        error=d.get("error"),
                    )
                )

            # Call original hooks
            for hook in original_hook:
                hook(d)

        opts["progress_hooks"] = [progress_hook]

        def _download():
            result = None
            error = None
            try:
                # Update status (sync call, will be handled by progress hook)
                with YoutubeDL(opts) as ydl:
                    ydl.download([url])
                    # Get info to return
                    info = ydl.extract_info(url, download=False)
                    result = {
                        "url": url,
                        "title": info.get("title"),
                        "id": info.get("id"),
                        "extractor": info.get("extractor"),
                        "duration": info.get("duration"),
                        "filename": ydl.prepare_filename(info),
                    }
            except DownloadError as e:
                error = str(e)
            except Exception as e:
                error = str(e)

            if error:
                # Schedule error update
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(
                        self.progress_tracker.update(
                            url=url, status="error", error=error
                        )
                    )
                else:
                    loop.run_until_complete(
                        self.progress_tracker.update(
                            url=url, status="error", error=error
                        )
                    )
                return {"url": url, "error": error}
            return result

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)

    async def get_progress(self, url: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a URL."""
        progress = await self.progress_tracker.get_progress(url)
        return progress.to_dict() if progress else None

    async def get_all_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get all progress information."""
        all_progress = await self.progress_tracker.get_all_progress()
        return {url: prog.to_dict() for url, prog in all_progress.items()}

