"""FastAPI server for yt-dlp-plus."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yt_dlp_plus.api.routes import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="yt-dlp-plus API",
        description="REST API for yt-dlp with async support and batch processing",
        version="0.1.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/api", tags=["download"])

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "yt-dlp-plus API",
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server()

