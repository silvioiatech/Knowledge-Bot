"""Book-like storage system for Knowledge Bot."""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import yaml
import aiofiles
from loguru import logger


class BookStorage:
    """Organize knowledge as a structured book."""
    
    # Book structure mapping
    BOOK_STRUCTURE = {
        # AI & Machine Learning
        "artificial intelligence": "01_Artificial_Intelligence",
        "ai": "01_Artificial_Intelligence", 
        "machine learning": "01_Artificial_Intelligence/ML",
        "chatgpt": "01_Artificial_Intelligence/LLMs",
        "llm": "01_Artificial_Intelligence/LLMs",
        "gpt": "01_Artificial_Intelligence/LLMs",
        "claude": "01_Artificial_Intelligence/LLMs",
        "gemini": "01_Artificial_Intelligence/LLMs",
        "neural network": "01_Artificial_Intelligence/ML",
        "deep learning": "01_Artificial_Intelligence/ML",
        
        # Making Money with AI
        "ai business": "02_Making_Money_with_AI",
        "ai money": "02_Making_Money_with_AI",
        "ai automation": "02_Making_Money_with_AI/Automation",
        "ai products": "02_Making_Money_with_AI/Products",
        "freelance": "02_Making_Money_with_AI/Freelancing",
        "saas": "02_Making_Money_with_AI/Products",
        "business": "02_Making_Money_with_AI",
        "entrepreneurship": "02_Making_Money_with_AI",
        
        # Computer Science
        "programming": "03_Computer_Science/Programming",
        "coding": "03_Computer_Science/Programming",
        "web development": "03_Computer_Science/Web_Dev",
        "python": "03_Computer_Science/Python",
        "javascript": "03_Computer_Science/JavaScript",
        "react": "03_Computer_Science/Web_Dev",
        "nextjs": "03_Computer_Science/Web_Dev",
        "node": "03_Computer_Science/JavaScript",
        "database": "03_Computer_Science/Databases",
        "sql": "03_Computer_Science/Databases",
        "git": "03_Computer_Science/Tools",
        "vscode": "03_Computer_Science/Tools",
        
        # Mac & Apple
        "mac": "04_Mac_and_Apple",
        "macos": "04_Mac_and_Apple/macOS",
        "apple": "04_Mac_and_Apple",
        "ios": "04_Mac_and_Apple/iOS",
        "swift": "04_Mac_and_Apple/Swift",
        "xcode": "04_Mac_and_Apple/Development",
        "iphone": "04_Mac_and_Apple/iOS",
        "ipad": "04_Mac_and_Apple/iOS",
        "shortcuts": "04_Mac_and_Apple/Automation",
        
        # Linux & DevOps
        "linux": "05_Linux_and_DevOps",
        "ubuntu": "05_Linux_and_DevOps/Ubuntu", 
        "docker": "05_Linux_and_DevOps/Docker",
        "kubernetes": "05_Linux_and_DevOps/Kubernetes",
        "devops": "05_Linux_and_DevOps/DevOps",
        "aws": "05_Linux_and_DevOps/Cloud",
        "cloud": "05_Linux_and_DevOps/Cloud",
        "server": "05_Linux_and_DevOps/Servers",
        "terminal": "05_Linux_and_DevOps/Command_Line",
        "bash": "05_Linux_and_DevOps/Command_Line",
        
        # Productivity
        "productivity": "06_Productivity_and_Tools",
        "automation": "06_Productivity_and_Tools/Automation",
        "notion": "06_Productivity_and_Tools/Apps",
        "obsidian": "06_Productivity_and_Tools/Apps",
        "workflow": "06_Productivity_and_Tools/Workflows",
        "organization": "06_Productivity_and_Tools/Organization",
        "time management": "06_Productivity_and_Tools/Time_Management",
    }
    
    def __init__(self):
        from config import Config
        self.vault_path = Path(Config.OBSIDIAN_VAULT_PATH)
        
        # Ensure the parent directory exists for external repos
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.vault_path.mkdir(exist_ok=True)
        
        logger.info(f"Initializing book storage at: {self.vault_path}")
        
        # Initialize git sync if configured
        self.git_sync_enabled = Config.AUTO_COMMIT and Config.GITHUB_USERNAME
        if self.git_sync_enabled:
            logger.info("Git sync enabled for private repository")
        
    async def initialize_book_structure(self):
        """Create book-like folder structure."""
        logger.info("Creating book structure...")
        
        # Create main sections
        sections = [
            "00_Index",
            "01_Artificial_Intelligence",
            "02_Making_Money_with_AI", 
            "03_Computer_Science",
            "04_Mac_and_Apple",
            "05_Linux_and_DevOps",
            "06_Productivity_and_Tools",
            "99_Resources"
        ]
        
        for section in sections:
            section_path = self.vault_path / section
            section_path.mkdir(exist_ok=True)
            
            # Create section index file
            await self._create_section_index(section_path, section)
        
        # Create master index
        await self._update_master_index()
        logger.success("Book structure initialized!")
    
    async def _create_section_index(self, section_path: Path, section_name: str):
        """Create index page for each section."""
        clean_name = section_name.split('_', 1)[1].replace('_', ' ') if '_' in section_name else section_name
        
        # Get emoji for section
        emoji_map = {
            "Index": "📑",
            "Artificial Intelligence": "🤖",
            "Making Money with AI": "💰",
            "Computer Science": "💻",
            "Mac and Apple": "🍎",
            "Linux and DevOps": "🐧", 
            "Productivity and Tools": "📈",
            "Resources": "📚"
        }
        
        emoji = emoji_map.get(clean_name, "📖")
        
        index_content = f"""# {emoji} {clean_name}

> Welcome to the **{clean_name}** section of your Knowledge Library

## 📑 Table of Contents

```dataview
TABLE WITHOUT ID
  "[[" + file.name + "|" + title + "]]" as "📄 Page",
  page_number as "#",
  difficulty_level as "📊 Level",
  estimated_reading_time as "⏱️ Time",
  date(file.ctime) as "📅 Added"
FROM "{section_name}"
WHERE file.name != "{section_name}" AND type = "book_page"
SORT page_number ASC
```

## 📊 Section Statistics

- **Total Pages**: `$= dv.pages('"{section_name}"').where(p => p.type == "book_page").length` pages
- **Last Updated**: `$= dv.date("today")`
- **Reading Time**: `$= dv.pages('"{section_name}"').where(p => p.type == "book_page").map(p => p.estimated_reading_time).join(", ")`

## 🏷️ Topics in This Section

```dataview
LIST
WHERE file.folder = "{section_name}"
GROUP BY tags
```

## 🔗 Quick Navigation

- [[00_Index/Home|← Back to Main Library]]
- Browse sections: [[01_Artificial_Intelligence/01_Artificial_Intelligence|🤖 AI]] | [[02_Making_Money_with_AI/02_Making_Money_with_AI|💰 Money]] | [[03_Computer_Science/03_Computer_Science|💻 CS]] | [[04_Mac_and_Apple/04_Mac_and_Apple|🍎 Mac]] | [[05_Linux_and_DevOps/05_Linux_and_DevOps|🐧 Linux]] | [[06_Productivity_and_Tools/06_Productivity_and_Tools|📈 Productivity]]

---

*This section is automatically updated when new content is added to your library.*
"""
        
        index_file = section_path / f"{section_name}.md"
        async with aiofiles.open(index_file, 'w', encoding='utf-8') as f:
            await f.write(index_content)
    
    def _determine_book_section(self, metadata: Dict[str, Any]) -> str:
        """Determine which book section this content belongs to."""
        subject = metadata.get('subject', '').lower()
        tags = [tag.lower() for tag in metadata.get('tags', [])]
        tools = [tool.lower() for tool in metadata.get('tools', [])]
        title = metadata.get('title', '').lower()
        
        # Check all content for categorization
        all_keywords = [subject, title] + tags + tools
        all_keywords = [k.lower() for k in all_keywords if k]
        
        # Find best matching section
        for keyword in all_keywords:
            for pattern, section in self.BOOK_STRUCTURE.items():
                if pattern in keyword or keyword in pattern:
                    return section
        
        # Default section based on general content
        if any(word in ' '.join(all_keywords) for word in ['code', 'program', 'dev', 'software']):
            return "03_Computer_Science/General"
        elif any(word in ' '.join(all_keywords) for word in ['money', 'business', 'earn']):
            return "02_Making_Money_with_AI"
        elif any(word in ' '.join(all_keywords) for word in ['productivity', 'tool', 'app']):
            return "06_Productivity_and_Tools"
        
        # Final fallback
        return "03_Computer_Science/General"
    
    async def save_as_book_page(self, content: str, metadata: Dict[str, Any]) -> str:
        """Save content as a book page with proper structure."""
        try:
            # Initialize structure if needed
            await self.initialize_book_structure()
            
            # Determine section
            section = self._determine_book_section(metadata)
            section_path = self.vault_path / section
            section_path.mkdir(parents=True, exist_ok=True)
            
            # Generate page number (for ordering)
            existing_pages = list(section_path.glob("*.md"))
            # Filter out section index files
            content_pages = [p for p in existing_pages if not p.stem.startswith(('0', '1', '2', '3', '4', '5', '6', '9')) or '_' not in p.stem[:3]]
            page_number = len(content_pages) + 1
            
            # Create filename with page number
            title = metadata.get('title', 'Untitled')
            clean_title = re.sub(r'[^\w\s-]', '', title).replace(' ', '_')[:40]
            filename = f"{page_number:03d}_{clean_title}.md"
            file_path = section_path / filename
            
            # Enhanced frontmatter for book structure
            frontmatter = {
                'title': title,
                'date': datetime.now().isoformat(),
                'page_number': page_number,
                'section': section,
                'subject': metadata.get('subject', ''),
                'difficulty_level': self._determine_difficulty(metadata),
                'estimated_reading_time': metadata.get('estimated_watch_time', '5 min'),
                'tools': metadata.get('tools', []),
                'tags': metadata.get('tags', []),
                'key_concepts': metadata.get('key_points', [])[:5],
                'source_url': metadata.get('original_url', ''),
                'source_platform': metadata.get('platform', ''),
                'type': 'book_page'
            }
            
            # Create book-formatted content
            book_content = self._format_as_book_page(content, frontmatter, section)
            
            # Save file
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(book_content)
            
            # Update master index
            await self._update_master_index()
            
            # Auto-sync to git if enabled
            if self.git_sync_enabled:
                try:
                    from services.git_sync import auto_sync_knowledge
                    await auto_sync_knowledge(str(file_path), frontmatter['title'])
                except Exception as e:
                    logger.warning(f"Git sync failed (non-critical): {e}")
            
            relative_path = str(file_path.relative_to(self.vault_path))
            logger.success(f"Saved as book page: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Failed to save book page: {e}")
            raise
    
    def _determine_difficulty(self, metadata: Dict[str, Any]) -> str:
        """Determine content difficulty level."""
        tools = metadata.get('tools', [])
        key_points = metadata.get('key_points', [])
        
        # Simple heuristic for difficulty
        technical_words = ['advanced', 'complex', 'expert', 'professional', 'enterprise']
        beginner_words = ['intro', 'basic', 'getting started', 'beginner', 'simple', 'easy']
        
        content_text = ' '.join([metadata.get('title', ''), metadata.get('subject', '')] + key_points).lower()
        
        if any(word in content_text for word in technical_words) or len(tools) > 3:
            return 'advanced'
        elif any(word in content_text for word in beginner_words):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _format_as_book_page(self, content: str, frontmatter: Dict, section: str) -> str:
        """Format content as a book page with navigation."""
        # Navigation breadcrumb
        section_parts = section.split('/')
        section_name = section_parts[0].split('_', 1)[1].replace('_', ' ') if len(section_parts[0].split('_')) > 1 else section_parts[0]
        subsection_name = section_parts[1].replace('_', ' ') if len(section_parts) > 1 else ''
        
        # Difficulty emoji
        difficulty_emoji = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}
        diff_emoji = difficulty_emoji.get(frontmatter.get('difficulty_level', 'intermediate'), '🟡')
        
        formatted = f"""---
{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)}---

# 📖 {frontmatter['title']}

> **📚 Section:** [[{section_parts[0]}/{section_parts[0]}|{section_name}]]{f" → {subsection_name}" if subsection_name else ""} | **📄 Page:** {frontmatter['page_number']}
> **🕐 Reading Time:** {frontmatter['estimated_reading_time']} | **📊 Level:** {diff_emoji} {frontmatter['difficulty_level'].title()}
> **🔗 Source:** [{frontmatter.get('source_platform', 'Video').title()}]({frontmatter.get('source_url', '#')})

---

## 🎯 Key Concepts

"""
        # Add key concepts as callouts
        key_concepts = frontmatter.get('key_concepts', [])
        if key_concepts:
            for i, concept in enumerate(key_concepts[:5], 1):
                formatted += f"> [!tip] Key Point {i}\n> {concept}\n\n"
        
        # Add tools section if available
        tools = frontmatter.get('tools', [])
        if tools:
            formatted += "## 🛠️ Tools & Technologies\n\n"
            for tool in tools:
                formatted += f"- **{tool}**\n"
            formatted += "\n"
        
        formatted += f"---\n\n{content}\n\n"
        
        # Add navigation footer
        section_link = f"{section_parts[0]}/{section_parts[0]}"
        formatted += f"""
---

## 📖 Navigation & References

**📑 Section Index:** [[{section_link}|📚 {section_name} Table of Contents]]

**🔗 Quick Links:** [[00_Index/Home|🏠 Main Library]] | [[01_Artificial_Intelligence/01_Artificial_Intelligence|🤖 AI]] | [[02_Making_Money_with_AI/02_Making_Money_with_AI|💰 Money]] | [[03_Computer_Science/03_Computer_Science|💻 CS]]

## 🏷️ Related Pages

```dataview
TABLE WITHOUT ID
  "[[" + file.name + "|" + title + "]]" as "Related Page",
  difficulty_level as "Level"
FROM "{section_parts[0]}"
WHERE type = "book_page" AND file.name != this.file.name
AND (contains(string(tags), string(this.tags)) OR contains(string(tools), string(this.tools)))
LIMIT 5
```

---

**📖 Page {frontmatter['page_number']}** | *Added: {frontmatter['date'][:10]}* | **🔖 [[00_Index/Home|Back to Library]]**
"""
        
        return formatted
    
    async def _update_master_index(self):
        """Update the main library index."""
        # Count pages in each section
        section_stats = {}
        for section_dir in self.vault_path.glob("[0-9][0-9]_*"):
            if section_dir.is_dir() and not section_dir.name.startswith("00_"):
                pages = list(section_dir.glob("*.md"))
                # Filter out index files
                content_pages = [p for p in pages if not p.stem == section_dir.name]
                section_stats[section_dir.name] = len(content_pages)
        
        index_content = f"""# 📚 My Knowledge Library

> **Your personal digital library of curated knowledge from videos**
> 
> *Last updated: {datetime.now().strftime("%B %d, %Y")}*

## 📊 Library Statistics

**📖 Total Sections:** {len(section_stats)}  
**📄 Total Pages:** {sum(section_stats.values())}  
**📅 Last Activity:** Today  
**🔄 Auto-Updated:** Yes  

## 📖 Library Sections

### 🤖 [[01_Artificial_Intelligence/01_Artificial_Intelligence|Artificial Intelligence]] 
*{section_stats.get('01_Artificial_Intelligence', 0)} pages*  
Everything about AI, Machine Learning, ChatGPT, and neural networks.

### 💰 [[02_Making_Money_with_AI/02_Making_Money_with_AI|Making Money with AI]]
*{section_stats.get('02_Making_Money_with_AI', 0)} pages*  
Business models, automation services, and AI products.

### 💻 [[03_Computer_Science/03_Computer_Science|Computer Science]]
*{section_stats.get('03_Computer_Science', 0)} pages*  
Programming, web development, algorithms, and software engineering.

### 🍎 [[04_Mac_and_Apple/04_Mac_and_Apple|Mac & Apple]]
*{section_stats.get('04_Mac_and_Apple', 0)} pages*  
macOS, iOS, Swift development, and Apple ecosystem.

### 🐧 [[05_Linux_and_DevOps/05_Linux_and_DevOps|Linux & DevOps]]
*{section_stats.get('05_Linux_and_DevOps', 0)} pages*  
Linux administration, Docker, Kubernetes, and cloud infrastructure.

### 📈 [[06_Productivity_and_Tools/06_Productivity_and_Tools|Productivity & Tools]]
*{section_stats.get('06_Productivity_and_Tools', 0)} pages*  
Workflow automation, note-taking, and digital organization.

---

## 📅 Recently Added Pages

```dataview
TABLE WITHOUT ID
  "[[" + file.name + "|📖 " + title + "]]" as "Latest Pages",
  section as "📚 Section",
  difficulty_level as "📊 Level",
  estimated_reading_time as "⏱️ Time"
FROM ""
WHERE type = "book_page"
SORT file.ctime DESC
LIMIT 8
```

## 🎯 Reading Recommendations

### 🟢 Beginner Friendly
```dataview
TABLE WITHOUT ID
  "[[" + file.name + "|" + title + "]]" as "📚 Start Here",
  section as "Section"
FROM ""
WHERE type = "book_page" AND difficulty_level = "beginner"
SORT page_number ASC
LIMIT 5
```

### 🔍 Quick Search Tips

- **`Ctrl/Cmd + O`** - Quick open any page
- **`Ctrl/Cmd + Shift + F`** - Search across entire library  
- **Click section links** - Browse by category
- **Use tags** - Find related content

## 🏷️ Popular Topics

```dataview
TABLE WITHOUT ID
  choice(length(rows) = 1, "[[" + rows[0].file.name + "|" + key + "]]", key + " (" + length(rows) + " pages)") as "🏷️ Topic"
FROM ""
WHERE type = "book_page"
FLATTEN tags as tag
WHERE tag
GROUP BY tag as key
SORT length(rows) DESC
LIMIT 10
```

---

## 🚀 Getting Started

**New to your library?** Start with any 🟢 beginner page, or jump into a section that interests you most!

**📱 Mobile Access:** Install Obsidian mobile app and sync this vault for reading anywhere.

---

*🤖 This library is automatically organized and updated by your Knowledge Bot*
"""
        
        index_file = self.vault_path / "00_Index" / "Home.md"
        index_file.parent.mkdir(exist_ok=True)
        
        async with aiofiles.open(index_file, 'w', encoding='utf-8') as f:
            await f.write(index_content)


# Integration function for the bot
async def save_knowledge_entry_as_book(content: str, metadata: Dict[str, Any]) -> str:
    """Save knowledge entry in book format."""
    storage = BookStorage()
    return await storage.save_as_book_page(content, metadata)