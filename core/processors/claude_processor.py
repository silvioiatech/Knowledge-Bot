"""Enhanced Claude processor for textbook-quality content generation."""

from typing import Dict, Any, List
import re

import httpx
from loguru import logger

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from core.models.content_models import (
    GeminiAnalysis, ClaudeOutput, ImagePlan
)


class EnhancedClaudeProcessor:
    """Enhanced Claude processor for creating comprehensive educational content."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        )
        self.model = CLAUDE_MODEL
    
    async def generate_textbook_content(
        self,
        analysis: GeminiAnalysis
    ) -> ClaudeOutput:
        """Generate comprehensive textbook-quality content from analysis."""
        
        logger.info(f"Generating textbook content for: {analysis.video_metadata.title}")
        
        try:
            # Create comprehensive prompt
            prompt = self._build_comprehensive_prompt(analysis)
            
            # Generate main content
            main_content = await self._generate_main_content(prompt)
            
            # Parse image plans from content
            image_plans = self._extract_image_plans(main_content)
            
            # Clean content (remove image plan markers)
            cleaned_content = self._clean_content_markers(main_content)
            
            # Create output object
            output = ClaudeOutput(
                markdown_content=cleaned_content,
                image_plans=image_plans
            )
            
            logger.info(f"Generated {output.word_count} words across {output.sections_count} sections")
            return output
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise
    
    def _build_comprehensive_prompt(self, analysis: GeminiAnalysis) -> str:
        """Build comprehensive prompt for textbook generation."""
        
        # Extract key information
        topic = analysis.content_outline.main_topic
        difficulty = analysis.content_outline.difficulty_level
        subtopics = analysis.content_outline.subtopics
        entities = [e.name for e in analysis.entities if e.confidence > 0.7]
        transcript_text = " ".join([seg.text for seg in analysis.transcript])
        
        # Build research facts section
        research_facts = []
        for fact in analysis.web_research_facts:
            if fact.confidence > 0.7:
                research_facts.append(f"- {fact.corrected_info} (Source: verified)")
        
        prompt = f"""
You are tasked with creating a comprehensive, textbook-quality educational guide based on video analysis data. This content will be saved as a professional knowledge base entry.

**CONTENT REQUIREMENTS:**
- Write 2500-3500 words of substantial, educational content
- Create a complete, self-contained learning resource
- Use proper academic structure with clear sections
- Include practical examples and real-world applications
- Maintain professional, educational tone throughout
- Generate complete sections - no truncation or "more content needed"

**VIDEO ANALYSIS DATA:**

**Main Topic:** {topic}
**Difficulty Level:** {difficulty}
**Key Subtopics:** {', '.join(subtopics[:10])}

**Key Entities/Technologies:**
{chr(10).join([f'- {entity}' for entity in entities[:15]])}

**Verified Facts & Claims:**
{chr(10).join(research_facts[:10])}

**Core Content (from transcript):**
{transcript_text[:2000]}...

**STRUCTURE REQUIREMENTS:**

# {topic}: Complete Guide

## 1. Overview and Introduction
- Comprehensive topic introduction
- Why this matters in current context
- Learning objectives and outcomes
- Prerequisites and background knowledge

## 2. Fundamental Concepts
- Core principles and definitions
- Key terminology with clear explanations
- Theoretical foundation
- Historical context where relevant

## 3. Technical Deep Dive
- Detailed technical explanation
- Step-by-step processes
- Architecture and implementation details
- Best practices and methodologies

## 4. Practical Applications
- Real-world use cases
- Industry applications
- Problem-solving examples
- Implementation strategies

## 5. Tools and Technologies
- Essential tools and platforms
- Setup and configuration guidance
- Feature comparisons
- Recommendations for different scenarios

## 6. Advanced Concepts
- Complex scenarios and edge cases
- Advanced techniques and optimizations
- Integration with other technologies
- Scaling and performance considerations

## 7. Common Challenges and Solutions
- Typical problems and pitfalls
- Debugging strategies
- Error handling approaches
- Performance optimization

## 8. Future Trends and Developments
- Emerging trends in the field
- Upcoming technologies and changes
- Career and learning path guidance
- Resources for continued learning

**IMAGE GENERATION INSTRUCTIONS:**
When appropriate sections would benefit from visual aids, include markers like this:
[IMAGE_PLAN: diagram_type | "Detailed description of the diagram needed" | section_name | priority_1-5]

Suitable diagram types: flowchart, architecture, sequence, chart, diagram, infographic

**QUALITY STANDARDS:**
- Each section should be 300-500 words minimum
- Include specific examples with code/configuration when applicable
- Use bullet points and numbered lists for clarity
- Add relevant technical specifications
- Ensure content flows logically between sections
- Make it comprehensive enough to serve as a complete reference

**WRITE THE COMPLETE GUIDE NOW:**
Generate the full, comprehensive guide following the structure above. Write substantial, detailed content for each section. This will be the final output - make it complete and professional.
        """
        
        return prompt
    
    async def _generate_main_content(self, prompt: str) -> str:
        """Generate main content using Claude API."""
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "max_tokens": 8000,  # Increased for comprehensive content
            "temperature": 0.3,
            "messages": messages
        }
        
        try:
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result['content'][0]['text']
            
            # Check if content appears truncated
            if self._is_content_truncated(content):
                logger.warning("Content appears truncated, attempting continuation...")
                content = await self._continue_content(content, messages)
            
            return content
            
        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            raise
    
    def _is_content_truncated(self, content: str) -> bool:
        """Check if content appears to be truncated."""
        # Look for signs of truncation
        truncation_indicators = [
            "...",
            "[Content continues",
            "[More details",
            "This section would include",
            "Additional information",
            content.endswith(("and", "or", "but", "the", "a", "an", ",", ":"))
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in truncation_indicators)
    
    async def _continue_content(self, partial_content: str, original_messages: List[Dict]) -> str:
        """Continue generating content if it was truncated."""
        
        continuation_prompt = f"""
The following content was generated but appears incomplete. Please continue and complete the guide, ensuring all sections are fully developed:

{partial_content}

CONTINUE FROM WHERE THIS LEFT OFF:
- Complete any unfinished sections
- Add the remaining sections if missing
- Ensure the guide reaches 2500-3500 words total
- Make sure all 8 sections are complete and substantial
- End with a proper conclusion
        """
        
        messages = original_messages + [
            {
                "role": "assistant", 
                "content": partial_content
            },
            {
                "role": "user",
                "content": continuation_prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "max_tokens": 6000,
            "temperature": 0.3,
            "messages": messages
        }
        
        try:
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            continuation = result['content'][0]['text']
            
            # Combine original and continuation
            complete_content = partial_content + "\n\n" + continuation
            return complete_content
            
        except Exception as e:
            logger.warning(f"Content continuation failed: {e}")
            return partial_content  # Return what we have
    
    def _extract_image_plans(self, content: str) -> List[ImagePlan]:
        """Extract image plan markers from content."""
        image_plans = []
        
        # Pattern: [IMAGE_PLAN: type | description | section | priority]
        pattern = r'\[IMAGE_PLAN:\s*([^|]+)\s*\|\s*"([^"]+)"\s*\|\s*([^|]+)\s*\|\s*priority_(\d+)\]'
        
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            image_type, description, section, priority = match
            
            # Create detailed prompt for image generation
            detailed_prompt = f"""
Create a {image_type.strip()} that illustrates: {description.strip()}

Context: This diagram is for the "{section.strip()}" section of an educational guide.
Style: Professional, clean, educational diagram suitable for a textbook.
Format: Clear labels, readable text, logical flow/organization.
            """.strip()
            
            image_plans.append(ImagePlan(
                image_type=image_type.strip(),
                description=description.strip(),
                placement_section=section.strip(),
                prompt=detailed_prompt,
                priority=int(priority)
            ))
        
        # Sort by priority (higher priority first)
        image_plans.sort(key=lambda x: x.priority, reverse=True)
        
        return image_plans
    
    def _clean_content_markers(self, content: str) -> str:
        """Remove image plan markers from final content."""
        # Remove IMAGE_PLAN markers
        pattern = r'\[IMAGE_PLAN:[^\]]+\]'
        cleaned = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    async def enhance_with_research(
        self,
        base_content: str,
        research_facts: List[Dict[str, Any]]
    ) -> str:
        """Enhance base content with additional research facts."""
        
        if not research_facts:
            return base_content
        
        research_context = "\n".join([
            f"- {fact.get('corrected_info', fact.get('text', ''))}"
            for fact in research_facts[:10]
        ])
        
        enhancement_prompt = f"""
The following educational content needs to be enhanced with additional verified facts and research:

EXISTING CONTENT:
{base_content[:1500]}...

ADDITIONAL VERIFIED FACTS TO INCORPORATE:
{research_context}

Please enhance the content by:
1. Integrating the additional facts naturally into relevant sections
2. Adding citations where appropriate
3. Expanding explanations with the new information
4. Maintaining the existing structure and flow
5. Ensuring factual accuracy and consistency

Return the enhanced version of the complete content.
        """
        
        messages = [
            {
                "role": "user",
                "content": enhancement_prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "max_tokens": 8000,
            "temperature": 0.2,
            "messages": messages
        }
        
        try:
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['content'][0]['text']
            
        except Exception as e:
            logger.warning(f"Content enhancement failed: {e}")
            return base_content  # Return original if enhancement fails
    
    async def generate_executive_summary(
        self,
        analysis: GeminiAnalysis
    ) -> str:
        """Generate executive summary for preview purposes."""
        
        prompt = f"""
Create a concise executive summary (200-300 words) for the following video analysis:

Topic: {analysis.content_outline.main_topic}
Quality Score: {analysis.quality_scores.overall}/100
Difficulty: {analysis.content_outline.difficulty_level}

Key Points:
{chr(10).join([f'- {claim.text}' for claim in analysis.claims[:5]])}

Entities Covered:
{', '.join([entity.name for entity in analysis.entities[:10]])}

Create a professional summary that highlights:
1. What the content covers
2. Key learning outcomes
3. Target audience
4. Why it's valuable
5. Main topics addressed

Write in a professional, engaging tone suitable for a knowledge base preview.
        """
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        payload = {
            "model": self.model,
            "max_tokens": 500,
            "temperature": 0.4,
            "messages": messages
        }
        
        try:
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Executive summary generation failed."
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()