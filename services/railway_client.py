"""Railway yt-dlp API client for video downloads."""

import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any

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
    
    async def health_check(self) -> bool:
        """Check if Railway API is responding."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try the healthz endpoint (matches your Railway API)
                response = await client.get(
                    f"{self.base_url}/healthz",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Railway API health check failed: {e}")
            return False
    
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
            # Optional health check (don't fail if this doesn't work)
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("Railway API health check failed, but continuing with download attempt")
            except Exception:
                logger.debug("Health check skipped due to error")
            
            # Start download request
            download_data = await self._start_download(url)
            request_id = download_data.get("request_id")
            
            if not request_id:
                raise RailwayDownloadError("No request ID received from Railway API")
            
            # Poll for completion
            logger.info(f"Starting to poll download status for request_id: {request_id}")
            result = await self._poll_download_status(request_id)
            
            if not result.get("file_url"):
                raise RailwayDownloadError("No file URL in completed download")
                
            logger.success(f"Railway download completed successfully for request_id: {request_id}")
            return result
            
        except httpx.RequestError as e:
            logger.error(f"Railway API request error: {e}")
            raise RailwayDownloadError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Railway download error: {e}")
            raise RailwayDownloadError(f"Download failed: {e}")
    
    async def _start_download(self, url: str) -> Dict[str, Any]:
        """Start download request and return request ID."""
        payload = {
            "url": url,
            "format": "best[height<=720]",  # Optimize for analysis
            "extract_flat": False
        }
        
        logger.info(f"Starting Railway download request for URL: {url}")
        logger.debug(f"Request payload: {payload}")
        logger.debug(f"Request URL: {self.base_url}/download")
        logger.debug(f"Request headers: {dict(self.headers)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/download",
                    headers=self.headers,
                    json=payload
                )
                
                logger.debug(f"Railway API response status: {response.status_code}")
                logger.debug(f"Railway API response headers: {dict(response.headers)}")
                logger.debug(f"Railway API response body: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"Download request started successfully, request_id: {result.get('request_id')}")
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Railway API HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Railway API request error: {e}")
                raise
    
    async def _poll_download_status(self, request_id: str, max_attempts: int = 120) -> Dict[str, Any]:
        """
        Poll download status until completion.
        
        Args:
            request_id: Download request ID
            max_attempts: Maximum polling attempts (10min timeout)
            
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
                    
                    logger.debug(f"Polling response status: {response.status_code}")
                    logger.debug(f"Polling response body: {response.text}")
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    status = result.get("status")
                    progress = result.get("progress", "Unknown")
                    logger.info(f"Download status: {status} | Progress: {progress} | Attempt: {attempt + 1}/{max_attempts}")
                    logger.debug(f"Full polling response: {result}")
                    
                    # Handle your Railway API status values (uppercase)
                    if status == "DONE":
                        logger.success(f"Download completed successfully after {attempt + 1} attempts")
                        return result
                    elif status == "ERROR":
                        # Try to extract detailed error information
                        error_details = []
                        
                        # Check multiple possible error fields
                        for error_field in ["error", "message", "stderr", "error_message", "details"]:
                            if error_field in result and result[error_field]:
                                error_details.append(str(result[error_field]))
                        
                        # If no error details found, use the full response
                        if not error_details:
                            error_details.append(f"No error details provided. Status: {status}")
                        
                        error_message = " | ".join(error_details)
                        logger.error(f"Download failed with status '{status}': {error_message}")
                        logger.debug(f"Full error response: {result}")
                        
                        # Check if this is a URL-related error
                        if any(keyword in error_message.lower() for keyword in ["url", "not found", "private", "unavailable"]):
                            raise RailwayDownloadError(f"Video URL error: {error_message}")
                        else:
                            raise RailwayDownloadError(f"Download service error: {error_message}")
                    elif status in ["QUEUED", "RUNNING"]:
                        logger.debug(f"Download in progress ({status}), waiting 5 seconds...")
                        await asyncio.sleep(5)  # Wait 5 seconds between polls
                        continue
                    else:
                        logger.warning(f"Unknown status '{status}', treating as in-progress and continuing to poll")
                        logger.debug(f"Raw response for unknown status: {result}")
                        await asyncio.sleep(5)  # Continue polling for unknown status
                        continue
                        
                except httpx.RequestError as e:
                    logger.warning(f"Polling error (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(5)
                        continue
                    raise RailwayDownloadError(f"Polling failed: {e}")
            
            raise RailwayDownloadError("Download timeout after 10 minutes")
    
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