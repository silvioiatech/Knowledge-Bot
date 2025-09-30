"""GPT service for content polishing and final formatting."""

import json
from typing import Dict, Any, Optional
import httpx
from loguru import logger

from config import Config


class GPTContentPolisher:
    """GPT service specifically for polishing and formatting content for Notion."""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = Config.GPT_MODEL
        self.max_tokens = Config.GPT_MAX_TOKENS
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured for GPT service")
        
        self.client = httpx.AsyncClient(
            timeout=120,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://knowledge-bot.railway.app",
                "X-Title": "Enhanced Knowledge Bot"
            }
        )
        
        logger.info(f"Initialized GPT Content Polisher with model: {self.model}")
    
    async def polish_content_for_notion(
        self, 
        claude_content: str, 
        title: str, 
        category: str,
        source_url: str
    ) -> str:
        """Polish Claude's architectural content into clean, professional Notion format."""
        
        polish_prompt = f"""
You are a professional content editor specializing in technical documentation for Notion databases.

TASK: Transform this educational content into a polished, professional format optimized for Notion.

REQUIREMENTS:
1. **Clean Markdown Format**: Perfect for Notion import
2. **Professional Tone**: Educational but accessible
3. **Clear Structure**: Logical flow with proper headings
4. **Technical Accuracy**: Maintain all technical details
5. **Consistent Formatting**: Uniform style throughout
6. **Notion-Optimized**: Use Notion-friendly markdown features

CONTENT TO POLISH:
Title: {title}
Category: {category}
Source: {source_url}

Raw Content:
{claude_content}

POLISHING GUIDELINES:
- Use clear, engaging headings (H1, H2, H3)
- Create bulleted and numbered lists for better readability
- Add code blocks with proper syntax highlighting when relevant
- Include callout boxes for important notes (use > blockquotes)
- Ensure smooth transitions between sections
- Make technical concepts accessible to the target audience
- Remove any redundancy or unclear phrasing
- Add practical examples where appropriate
- Format any links properly
- Ensure perfect grammar and punctuation

OUTPUT FORMAT:
Return the polished content in clean markdown format, ready for Notion import.
Do not include any metadata headers - just the polished content.

Begin with the title as an H1, then provide the polished content.
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional technical content editor. Your job is to polish and format educational content for maximum clarity and impact."
                        },
                        {
                            "role": "user", 
                            "content": polish_prompt
                        }
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.3,  # Lower temperature for consistent formatting
                    "top_p": 0.9
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"GPT API error: {response.status_code} - {response.text}")
                return claude_content  # Return original if polishing fails
            
            result = response.json()
            polished_content = result["choices"][0]["message"]["content"].strip()
            
            logger.success(f"Content polished successfully - {len(polished_content)} characters")
            return polished_content
            
        except Exception as e:
            logger.error(f"GPT polishing failed: {e}")
            return claude_content  # Return original content if polishing fails
    
    async def enhance_notion_blocks(
        self, 
        content: str, 
        target_word_count: int = 2000
    ) -> str:
        """Enhance content specifically for Notion block structure."""
        
        enhance_prompt = f"""
Optimize this content for Notion's block-based structure.

TARGET: {target_word_count} words

REQUIREMENTS:
1. **Perfect Block Structure**: Each paragraph should be a clear Notion block
2. **Rich Formatting**: Use bold, italic, code, and lists effectively
3. **Logical Flow**: Clear progression from basic to advanced concepts
4. **Practical Focus**: Include actionable insights and examples
5. **Professional Polish**: Editorial quality suitable for knowledge base

Content to enhance:
{content}

OPTIMIZATION GUIDELINES:
- Break long paragraphs into digestible blocks
- Use subheadings to create clear sections
- Add practical examples with code blocks
- Include tips and best practices as callouts
- Ensure each block has a clear purpose
- Maintain technical accuracy while improving readability
- Add transitional phrases for better flow
- Include relevant terminology and definitions

Return the enhanced content in clean markdown format.
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a Notion content optimization specialist. Create perfectly structured content for knowledge bases."
                        },
                        {
                            "role": "user",
                            "content": enhance_prompt
                        }
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.2,
                    "top_p": 0.85
                }
            )
            
            if response.status_code != 200:
                logger.error(f"GPT block enhancement error: {response.status_code}")
                return content
            
            result = response.json()
            enhanced_content = result["choices"][0]["message"]["content"].strip()
            
            logger.success("Content enhanced for Notion blocks")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"GPT block enhancement failed: {e}")
            return content
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()