"""Pydantic models for API requests and responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class DownloadRequest(BaseModel):
    """Request to download a URL."""

    url: HttpUrl
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    extract_audio: bool = False
    audio_format: str = "mp3"


class BatchDownloadRequest(BaseModel):
    """Request to download multiple URLs."""

    urls: List[HttpUrl]
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    max_concurrent: int = Field(default=3, ge=1, le=10)
    extract_audio: bool = False
    audio_format: str = "mp3"


class DownloadResponse(BaseModel):
    """Response from a download request."""

    url: str
    status: str
    filename: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    error: Optional[str] = None


class BatchDownloadResponse(BaseModel):
    """Response from a batch download request."""

    job_id: str
    total: int
    queued: int
    status: str


class ProgressResponse(BaseModel):
    """Progress information for a download."""

    url: str
    status: str
    downloaded_bytes: int
    total_bytes: Optional[int] = None
    progress_percent: Optional[float] = None
    speed: Optional[float] = None
    eta: Optional[int] = None
    filename: Optional[str] = None
    error: Optional[str] = None


class QueueStatusResponse(BaseModel):
    """Queue status information."""

    queue_size: int
    active: int
    completed: int
    failed: int
    max_concurrent: int


class InfoRequest(BaseModel):
    """Request to extract info from a URL."""

    url: HttpUrl
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InfoResponse(BaseModel):
    """Response with video/audio information."""

    url: str
    title: Optional[str] = None
    id: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    view_count: Optional[int] = None
    formats: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

