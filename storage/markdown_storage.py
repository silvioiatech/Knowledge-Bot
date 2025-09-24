"""Markdown storage manager for knowledge base."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    import aiofiles
    from loguru import logger
except ImportError:
    yaml = None
    aiofiles = None
    logger = None

from config import Config


class MarkdownStorageError(Exception):
    """Custom exception for storage failures."""
    pass


class MarkdownStorage:
    """Manager for saving and organizing knowledge base entries."""
    
    def __init__(self):
        self.knowledge_base_path = Config.KNOWLEDGE_BASE_PATH
        self.knowledge_base_path.mkdir(exist_ok=True)
    
    def _serialize_frontmatter(self, data: Dict[str, Any]) -> str:
        """
        Serialize frontmatter data to YAML or JSON fallback.
        
        Args:
            data: Dictionary to serialize
            
        Returns:
            Serialized string
            
        Raises:
            MarkdownStorageError: If serialization fails
        """
        try:
            if yaml is not None:
                # Use safe_dump for security and better formatting
                return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)
            else:
                # Fallback to JSON if PyYAML not available
                if logger:
                    logger.warning("PyYAML not available, using JSON fallback for frontmatter")
                
                # Format JSON nicely for readability
                json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
                return f"# YAML frontmatter (JSON format - install PyYAML for proper YAML)\n{json_str}\n"
        except Exception as e:
            raise MarkdownStorageError(f"Failed to serialize frontmatter: {e}")
    
    async def save_entry(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Save enriched content as categorized Markdown file.
        
        Args:
            content: Enriched Markdown content from Claude
            metadata: Analysis metadata from Gemini
            
        Returns:
            Relative path to saved file
            
        Raises:
            MarkdownStorageError: If save fails
        """
        try:
            if logger:
                logger.info("Saving knowledge entry to Markdown")
            
            # Generate filename and category
            filename = self._generate_filename(metadata)
            category = self._get_category(metadata.get("subject", "Unknown"))
            
            # Create category directory
            category_path = self.knowledge_base_path / category
            category_path.mkdir(exist_ok=True)
            
            # Create full file path
            file_path = category_path / f"{filename}.md"
            
            # Prepare frontmatter
            frontmatter = self._create_frontmatter(metadata)
            
            # Serialize frontmatter with fallback
            frontmatter_str = self._serialize_frontmatter(frontmatter)
            
            # Combine frontmatter and content
            full_content = f"---\n{frontmatter_str}---\n\n{content}"
            
            # Save file
            if aiofiles:
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(full_content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_content)
            
            # Return relative path
            relative_path = f"{category}/{filename}.md"
            
            if logger:
                logger.success(f"Knowledge entry saved to {relative_path}")
            
            return relative_path
            
        except Exception as e:
            if logger:
                logger.error(f"Storage error: {e}")
            raise MarkdownStorageError(f"Failed to save entry: {e}")
    
    def _generate_filename(self, metadata: Dict[str, Any]) -> str:
        """Generate safe filename from title and date."""
        title = metadata.get("title", "untitled")
        
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        clean_title = clean_title.strip('-').lower()
        
        # Limit length
        if len(clean_title) > 50:
            clean_title = clean_title[:50]
        
        # Add date
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Create unique filename
        base_filename = f"{date_str}-{clean_title}"
        
        # Ensure uniqueness
        counter = 1
        filename = base_filename
        while (self.knowledge_base_path / self._get_category(metadata.get("subject", "Unknown")) / f"{filename}.md").exists():
            filename = f"{base_filename}-{counter}"
            counter += 1
        
        return filename
    
    def _get_category(self, subject: str) -> str:
        """Map video subject to category folder."""
        subject_lower = subject.lower()
        
        # Category mapping
        category_mapping = {
            # AI & Machine Learning
            "ai": "artificial-intelligence",
            "artificial intelligence": "artificial-intelligence", 
            "machine learning": "artificial-intelligence",
            "deep learning": "artificial-intelligence",
            "neural networks": "artificial-intelligence",
            "chatgpt": "artificial-intelligence",
            "llm": "artificial-intelligence",
            
            # Development & Programming
            "programming": "development",
            "coding": "development",
            "python": "development",
            "javascript": "development", 
            "web development": "development",
            "app development": "development",
            "software": "development",
            "api": "development",
            "database": "development",
            
            # Design & Creativity
            "design": "design",
            "graphic design": "design",
            "ui design": "design",
            "ux design": "design",
            "photoshop": "design",
            "figma": "design",
            "creative": "design",
            "art": "design",
            
            # Business & Marketing
            "business": "business",
            "marketing": "business",
            "social media": "business",
            "entrepreneurship": "business",
            "sales": "business",
            "finance": "business",
            
            # Productivity & Tools
            "productivity": "productivity",
            "tools": "productivity",
            "automation": "productivity",
            "workflow": "productivity",
            "organization": "productivity",
            
            # Education & Learning
            "education": "education", 
            "tutorial": "education",
            "learning": "education",
            "course": "education",
            "teaching": "education",
        }
        
        # Find matching category
        for keyword, category in category_mapping.items():
            if keyword in subject_lower:
                return category
        
        # Default category
        return "general"
    
    def _create_frontmatter(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create YAML frontmatter from metadata."""
        now = datetime.now()
        
        frontmatter = {
            "title": metadata.get("title", "Untitled"),
            "date": now.isoformat(),
            "created_date": now.strftime("%Y-%m-%d"),
            "source_url": metadata.get("original_url", ""),
            "platform": self._detect_platform(metadata.get("original_url", "")),
            "subject": metadata.get("subject", "Unknown"),
            "difficulty_level": metadata.get("difficulty_level", "unknown"),
            "estimated_watch_time": metadata.get("estimated_watch_time", "unknown"),
            "tools": metadata.get("tools", []),
            "tags": metadata.get("tags", []),
            "key_points_count": len(metadata.get("key_points", [])),
            "has_resources": len(metadata.get("resources", [])) > 0,
            "bot_processed": True,
            "processing_date": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add summary if available
        summary = metadata.get("summary", "")
        if summary and len(summary) <= 200:
            frontmatter["summary"] = summary
        
        return frontmatter
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL."""
        if not url:
            return "unknown"
        
        if "tiktok.com" in url or "vm.tiktok.com" in url:
            return "tiktok"
        elif "instagram.com" in url:
            return "instagram"
        else:
            return "unknown"
    
    def list_entries(self, category: Optional[str] = None) -> list[str]:
        """List all knowledge base entries."""
        try:
            entries = []
            
            if category:
                # List entries in specific category
                category_path = self.knowledge_base_path / category
                if category_path.exists():
                    for file_path in category_path.glob("*.md"):
                        entries.append(f"{category}/{file_path.name}")
            else:
                # List all entries
                for category_dir in self.knowledge_base_path.iterdir():
                    if category_dir.is_dir():
                        for file_path in category_dir.glob("*.md"):
                            entries.append(f"{category_dir.name}/{file_path.name}")
            
            return sorted(entries)
            
        except Exception as e:
            if logger:
                logger.error(f"Error listing entries: {e}")
            return []
    
    def get_categories(self) -> list[str]:
        """Get list of available categories."""
        try:
            categories = []
            for path in self.knowledge_base_path.iterdir():
                if path.is_dir() and not path.name.startswith('.'):
                    categories.append(path.name)
            return sorted(categories)
        except Exception as e:
            if logger:
                logger.error(f"Error getting categories: {e}")
            return []


# Convenience function for external use
async def save_knowledge_entry(content: str, metadata: Dict[str, Any]) -> str:
    """
    Save knowledge entry to Markdown file.
    
    Args:
        content: Enriched content from Claude
        metadata: Analysis metadata from Gemini
        
    Returns:
        Relative path to saved file
    """
    storage = MarkdownStorage()
    return await storage.save_entry(content, metadata)