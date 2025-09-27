"""Notion storage service for knowledge entries."""

import asyncio
from typing import Dict, Any, Optional

import httpx
from loguru import logger

from config import Config
from core.models.content_models import GeminiAnalysis


class NotionStorageError(Exception):
    """Custom exception for Notion storage errors."""
    pass


class NotionStorage:
    """Service for storing knowledge entries in Notion database."""
    
    def __init__(self):
        self.enabled = bool(Config.NOTION_API_KEY and Config.NOTION_DATABASE_ID)
        
        if self.enabled:
            self.http_client = httpx.AsyncClient(
                timeout=30,
                headers={
                    "Authorization": f"Bearer {Config.NOTION_API_KEY}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28"
                }
            )
            logger.info("Notion client initialized successfully")
        else:
            logger.warning("Notion storage disabled - missing API key or database ID")
    
    async def save_entry(
        self, 
        analysis: GeminiAnalysis, 
        enriched_content: str, 
        video_url: str
    ) -> str:
        """Save knowledge entry to Notion database."""
        if not self.enabled:
            raise NotionStorageError("Notion storage not configured")
        
        try:
            # Create basic Notion page
            page_data = {
                "parent": {"database_id": Config.NOTION_DATABASE_ID},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {"content": analysis.video_metadata.title or "Untitled Video"}
                            }
                        ]
                    },
                    "Source Video": {
                        "url": video_url
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": enriched_content[:2000]}
                                }
                            ]
                        }
                    }
                ]
            }
            
            # Create Notion page
            response = await self.http_client.post(
                "https://api.notion.com/v1/pages",
                json=page_data
            )
            
            if response.status_code == 200:
                result = response.json()
                page_url = result.get("url", "")
                logger.success(f"Notion page created successfully: {page_url}")
                return page_url
            else:
                logger.error(f"Notion API error: {response.status_code} - {response.text}")
                raise NotionStorageError(f"Failed to create Notion page: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to save entry to Notion: {e}")
            raise NotionStorageError(f"Storage failed: {e}")
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()
