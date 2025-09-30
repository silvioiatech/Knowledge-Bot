"""GPT service for course/KB finalization and content formatting."""

import httpx
from loguru import logger

from config import Config
from core.models.content_models import GeminiAnalysis


class GPTFinalizerService:
    """GPT service for finalizing content into course/knowledge base format."""
    
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
        
        logger.info(f"Initialized GPT Finalizer with model: {self.model}")
    
    async def finalize_to_course_format(
        self, 
        markdown_from_claude: str, 
        analysis: GeminiAnalysis
    ) -> str:
        """Transform Claude's content into structured course/knowledge base format."""
        
        # Extract key metadata from analysis
        title = analysis.video_metadata.title or "Technical Course"
        main_topic = analysis.content_outline.main_topic
        difficulty = analysis.content_outline.difficulty_level
        key_concepts = analysis.content_outline.key_concepts[:5]
        learning_objectives = analysis.content_outline.learning_objectives[:3]
        
        finalize_prompt = f"""
Transform this educational content into a comprehensive course/knowledge base format.

COURSE METADATA:
- Title: {title}
- Subject: {main_topic}
- Difficulty: {difficulty}
- Key Concepts: {', '.join(key_concepts)}
- Learning Objectives: {', '.join(learning_objectives)}

SOURCE CONTENT:
{markdown_from_claude}

REQUIRED COURSE STRUCTURE:
1. **Course Overview** (2-3 sentences)
2. **Learning Objectives** (3-5 clear outcomes)
3. **Prerequisites** (what learners need to know)
4. **Course Modules/Chapters** (2-4 logical sections)
5. **Step-by-Step Labs/Exercises** (practical activities)
6. **Assessment/Quiz** (3-5 questions to test understanding)
7. **Glossary** (key terms and definitions)
8. **Resources & References** (additional learning materials)

FORMATTING REQUIREMENTS:
- Maintain YAML frontmatter at the top
- Add a Table of Contents after frontmatter
- Use clear headings (H1, H2, H3)
- Include code blocks where relevant
- Add practical examples and exercises
- Use callouts for important notes (> blockquotes)
- Ensure professional, educational tone
- Make content self-contained and comprehensive

OUTPUT: Return the complete course in markdown format, ready for knowledge base storage.
"""

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional course designer specializing in technical education. Create comprehensive, structured learning materials."
                        },
                        {
                            "role": "user", 
                            "content": finalize_prompt
                        }
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.2,  # Low temperature for consistent structure
                    "top_p": 0.9
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"GPT API error: {response.status_code} - {response.text}")
                return markdown_from_claude  # Return original if finalization fails
            
            result = response.json()
            finalized_content = result["choices"][0]["message"]["content"].strip()
            
            logger.success(f"Content finalized to course format - {len(finalized_content)} characters")
            return finalized_content
            
        except Exception as e:
            logger.error(f"GPT finalization failed: {e}")
            return markdown_from_claude  # Return original content if finalization fails
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()