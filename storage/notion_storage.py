"""
Enhanced Notion Storage Service with exact database schema integration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import httpx
from config import Config
from core.models.content_models import GeminiAnalysis, NotionPayload

logger = logging.getLogger(__name__)

class EnhancedNotionStorageService:
    """Enhanced Notion storage service with exact field mapping to Knowledge Base database."""
    
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {Config.NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.database_id = Config.NOTION_DATABASE_ID
    
    async def save_enhanced_entry(self, notion_payload: NotionPayload) -> tuple[bool, Optional[str]]:
        """
        Save entry to Notion database with comprehensive metadata and exact field mapping.
        Returns: (success, notion_page_url)
        """
        if not Config.USE_NOTION_STORAGE or not self.database_id:
            logger.info("Notion storage disabled or not configured")
            return False, None
        
        try:
            # Create the Notion page request
            page_data = notion_payload.to_notion_request(self.database_id)
            
            logger.info(f"Creating Notion page: {notion_payload.title}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    page_url = result.get("url", "")
                    
                    logger.info(f"Successfully created Notion page: {page_url}")
                    
                    # Update page content with the markdown
                    if notion_payload.content_blocks:
                        await self._update_page_content(result["id"], notion_payload.content_blocks)
                    
                    return True, page_url
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    logger.error(f"Notion API error {response.status_code}: {error_data}")
                    return False, None
                    
        except Exception as e:
            logger.error(f"Error saving to Notion: {e}")
            return False, None
    
    async def _update_page_content(self, page_id: str, content_blocks: List[Dict[str, Any]]) -> bool:
        """Update the page content with markdown blocks."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/blocks/{page_id}/children",
                    headers=self.headers,
                    json={"children": content_blocks[:100]}  # Notion has limits
                )
                
                if response.status_code == 200:
                    logger.info("Successfully updated page content")
                    return True
                else:
                    logger.error(f"Failed to update page content: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating page content: {e}")
            return False
    
    async def verify_database_schema(self) -> Dict[str, Any]:
        """
        Verify that the Notion database has all required fields with correct types.
        Returns schema validation results.
        """
        if not self.database_id:
            return {"valid": False, "error": "Database ID not configured"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/databases/{self.database_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return {"valid": False, "error": f"API error: {response.status_code}"}
                
                database_info = response.json()
                properties = database_info.get("properties", {})
                
                # Required fields mapping
                required_fields = {
                    "Title": "title",
                    "Category": "select", 
                    "Subcategory": "select",
                    "Content Quality": "select",
                    "Difficulty": "select",
                    "Word Count": "number",
                    "Processing Date": "date",
                    "Source Video": "url",
                    "Key Points": "rich_text",
                    "Gemini Confidence": "number",
                    "Tags": "multi_select",
                    "Tools Mentioned": "multi_select",
                    "Platform Specific": "multi_select",
                    "Auto-Created Category": "checkbox",
                    "Verified": "checkbox",
                    "Ready for Script": "checkbox",
                    "Ready for eBook": "checkbox"
                }
                
                validation_results = {
                    "valid": True,
                    "missing_fields": [],
                    "incorrect_types": [],
                    "available_fields": list(properties.keys())
                }
                
                # Check each required field
                for field_name, expected_type in required_fields.items():
                    if field_name not in properties:
                        validation_results["missing_fields"].append(field_name)
                        validation_results["valid"] = False
                    else:
                        actual_type = properties[field_name].get("type")
                        if actual_type != expected_type:
                            validation_results["incorrect_types"].append({
                                "field": field_name,
                                "expected": expected_type,
                                "actual": actual_type
                            })
                            validation_results["valid"] = False
                
                return validation_results
                
        except Exception as e:
            logger.error(f"Error verifying database schema: {e}")
            return {"valid": False, "error": str(e)}
    
    async def get_existing_categories(self) -> List[str]:
        """Get list of existing categories from the database to ensure consistency."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/databases/{self.database_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    database_info = response.json()
                    category_property = database_info.get("properties", {}).get("Category", {})
                    
                    if category_property.get("type") == "select":
                        select_options = category_property.get("select", {}).get("options", [])
                        return [option["name"] for option in select_options]
                
                return []
                
        except Exception as e:
            logger.error(f"Error getting existing categories: {e}")
            return []
    
    async def search_similar_entries(self, title: str, source_url: str) -> List[Dict[str, Any]]:
        """Search for similar entries to avoid duplicates."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Search by source URL first (most reliable)
                search_data = {
                    "filter": {
                        "property": "Source Video",
                        "url": {
                            "equals": source_url
                        }
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/databases/{self.database_id}/query",
                    headers=self.headers,
                    json=search_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return results.get("results", [])
                
                return []
                
        except Exception as e:
            logger.error(f"Error searching for similar entries: {e}")
            return []
    
    def create_notion_content_blocks(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Convert markdown content to Notion blocks with better parsing.
        """
        blocks = []
        lines = markdown_content.split('\n')
        current_block = None
        
        for line in lines:
            stripped_line = line.strip()
            
            if not stripped_line:
                # Empty line - finish current block if exists
                if current_block:
                    blocks.append(current_block)
                    current_block = None
                continue
            
            # Headers
            if stripped_line.startswith('# '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": stripped_line[2:]}}]
                    }
                }
            elif stripped_line.startswith('## '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_2", 
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": stripped_line[3:]}}]
                    }
                }
            elif stripped_line.startswith('### '):
                if current_block:
                    blocks.append(current_block)
                current_block = {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": stripped_line[4:]}}]
                    }
                }
            # Bullet points
            elif stripped_line.startswith('- ') or stripped_line.startswith('* '):
                if current_block and current_block.get("type") != "bulleted_list_item":
                    blocks.append(current_block)
                    current_block = None
                
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": stripped_line[2:]}}]
                    }
                })
            # Code blocks
            elif stripped_line.startswith('```'):
                if current_block:
                    blocks.append(current_block)
                # For simplicity, treat as paragraph (Notion code blocks are complex)
                current_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Code block (see original markdown)"}}]
                    }
                }
            # Regular paragraph
            else:
                if current_block and current_block.get("type") == "paragraph":
                    # Append to existing paragraph
                    existing_text = current_block["paragraph"]["rich_text"][0]["text"]["content"]
                    current_block["paragraph"]["rich_text"][0]["text"]["content"] = f"{existing_text}\n{stripped_line}"
                else:
                    if current_block:
                        blocks.append(current_block)
                    current_block = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": stripped_line[:2000]}}]  # Notion limit
                        }
                    }
        
        # Add final block
        if current_block:
            blocks.append(current_block)
        
        return blocks[:100]  # Notion has block limits
    
    async def update_content_quality(self, page_url: str, new_quality: str) -> bool:
        """Update the content quality level of an existing entry."""
        try:
            # Extract page ID from URL
            page_id = page_url.split('/')[-1].split('-')[-1]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json={
                        "properties": {
                            "Content Quality": {
                                "select": {"name": new_quality}
                            }
                        }
                    }
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error updating content quality: {e}")
            return False

# For backward compatibility
class NotionStorageService(EnhancedNotionStorageService):
    """Alias for backward compatibility."""
    pass
