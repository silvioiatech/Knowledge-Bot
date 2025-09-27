"""Claude service for content enrichment via OpenRouter."""

import asyncio
import json
from typing import Dict, Any, List

import httpx
from loguru import logger

from config import Config
from core.models.content_models import GeminiAnalysis


class ClaudeServiceError(Exception):
    """Custom exception for Claude service errors."""
    pass


class ClaudeService:
    """Service for enriching content using Claude via OpenRouter."""
    
    def __init__(self):
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        self.http_client = httpx.AsyncClient(
            timeout=120,
            headers={
                "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://knowledge-bot.dev",
                "X-Title": "Knowledge Bot"
            }
        )
    
    async def enrich_content(self, analysis: GeminiAnalysis) -> str:
        """Enrich Gemini analysis into comprehensive educational content."""
        logger.info("Starting Claude content enrichment via OpenRouter")
        
        try:
            # Create enrichment prompt
            prompt = self._create_enrichment_prompt(analysis)
            
            # Call OpenRouter Claude API
            response = await self.http_client.post(
                f"{Config.OPENROUTER_BASE_URL}/chat/completions",
                json={
                    "model": Config.CLAUDE_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert educational content creator specializing in transforming technical video analysis into comprehensive, textbook-quality learning materials."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": Config.OPENROUTER_MAX_TOKENS,
                    "temperature": 0.7,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise ClaudeServiceError(f"API error: {response.status_code}")
            
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                raise ClaudeServiceError("No response from Claude API")
            
            enriched_content = result['choices'][0]['message']['content']
            
            logger.success("Claude enrichment completed via OpenRouter")
            return enriched_content
            
        except httpx.RequestError as e:
            logger.error(f"HTTP request failed: {e}")
            raise ClaudeServiceError(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Content enrichment failed: {e}")
            raise ClaudeServiceError(f"Enrichment failed: {e}")
    
    def _create_enrichment_prompt(self, analysis: GeminiAnalysis) -> str:
        """Create comprehensive prompt for Claude enrichment."""
        
        # Extract key information
        title = analysis.video_metadata.title or "Technical Tutorial"
        main_topic = analysis.content_outline.main_topic
        difficulty = analysis.content_outline.difficulty_level
        
        # Extract entities and concepts
        key_concepts = [e.name for e in analysis.entities if e.type in ['concept', 'technology']][:8]
        tools_mentioned = [e.name for e in analysis.entities if e.type == 'technology'][:5]
        
        # Extract research findings if available
        research_summary = ""
        if hasattr(analysis, 'fact_checks') and analysis.fact_checks:
            research_topics = [r.get('query', '') for r in analysis.fact_checks[:3]]
            research_summary = f"\nWeb Research Conducted: {', '.join(research_topics)}"
        
        # Get transcript content
        transcript_text = ""
        if analysis.transcript:
            try:
                if hasattr(analysis.transcript[0], 'text'):
                    transcript_text = " ".join([seg.text for seg in analysis.transcript[:10]])
                else:
                    transcript_text = " ".join([seg.get('text', '') for seg in analysis.transcript[:10]])
            except:
                transcript_text = "Transcript processing error"
        
        prompt = f"""
Transform this technical video analysis into a comprehensive educational guide:

**Video Title:** {title}
**Main Topic:** {main_topic}
**Difficulty Level:** {difficulty}
**Key Concepts:** {', '.join(key_concepts) if key_concepts else 'Various technical concepts'}
**Tools/Technologies:** {', '.join(tools_mentioned) if tools_mentioned else 'Not specified'}
{research_summary}

**Video Content Preview:** {transcript_text[:500]}...

**Your Task:**
Create a comprehensive, textbook-quality educational guide that transforms this video content into structured learning material. 

**Required Structure:**
1. **Executive Summary** (2-3 sentences overview)
2. **Learning Objectives** (what readers will learn)  
3. **Prerequisites** (required background knowledge)
4. **Core Concepts** (detailed explanations of key ideas)
5. **Technical Implementation** (practical examples and code if applicable)
6. **Best Practices** (industry standards and recommendations)
7. **Common Pitfalls** (mistakes to avoid)
8. **Advanced Applications** (real-world use cases)
9. **Further Learning** (next steps and resources)

**Writing Guidelines:**
- Use clear, educational language appropriate for {difficulty} level
- Include practical examples and analogies
- Structure with headers, bullet points, and numbered lists
- Add code snippets where relevant (use ```language syntax```)
- Include [DIAGRAM: Description] placeholders for technical concepts that would benefit from visual aids
- Maintain an engaging, informative tone
- Ensure content is comprehensive yet accessible

**Quality Standards:**
- Minimum 2000 words of substantive educational content
- Technical accuracy and up-to-date information
- Clear progression from basic to advanced concepts
- Actionable insights and practical applications

Transform the video analysis into educational content that could serve as a chapter in a technical textbook or comprehensive tutorial.
"""
        
        return prompt
    
    async def generate_executive_summary(self, analysis: GeminiAnalysis) -> str:
        """Generate a quick executive summary for preview purposes."""
        try:
            summary_prompt = f"""
Based on this video analysis, create a concise 3-sentence executive summary:

Topic: {analysis.content_outline.main_topic}
Key Concepts: {', '.join([e.name for e in analysis.entities[:5]])}
Difficulty: {analysis.content_outline.difficulty_level}

Provide a clear, informative summary that captures the essence of what this video teaches.
"""
            
            response = await self.http_client.post(
                f"{Config.OPENROUTER_BASE_URL}/chat/completions",
                json={
                    "model": Config.CLAUDE_MODEL,
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "max_tokens": 200,
                    "temperature": 0.5
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    return result['choices'][0]['message']['content']
            
            return "Comprehensive technical content covering key concepts and practical applications."
            
        except Exception as e:
            logger.warning(f"Executive summary generation failed: {e}")
            return "Technical tutorial with practical insights and implementation guidance."
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
