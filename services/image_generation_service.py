""""""Image generation service using OpenRouter API."""

Smart Image Generation Service with conditional generation based on Claude evaluation.

"""import asyncio

import base64

import asyncioimport re

import base64from typing import List, Dict, Any, Optional

import loggingfrom pathlib import Path

from datetime import datetime

from typing import List, Optional, Dict, Anyimport httpx

from pathlib import Pathfrom loguru import logger



import httpxfrom config import Config

import aiofiles

from config import Config

from core.models.content_models import ImagePlan, ImageEvaluationResult, GeneratedImageclass ImageGenerationError(Exception):

    """Custom exception for image generation errors."""

logger = logging.getLogger(__name__)    pass



class ImageGenerationError(Exception):

    """Custom exception for image generation errors."""class ImageGenerationService:

    pass    """Service for generating technical diagrams and images via OpenRouter."""

    

class SmartImageGenerationService:    def __init__(self):

    """        if not Config.OPENROUTER_API_KEY:

    Smart image generation service that only creates images when Claude determines             logger.warning("OPENROUTER_API_KEY not configured - image generation disabled")

    they would genuinely enhance understanding - optimizing costs.            self.enabled = False

    """        else:

                self.enabled = True

    def __init__(self):            

        self.base_url = "https://openrouter.ai/api/v1"        self.http_client = httpx.AsyncClient(

        self.headers = {            timeout=60,

            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",            headers={

            "HTTP-Referer": Config.RAILWAY_STATIC_URL or "https://github.com/silvioiatech/Knowledge-Bot",                "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",

            "X-Title": "Knowledge Bot - Smart Image Generation"                "Content-Type": "application/json",

        }                "HTTP-Referer": "https://knowledge-bot.dev",

        self.image_model = "google/gemini-2.5-flash-image-preview"                "X-Title": "Knowledge Bot"

                }

    async def generate_conditional_images(self, image_evaluation: ImageEvaluationResult,         )

                                        content_title: str) -> List[GeneratedImage]:        

        """        logger.info(f"Initialized diagram generator with model: {Config.IMAGE_MODEL}")

        Generate images only if Claude determined they would enhance understanding.    

        This replaces automatic generation with intelligent conditional generation.    async def generate_textbook_diagrams(self, content: str) -> str:

        """        """Generate technical diagrams for textbook content."""

        try:        if not self.enabled:

            if not image_evaluation.needs_images:            logger.info("Image generation disabled - skipping diagram generation")

                logger.info(f"Skipping image generation for '{content_title}': {image_evaluation.reasoning}")            return content

                return []        

                    logger.info("Starting technical diagram generation")

            logger.info(f"Generating {len(image_evaluation.image_plans)} images for '{content_title}' "        

                       f"(complexity: {image_evaluation.complexity_score}/10)")        try:

                        # Extract diagram placeholders from content

            generated_images = []            diagram_placeholders = self.extract_diagram_placeholders(content)

                        logger.debug(f"Found {len(diagram_placeholders)} diagram placeholders")

            # Generate images for each approved plan            

            for i, plan in enumerate(image_evaluation.image_plans):            if not diagram_placeholders:

                try:                logger.info("No diagram placeholders found in content")

                    image_data = await self._generate_single_image(plan, content_title, i)                return content

                    if image_data:            

                        generated_images.append(image_data)            # Generate diagrams for each placeholder

                                    generated_diagrams = []

                    # Add delay between generations to respect rate limits            for placeholder in diagram_placeholders:

                    if i < len(image_evaluation.image_plans) - 1:                try:

                        await asyncio.sleep(2)                    diagram_data = await self.generate_single_diagram(placeholder)

                                            generated_diagrams.append(diagram_data)

                except Exception as e:                except Exception as e:

                    logger.error(f"Failed to generate image {i+1} for '{content_title}': {e}")                    logger.error(f"Failed to generate diagram for '{placeholder['title']}': {e}")

                    continue                    continue

                        

            logger.info(f"Successfully generated {len(generated_images)}/{len(image_evaluation.image_plans)} "            # Integrate diagrams into content

                       f"images for '{content_title}'")            enhanced_content = self.integrate_diagrams_into_content(content, generated_diagrams)

                        logger.debug(f"Integrated {len(generated_diagrams)} diagrams into content")

            return generated_images            

                        return enhanced_content

        except Exception as e:            

            logger.error(f"Error in conditional image generation: {e}")        except Exception as e:

            return []            logger.error(f"Diagram generation failed: {e}")

                return content  # Return original content on error

    async def _generate_single_image(self, plan: ImagePlan, content_title: str,     

                                   index: int) -> Optional[GeneratedImage]:    def extract_diagram_placeholders(self, content: str) -> List[Dict[str, Any]]:

        """Generate a single image based on the plan."""        """Extract diagram placeholders from content."""

        try:        # Look for diagram markers like [DIAGRAM: title] or ![Diagram](placeholder)

            # Enhanced prompt for better image quality        placeholders = []

            enhanced_prompt = self._enhance_image_prompt(plan)        

                    # Pattern 1: [DIAGRAM: Title]

            logger.info(f"Generating {plan.image_type} image: {plan.description}")        diagram_pattern = r'\[DIAGRAM:\s*([^\]]+)\]'

                    matches = re.finditer(diagram_pattern, content, re.IGNORECASE)

            async with httpx.AsyncClient(timeout=60.0) as client:        

                response = await client.post(        for match in matches:

                    f"{self.base_url}/chat/completions",            title = match.group(1).strip()

                    headers=self.headers,            placeholders.append({

                    json={                'type': 'diagram',

                        "model": self.image_model,                'title': title,

                        "messages": [                'placeholder': match.group(0),

                            {                'position': match.start(),

                                "role": "user",                'context': self._extract_context(content, match.start(), match.end())

                                "content": enhanced_prompt            })

                            }        

                        ],        # Pattern 2: ![Diagram](diagram_placeholder)

                        "max_tokens": 1000,        image_pattern = r'!\[([^\]]*[Dd]iagram[^\]]*)\]\(([^)]*placeholder[^)]*)\)'

                        "temperature": 0.7        matches = re.finditer(image_pattern, content, re.IGNORECASE)

                    }        

                )        for match in matches:

                            title = match.group(1).strip()

                if response.status_code != 200:            placeholders.append({

                    logger.error(f"Image generation API error: {response.status_code} - {response.text}")                'type': 'image_placeholder',

                    return None                'title': title,

                                'placeholder': match.group(0),

                result = response.json()                'position': match.start(),

                                'context': self._extract_context(content, match.start(), match.end())

                # Extract image data from response            })

                image_url = self._extract_image_url(result)        

                if not image_url:        return placeholders

                    logger.error("No image URL found in response")    

                    return None    def _extract_context(self, content: str, start_pos: int, end_pos: int, context_length: int = 500) -> str:

                        """Extract surrounding context for better diagram generation."""

                # Download and save image        context_start = max(0, start_pos - context_length)

                image_data = await self._download_and_save_image(        context_end = min(len(content), end_pos + context_length)

                    image_url, content_title, plan.image_type, index        return content[context_start:context_end]

                )    

                    async def generate_single_diagram(self, placeholder: Dict[str, Any]) -> Dict[str, Any]:

                return GeneratedImage(        """Generate a single technical diagram."""

                    image_plan=plan,        if not self.enabled:

                    image_url=image_url,            raise ImageGenerationError("Image generation not enabled")

                    image_data=image_data,        

                    generation_timestamp=datetime.now(),        title = placeholder['title']

                    alt_text=self._generate_alt_text(plan)        context = placeholder.get('context', '')

                )        

                        # Create detailed prompt for technical diagram

        except Exception as e:        prompt = self._create_diagram_prompt(title, context)

            logger.error(f"Error generating single image: {e}")        

            return None        try:

                # Generate image via OpenRouter

    def _enhance_image_prompt(self, plan: ImagePlan) -> str:            response = await self.http_client.post(

        """Enhance the image prompt for better generation results."""                f"{Config.OPENROUTER_BASE_URL}/chat/completions",

        style_instructions = {                json={

            "flowchart": "Create a clean, professional flowchart with clear arrows and labeled boxes. Use a modern, minimalist design with consistent colors.",                    "model": Config.IMAGE_MODEL,

            "diagram": "Generate a technical diagram with clear labels, proper spacing, and professional styling. Use a clean white background.",                    "messages": [

            "sequence": "Create a sequence diagram showing the flow of interactions over time. Use standard UML sequence diagram conventions.",                        {

            "architecture": "Design a system architecture diagram with clearly labeled components, connections, and data flows. Use consistent geometric shapes.",                            "role": "user",

            "chart": "Create a clean data visualization chart with proper axes, labels, and legend. Use professional color scheme."                            "content": prompt

        }                        }

                            ],

        style_instruction = style_instructions.get(plan.image_type, "Create a clean, professional diagram")                    "max_tokens": 1000,

                            "temperature": 0.7

        enhanced_prompt = f"""                }

        {style_instruction}            )

                    

        Content: {plan.description}            if response.status_code != 200:

                        logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")

        Requirements:                raise ImageGenerationError(f"API error: {response.status_code}")

        - Professional, clean design            

        - Clear, readable labels            result = response.json()

        - Consistent color scheme            

        - High contrast for readability            # Extract image data from response

        - Suitable for educational content            if 'choices' in result and result['choices']:

        - Section placement: {plan.placement_section}                content_response = result['choices'][0]['message']['content']

                        

        Specific instructions: {plan.prompt}                # For now, return a placeholder since image generation varies by model

                        return {

        Generate a high-quality image that enhances understanding of the concept.                    'title': title,

        """                    'placeholder': placeholder['placeholder'],

                            'image_url': None,  # Would contain actual image URL/data

        return enhanced_prompt.strip()                    'alt_text': f"Technical diagram: {title}",

                        'description': content_response[:200] + "..." if len(content_response) > 200 else content_response

    def _extract_image_url(self, api_response: Dict[Any, Any]) -> Optional[str]:                }

        """Extract image URL from API response."""            else:

        try:                raise ImageGenerationError("No valid response from image generation API")

            # This will depend on the actual response format of Gemini 2.5 Flash Image Preview                

            # For now, assuming it returns in choices[0].message.content or a similar structure        except httpx.RequestError as e:

                        logger.error(f"HTTP request failed for diagram generation: {e}")

            content = api_response.get("choices", [{}])[0].get("message", {}).get("content", "")            raise ImageGenerationError(f"Request failed: {e}")

                

            # Look for image URLs in the response    def _create_diagram_prompt(self, title: str, context: str) -> str:

            if "http" in content:        """Create a detailed prompt for technical diagram generation."""

                # Extract URL - this is a simplified version        return f"""

                import reCreate a technical diagram for: "{title}"

                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

                urls = re.findall(url_pattern, content)Context from educational content:

                if urls:{context[:800]}

                    return urls[0]

            Requirements:

            # Check if response contains base64 image data- Clean, professional technical diagram

            if "data:image" in content:- Clear labels and annotations

                return content- Educational/instructional style

            - Suitable for technical documentation

            return None- High contrast for readability

            - Vector-style appearance preferred

        except Exception as e:

            logger.error(f"Error extracting image URL: {e}")The diagram should illustrate the technical concept clearly and be suitable for educational materials.

            return None"""

        

    async def _download_and_save_image(self, image_url: str, content_title: str,     def integrate_diagrams_into_content(self, content: str, diagrams: List[Dict[str, Any]]) -> str:

                                     image_type: str, index: int) -> Optional[bytes]:        """Integrate generated diagrams back into content."""

        """Download and save image to Railway storage."""        enhanced_content = content

        try:        

            # Create filename        # Sort diagrams by position (reverse order to maintain positions)

            safe_title = "".join(c for c in content_title if c.isalnum() or c in (' ', '-', '_')).rstrip()        diagrams.sort(key=lambda x: x.get('placeholder', {}).get('position', 0), reverse=True)

            safe_title = safe_title.replace(' ', '-').lower()[:30]        

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")        for diagram in diagrams:

            filename = f"{safe_title}_{image_type}_{index}_{timestamp}.png"            placeholder = diagram.get('placeholder', '')

                        if not placeholder:

            # Ensure images directory exists                continue

            images_dir = Path(Config.KNOWLEDGE_BASE_PATH) / "images"            

            images_dir.mkdir(parents=True, exist_ok=True)            # Create markdown for the diagram

                        if diagram.get('image_url'):

            image_path = images_dir / filename                replacement = f"![{diagram['alt_text']}]({diagram['image_url']})\n*{diagram['description']}*"

                        else:

            if image_url.startswith("data:image"):                # Fallback to descriptive text if image generation failed

                # Handle base64 encoded images                replacement = f"""

                header, encoded = image_url.split(",", 1)**{diagram['title']}**

                image_data = base64.b64decode(encoded){diagram.get('description', 'Technical diagram would be displayed here.')}

            else:"""

                # Download from URL            

                async with httpx.AsyncClient() as client:            # Replace placeholder with actual content

                    response = await client.get(image_url)            enhanced_content = enhanced_content.replace(placeholder, replacement)

                    if response.status_code == 200:        

                        image_data = response.content        logger.debug(f"Integrated {len(diagrams)} diagrams into content")

                    else:        return enhanced_content

                        logger.error(f"Failed to download image: {response.status_code}")    

                        return None    async def close(self):

                    """Clean up resources."""

            # Save to file        if hasattr(self, 'http_client'):

            async with aiofiles.open(image_path, 'wb') as f:            await self.http_client.aclose()

                await f.write(image_data)

            

            logger.info(f"Saved image: {filename}")# Backwards compatibility alias

            return image_dataclass DiagramGenerator(ImageGenerationService):

                """Backwards compatibility alias."""

        except Exception as e:    pass

            logger.error(f"Error downloading/saving image: {e}")
            return None
    
    def _generate_alt_text(self, plan: ImagePlan) -> str:
        """Generate appropriate alt text for the image."""
        return f"{plan.image_type.title()} showing {plan.description}"
    
    def insert_images_into_content(self, content: str, generated_images: List[GeneratedImage]) -> str:
        """
        Insert generated images into markdown content at appropriate locations.
        """
        if not generated_images:
            return content
        
        try:
            updated_content = content
            
            for i, image in enumerate(generated_images):
                plan = image.image_plan
                
                # Find the section to insert the image
                section_header = f"## {plan.placement_section}"
                
                # Create image markdown
                image_filename = f"images/{Path(image.image_url).name}" if not image.image_url.startswith("data:") else f"image_{i+1}.png"
                image_markdown = f"\n\n![{image.alt_text}]({image_filename})\n\n*{plan.description}*\n\n"
                
                # Insert after the section header
                if section_header in updated_content:
                    updated_content = updated_content.replace(
                        section_header,
                        section_header + image_markdown,
                        1  # Only replace first occurrence
                    )
                else:
                    # If section not found, add at the end
                    updated_content += f"\n\n## Visual Reference\n\n{image_markdown}"
            
            return updated_content
            
        except Exception as e:
            logger.error(f"Error inserting images into content: {e}")
            return content
    
    def get_generation_summary(self, image_evaluation: ImageEvaluationResult, 
                             generated_images: List[GeneratedImage]) -> str:
        """Generate a summary of the image generation process."""
        if not image_evaluation.needs_images:
            return f"💡 No images generated - {image_evaluation.reasoning}"
        
        if not generated_images:
            return f"❌ Image generation failed - attempted {len(image_evaluation.image_plans)} images"
        
        success_rate = len(generated_images) / len(image_evaluation.image_plans) * 100
        
        summary_parts = [
            f"🎨 Generated {len(generated_images)}/{len(image_evaluation.image_plans)} images ({success_rate:.0f}% success)",
            f"📊 Content complexity: {image_evaluation.complexity_score}/10",
            f"🎯 Content type: {image_evaluation.content_type}",
        ]
        
        if generated_images:
            image_types = [img.image_plan.image_type for img in generated_images]
            summary_parts.append(f"🖼️ Types: {', '.join(image_types)}")
        
        return "\n".join(summary_parts)

# For backward compatibility
class ImageGenerationService(SmartImageGenerationService):
    """Alias for backward compatibility."""
    pass