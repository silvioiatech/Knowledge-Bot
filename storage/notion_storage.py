"""Notion database storage for Knowledge Bot."""

from typing import Dict, Any, List
from datetime import datetime
from notion_client import Client
from loguru import logger
from config import Config


class NotionStorage:
    """Handle saving knowledge entries to Notion database."""
    
    # Category mapping to emoji versions
    CATEGORY_MAPPING = {
        "artificial intelligence": "🤖 AI",
        "ai": "🤖 AI",
        "machine learning": "🤖 AI",
        "chatgpt": "🤖 AI",
        "llm": "🤖 AI",
        "gpt": "🤖 AI",
        "claude": "🤖 AI",
        "gemini": "🤖 AI",
        "neural network": "🤖 AI",
        "deep learning": "🤖 AI",
        
        "programming": "💻 PROGRAMMING",
        "coding": "💻 PROGRAMMING",
        "web development": "💻 PROGRAMMING",
        "python": "💻 PROGRAMMING",
        "javascript": "💻 PROGRAMMING",
        "react": "💻 PROGRAMMING",
        "nextjs": "💻 PROGRAMMING",
        "node": "💻 PROGRAMMING",
        "database": "💻 PROGRAMMING",
        "sql": "💻 PROGRAMMING",
        "git": "💻 PROGRAMMING",
        "vscode": "💻 PROGRAMMING",
        
        "linux": "🐧 LINUX",
        "ubuntu": "🐧 LINUX",
        "docker": "🐧 LINUX",
        "kubernetes": "🐧 LINUX",
        "devops": "🐧 LINUX",
        "aws": "🐧 LINUX",
        "cloud": "🐧 LINUX",
        "server": "🐧 LINUX",
        "terminal": "🐧 LINUX",
        "bash": "🐧 LINUX",
        
        "mac": "🍎 MAC",
        "macos": "🍎 MAC",
        "apple": "🍎 MAC",
        "ios": "🍎 MAC",
        "swift": "🍎 MAC",
        "xcode": "🍎 MAC",
        "iphone": "🍎 MAC",
        "ipad": "🍎 MAC",
        "shortcuts": "🍎 MAC",
        
        "ai business": "💰 MONETIZATION",
        "ai money": "💰 MONETIZATION",
        "business": "💰 MONETIZATION",
        "entrepreneurship": "💰 MONETIZATION",
        "freelance": "💰 MONETIZATION",
        "saas": "💰 MONETIZATION",
        "making money": "💰 MONETIZATION",
        "monetization": "💰 MONETIZATION",
        
        "productivity": "📈 PRODUCTIVITY",
        "automation": "📈 PRODUCTIVITY",
        "notion": "📈 PRODUCTIVITY",
        "obsidian": "📈 PRODUCTIVITY",
        "workflow": "📈 PRODUCTIVITY",
        "organization": "📈 PRODUCTIVITY",
        "time management": "📈 PRODUCTIVITY",
    }
    
    # Difficulty mapping
    DIFFICULTY_MAPPING = {
        "beginner": "🟢 Beginner",
        "intermediate": "🟡 Intermediate", 
        "advanced": "🔴 Advanced"
    }
    
    def __init__(self):
        """Initialize Notion client."""
        self.client = None
        self.database_id = Config.NOTION_DATABASE_ID
        
        if Config.NOTION_API_KEY:
            try:
                self.client = Client(auth=Config.NOTION_API_KEY)
                logger.info("Notion client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Notion client: {e}")
                raise
        else:
            logger.warning("Notion API key not provided")
            raise ValueError("Notion API key is required")
    
    def _determine_category(self, metadata: Dict[str, Any]) -> str:
        """Determine the category based on metadata."""
        subject = metadata.get('subject', '').lower()
        tags = [tag.lower() for tag in metadata.get('tags', [])]
        tools = [tool.lower() for tool in metadata.get('tools', [])]
        title = metadata.get('title', '').lower()
        
        # Combine all keywords for analysis
        all_keywords = [subject, title] + tags + tools
        all_keywords = [k for k in all_keywords if k]
        
        # Find best matching category
        for keyword in all_keywords:
            for pattern, category in self.CATEGORY_MAPPING.items():
                if pattern in keyword or keyword in pattern:
                    return category
        
        # Default category
        return "💻 PROGRAMMING"
    
    def _determine_subcategory(self, metadata: Dict[str, Any], category: str) -> str:
        """Determine subcategory based on category and metadata."""
        tools = metadata.get('tools', [])
        tags = metadata.get('tags', [])
        
        if category == "🤖 AI":
            if any(tool.lower() in ['chatgpt', 'gpt', 'openai'] for tool in tools):
                return "ChatGPT/OpenAI"
            elif any(tool.lower() in ['claude', 'anthropic'] for tool in tools):
                return "Claude/Anthropic"
            elif any(tool.lower() in ['gemini', 'google'] for tool in tools):
                return "Gemini/Google"
            elif any(tag.lower() in ['machine learning', 'ml'] for tag in tags):
                return "Machine Learning"
            else:
                return "General AI"
        
        elif category == "💻 PROGRAMMING":
            if any(tool.lower() in ['python'] for tool in tools):
                return "Python"
            elif any(tool.lower() in ['javascript', 'js', 'react', 'node'] for tool in tools):
                return "JavaScript"
            elif any(tool.lower() in ['web', 'html', 'css'] for tool in tools):
                return "Web Development"
            else:
                return "General Programming"
        
        elif category == "🐧 LINUX":
            if any(tool.lower() in ['docker'] for tool in tools):
                return "Docker"
            elif any(tool.lower() in ['kubernetes', 'k8s'] for tool in tools):
                return "Kubernetes"
            elif any(tool.lower() in ['aws', 'cloud'] for tool in tools):
                return "Cloud Services"
            else:
                return "System Administration"
        
        elif category == "🍎 MAC":
            if any(tool.lower() in ['ios', 'iphone', 'ipad'] for tool in tools):
                return "iOS Development"
            elif any(tool.lower() in ['swift'] for tool in tools):
                return "Swift Programming"
            else:
                return "macOS Tips"
        
        elif category == "💰 MONETIZATION":
            if any(tag.lower() in ['business', 'entrepreneurship'] for tag in tags):
                return "Business Strategy"
            elif any(tag.lower() in ['freelance'] for tag in tags):
                return "Freelancing"
            else:
                return "AI Business"
        
        elif category == "📈 PRODUCTIVITY":
            if any(tool.lower() in ['notion'] for tool in tools):
                return "Notion"
            elif any(tool.lower() in ['obsidian'] for tool in tools):
                return "Obsidian"
            else:
                return "Workflow Automation"
        
        return "General"
    
    def _determine_difficulty(self, metadata: Dict[str, Any]) -> str:
        """Determine difficulty level."""
        tools = metadata.get('tools', [])
        key_points = metadata.get('key_points', [])
        title = metadata.get('title', '').lower()
        
        # Combine content for analysis
        content_text = ' '.join([title] + key_points).lower()
        
        # Check for difficulty indicators
        advanced_indicators = ['advanced', 'expert', 'professional', 'complex', 'enterprise', 'production']
        beginner_indicators = ['intro', 'basic', 'getting started', 'beginner', 'simple', 'easy', 'tutorial']
        
        if any(indicator in content_text for indicator in advanced_indicators) or len(tools) > 3:
            return self.DIFFICULTY_MAPPING['advanced']
        elif any(indicator in content_text for indicator in beginner_indicators):
            return self.DIFFICULTY_MAPPING['beginner']
        else:
            return self.DIFFICULTY_MAPPING['intermediate']
    
    def _convert_markdown_to_blocks(self, markdown_content: str) -> List[Dict]:
        """Convert markdown content to Notion blocks."""
        blocks = []
        lines = markdown_content.split('\n')
        current_paragraph = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                if current_paragraph:
                    # Add accumulated paragraph
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                i += 1
                continue
            
            # Headers
            if line.startswith('# '):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            elif line.startswith('### '):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
            
            # Code blocks
            elif line.startswith('```'):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                
                # Collect code block content
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                code_content = '\n'.join(code_lines)
                if code_content:
                    blocks.append({
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": code_content}}],
                            "language": "python"  # Default language
                        }
                    })
            
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if paragraph_text:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                            }
                        })
                    current_paragraph = []
                
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            
            # Regular paragraph content
            else:
                current_paragraph.append(line)
            
            i += 1
        
        # Add any remaining paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            if paragraph_text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph_text}}]
                    }
                })
        
        return blocks
    
    async def _get_database_properties(self) -> Dict[str, Any]:
        """Get the actual properties of the Notion database."""
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            return response.get('properties', {})
        except Exception as e:
            logger.warning(f"Failed to retrieve database schema: {e}")
            return {}

    async def save_entry(self, content: str, metadata: Dict[str, Any]) -> str:
        """Save entry to Notion database and return page URL."""
        try:
            if not self.client:
                raise ValueError("Notion client not initialized")
            
            # Get actual database properties to avoid errors
            db_properties = await self._get_database_properties()
            available_props = list(db_properties.keys())
            
            logger.info(f"Available Notion properties: {available_props}")
            
            # Determine category and difficulty
            category = self._determine_category(metadata)
            difficulty = self._determine_difficulty(metadata)
            
            # Start with minimal required properties
            properties = {}
            
            # Add title (required - try different possible names)
            title_content = metadata.get('title', 'Untitled')
            for title_prop in ['Title', 'Name', 'title', 'name']:
                if title_prop in available_props:
                    prop_config = db_properties[title_prop]
                    if prop_config.get('type') == 'title':
                        properties[title_prop] = {
                            "title": [{"type": "text", "text": {"content": title_content}}]
                        }
                        break
            
            # Add other properties only if they exist in the database
            if metadata.get('original_url'):
                for url_prop in ['Source', 'URL', 'Source Video', 'Video URL', 'Link']:
                    if url_prop in available_props:
                        prop_config = db_properties[url_prop]
                        if prop_config.get('type') == 'url':
                            properties[url_prop] = {"url": metadata.get('original_url', '')}
                            break
            
            # Category
            for cat_prop in ['Category', 'Type', 'Subject', 'Topic']:
                if cat_prop in available_props:
                    prop_config = db_properties[cat_prop]
                    if prop_config.get('type') == 'select':
                        properties[cat_prop] = {"select": {"name": category}}
                        break
            
            # Tags
            if metadata.get('tags'):
                for tag_prop in ['Tags', 'Labels', 'Keywords']:
                    if tag_prop in available_props:
                        prop_config = db_properties[tag_prop]
                        if prop_config.get('type') == 'multi_select':
                            properties[tag_prop] = {
                                "multi_select": [{"name": tag} for tag in metadata['tags'][:10]]
                            }
                            break
            
            # Tools
            if metadata.get('tools'):
                for tools_prop in ['Tools', 'Tools Mentioned', 'Software', 'Technologies']:
                    if tools_prop in available_props:
                        prop_config = db_properties[tools_prop]
                        if prop_config.get('type') == 'multi_select':
                            properties[tools_prop] = {
                                "multi_select": [{"name": tool} for tool in metadata['tools'][:10]]
                            }
                            break
            
            # Platform
            if metadata.get('platform'):
                for platform_prop in ['Platform', 'Source Platform', 'Video Platform']:
                    if platform_prop in available_props:
                        prop_config = db_properties[platform_prop]
                        if prop_config.get('type') == 'select':
                            properties[platform_prop] = {
                                "select": {"name": metadata['platform'].title()}
                            }
                            break
            
            # Difficulty
            for diff_prop in ['Difficulty', 'Level', 'Complexity']:
                if diff_prop in available_props:
                    prop_config = db_properties[diff_prop]
                    if prop_config.get('type') == 'select':
                        properties[diff_prop] = {"select": {"name": difficulty}}
                        break
            
            # Date
            for date_prop in ['Date', 'Created', 'Added', 'Date Added']:
                if date_prop in available_props:
                    prop_config = db_properties[date_prop]
                    if prop_config.get('type') == 'date':
                        properties[date_prop] = {
                            "date": {"start": datetime.now().isoformat()}
                        }
                        break
            
            logger.info(f"Using properties: {list(properties.keys())}")
            
            # Convert content to Notion blocks
            content_blocks = self._convert_markdown_to_blocks(content)
            
            # Create the page
            logger.info(f"Creating Notion page: {title_content}")
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=content_blocks
            )
            
            page_url = response.get('url', '')
            
            logger.success(f"Notion page created successfully: {page_url}")
            
            return page_url
            
        except Exception as e:
            error_msg = str(e)
            if "property" in error_msg.lower() and "not" in error_msg.lower():
                logger.error(f"Notion database schema mismatch: {e}")
                logger.info("The bot will automatically detect available properties in your database")
                
                # Try with absolutely minimal properties
                try:
                    minimal_properties = {}
                    # Find any title property
                    db_props = await self._get_database_properties()
                    for prop_name, prop_config in db_props.items():
                        if prop_config.get('type') == 'title':
                            minimal_properties[prop_name] = {
                                "title": [{"type": "text", "text": {"content": metadata.get('title', 'Untitled')}}]
                            }
                            break
                    
                    if minimal_properties:
                        content_blocks = self._convert_markdown_to_blocks(content)
                        response = self.client.pages.create(
                            parent={"database_id": self.database_id},
                            properties=minimal_properties,
                            children=content_blocks
                        )
                        logger.success("Created page with minimal properties")
                        return response.get('url', '')
                    else:
                        raise Exception("No title property found in database")
                        
                except Exception as minimal_error:
                    logger.error(f"Even minimal page creation failed: {minimal_error}")
                    raise
            else:
                logger.error(f"Failed to save entry to Notion: {e}")
                raise


# Integration function for the bot
async def save_knowledge_entry_to_notion(content: str, metadata: Dict[str, Any]) -> str:
    """Save knowledge entry to Notion database."""
    storage = NotionStorage()
    return await storage.save_entry(content, metadata)