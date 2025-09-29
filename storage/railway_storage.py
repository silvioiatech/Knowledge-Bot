"""Railway persistent storage for knowledge entries."""

import asyncio
import os
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from loguru import logger
from core.models.content_models import GeminiAnalysis


class RailwayStorage:
    """Storage adapter for Railway persistent file system."""
    
    def __init__(self):
        self.base_url = os.getenv('RAILWAY_STATIC_URL', 'http://localhost:8000')
        self.local_storage_path = Path("/app/knowledge_base") if os.getenv('RAILWAY_ENVIRONMENT') else Path("./knowledge_base_local")
        self.images_path = self.local_storage_path / "images"
        
        # Ensure directories exist
        self._create_directory_structure()
        
        logger.info(f"Railway storage initialized at {self.local_storage_path}")
    
    def _create_directory_structure(self):
        """Create local directory structure."""
        categories = [
            "ai", "web-development", "programming", "devops",
            "mobile", "security", "data", "macos", "linux", "windows", "general"
        ]
        
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        for category in categories:
            (self.local_storage_path / category).mkdir(exist_ok=True)
    
    def _determine_category_folder(self, analysis: GeminiAnalysis) -> str:
        """Determine category folder from analysis."""
        main_topic = analysis.content_outline.main_topic.lower()
        entities = [entity.name.lower() for entity in analysis.entities]
        
        # Category mapping
        if any(term in main_topic or any(term in entity for entity in entities) 
               for term in ["ai", "machine learning", "neural", "gpt", "claude"]):
            return "ai"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["web", "javascript", "react", "vue", "html", "css"]):
            return "web-development"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["python", "java", "golang", "rust", "programming"]):
            return "programming"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["devops", "docker", "kubernetes", "cloud"]):
            return "devops"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["mobile", "ios", "android", "flutter"]):
            return "mobile"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["security", "cybersecurity", "encryption"]):
            return "security"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["data", "analytics", "database", "sql"]):
            return "data"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["mac", "macos", "osx", "apple"]):
            return "macos"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["linux", "ubuntu", "debian", "bash"]):
            return "linux"
        elif any(term in main_topic or any(term in entity for entity in entities)
                for term in ["windows", "microsoft", "powershell"]):
            return "windows"
        else:
            return "general"
    
    def _generate_filename(self, title: str) -> str:
        """Generate clean filename with date prefix."""
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in ' -').strip()
        clean_title = clean_title.replace(' ', '-').lower()[:50]
        
        return f"{date_str}-{clean_title}.md"
    
    def _create_markdown_content(
        self, 
        analysis: GeminiAnalysis, 
        enriched_content: str, 
        video_url: str
    ) -> str:
        """Create markdown content with YAML frontmatter."""
        
        # Extract tools and tags
        tools = [entity.name for entity in analysis.entities if entity.type == 'technology'][:5]
        tags = [entity.name for entity in analysis.entities if entity.type in ['concept', 'technology']][:8]
        
        # YAML frontmatter
        frontmatter = f"""---
title: "{analysis.video_metadata.title}"
date: {datetime.now().strftime('%Y-%m-%d')}
source_url: "{video_url}"
platform: "{video_url.split('/')[2].split('.')[0]}"
category: "{analysis.content_outline.main_topic}"
difficulty: "{analysis.content_outline.difficulty_level}"
duration: {analysis.video_metadata.duration}
quality_score: {int(analysis.quality_scores.overall)}
tools: {tools}
tags: {tags}
---

"""
        
        # Combine frontmatter with enriched content
        full_content = frontmatter + enriched_content
        
        return full_content
    
    async def save_entry(
        self, 
        analysis: GeminiAnalysis, 
        enriched_content: str, 
        video_url: str
    ) -> str:
        """Save knowledge entry to Railway storage and return URL."""
        
        try:
            # Determine category and filename
            category = self._determine_category_folder(analysis)
            filename = self._generate_filename(analysis.video_metadata.title)
            
            # Create full markdown content
            markdown_content = self._create_markdown_content(analysis, enriched_content, video_url)
            
            # Save to local file system (Railway persistent volume)
            category_path = self.local_storage_path / category
            file_path = category_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Generate public URL
            public_url = f"{self.base_url}/view/{category}/{filename}"
            
            logger.success(f"Saved knowledge entry to Railway storage: {file_path}")
            logger.info(f"Public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to save to Railway storage: {e}")
            raise
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            total_files = 0
            categories_stats = {}
            
            for category_dir in self.local_storage_path.iterdir():
                if category_dir.is_dir() and category_dir.name != "images":
                    md_files = list(category_dir.glob("*.md"))
                    categories_stats[category_dir.name] = len(md_files)
                    total_files += len(md_files)
            
            total_images = len(list(self.images_path.glob("*"))) if self.images_path.exists() else 0
            
            return {
                "total_files": total_files,
                "total_images": total_images,
                "categories": categories_stats,
                "storage_path": str(self.local_storage_path),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    def get_browse_url(self) -> str:
        """Get the URL for browsing the knowledge base."""
        return f"{self.base_url}/kb/"