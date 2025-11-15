"""API routes for yt-dlp-plus."""

import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from yt_dlp_plus.api.models import (
    DownloadRequest,
    DownloadResponse,
    BatchDownloadRequest,
    BatchDownloadResponse,
    ProgressResponse,
    QueueStatusResponse,
    InfoRequest,
    InfoResponse,
)
from yt_dlp_plus.async_ops import AsyncDownloader
from yt_dlp_plus.batch import BatchProcessor, Priority

router = APIRouter()

# Global instances
_downloader: AsyncDownloader = None
_batch_processor: BatchProcessor = None
_active_jobs: Dict[str, BatchProcessor] = {}


def get_downloader() -> AsyncDownloader:
    """Get or create global downloader instance."""
    global _downloader
    if _downloader is None:
        _downloader = AsyncDownloader()
    return _downloader


def get_batch_processor(job_id: Optional[str] = None) -> BatchProcessor:
    """Get or create batch processor instance."""
    global _batch_processor
    if job_id and job_id in _active_jobs:
        return _active_jobs[job_id]
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor


@router.post("/download", response_model=DownloadResponse)
async def download(request: DownloadRequest):
    """Download a single URL."""
    try:
        downloader = get_downloader()
        options = request.options.copy()

        # Handle audio extraction
        if request.extract_audio:
            options["format"] = "bestaudio/best"
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": request.audio_format,
                }
            ]

        result = await downloader.download(str(request.url), **options)

        if "error" in result:
            return DownloadResponse(
                url=str(request.url), status="error", error=result["error"]
            )

        return DownloadResponse(
            url=str(request.url),
            status="completed",
            filename=result.get("filename"),
            title=result.get("title"),
            duration=result.get("duration"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchDownloadResponse)
async def batch_download(request: BatchDownloadRequest):
    """Start a batch download job."""
    try:
        job_id = str(uuid.uuid4())
        processor = BatchProcessor(max_concurrent=request.max_concurrent)

        # Add all URLs to queue
        for url in request.urls:
            options = request.options.copy()
            if request.extract_audio:
                options["format"] = "bestaudio/best"
                options["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": request.audio_format,
                    }
                ]
            await processor.add_url(
                url=str(url), priority=Priority.NORMAL, options=options
            )

        # Start processing
        await processor.start()
        _active_jobs[job_id] = processor

        return BatchDownloadResponse(
            job_id=job_id,
            total=len(request.urls),
            queued=len(request.urls),
            status="queued",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/{job_id}/status", response_model=QueueStatusResponse)
async def get_batch_status(job_id: str):
    """Get status of a batch download job."""
    if job_id not in _active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    processor = _active_jobs[job_id]
    status = await processor.get_status()

    return QueueStatusResponse(
        queue_size=status["queue_size"],
        active=status["active"],
        completed=status["completed"],
        failed=status["failed"],
        max_concurrent=status["max_concurrent"],
    )


@router.get("/progress/{url:path}", response_model=ProgressResponse)
async def get_progress(url: str):
    """Get progress for a specific URL."""
    try:
        downloader = get_downloader()
        progress = await downloader.get_progress(url)

        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")

        return ProgressResponse(**progress)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress", response_model=Dict[str, ProgressResponse])
async def get_all_progress():
    """Get progress for all active downloads."""
    try:
        downloader = get_downloader()
        all_progress = await downloader.get_all_progress()

        return {
            url: ProgressResponse(**prog)
            for url, prog in all_progress.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/info", response_model=InfoResponse)
async def get_info(request: InfoRequest):
    """Extract information about a URL without downloading."""
    try:
        downloader = get_downloader()
        info = await downloader.extract_info(str(request.url), **request.options)

        if not info:
            return InfoResponse(url=str(request.url), error="No info available")

        return InfoResponse(
            url=str(request.url),
            title=info.get("title"),
            id=info.get("id"),
            duration=info.get("duration"),
            uploader=info.get("uploader"),
            view_count=info.get("view_count"),
            formats=info.get("formats"),
        )
    except Exception as e:
        return InfoResponse(url=str(request.url), error=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

