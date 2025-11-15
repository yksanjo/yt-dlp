"""
yt-dlp-plus: Enhanced yt-dlp with async support, REST API, and batch processing.

This package extends yt-dlp with modern features while maintaining full backward compatibility.
"""

__version__ = "0.1.0"
__author__ = "yksanjo"

# Import original yt-dlp for backward compatibility
from yt_dlp import *  # noqa: F403, F401

# Export new features
from yt_dlp_plus.async_ops import AsyncDownloader  # noqa: F401
from yt_dlp_plus.batch import BatchProcessor  # noqa: F401

__all__ = [
    "AsyncDownloader",
    "BatchProcessor",
]

