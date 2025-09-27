"""Image generation service using OpenRouter API."""

import asyncio
import base64
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

import httpx
from loguru import logger

from config import Config


class ImageGenerationError(Exception):
    """Custom exception for image generation errors."""
    pass


class ImageGenerationService:
    """Service for generating technical diagrams and images via OpenRouter."""
    
    def __init__(self):
        if not Config.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not configured - image generation disabled")
            self.enabled = False
        else:
            self.enabled = True
            
        self.http_client = httpx.AsyncClient(
            timeout=60,
            headers={
                "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://knowledge-bot.dev",
                "X-Title": "Knowledge Bot"
            }
        )
        
        logger.info(f"Initialized diagram generator with model: {Config.IMAGE_MODEL}")
    
    async def generate_textbook_diagrams(self, content: str) -> str:
        """Generate technical diagrams for textbook content."""
        if not self.enabled:
            logger.info("Image generation disabled - skipping diagram generation")
            return content
        
        logger.info("Starting technical diagram generation")
        
        try:
            # Extract diagram placeholders from content
            diagram_placeholders = self.extract_diagram_placeholders(content)
            logger.debug(f"Found {len(diagram_placeholders)} diagram placeholders")
            
            if not diagram_placeholders:
                logger.info("No diagram placeholders found in content")
                return content
            
            # Generate diagrams for each placeholder
            generated_diagrams = []
            for placeholder in diagram_placeholders:
                try:
                    diagram_data = await self.generate_single_diagram(placeholder)
                    generated_diagrams.append(diagram_data)
                except Exception as e:
                    logger.error(f"Failed to generate diagram for '{placeholder['title']}': {e}")
                    continue
            
            # Integrate diagrams into content
            enhanced_content = self.integrate_diagrams_into_content(content, generated_diagrams)
            logger.debug(f"Integrated {len(generated_diagrams)} diagrams into content")
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return content  # Return original content on error
    
    def extract_diagram_placeholders(self, content: str) -> List[Dict[str, Any]]:
        """Extract diagram placeholders from content."""
        # Look for diagram markers like [DIAGRAM: title] or ![Diagram](placeholder)
        placeholders = []
        
        # Pattern 1: [DIAGRAM: Title]
        diagram_pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
        matches = re.finditer(diagram_pattern, content, re.IGNORECASE)
        
        for match in matches:
            title = match.group(1).strip()
            placeholders.append({
                'type': 'diagram',
                'title': title,
                'placeholder': match.group(0),
                'position': match.start(),
                'context': self._extract_context(content, match.start(), match.end())
            })
        
        # Pattern 2: ![Diagram](diagram_placeholder)
        image_pattern = r'!\[([^\]]*[Dd]iagram[^\]]*)\]\(([^)]*placeholder[^)]*)\)'
        matches = re.finditer(image_pattern, content, re.IGNORECASE)
        
        for match in matches:
            title = match.group(1).strip()
            placeholders.append({
                'type': 'image_placeholder',
                'title': title,
                'placeholder': match.group(0),
                'position': match.start(),
                'context': self._extract_context(content, match.start(), match.end())
            })
        
        return placeholders
    
    def _extract_context(self, content: str, start_pos: int, end_pos: int, context_length: int = 500) -> str:
        """Extract surrounding context for better diagram generation."""
        context_start = max(0, start_pos - context_length)
        context_end = min(len(content), end_pos + context_length)
        return content[context_start:context_end]
    
    async def generate_single_diagram(self, placeholder: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single technical diagram."""
        if not self.enabled:
            raise ImageGenerationError("Image generation not enabled")
        
        title = placeholder['title']
        context = placeholder.get('context', '')
        
        # Create detailed prompt for technical diagram
        prompt = self._create_diagram_prompt(title, context)
        
        try:
            # Generate image via OpenRouter
            response = await self.http_client.post(
                f"{Config.OPENROUTER_BASE_URL}/chat/completions",
                json={
                    "model": Config.IMAGE_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise ImageGenerationError(f"API error: {response.status_code}")
            
            result = response.json()
            
            # Extract image data from response
            if 'choices' in result and result['choices']:
                content_response = result['choices'][0]['message']['content']
                
                # For now, return a placeholder since image generation varies by model
                return {
                    'title': title,
                    'placeholder': placeholder['placeholder'],
                    'image_url': None,  # Would contain actual image URL/data
                    'alt_text': f"Technical diagram: {title}",
                    'description': content_response[:200] + "..." if len(content_response) > 200 else content_response
                }
            else:
                raise ImageGenerationError("No valid response from image generation API")
                
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed for diagram generation: {e}")
            raise ImageGenerationError(f"Request failed: {e}")
    
    def _create_diagram_prompt(self, title: str, context: str) -> str:
        """Create a detailed prompt for technical diagram generation."""
        return f"""
Create a technical diagram for: "{title}"

Context from educational content:
{context[:800]}

Requirements:
- Clean, professional technical diagram
- Clear labels and annotations
- Educational/instructional style
- Suitable for technical documentation
- High contrast for readability
- Vector-style appearance preferred

The diagram should illustrate the technical concept clearly and be suitable for educational materials.
"""
    
    def integrate_diagrams_into_content(self, content: str, diagrams: List[Dict[str, Any]]) -> str:
        """Integrate generated diagrams back into content."""
        enhanced_content = content
        
        # Sort diagrams by position (reverse order to maintain positions)
        diagrams.sort(key=lambda x: x.get('placeholder', {}).get('position', 0), reverse=True)
        
        for diagram in diagrams:
            placeholder = diagram.get('placeholder', '')
            if not placeholder:
                continue
            
            # Create markdown for the diagram
            if diagram.get('image_url'):
                replacement = f"![{diagram['alt_text']}]({diagram['image_url']})\n*{diagram['description']}*"
            else:
                # Fallback to descriptive text if image generation failed
                replacement = f"""
**{diagram['title']}**
{diagram.get('description', 'Technical diagram would be displayed here.')}
"""
            
            # Replace placeholder with actual content
            enhanced_content = enhanced_content.replace(placeholder, replacement)
        
        logger.debug(f"Integrated {len(diagrams)} diagrams into content")
        return enhanced_content
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()


# Backwards compatibility alias
class DiagramGenerator(ImageGenerationService):
    """Backwards compatibility alias."""
    pass
