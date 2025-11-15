"""CLI commands for yt-dlp-plus."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import typer

from yt_dlp_plus.async_ops import AsyncDownloader
from yt_dlp_plus.batch import BatchProcessor, Priority
from yt_dlp_plus.api.server import run_server

app = typer.Typer(name="yt-dlp-plus", help="Enhanced yt-dlp with async and API support")


@app.command()
def download(
    url: str = typer.Argument(..., help="URL to download"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Format"),
    extract_audio: bool = typer.Option(False, "--extract-audio", "-x", help="Extract audio"),
    audio_format: str = typer.Option("mp3", "--audio-format", help="Audio format"),
):
    """Download a single URL asynchronously."""
    async def _download():
        downloader = AsyncDownloader()
        options = {}
        
        if output:
            options["outtmpl"] = str(output)
        if format:
            options["format"] = format
        if extract_audio:
            options["format"] = "bestaudio/best"
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
            }]
        
        result = await downloader.download(url, **options)
        
        if "error" in result:
            typer.echo(f"Error: {result['error']}", err=True)
            sys.exit(1)
        
        typer.echo(f"Downloaded: {result.get('filename', 'Unknown')}")
    
    asyncio.run(_download())


@app.command()
def batch(
    urls: List[str] = typer.Argument(..., help="URLs to download"),
    max_concurrent: int = typer.Option(3, "--max-concurrent", "-j", help="Max concurrent downloads"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
):
    """Download multiple URLs in batch."""
    async def _batch():
        processor = BatchProcessor(max_concurrent=max_concurrent)
        
        options = {}
        if output_dir:
            options["outtmpl"] = str(output_dir / "%(title)s.%(ext)s")
        
        results = await processor.process_urls(urls, options=options)
        
        for result in results:
            if "error" in result:
                typer.echo(f"Error for {result['url']}: {result['error']}", err=True)
            else:
                typer.echo(f"Downloaded: {result.get('filename', 'Unknown')}")
    
    asyncio.run(_batch())


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
):
    """Start the REST API server."""
    run_server(host=host, port=port, reload=reload)


@app.command()
def info(
    url: str = typer.Argument(..., help="URL to get info for"),
):
    """Get information about a URL without downloading."""
    async def _info():
        downloader = AsyncDownloader()
        info = await downloader.extract_info(url)
        
        typer.echo(f"Title: {info.get('title', 'Unknown')}")
        typer.echo(f"Duration: {info.get('duration', 'Unknown')} seconds")
        typer.echo(f"Uploader: {info.get('uploader', 'Unknown')}")
        typer.echo(f"View count: {info.get('view_count', 'Unknown')}")
    
    asyncio.run(_info())


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()

