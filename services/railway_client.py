"""Railway yt-dlp service client for video downloads."""

import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any

import httpx
from loguru import logger

from config import Config
from utils.retry_utils import api_retry, download_retry


class RailwayClientError(Exception):
    """Custom exception for Railway client errors."""
    pass


class RailwayClient:
    """Client for Railway yt-dlp download service."""
    
    def __init__(self):
        if not Config.RAILWAY_API_URL:
            raise ValueError("RAILWAY_API_URL not configured")
        
        self.base_url = Config.RAILWAY_API_URL.rstrip('/')
        self.http_client = httpx.AsyncClient(
            timeout=300,  # 5 minutes for video downloads
            headers={
                "Content-Type": "application/json"
            }
        )
        
        # Ensure temp directory exists
        Path(Config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    
    async def download_video(self, video_url: str) -> str:
        """Download video and return local file path."""
        logger.info(f"Starting Railway download request for URL: {video_url}")
        
        # Try different format selectors if initial download fails
        format_selectors = ["best/worst", "worst", "best[height<=720]", "mp4"]
        
        for attempt, format_selector in enumerate(format_selectors, 1):
            try:
                logger.info(f"Download attempt {attempt}/{len(format_selectors)} with format: {format_selector}")
                
                # Start download request
                request_id = await self._start_download(video_url, format_selector)
                
                # Poll for completion
                logger.info(f"Starting to poll download status for request_id: {request_id}")
                download_response = await self._poll_download_status(request_id)
                
                # Download file locally
                file_url = download_response['file_url']
                local_path = await self.download_file(file_url)
                
                logger.success(f"Railway download completed successfully for request_id: {request_id}")
                return local_path
                
            except RailwayClientError as e:
                if "yt-dlp failed" in str(e) and attempt < len(format_selectors):
                    logger.warning(f"Attempt {attempt} failed with yt-dlp error, trying next format selector...")
                    await asyncio.sleep(2)  # Brief delay between attempts
                    continue
                else:
                    logger.error(f"Railway download error: {e}")
                    raise RailwayClientError(f"Download failed: {e}")
            except Exception as e:
                logger.error(f"Railway download error: {e}")
                raise RailwayClientError(f"Download failed: {e}")
        
        raise RailwayClientError("All download attempts failed")
    
    async def _start_download(self, video_url: str, format_selector: str = "best/worst") -> str:
        """Start video download request."""
        payload = {
            "url": video_url,
            "format": format_selector,
            "path": "videos/{safe_title}-{id}.{ext}"
        }
        
        logger.info(f"Using format selector: {payload['format']}")
        logger.debug(f"Request payload: {payload}")
        logger.debug(f"Request URL: {self.base_url}/download")
        logger.debug(f"Request headers: {dict(self.http_client.headers)}")
        
        response = await self.http_client.post(
            f"{self.base_url}/download",
            json=payload
        )
        
        logger.debug(f"Railway API response status: {response.status_code}")
        logger.debug(f"Railway API response headers: {dict(response.headers)}")
        logger.debug(f"Railway API response body: {response.text}")
        
        if response.status_code != 200:
            raise RailwayClientError(f"Download request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        request_id = result.get('request_id')
        
        if not request_id:
            raise RailwayClientError("No request_id in response")
        
        logger.info(f"Download request started successfully, request_id: {request_id}")
        return request_id
    
    async def _poll_download_status(self, request_id: str, max_attempts: int = 120) -> Dict[str, Any]:
        """Poll download status until completion."""
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self.http_client.get(f"{self.base_url}/downloads/{request_id}")
                
                logger.debug(f"Polling response status: {response.status_code}")
                logger.debug(f"Polling response body: {response.text}")
                
                if response.status_code != 200:
                    logger.error(f"Polling failed: {response.status_code} - {response.text}")
                    await asyncio.sleep(5)
                    continue
                
                result = response.json()
                status = result.get('status')
                
                logger.info(f"Download status: {status} | Progress: Unknown | Attempt: {attempt}/{max_attempts}")
                logger.debug(f"Full polling response: {result}")
                
                if status == 'DONE':
                    logger.success(f"Download completed successfully after {attempt} attempts")
                    return result
                elif status == 'ERROR':
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"Download failed with status 'ERROR': {error_msg}")
                    logger.debug(f"Full error response: {result}")
                    raise RailwayClientError(f"Download service error: {error_msg}")
                elif status in ['QUEUED', 'RUNNING']:
                    logger.debug(f"Download in progress ({status}), waiting 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.warning(f"Unknown status '{status}', continuing to poll...")
                    await asyncio.sleep(5)
                    
            except RailwayClientError:
                raise  # Re-raise service errors
            except Exception as e:
                logger.warning(f"Polling error (attempt {attempt}): {e}")
                await asyncio.sleep(5)
        
        raise RailwayClientError(f"Download timeout after {max_attempts} attempts")
    
    async def download_file(self, file_url: str) -> str:
        """Download file from Railway service to local temp directory."""
        logger.info(f"Downloading video file from {file_url}")
        
        try:
            # Ensure URL has proper protocol
            if not file_url.startswith(('http://', 'https://')):
                file_url = f"https://{file_url}"
            
            # Generate unique local filename
            file_id = str(uuid.uuid4())[:8]
            local_path = Path(Config.TEMP_DIR) / f"video_{file_id}.mp4"
            
            # Download file
            async with self.http_client.stream('GET', file_url) as response:
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
            
            logger.success(f"Video downloaded to {local_path}")
            return str(local_path)
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise RailwayClientError(f"File download error: {e}")
    
    async def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary downloaded file."""
        try:
            Path(file_path).unlink(missing_ok=True)
            logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    async def get_video_info(self, video_url: str) -> Dict[str, Any]:
        """Get video information without downloading."""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/info",
                json={"url": video_url}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise RailwayClientError(f"Info request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Video info request failed: {e}")
            raise RailwayClientError(f"Info request error: {e}")
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
