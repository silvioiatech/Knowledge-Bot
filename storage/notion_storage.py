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
        tools = [t.lower() for t in metadata.get('tools', [])]
        tags = [t.lower() for t in metadata.get('tags', [])]
        title = metadata.get('title', '').lower()
        key_points = ' '.join(metadata.get('key_points', [])).lower()
        
        # Combine all text for better detection
        all_text = f"{title} {' '.join(tools)} {' '.join(tags)} {key_points}"
        
        if category == "🤖 AI":
            # Check for specific AI subcategories
            if any(word in all_text for word in ['agent', 'multi-agent', 'autonomous', 'orchestration']):
                return "Agents"
            elif any(word in all_text for word in ['chatgpt', 'gpt-4', 'openai']):
                return "Programs"  
            elif any(word in all_text for word in ['automation', 'workflow', 'pipeline']):
                return "Automations"
            elif any(word in all_text for word in ['claude', 'anthropic']):
                return "Programs"
            elif any(word in all_text for word in ['gemini', 'bard', 'google ai']):
                return "Programs"
            elif any(word in all_text for word in ['llm', 'language model', 'transformer']):
                return "Models"
            elif any(word in all_text for word in ['prompt', 'prompting']):
                return "Prompting"
            else:
                return "General"
        
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
            
            # Determine category, subcategory and difficulty
            category = self._determine_category(metadata)
            subcategory = self._determine_subcategory(metadata, category)
            difficulty = self._determine_difficulty(metadata)
            
            if logger:
                logger.info(f"Category: {category}, Subcategory: {subcategory}")
            
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
            
            # Add subcategory - CHECK FOR EXACT PROPERTY NAME IN YOUR DATABASE
            for sub_prop in ['Subcategory', 'Sub-category', 'SubCategory']:
                if sub_prop in available_props:
                    prop_config = db_properties[sub_prop]
                    if prop_config.get('type') == 'select':
                        properties[sub_prop] = {"select": {"name": subcategory}}
                        if logger:
                            logger.info(f"Setting subcategory: {subcategory}")
                        break
            
            # Tags
            if metadata.get('tags'):
                for tag_prop in ['Tags', 'Labels', 'Keywords']:
                    if tag_prop in available_props:
                        prop_config = db_properties[tag_prop]
                        if prop_config.get('type') == 'multi_select':
                            # Handle both list and string formats
                            tags_list = metadata['tags']
                            if isinstance(tags_list, str):
                                # Split comma-separated string and clean up
                                tags_list = [tag.strip() for tag in tags_list.split(',')]
                            
                            # Clean up tag names to avoid Notion validation errors
                            cleaned_tags = []
                            for tag in tags_list[:10]:
                                # Remove commas and limit length
                                clean_tag = str(tag).replace(',', ' -').strip()[:100]
                                if clean_tag:
                                    cleaned_tags.append(clean_tag)
                            
                            properties[tag_prop] = {
                                "multi_select": [{"name": tag} for tag in cleaned_tags]
                            }
                            break
            
            # Tools
            if metadata.get('tools'):
                for tools_prop in ['Tools', 'Tools Mentioned', 'Software', 'Technologies']:
                    if tools_prop in available_props:
                        prop_config = db_properties[tools_prop]
                        if prop_config.get('type') == 'multi_select':
                            # Handle both list and string formats
                            tools_list = metadata['tools']
                            if isinstance(tools_list, str):
                                # Split comma-separated string and clean up
                                tools_list = [tool.strip() for tool in tools_list.split(',')]
                            
                            # Clean up tool names to avoid Notion validation errors
                            cleaned_tools = []
                            for tool in tools_list[:10]:
                                # Remove commas and limit length
                                clean_tool = str(tool).replace(',', ' -').strip()[:100]
                                if clean_tool:
                                    cleaned_tools.append(clean_tool)
                            
                            properties[tools_prop] = {
                                "multi_select": [{"name": tool} for tool in cleaned_tools]
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
            
            # Content Quality - determine based on word count and completeness
            content_quality = self._determine_content_quality(content, metadata)
            if 'Content Quality' in available_props:
                prop_config = db_properties['Content Quality']
                if prop_config.get('type') == 'select':
                    properties['Content Quality'] = {"select": {"name": content_quality}}
            
            # Cross References - analyze content for reference types
            cross_references = self._determine_cross_references(content, metadata)
            if 'Cross References' in available_props and cross_references:
                prop_config = db_properties['Cross References']
                if prop_config.get('type') == 'multi_select':
                    properties['Cross References'] = {
                        "multi_select": [{"name": ref} for ref in cross_references]
                    }
            
            # Gemini Confidence - extract from analysis metadata
            if 'Gemini Confidence' in available_props:
                confidence = metadata.get('confidence_score', metadata.get('analysis_confidence', 85))
                prop_config = db_properties['Gemini Confidence']
                if prop_config.get('type') == 'number':
                    properties['Gemini Confidence'] = {"number": confidence}
            
            # Key Points - format as readable text
            if 'Key Points' in available_props and metadata.get('key_points'):
                key_points_text = self._format_key_points(metadata.get('key_points', []))
                prop_config = db_properties['Key Points']
                if prop_config.get('type') == 'rich_text':
                    properties['Key Points'] = {
                        "rich_text": [{"type": "text", "text": {"content": key_points_text}}]
                    }
                elif prop_config.get('type') == 'text':
                    properties['Key Points'] = {
                        "rich_text": [{"type": "text", "text": {"content": key_points_text}}]
                    }
            
            # Platform Specific - determine from content and tools
            platform_specific = self._determine_platform_specific(content, metadata)
            if 'Platform Specific' in available_props and platform_specific:
                prop_config = db_properties['Platform Specific']
                if prop_config.get('type') == 'multi_select':
                    properties['Platform Specific'] = {
                        "multi_select": [{"name": platform} for platform in platform_specific]
                    }
            
            # Word Count - count actual words in generated content
            if 'Word Count' in available_props:
                word_count = len(content.split())
                prop_config = db_properties['Word Count']
                if prop_config.get('type') == 'number':
                    properties['Word Count'] = {"number": word_count}
            
            # Processing Date - set to current date
            if 'Processing Date' in available_props:
                prop_config = db_properties['Processing Date']
                if prop_config.get('type') == 'date':
                    properties['Processing Date'] = {
                        "date": {"start": datetime.now().isoformat()}
                    }
            
            # Date (fallback for other date fields)
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

    def _determine_content_quality(self, content: str, metadata: Dict[str, Any]) -> str:
        """Determine content quality based on word count, completeness, and structure."""
        word_count = len(content.split())
        
        # Check for structure indicators
        has_headers = '##' in content or '#' in content
        has_code = '```' in content
        has_examples = any(word in content.lower() for word in ['example', 'implementation', 'usage'])
        has_best_practices = 'best practice' in content.lower() or 'recommended' in content.lower()
        
        # Quality scoring
        quality_score = 0
        
        # Word count scoring
        if word_count >= 2500:
            quality_score += 3
        elif word_count >= 1500:
            quality_score += 2
        elif word_count >= 800:
            quality_score += 1
        
        # Structure scoring
        if has_headers:
            quality_score += 1
        if has_code:
            quality_score += 1
        if has_examples:
            quality_score += 1
        if has_best_practices:
            quality_score += 1
        
        # Determine quality level
        if quality_score >= 6:
            return "⭐⭐⭐⭐⭐ Production Ready"
        elif quality_score >= 5:
            return "⭐⭐⭐⭐ Excellent"
        elif quality_score >= 3:
            return "⭐⭐⭐ Good"
        elif quality_score >= 2:
            return "⭐⭐ Basic"
        else:
            return "⭐ Raw"
    
    def _determine_cross_references(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Determine cross-reference types based on content analysis."""
        references = []
        content_lower = content.lower()
        
        # Check for prerequisites
        if any(word in content_lower for word in ['prerequisite', 'requirement', 'before', 'setup', 'install']):
            references.append("Prerequisites")
        
        # Check for related topics
        if any(word in content_lower for word in ['related', 'similar', 'also see', 'alternative', 'comparison']):
            references.append("Related")
        
        # Check for advanced topics
        if any(word in content_lower for word in ['advanced', 'complex', 'enterprise', 'production', 'optimization']):
            references.append("Advanced Topics")
        
        return references
    
    def _format_key_points(self, key_points: List[str]) -> str:
        """Format key points as readable numbered list."""
        if not key_points:
            return ""
        
        formatted_points = []
        for i, point in enumerate(key_points[:8], 1):  # Limit to 8 points
            # Clean up the point
            clean_point = point.strip()
            if not clean_point.endswith('.'):
                clean_point += '.'
            formatted_points.append(f"{i}. {clean_point}")
        
        return '\n'.join(formatted_points)
    
    def _determine_platform_specific(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Determine platform specificity from content and metadata."""
        platforms = []
        content_lower = content.lower()
        tools = [tool.lower() for tool in metadata.get('tools', [])]
        title_lower = metadata.get('title', '').lower()
        
        # Combine text for analysis
        all_text = f"{content_lower} {' '.join(tools)} {title_lower}"
        
        # Platform detection
        if any(word in all_text for word in ['macos', 'mac os', 'apple', 'xcode', 'homebrew', 'finder']):
            platforms.append("macOS")
        
        if any(word in all_text for word in ['linux', 'ubuntu', 'debian', 'fedora', 'centos', 'bash', 'apt', 'yum']):
            platforms.append("Linux")
        
        if any(word in all_text for word in ['windows', 'powershell', 'cmd', 'chocolatey', 'winget']):
            platforms.append("Windows")
        
        if any(word in all_text for word in ['ios', 'iphone', 'ipad', 'swift', 'objective-c']):
            platforms.append("iOS")
        
        if any(word in all_text for word in ['android', 'kotlin', 'java', 'gradle']):
            platforms.append("Android")
        
        # If no specific platforms detected, check for universal indicators
        if not platforms:
            if any(word in all_text for word in ['cross-platform', 'multiplatform', 'universal', 'web', 'browser', 'cloud']):
                platforms.append("Universal")
        
        # Default to Universal if still no platforms and content seems general
        if not platforms and len(content.split()) > 500:
            platforms.append("Universal")
        
        return platforms


# Integration function for the bot
async def save_knowledge_entry_to_notion(content: str, metadata: Dict[str, Any]) -> str:
    """Save knowledge entry to Notion database."""
    storage = NotionStorage()
    return await storage.save_entry(content, metadata)