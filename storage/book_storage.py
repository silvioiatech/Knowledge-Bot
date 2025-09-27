"""Book storage service for knowledge management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from loguru import logger

from config import Config
from core.models.content_models import ContentData


class BookStorage:
    """Manages knowledge base storage as structured book format."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or Config.KNOWLEDGE_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize book structure
        self.chapters_dir = self.base_path / "chapters"
        self.metadata_dir = self.base_path / "metadata"
        
        for directory in [self.chapters_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def store_chapter(self, content_data: ContentData) -> str:
        """Store content as a structured book chapter."""
        try:
            # Generate chapter metadata
            chapter_id = self._generate_chapter_id(content_data)
            chapter_file = self.chapters_dir / f"{chapter_id}.md"
            metadata_file = self.metadata_dir / f"{chapter_id}.json"
            
            # Create chapter content
            chapter_content = self._format_chapter_content(content_data)
            
            # Create metadata
            metadata = {
                "id": chapter_id,
                "title": content_data.title,
                "source_url": content_data.source_url,
                "created_at": datetime.now().isoformat(),
                "category": content_data.category,
                "tools": content_data.tools,
                "tags": content_data.tags,
                "summary": content_data.summary[:200] + "..." if len(content_data.summary) > 200 else content_data.summary,
                "estimated_read_time": self._calculate_read_time(chapter_content),
                "word_count": len(chapter_content.split())
            }
            
            # Write files
            chapter_file.write_text(chapter_content, encoding="utf-8")
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            
            logger.info(f"Stored chapter: {chapter_id}")
            return str(chapter_file)
            
        except Exception as e:
            logger.error(f"Failed to store chapter: {e}")
            raise
    
    def _generate_chapter_id(self, content_data: ContentData) -> str:
        """Generate unique chapter ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = "".join(c.lower() if c.isalnum() else "_" for c in content_data.title)[:30]
        return f"{timestamp}_{title_slug}"
    
    def _format_chapter_content(self, content_data: ContentData) -> str:
        """Format content as structured chapter."""
        content = f"""# {content_data.title}

**Source:** {content_data.source_url}
**Category:** {content_data.category}
**Tools:** {", ".join(content_data.tools)}
**Tags:** {", ".join(content_data.tags)}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

{content_data.summary}

---

{content_data.enriched_content}

---

## Key Resources

"""
        
        if content_data.resources:
            for resource in content_data.resources:
                content += f"- [{resource.get('title', 'Resource')}]({resource.get('url', '#')})\n"
        
        if hasattr(content_data, 'generated_images') and content_data.generated_images:
            content += "\n## Visual Aids\n\n"
            for img_path in content_data.generated_images:
                content += f"![Diagram](../{Path(img_path).name})\n\n"
        
        return content
    
    def _calculate_read_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        word_count = len(content.split())
        # Average reading speed: 200 words per minute
        return max(1, round(word_count / 200))
    
    async def get_book_index(self) -> Dict[str, Any]:
        """Get structured index of all chapters."""
        try:
            chapters = []
            
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    metadata = json.loads(metadata_file.read_text())
                    chapters.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to read metadata {metadata_file}: {e}")
            
            # Sort by creation date
            chapters.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Group by category
            categories = {}
            for chapter in chapters:
                category = chapter.get('category', 'Uncategorized')
                if category not in categories:
                    categories[category] = []
                categories[category].append(chapter)
            
            return {
                "total_chapters": len(chapters),
                "categories": categories,
                "recent_chapters": chapters[:10],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate book index: {e}")
            return {"error": str(e)}
    
    async def search_chapters(self, query: str) -> List[Dict[str, Any]]:
        """Search chapters by content or metadata."""
        try:
            results = []
            query_lower = query.lower()
            
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    metadata = json.loads(metadata_file.read_text())
                    
                    # Search in title, summary, tools, tags
                    searchable_text = " ".join([
                        metadata.get('title', ''),
                        metadata.get('summary', ''),
                        " ".join(metadata.get('tools', [])),
                        " ".join(metadata.get('tags', []))
                    ]).lower()
                    
                    if query_lower in searchable_text:
                        # Add relevance score (simple keyword matching)
                        relevance = searchable_text.count(query_lower)
                        metadata['relevance_score'] = relevance
                        results.append(metadata)
                
                except Exception as e:
                    logger.warning(f"Failed to search metadata {metadata_file}: {e}")
            
            # Sort by relevance
            results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Chapter search failed: {e}")
            return []
    
    async def get_chapter_content(self, chapter_id: str) -> Optional[str]:
        """Get full chapter content by ID."""
        try:
            chapter_file = self.chapters_dir / f"{chapter_id}.md"
            if chapter_file.exists():
                return chapter_file.read_text(encoding="utf-8")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chapter content {chapter_id}: {e}")
            return None
    
    async def generate_table_of_contents(self) -> str:
        """Generate markdown table of contents."""
        try:
            index = await self.get_book_index()
            
            toc = "# Knowledge Base Table of Contents\n\n"
            toc += f"**Total Chapters:** {index['total_chapters']}\n"
            toc += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for category, chapters in index.get('categories', {}).items():
                toc += f"## {category}\n\n"
                
                for chapter in chapters:
                    toc += f"- [{chapter['title']}](chapters/{chapter['id']}.md)"
                    toc += f" ({chapter['word_count']} words, {chapter['estimated_read_time']} min read)\n"
                
                toc += "\n"
            
            # Write TOC file
            toc_file = self.base_path / "README.md"
            toc_file.write_text(toc, encoding="utf-8")
            
            logger.info("Generated table of contents")
            return toc
            
        except Exception as e:
            logger.error(f"Failed to generate TOC: {e}")
            return f"# Knowledge Base\n\nError generating TOC: {e}"
    
    async def export_book_metadata(self) -> Dict[str, Any]:
        """Export complete book metadata for analysis."""
        try:
            index = await self.get_book_index()
            
            # Calculate statistics
            total_words = sum(
                chapter.get('word_count', 0) 
                for chapters in index.get('categories', {}).values()
                for chapter in chapters
            )
            
            total_read_time = sum(
                chapter.get('estimated_read_time', 0)
                for chapters in index.get('categories', {}).values() 
                for chapter in chapters
            )
            
            # Tool frequency analysis
            tool_usage = {}
            for chapters in index.get('categories', {}).values():
                for chapter in chapters:
                    for tool in chapter.get('tools', []):
                        tool_usage[tool] = tool_usage.get(tool, 0) + 1
            
            return {
                "book_stats": {
                    "total_chapters": index['total_chapters'],
                    "total_categories": len(index.get('categories', {})),
                    "total_words": total_words,
                    "total_read_time_minutes": total_read_time,
                    "average_chapter_length": total_words // max(1, index['total_chapters'])
                },
                "category_breakdown": {
                    cat: len(chapters) 
                    for cat, chapters in index.get('categories', {}).items()
                },
                "tool_usage_frequency": dict(sorted(
                    tool_usage.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )),
                "export_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export book metadata: {e}")
            return {"error": str(e)}
