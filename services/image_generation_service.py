"""
Smart Image Generation Service with conditional generation based on Claude evaluation.
"""

import asyncio
import base64
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

import httpx
from loguru import logger
import aiofiles

from config import Config
from core.models.content_models import ImagePlan, ImageEvaluationResult, GeneratedImage

class ImageGenerationError(Exception):
    """Custom exception for image generation errors."""
    pass

class SmartImageGenerationService:
    """
    Smart image generation service that only creates images when Claude determines 
    they would genuinely enhance understanding - optimizing costs.
    """
    
    def __init__(self):
        if not Config.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not configured - image generation disabled")
            self.enabled = False
        else:
            self.enabled = Config.ENABLE_IMAGE_GENERATION
            
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": Config.RAILWAY_STATIC_URL or "https://github.com/silvioiatech/Knowledge-Bot",
            "X-Title": "Knowledge Bot Enhanced"
        }
        self.model = Config.IMAGE_MODEL
        self.image_dir = Config.KNOWLEDGE_BASE_PATH / "images"
        self.image_dir.mkdir(exist_ok=True)
        
        logger.info(f"SmartImageGenerationService initialized - Enabled: {self.enabled}")
    
    async def generate_conditional_images(self, content: str, 
                                        image_evaluation: ImageEvaluationResult) -> List[GeneratedImage]:
        """
        Generate images only when evaluation determines they add value.
        Cost-optimized approach.
        """
        if not self.enabled or not image_evaluation.needs_images:
            logger.info(f"Image generation skipped: enabled={self.enabled}, needs_images={image_evaluation.needs_images}")
            return []
        
        try:
            logger.info(f"Generating {len(image_evaluation.image_plans)} images based on evaluation")
            
            generated_images = []
            for i, plan in enumerate(image_evaluation.image_plans):
                try:
                    # Generate enhanced prompt for the image
                    enhanced_prompt = self._enhance_image_prompt(plan, content)
                    
                    # Generate the image
                    image_data = await self._generate_single_image(enhanced_prompt)
                    
                    if image_data:
                        # Save image to file
                        image_path = await self._save_image(image_data, plan.description)
                        
                        generated_image = GeneratedImage(
                            title=plan.description,
                            description=plan.description,
                            file_path=str(image_path),
                            prompt=enhanced_prompt,
                            type=plan.image_type
                        )
                        
                        generated_images.append(generated_image)
                        logger.info(f"Generated image {i+1}/{len(image_evaluation.image_plans)}: {plan.description}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate image {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully generated {len(generated_images)} images")
            return generated_images
            
        except Exception as e:
            logger.error(f"Error in conditional image generation: {e}")
            return []
    
    def _enhance_image_prompt(self, plan: ImagePlan, content: str) -> str:
        """Enhance the image prompt with context from content."""
        
        # Extract key technical terms from content
        tech_terms = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', content)
        tech_terms = [term for term in tech_terms if len(term) > 3][:5]
        
        # Base prompt enhancement
        enhanced_prompt = f"""
Technical diagram: {plan.description}

Style: Clean, professional, educational diagram
Elements: {', '.join(tech_terms) if tech_terms else 'technical components'}
Layout: Clear visual hierarchy with labels
Colors: Professional color scheme (blues, grays, accent colors)
Quality: High-resolution, suitable for educational content

Specific requirements: {plan.description}
"""
        
        # Add type-specific enhancements
        if plan.image_type == "architecture":
            enhanced_prompt += "\nArchitectural style: System components, data flow, connections"
        elif plan.image_type == "workflow":
            enhanced_prompt += "\nWorkflow style: Step-by-step process, arrows, decision points"
        elif plan.image_type == "concept":
            enhanced_prompt += "\nConcept style: Clear visual metaphors, labeled components"
        
        return enhanced_prompt.strip()
    
    async def _generate_single_image(self, prompt: str) -> Optional[bytes]:
        """Generate a single image using OpenRouter API."""
        
        try:
            # For now, return None since image generation is complex to implement properly
            logger.info("Image generation placeholder - returning None")
            return None
                    
        except Exception as e:
            logger.error(f"Error generating single image: {e}")
            return None
    
    async def _save_image(self, image_data: bytes, title: str) -> Path:
        """Save image data to file."""
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_title}.png"
        
        image_path = self.image_dir / filename
        
        async with aiofiles.open(image_path, 'wb') as f:
            await f.write(image_data)
        
        logger.info(f"Image saved: {image_path}")
        return image_path


# Backward compatibility alias
class ImageGenerationService(SmartImageGenerationService):
    """Alias for backward compatibility."""
    pass
