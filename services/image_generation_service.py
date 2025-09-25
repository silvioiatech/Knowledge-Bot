"""AI-powered technical diagram generation service using Gemini 2.5 Flash Image Preview."""

import asyncio
import base64
import re
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple

try:
    import httpx
    from loguru import logger
except ImportError:
    httpx = None
    logger = None

from config import Config


class DiagramGenerationError(Exception):
    """Custom exception for diagram generation errors."""
    pass


class DiagramGenerator:
    """Generate technical diagrams for textbook-quality content using Gemini 2.5 Flash Image Preview."""
    
    def __init__(self):
        """Initialize the diagram generator."""
        if not httpx:
            raise DiagramGenerationError("httpx not installed")
        
        if not Config.OPENROUTER_API_KEY:
            raise DiagramGenerationError("OPENROUTER_API_KEY not configured")
        
        if not Config.ENABLE_IMAGE_GENERATION:
            raise DiagramGenerationError("Image generation disabled in configuration")
        
        self.api_key = Config.OPENROUTER_API_KEY
        self.image_model = Config.IMAGE_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        self.max_images = Config.MAX_IMAGES_PER_ENTRY
        
        if logger:
            logger.info(f"Initialized diagram generator with model: {self.image_model}")
    
    async def generate_textbook_diagrams(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate 1-3 technical diagrams based on content analysis.
        
        Args:
            content: The enriched markdown content with [DIAGRAM: ...] placeholders
            metadata: Analysis metadata from Gemini
            
        Returns:
            List of generated diagram dictionaries with base64 data and descriptions
            
        Raises:
            DiagramGenerationError: If generation fails
        """
        try:
            if logger:
                logger.info("Starting technical diagram generation")
            
            # Extract diagram needs from content
            diagram_needs = self.extract_diagram_placeholders(content)
            
            if not diagram_needs:
                if logger:
                    logger.info("No diagram placeholders found in content")
                return []
            
            generated_images = []
            
            # Generate up to max_images diagrams
            for i, diagram_desc in enumerate(diagram_needs[:self.max_images]):
                try:
                    if logger:
                        logger.debug(f"Generating diagram {i+1}/{len(diagram_needs[:self.max_images])}: {diagram_desc}")
                    
                    # Create technical prompt for this diagram
                    prompt = self.create_technical_diagram_prompt(diagram_desc, metadata)
                    
                    # Generate the diagram
                    image_data = await self._call_image_generation_api(prompt)
                    
                    if image_data:
                        generated_images.append({
                            "description": diagram_desc,
                            "base64_data": image_data,
                            "position": i,
                            "placeholder": f"[DIAGRAM: {diagram_desc}]"
                        })
                        
                        if logger:
                            logger.success(f"Successfully generated diagram: {diagram_desc}")
                    
                except Exception as e:
                    if logger:
                        logger.warning(f"Failed to generate diagram '{diagram_desc}': {e}")
                    continue
            
            if logger:
                logger.success(f"Generated {len(generated_images)} technical diagrams")
            
            return generated_images
            
        except Exception as e:
            if logger:
                logger.error(f"Diagram generation failed: {e}")
            raise DiagramGenerationError(f"Failed to generate diagrams: {e}")
    
    def extract_diagram_placeholders(self, content: str) -> List[str]:
        """
        Extract [DIAGRAM: description] placeholders from content.
        
        Args:
            content: Markdown content with diagram placeholders
            
        Returns:
            List of diagram descriptions
        """
        # Regex to find [DIAGRAM: description] patterns
        pattern = r'\[DIAGRAM:\s*([^\]]+)\]'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        # Clean up descriptions
        descriptions = [match.strip() for match in matches]
        
        if logger:
            logger.debug(f"Found {len(descriptions)} diagram placeholders")
            
        return descriptions
    
    def create_technical_diagram_prompt(self, description: str, metadata: Dict[str, Any]) -> str:
        """
        Create detailed prompt for technical diagram generation.
        
        Args:
            description: Description of the diagram to generate
            metadata: Analysis metadata for context
            
        Returns:
            Detailed prompt for image generation
        """
        tools = metadata.get('tools', [])
        subject = metadata.get('subject', 'programming')
        production_ready = metadata.get('production_ready', False)
        platform_specific = metadata.get('platform_specific', [])
        
        # Determine diagram type and style
        diagram_type = self._classify_diagram_type(description)
        
        prompt = f"""Create a professional technical diagram for a textbook.

**Diagram Request:** {description}
**Context:** {subject} tutorial/reference
**Technologies:** {', '.join(tools[:5])}
**Environment:** {'Production' if production_ready else 'Development'}
**Platform:** {', '.join(platform_specific) if platform_specific else 'Universal'}

**Diagram Type:** {diagram_type}

**Requirements:**
- Clean, professional design suitable for technical documentation
- Use standard notation and symbols ({self._get_notation_style(diagram_type)})
- Include clear labels and annotations
- Add arrows showing data/control flow where applicable
- Use consistent color coding for different components
- Make it educational and easy to understand
- Technical accuracy is critical
- Include a legend if using symbols or color coding

**Style Guidelines:**
- Professional technical documentation style (not artistic)
- High contrast for readability
- Consistent typography and spacing
- Modern, clean aesthetic
- Suitable for both digital and print publication

**Content Focus:**
- Emphasize the key concepts being illustrated
- Show relationships between components clearly
- Include relevant technical details
- Make complex concepts visually accessible
- Support the learning objectives

Generate a high-quality technical diagram that would be appropriate for inclusion in a professional textbook or technical reference manual."""
        
        return prompt
    
    def _classify_diagram_type(self, description: str) -> str:
        """Classify the type of diagram based on description."""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['architecture', 'system', 'component']):
            return "System Architecture"
        elif any(keyword in description_lower for keyword in ['flow', 'process', 'workflow']):
            return "Process Flow"
        elif any(keyword in description_lower for keyword in ['database', 'schema', 'erd']):
            return "Database Schema"
        elif any(keyword in description_lower for keyword in ['network', 'topology', 'infrastructure']):
            return "Network Diagram"
        elif any(keyword in description_lower for keyword in ['api', 'request', 'response']):
            return "API Interaction"
        elif any(keyword in description_lower for keyword in ['decision', 'logic', 'algorithm']):
            return "Decision Tree"
        elif any(keyword in description_lower for keyword in ['hierarchy', 'tree', 'structure']):
            return "Hierarchical Structure"
        else:
            return "Technical Diagram"
    
    def _get_notation_style(self, diagram_type: str) -> str:
        """Get appropriate notation style for diagram type."""
        notation_map = {
            "System Architecture": "UML component diagrams, boxes and arrows",
            "Process Flow": "BPMN flowchart notation",
            "Database Schema": "ERD notation with relationships",
            "Network Diagram": "Network topology symbols",
            "API Interaction": "Sequence diagram notation",
            "Decision Tree": "Flowchart decision symbols",
            "Hierarchical Structure": "Tree diagram notation",
            "Technical Diagram": "Standard technical symbols"
        }
        return notation_map.get(diagram_type, "Standard technical symbols")
    
    async def _call_image_generation_api(self, prompt: str) -> Optional[str]:
        """
        Call Gemini 2.5 Flash Image Preview via OpenRouter.
        
        Args:
            prompt: The image generation prompt
            
        Returns:
            Base64 encoded image data or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/Knowledge-Bot",
                "X-Title": "Knowledge Bot - Diagram Generator"
            }
            
            payload = {
                "model": self.image_model,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "modalities": ["image", "text"],
                "max_tokens": 2000,
                "temperature": 0.3  # Lower temperature for consistent technical diagrams
            }
            
            async with httpx.AsyncClient(timeout=120) as client:  # Longer timeout for image generation
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract images from response
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]
                    images = message.get("images", [])
                    
                    if images and len(images) > 0:
                        # Return the first image's base64 data
                        return images[0].get("data")
                
                if logger:
                    logger.warning("No images found in API response")
                return None
                
        except Exception as e:
            if logger:
                logger.error(f"Image generation API call failed: {e}")
            return None
    
    def base64_to_file_info(self, base64_data: str, description: str) -> Dict[str, Any]:
        """
        Convert base64 image data to file information for storage.
        
        Args:
            base64_data: Base64 encoded image data
            description: Description of the diagram
            
        Returns:
            Dictionary with file information
        """
        try:
            # Decode base64 data
            image_bytes = base64.b64decode(base64_data)
            
            # Create a safe filename from description
            safe_filename = re.sub(r'[^\w\s-]', '', description)
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            filename = f"diagram-{safe_filename.lower()}.png"
            
            return {
                "filename": filename,
                "data": image_bytes,
                "size": len(image_bytes),
                "format": "PNG",
                "description": description
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to process base64 image data: {e}")
            raise DiagramGenerationError(f"Image processing failed: {e}")


def integrate_diagrams_into_content(content: str, diagrams: List[Dict[str, Any]]) -> str:
    """
    Integrate generated diagram references into the content.
    
    Args:
        content: Original markdown content with [DIAGRAM: ...] placeholders
        diagrams: List of generated diagrams
        
    Returns:
        Updated content with diagram references
    """
    updated_content = content
    
    for diagram in diagrams:
        placeholder = diagram["placeholder"]
        description = diagram["description"]
        
        # Replace placeholder with diagram reference
        diagram_reference = f"""
![{description}](diagram-{diagram['position']}.png)
*{description}*
"""
        
        updated_content = updated_content.replace(placeholder, diagram_reference)
    
    if logger:
        logger.debug(f"Integrated {len(diagrams)} diagrams into content")
    
    return updated_content


# Convenience function for external use
async def generate_content_diagrams(content: str, metadata: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate diagrams for content and return updated content with diagram list.
    
    Args:
        content: Markdown content with diagram placeholders
        metadata: Analysis metadata
        
    Returns:
        Tuple of (updated_content, diagram_list)
    """
    if not Config.ENABLE_IMAGE_GENERATION:
        if logger:
            logger.info("Image generation disabled, skipping diagram generation")
        return content, []
    
    try:
        generator = DiagramGenerator()
        diagrams = await generator.generate_textbook_diagrams(content, metadata)
        updated_content = integrate_diagrams_into_content(content, diagrams)
        return updated_content, diagrams
    
    except Exception as e:
        if logger:
            logger.warning(f"Diagram generation failed, continuing without images: {e}")
        return content, []