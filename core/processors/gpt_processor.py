"""GPT processor for final content assembly and quality assurance."""

from typing import Dict, Any, List
import re

import httpx
from loguru import logger

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, GPT_MODEL, GPT_MAX_TOKENS
from core.models.content_models import (
    GeminiAnalysis, ClaudeOutput, GeneratedImage, NotionPayload
)


class GPTAssemblyProcessor:
    """GPT processor for final content assembly and quality assurance."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/knowledge-bot",
                "X-Title": "Knowledge Bot"
            }
        )
        self.model = GPT_MODEL
        self.base_url = OPENROUTER_BASE_URL
    
    async def assemble_final_content(
        self,
        analysis: GeminiAnalysis,
        claude_output: ClaudeOutput,
        generated_images: List[GeneratedImage]
    ) -> Dict[str, Any]:
        """Assemble all components into final polished content."""
        
        logger.info("Starting final content assembly with GPT")
        
        try:
            # Step 1: Insert images into content
            content_with_images = await self._insert_images_into_content(
                claude_output.markdown_content,
                generated_images
            )
            
            # Step 2: Perform quality review and corrections
            reviewed_content = await self._perform_quality_review(
                content_with_images,
                analysis
            )
            
            # Step 3: Generate final metadata
            final_metadata = await self._generate_final_metadata(
                reviewed_content,
                analysis,
                claude_output
            )
            
            # Step 4: Create cross-references and related topics
            cross_references = await self._generate_cross_references(
                analysis,
                reviewed_content
            )
            
            # Step 5: Final formatting and structure optimization
            final_content = await self._optimize_final_structure(reviewed_content)
            
            return {
                "content": final_content,
                "metadata": final_metadata,
                "cross_references": cross_references,
                "quality_score": await self._calculate_final_quality_score(
                    final_content, 
                    analysis, 
                    claude_output
                ),
                "word_count": len(final_content.split()),
                "readability_score": await self._calculate_readability(final_content),
                "completeness_check": await self._verify_completeness(
                    final_content, 
                    claude_output.image_plans
                )
            }
            
        except Exception as e:
            logger.error(f"Final assembly failed: {e}")
            raise
    
    async def _insert_images_into_content(
        self,
        content: str,
        generated_images: List[GeneratedImage]
    ) -> str:
        """Insert generated images into appropriate sections of the content."""
        
        if not generated_images:
            return content
        
        # Create image insertion map by section
        image_map = {}
        for img in generated_images:
            section = img.image_plan.placement_section
            if section not in image_map:
                image_map[section] = []
            image_map[section].append(img)
        
        # Insert images after section headers
        modified_content = content
        
        for section, images in image_map.items():
            # Find section header (## Section Name)
            section_pattern = rf"(##\s+.*{re.escape(section)}.*?\n)"
            match = re.search(section_pattern, modified_content, re.IGNORECASE)
            
            if match:
                # Insert images after the section header
                insertion_point = match.end()
                
                image_markdown = "\n"
                for img in images:
                    image_markdown += f"\n![{img.alt_text}]({img.image_url})\n"
                    image_markdown += f"*{img.image_plan.description}*\n\n"
                
                modified_content = (
                    modified_content[:insertion_point] +
                    image_markdown +
                    modified_content[insertion_point:]
                )
        
        return modified_content
    
    async def _perform_quality_review(
        self,
        content: str,
        analysis: GeminiAnalysis
    ) -> str:
        """Perform comprehensive quality review and corrections."""
        
        prompt = f"""
You are a technical editor reviewing educational content for quality assurance. Please review the following content and make improvements:

CONTENT TO REVIEW:
{content[:4000]}...

ORIGINAL ANALYSIS CONTEXT:
- Topic: {analysis.content_outline.main_topic}
- Quality Score: {analysis.quality_scores.overall}/100
- Difficulty: {analysis.content_outline.difficulty_level}
- Key Issues Found: {len(analysis.web_research_facts)} fact corrections needed

REVIEW TASKS:
1. Fix any grammatical errors or awkward phrasing
2. Ensure technical accuracy and consistency
3. Improve flow and readability
4. Add missing transitions between sections
5. Enhance clarity of complex concepts
6. Verify all claims are properly supported
7. Ensure consistent terminology throughout

REQUIREMENTS:
- Maintain the educational, professional tone
- Keep all sections and structure intact
- Don't change the fundamental content or meaning
- Focus on polish and clarity improvements
- Ensure accessibility and readability

Return the improved version of the content, maintaining all markdown formatting and structure.
        """
        
        try:
            response = await self._call_gpt(prompt, max_tokens=6000, temperature=0.2)
            return response
        except Exception as e:
            logger.warning(f"Quality review failed: {e}")
            return content  # Return original if review fails
    
    async def _generate_final_metadata(
        self,
        content: str,
        analysis: GeminiAnalysis,
        claude_output: ClaudeOutput
    ) -> Dict[str, Any]:
        """Generate comprehensive metadata for the final content."""
        
        word_count = len(content.split())
        
        prompt = f"""
Analyze this educational content and generate comprehensive metadata:

CONTENT SAMPLE:
{content[:2000]}...

ANALYSIS DATA:
- Original Topic: {analysis.content_outline.main_topic}
- Entities: {len(analysis.entities)} identified
- Quality Score: {analysis.quality_scores.overall}/100
- Word Count: {word_count}

Generate metadata in this JSON format:
{{
    "title": "Clear, descriptive title",
    "description": "2-sentence description of what this content covers",
    "tags": ["relevant", "topic", "tags"],
    "difficulty": "beginner|intermediate|advanced|expert",
    "estimated_read_time": "X minutes",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "learning_objectives": ["objective1", "objective2"],
    "prerequisites": ["prereq1", "prereq2"],
    "content_type": "guide|tutorial|reference|overview",
    "industry_relevance": ["industry1", "industry2"],
    "last_updated": "2024",
    "content_quality": "excellent|good|fair"
}}

Be specific and accurate based on the actual content provided.
        """
        
        try:
            response = await self._call_gpt(prompt, max_tokens=1000, temperature=0.3)
            
            # Parse JSON response
            import json
            metadata = json.loads(response)
            return metadata
            
        except Exception as e:
            logger.warning(f"Metadata generation failed: {e}")
            return {
                "title": analysis.content_outline.main_topic,
                "description": f"Educational guide covering {analysis.content_outline.main_topic}",
                "tags": [analysis.content_outline.main_topic.lower()],
                "difficulty": analysis.content_outline.difficulty_level,
                "estimated_read_time": f"{claude_output.estimated_reading_time} minutes",
                "content_quality": "good"
            }
    
    async def _generate_cross_references(
        self,
        analysis: GeminiAnalysis,
        content: str
    ) -> List[str]:
        """Generate cross-references and related topics."""
        
        entities = [e.name for e in analysis.entities[:10]]
        
        prompt = f"""
Based on this educational content about "{analysis.content_outline.main_topic}", suggest related topics and cross-references that would be valuable for learners.

KEY ENTITIES IN CONTENT: {', '.join(entities)}

CONTENT SAMPLE: {content[:1500]}...

Generate 5-8 related topics that learners might want to explore next. Format as a simple list:
- Related Topic 1
- Related Topic 2
- etc.

Focus on:
1. Natural next steps in learning progression
2. Related technologies or concepts mentioned
3. Practical applications in different contexts
4. Foundational concepts that support this topic
5. Advanced topics that build on this knowledge
        """
        
        try:
            response = await self._call_gpt(prompt, max_tokens=500, temperature=0.4)
            
            # Parse response into list
            cross_refs = []
            for line in response.split('\n'):
                if line.strip().startswith('- '):
                    cross_refs.append(line.strip()[2:])
            
            return cross_refs
            
        except Exception as e:
            logger.warning(f"Cross-reference generation failed: {e}")
            return []
    
    async def _optimize_final_structure(self, content: str) -> str:
        """Final structure optimization and formatting."""
        
        prompt = f"""
Perform final structural optimization on this educational content:

CONTENT:
{content}

OPTIMIZATION TASKS:
1. Ensure consistent heading hierarchy (H1, H2, H3)
2. Add table of contents if beneficial
3. Improve paragraph breaks and white space
4. Add summary boxes or callouts where helpful
5. Ensure code blocks and examples are properly formatted
6. Add navigation aids (section links, back-to-top)
7. Optimize for readability and scanning

FORMATTING GUIDELINES:
- Use proper markdown formatting
- Maintain professional, educational tone
- Add emphasis (bold/italic) for key terms
- Use bullet points and numbered lists effectively
- Ensure accessibility (proper heading structure)

Return the optimized content with improved structure and formatting.
        """
        
        try:
            response = await self._call_gpt(prompt, max_tokens=6000, temperature=0.1)
            return response
        except Exception as e:
            logger.warning(f"Structure optimization failed: {e}")
            return content
    
    async def _calculate_final_quality_score(
        self,
        content: str,
        analysis: GeminiAnalysis,
        claude_output: ClaudeOutput
    ) -> float:
        """Calculate final quality score based on multiple factors."""
        
        word_count = len(content.split())
        
        # Base quality from analysis
        base_quality = analysis.quality_scores.overall
        
        # Word count factor (optimal range: 2500-4000 words)
        if 2500 <= word_count <= 4000:
            word_factor = 1.0
        elif 2000 <= word_count < 2500:
            word_factor = 0.9
        elif 4000 < word_count <= 5000:
            word_factor = 0.95
        else:
            word_factor = 0.8
        
        # Image factor (having images improves quality)
        image_factor = 1.1 if claude_output.image_plans else 1.0
        
        # Structure factor (number of sections)
        if 6 <= claude_output.sections_count <= 12:
            structure_factor = 1.0
        else:
            structure_factor = 0.9
        
        # Calculate final score
        final_score = base_quality * word_factor * image_factor * structure_factor
        return min(100.0, final_score)  # Cap at 100
    
    async def _calculate_readability(self, content: str) -> str:
        """Calculate readability score."""
        
        # Simple readability assessment based on sentence and word length
        sentences = content.count('.') + content.count('!') + content.count('?')
        words = len(content.split())
        
        if sentences == 0:
            return "unknown"
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 15:
            return "easy"
        elif avg_words_per_sentence < 20:
            return "moderate"
        else:
            return "complex"
    
    async def _verify_completeness(
        self,
        content: str,
        image_plans: List
    ) -> Dict[str, Any]:
        """Verify content completeness."""
        
        sections = content.count('##')
        word_count = len(content.split())
        has_images = len(image_plans) > 0
        
        completeness_score = 0
        
        # Check word count
        if word_count >= 2500:
            completeness_score += 30
        elif word_count >= 2000:
            completeness_score += 20
        else:
            completeness_score += 10
        
        # Check sections
        if sections >= 8:
            completeness_score += 30
        elif sections >= 6:
            completeness_score += 20
        else:
            completeness_score += 10
        
        # Check images
        if has_images:
            completeness_score += 20
        
        # Check structure elements
        has_intro = "## 1." in content or "## Overview" in content
        has_conclusion = "conclusion" in content.lower() or "summary" in content.lower()
        
        if has_intro:
            completeness_score += 10
        if has_conclusion:
            completeness_score += 10
        
        return {
            "score": completeness_score,
            "word_count": word_count,
            "sections": sections,
            "has_images": has_images,
            "has_intro": has_intro,
            "has_conclusion": has_conclusion
        }
    
    async def _call_gpt(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.3
    ) -> str:
        """Make API call to GPT."""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technical writer and editor specializing in educational content."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = await self.http_client.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
    
    async def create_notion_payload(
        self,
        final_content: Dict[str, Any],
        analysis: GeminiAnalysis,
        video_url: str
    ) -> NotionPayload:
        """Create final Notion API payload."""
        
        metadata = final_content['metadata']
        
        # Create properties for Notion database
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": metadata.get('title', analysis.content_outline.main_topic)
                        }
                    }
                ]
            },
            "Source URL": {
                "url": video_url
            },
            "Platform": {
                "select": {
                    "name": analysis.video_metadata.platform.title()
                }
            },
            "Content Quality": {
                "select": {
                    "name": self._get_quality_rating(final_content['quality_score'])
                }
            },
            "Difficulty": {
                "select": {
                    "name": metadata.get('difficulty', 'intermediate').title()
                }
            },
            "Word Count": {
                "number": final_content['word_count']
            },
            "Estimated Reading Time": {
                "number": int(metadata.get('estimated_read_time', '5').split()[0])
            },
            "Tags": {
                "multi_select": [
                    {"name": tag} for tag in metadata.get('tags', [])[:10]
                ]
            },
            "Key Concepts": {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(metadata.get('key_concepts', []))
                        }
                    }
                ]
            },
            "Cross References": {
                "rich_text": [
                    {
                        "text": {
                            "content": " | ".join(final_content.get('cross_references', []))
                        }
                    }
                ]
            },
            "Gemini Confidence": {
                "number": round(analysis.quality_scores.overall)
            },
            "Processing Date": {
                "date": {
                    "start": analysis.analysis_timestamp.strftime("%Y-%m-%d")
                }
            }
        }
        
        # Convert markdown content to Notion blocks
        content_blocks = await self._markdown_to_notion_blocks(final_content['content'])
        
        return NotionPayload(
            properties=properties,
            content_blocks=content_blocks
        )
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating."""
        if score >= 90:
            return "⭐⭐⭐⭐⭐"
        elif score >= 80:
            return "⭐⭐⭐⭐"
        elif score >= 70:
            return "⭐⭐⭐"
        elif score >= 60:
            return "⭐⭐"
        else:
            return "⭐"
    
    async def _markdown_to_notion_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Convert markdown content to Notion blocks format."""
        
        blocks = []
        lines = content.split('\n')
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
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
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": paragraph_text}
                                    }
                                ]
                            }
                        })
                    current_paragraph = []
                continue
            
            # Handle headers
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line[2:]}
                            }
                        ]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line[3:]}
                            }
                        ]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line[4:]}
                            }
                        ]
                    }
                })
            # Handle bullet points
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": line[2:]}
                            }
                        ]
                    }
                })
            # Handle images
            elif line.startswith('!['):
                # Extract image URL
                match = re.search(r'\[([^\]]*)\]\(([^)]+)\)', line)
                if match:
                    alt_text, url = match.groups()
                    blocks.append({
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {"url": url}
                        }
                    })
            else:
                # Regular text - accumulate for paragraph
                current_paragraph.append(line)
        
        # Add any remaining paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            if paragraph_text:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": paragraph_text}
                            }
                        ]
                    }
                })
        
        return blocks
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()