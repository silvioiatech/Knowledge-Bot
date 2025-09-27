"""Markdown storage service for knowledge entries."""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from loguru import logger

from config import Config
from core.models.content_models import GeminiAnalysis


class MarkdownStorageError(Exception):
    """Custom exception for Markdown storage errors."""
    pass


class MarkdownStorage:
    """Service for storing knowledge entries as Markdown files."""
    
    def __init__(self):
        self.base_path = Path(Config.KNOWLEDGE_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_entry(
        self,
        analysis: GeminiAnalysis,
        enriched_content: str,
        video_url: str
    ) -> str:
        """Save knowledge entry as Markdown file."""
        logger.info("Saving knowledge entry to Markdown")
        
        try:
            # Generate filename
            title = analysis.video_metadata.title or "untitled-video"
            clean_title = self._clean_filename(title)
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"{timestamp}-{clean_title}.md"
            
            # Determine category folder
            category = self._determine_category(analysis)
            category_path = self.base_path / self._clean_filename(category.lower().replace("🤖", "ai").replace("🌐", "web").replace("💻", "programming").replace("⚙️", "devops").replace("📱", "mobile").replace("🛡️", "security").replace("📊", "data"))
            category_path.mkdir(exist_ok=True)
            
            file_path = category_path / filename
            
            # Create markdown content with frontmatter
            markdown_content = self._create_markdown_content(
                analysis, enriched_content, video_url
            )
            
            # Save file
            file_path.write_text(markdown_content, encoding='utf-8')
            
            relative_path = file_path.relative_to(self.base_path)
            logger.success(f"Knowledge entry saved to {relative_path}")
            
            return str(relative_path)
            
        except Exception as e:
            logger.error(f"Failed to save markdown file: {e}")
            raise MarkdownStorageError(f"Save failed: {e}")
    
    def _clean_filename(self, text: str) -> str:
        """Clean text for use as filename."""
        import re
        # Remove or replace invalid filename characters
        clean = re.sub(r'[^\w\s-]', '', text.lower())
        clean = re.sub(r'[-\s]+', '-', clean)
        return clean.strip('-')[:50]  # Limit length
    
    def _determine_category(self, analysis: GeminiAnalysis) -> str:
        """Determine category based on analysis content."""
        main_topic = analysis.content_outline.main_topic.lower()
        entities = [e.name.lower() for e in analysis.entities]
        
        # Check category mappings from config
        from config import CATEGORY_MAPPINGS
        
        for category, keywords in CATEGORY_MAPPINGS.items():
            if any(keyword in main_topic or any(keyword in entity for entity in entities) 
                   for keyword in keywords):
                return category
        
        return "📚 General Tech"
    
    def _create_markdown_content(
        self, 
        analysis: GeminiAnalysis, 
        enriched_content: str, 
        video_url: str
    ) -> str:
        """Create markdown content with frontmatter."""
        
        # Extract metadata
        title = analysis.video_metadata.title or "Untitled Video"
        author = analysis.video_metadata.author or "Unknown"
        tools = [e.name for e in analysis.entities if e.type == 'technology'][:5]
        key_concepts = [e.name for e in analysis.entities if e.type in ['concept', 'technology']][:8]
        
        # Create frontmatter
        frontmatter = f"""---
title: "{title}"
source_video: "{video_url}"
author: "{author}"
platform: "{analysis.video_metadata.platform}"
category: "{self._determine_category(analysis)}"
difficulty: "{analysis.content_outline.difficulty_level}"
tools: {tools}
key_concepts: {key_concepts}
processing_date: "{datetime.now().isoformat()}"
quality_score: {analysis.quality_scores.overall:.2f}
---

"""
        
        # Combine frontmatter with content
        full_content = frontmatter + enriched_content
        
        return full_content
