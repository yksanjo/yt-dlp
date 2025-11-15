"""REST API for yt-dlp-plus."""

try:
    from yt_dlp_plus.api.server import create_app, run_server
    __all__ = ["create_app", "run_server"]
except ImportError as e:
    # API dependencies not installed
    def create_app():
        raise ImportError("API dependencies not installed. Install with: pip install yt-dlp-plus[api]")
    
    def run_server(*args, **kwargs):
        raise ImportError("API dependencies not installed. Install with: pip install yt-dlp-plus[api]")
    
    __all__ = ["create_app", "run_server"]

