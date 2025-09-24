"""Railway yt-dlp API client for video downloads."""

import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
from loguru import logger

from config import Config


class RailwayDownloadError(Exception):
    """Custom exception for Railway download failures."""
    pass


class RailwayClient:
    """Async client for Railway yt-dlp API service."""
    
    def __init__(self):
        if not Config.RAILWAY_API_URL:
            raise RailwayDownloadError("RAILWAY_API_URL is not configured")
        
        self.base_url = Config.RAILWAY_API_URL.rstrip('/')
        self.api_key = Config.RAILWAY_API_KEY  # Can be empty/None
        self.timeout = Config.RAILWAY_DOWNLOAD_TIMEOUT
        
        # Headers - only add Authorization if API key is provided
        self.headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key.strip():
            self.headers["Authorization"] = f"Bearer {self.api_key.strip()}"
    
    async def download_video(self, url: str) -> Dict[str, Any]:
        """
        Download video from URL via Railway API.
        
        Args:
            url: TikTok or Instagram video URL
            
        Returns:
            Dict containing video metadata and download info
            
        Raises:
            RailwayDownloadError: If download fails
        """
        try:
            # Start download request
            download_data = await self._start_download(url)
            request_id = download_data.get("request_id")
            
            if not request_id:
                raise RailwayDownloadError("No request ID received from Railway API")
            
            # Poll for completion
            result = await self._poll_download_status(request_id)
            
            if not result.get("file_url"):
                raise RailwayDownloadError("No file URL in completed download")
                
            return result
            
        except httpx.RequestError as e:
            logger.error(f"Railway API request error: {e}")
            raise RailwayDownloadError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Railway download error: {e}")
            raise RailwayDownloadError(f"Download failed: {e}")
    
    async def _start_download(self, url: str) -> Dict[str, Any]:
        """Start download request and return request ID."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/download",
                headers=self.headers,
                json={
                    "url": url,
                    "format": "best[height<=720]",  # Optimize for analysis
                    "extract_flat": False
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def _poll_download_status(self, request_id: str, max_attempts: int = 60) -> Dict[str, Any]:
        """
        Poll download status until completion.
        
        Args:
            request_id: Download request ID
            max_attempts: Maximum polling attempts (5min timeout)
            
        Returns:
            Completed download result
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/downloads/{request_id}",
                        headers=self.headers
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    status = result.get("status")
                    logger.debug(f"Download status: {status} (attempt {attempt + 1})")
                    
                    if status == "completed":
                        return result
                    elif status == "failed":
                        error = result.get("error", "Unknown error")
                        raise RailwayDownloadError(f"Download failed: {error}")
                    elif status in ["pending", "processing"]:
                        await asyncio.sleep(5)  # Wait 5 seconds between polls
                        continue
                    else:
                        raise RailwayDownloadError(f"Unknown status: {status}")
                        
                except httpx.RequestError as e:
                    logger.warning(f"Polling error (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(5)
                        continue
                    raise RailwayDownloadError(f"Polling failed: {e}")
            
            raise RailwayDownloadError("Download timeout after 5 minutes")
    
    async def download_file(self, file_url: str) -> Path:
        """
        Download the actual video file from URL.
        
        Args:
            file_url: Direct URL to video file
            
        Returns:
            Path to downloaded temporary file
            
        Raises:
            RailwayDownloadError: If file download fails
        """
        try:
            # Create temporary file
            temp_dir = Path(tempfile.gettempdir()) / "knowledge_bot"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            file_path = temp_dir / filename
            
            # Download file
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Downloading video file from {file_url}")
                
                async with client.stream("GET", file_url) as response:
                    response.raise_for_status()
                    
                    with open(file_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            
            logger.success(f"Video downloaded to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"File download error: {e}")
            raise RailwayDownloadError(f"File download failed: {e}")
    
    async def cleanup_temp_file(self, file_path: Path) -> None:
        """Clean up temporary downloaded file."""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")


# Convenience function for external use
async def download_video_from_url(url: str) -> tuple[Dict[str, Any], Path]:
    """
    Download video and return metadata + file path.
    
    Returns:
        Tuple of (metadata_dict, file_path)
    """
    client = RailwayClient()
    
    # Get download info
    download_info = await client.download_video(url)
    
    # Download actual file
    file_path = await client.download_file(download_info["file_url"])
    
    return download_info, file_path