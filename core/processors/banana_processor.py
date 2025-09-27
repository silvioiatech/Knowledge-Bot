"""Banana API processor for generating educational diagrams and flowcharts."""

from typing import List, Dict, Any, Optional
from io import BytesIO

import httpx
from loguru import logger
from PIL import Image

from config import Config
from core.models.content_models import ImagePlan, GeneratedImage


class BananaImageProcessor:
    """Processor for generating educational diagrams using OpenRouter image models."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=120.0,  # Image generation can take time
            headers={
                "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/knowledge-bot",
                "X-Title": "Knowledge Bot"
            }
        )
        self.model = Config.IMAGE_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
    
    async def generate_images(
        self,
        image_plans: List[ImagePlan],
        max_images: int = 5
    ) -> List[GeneratedImage]:
        """Generate images from image plans."""
        
        if not image_plans:
            logger.info("No image plans provided")
            return []
        
        # Sort by priority and limit
        sorted_plans = sorted(image_plans, key=lambda x: x.priority, reverse=True)[:max_images]
        
        generated_images = []
        
        for plan in sorted_plans:
            try:
                logger.info(f"Generating {plan.image_type} for section: {plan.placement_section}")
                
                # Generate enhanced prompt
                enhanced_prompt = self._enhance_prompt_for_education(plan)
                
                # Generate image
                image_data = await self._generate_single_image(enhanced_prompt, plan.image_type)
                
                if image_data:
                    # Create alt text
                    alt_text = self._generate_alt_text(plan)
                    
                    generated_image = GeneratedImage(
                        image_plan=plan,
                        image_url="",  # Will be set when uploaded
                        image_data=image_data,
                        alt_text=alt_text
                    )
                    
                    generated_images.append(generated_image)
                    logger.info(f"Successfully generated {plan.image_type}")
                
            except Exception as e:
                logger.error(f"Failed to generate {plan.image_type}: {e}")
                continue
        
        logger.info(f"Generated {len(generated_images)} images out of {len(sorted_plans)} planned")
        return generated_images
    
    def _enhance_prompt_for_education(self, plan: ImagePlan) -> str:
        """Enhance the prompt for educational content generation."""
        
        # Base educational style instructions
        base_instructions = """
Create a professional, educational diagram suitable for a textbook or technical documentation.
Style requirements:
- Clean, minimalist design with clear typography
- Professional color scheme (blues, greys, accent colors)
- Clear labels and readable text (minimum 12pt equivalent)
- Logical flow and organization
- High contrast for accessibility
- Vector-style appearance with crisp edges
        """
        
        # Type-specific enhancements
        type_enhancements = {
            "flowchart": """
Flowchart specific requirements:
- Use standard flowchart symbols (rectangles for processes, diamonds for decisions)
- Clear directional arrows
- Consistent spacing and alignment
- Decision points clearly labeled with Yes/No paths
- Start and end points clearly marked
            """,
            
            "architecture": """
Architecture diagram requirements:
- Show clear component boundaries and relationships
- Use boxes and connecting lines to show data flow
- Include component labels and brief descriptions
- Show interfaces and communication paths
- Use consistent iconography for similar components
            """,
            
            "sequence": """
Sequence diagram requirements:
- Clear timeline progression from left to right or top to bottom
- Distinct actors/participants clearly labeled
- Message arrows with descriptive labels
- Activation boxes where appropriate
- Clear temporal ordering of events
            """,
            
            "chart": """
Chart/graph requirements:
- Clear axes labels and scales
- Legend if multiple data series
- Appropriate chart type for the data
- Clear title and subtitle
- Readable data point labels
- Professional color coding
            """,
            
            "diagram": """
Diagram requirements:
- Clear component relationships
- Consistent visual hierarchy
- Appropriate use of color for grouping/emphasis
- All elements clearly labeled
- Logical spatial organization
            """
        }
        
        # Get type-specific enhancement
        type_enhancement = type_enhancements.get(plan.image_type, type_enhancements["diagram"])
        
        # Combine all parts
        enhanced_prompt = f"""
{base_instructions}

{type_enhancement}

Content Description:
{plan.prompt}

Additional Context:
- This diagram is for an educational guide section: "{plan.placement_section}"
- Target audience: technical learners and professionals
- Should complement written educational content
- Must be self-explanatory and informative

Generate a professional, educational {plan.image_type} that clearly illustrates the concept described above.
        """.strip()
        
        return enhanced_prompt
    
    async def _generate_single_image(
        self, 
        prompt: str, 
        image_type: str
    ) -> Optional[bytes]:
        """Generate a single image using OpenRouter image models."""
        
        logger.info(f"Generating {image_type} with OpenRouter image model")
        
        try:
            # Call OpenRouter image generation API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 1000,  # For image generation
                "temperature": 0.7
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                # Handle image generation response
                # For now, fallback to placeholder until proper image parsing is implemented
                logger.info("Image generation API called, using placeholder for demo")
                return self._create_placeholder_image(image_type, prompt)
            else:
                logger.warning(f"Image generation API returned {response.status_code}")
                return self._create_placeholder_image(image_type, prompt)
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            # Fallback to placeholder
            return self._create_placeholder_image(image_type, prompt)
    
    def _create_placeholder_image(self, image_type: str, prompt: str) -> bytes:
        """Create a placeholder image for demonstration."""
        
        try:
            # Create a simple placeholder image
            width, height = 800, 600
            
            # For placeholder - will be enhanced with actual image generation
            
            # Create image
            img = Image.new('RGB', (width, height), color='white')
            
            # For now, just return a solid color image as placeholder
            # In production, this would be replaced with actual API generation
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Placeholder creation failed: {e}")
            # Return minimal bytes if everything fails
            return b''
    
    def _generate_alt_text(self, plan: ImagePlan) -> str:
        """Generate descriptive alt text for accessibility."""
        
        return f"{plan.image_type.title()} diagram showing {plan.description} " \
               f"for the {plan.placement_section} section of the educational guide."
    
    async def should_generate_images(
        self,
        content_length: int,
        technical_complexity: str,
        image_plans: List[ImagePlan]
    ) -> bool:
        """Determine if images should be generated based on content analysis."""
        
        # Generate images if:
        # 1. Content is substantial (>2000 words)
        # 2. Technical complexity is intermediate or advanced
        # 3. We have high-priority image plans
        
        if content_length < 2000:
            logger.info("Content too short for image generation")
            return False
        
        if technical_complexity.lower() == "beginner" and len(image_plans) < 2:
            logger.info("Beginner content with few image plans - skipping generation")
            return False
        
        high_priority_plans = [p for p in image_plans if p.priority >= 3]
        if not high_priority_plans:
            logger.info("No high-priority image plans - skipping generation")
            return False
        
        logger.info("Content meets criteria for image generation")
        return True
    
    async def optimize_image_for_web(self, image_data: bytes) -> bytes:
        """Optimize image for web delivery."""
        
        try:
            # Load image
            img = Image.open(BytesIO(image_data))
            
            # Optimize: resize if too large, compress
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save with optimization
            output_buffer = BytesIO()
            img.save(
                output_buffer, 
                format='JPEG',
                quality=85,
                optimize=True
            )
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return image_data  # Return original if optimization fails
    
    async def upload_image_to_storage(self, image_data: bytes, filename: str) -> str:
        """Upload image to storage and return URL."""
        
        # Placeholder for image upload functionality
        # In production, this would upload to S3, Cloudinary, etc.
        
        logger.info(f"Uploading image: {filename}")
        
        # For MVP, return a placeholder URL
        placeholder_url = f"https://placeholder-storage.com/{filename}"
        
        return placeholder_url
    
    async def process_all_images(
        self,
        image_plans: List[ImagePlan],
        content_analysis: Dict[str, Any]
    ) -> List[GeneratedImage]:
        """Complete image processing pipeline."""
        
        # Check if we should generate images
        should_generate = await self.should_generate_images(
            content_length=content_analysis.get('word_count', 0),
            technical_complexity=content_analysis.get('difficulty', 'beginner'),
            image_plans=image_plans
        )
        
        if not should_generate:
            return []
        
        # Generate images
        generated_images = await self.generate_images(image_plans)
        
        # Process and upload each image
        processed_images = []
        for img in generated_images:
            try:
                # Optimize for web
                optimized_data = await self.optimize_image_for_web(img.image_data)
                
                # Generate filename
                filename = f"{img.image_plan.image_type}_{img.image_plan.placement_section}_{img.generation_timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                filename = filename.replace(" ", "_").replace("/", "_")
                
                # Upload to storage
                image_url = await self.upload_image_to_storage(optimized_data, filename)
                
                # Update image object
                img.image_url = image_url
                img.image_data = optimized_data
                
                processed_images.append(img)
                
            except Exception as e:
                logger.error(f"Failed to process image {img.image_plan.image_type}: {e}")
                continue
        
        return processed_images
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()