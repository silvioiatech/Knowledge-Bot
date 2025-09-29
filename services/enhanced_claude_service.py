"""
Enhanced Claude service with intelligent image evaluation and Notion integration.
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

import httpx
from config import Config
from core.models.content_models import (
    GeminiAnalysis, CategorySuggestion, ImageEvaluationResult, 
    ImagePlan, NotionFieldMappings, NotionPayload
)

logger = logging.getLogger(__name__)

class EnhancedClaudeService:
    """Enhanced Claude service with intelligent decision-making capabilities."""
    
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "HTTP-Referer": Config.RAILWAY_STATIC_URL or "https://github.com/silvioiatech/Knowledge-Bot",
            "X-Title": "Knowledge Bot - Enhanced Processing"
        }
    
    async def analyze_content_for_categories(self, gemini_analysis: GeminiAnalysis) -> CategorySuggestion:
        """
        Analyze Gemini content and suggest appropriate categories with confidence scoring.
        """
        try:
            # Extract key content for analysis
            content_outline = gemini_analysis.content_outline
            video_metadata = gemini_analysis.video_metadata
            entities = [entity.name for entity in gemini_analysis.entities[:10]]  # Top 10 entities
            
            # Create analysis prompt
            prompt = f"""
            Analyze this video content and suggest the most appropriate category and subcategory from the exact options provided.
            
            CONTENT ANALYSIS:
            Video Title: {video_metadata.title}
            Main Topic: {content_outline.main_topic}
            Platform: {video_metadata.platform}
            Key Entities: {', '.join(entities)}
            Subtopics: {', '.join(content_outline.subtopics[:5])}
            Difficulty: {content_outline.difficulty_level}
            
            EXACT CATEGORY OPTIONS (use key name):
            - apple: 🍎 APPLE (Apple ecosystem, macOS, iOS apps, Apple development)
            - linux: 🐧 LINUX (Linux systems, distributions, command line, open source)
            - ai: 🤖 AI (Artificial intelligence, machine learning, AI tools, automation)
            - monetization: 💰 MONETIZATION (Business strategies, revenue generation, marketing)
            - external_devices: 🔌 EXTERNAL_DEVICES (Hardware, peripherals, IoT, devices)
            - mobile_dev: 📱 MOBILE_DEV (Mobile app development, iOS/Android programming)
            - cloud: ☁️ CLOUD (Cloud services, deployment, infrastructure, SaaS)
            - security: 🔒 SECURITY (Cybersecurity, privacy, encryption, safety)
            - productivity: 📈 PRODUCTIVITY (Workflows, tools, optimization, efficiency)
            
            EXACT SUBCATEGORY OPTIONS:
            Programs, Automations, Agents, System Config, Development, Hardware, Networking, Tools, Workflow Automation
            
            EXACT DIFFICULTY OPTIONS:
            Beginner, Intermediate, Advanced, Expert, 🔴 Advanced
            
            EXACT PLATFORM OPTIONS:
            macOS, Linux, Windows, iOS, Android, Universal
            
            Respond with JSON only:
            {{
                "category": "category_key",
                "category_display": "🤖 AI",
                "subcategory": "exact_subcategory_name",
                "confidence": 85,
                "reasoning": "Brief explanation for the categorization",
                "difficulty": "Intermediate",
                "platform_specific": ["macOS", "Universal"]
            }}
            
            Choose the single most appropriate category with high confidence. Consider the main topic and technical complexity.
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": Config.CLAUDE_MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Claude API error: {response.status_code} - {response.text}")
                    return self._get_fallback_category(content_outline.main_topic)
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    category_data = json.loads(content.strip())
                    
                    # Validate category key
                    if category_data["category"] not in NotionFieldMappings.CATEGORIES:
                        category_data["category"] = "ai"
                        category_data["category_display"] = "🤖 AI"
                    
                    return CategorySuggestion(
                        category=category_data["category"],
                        category_display=category_data.get("category_display", 
                            NotionFieldMappings.get_category_emoji_name(category_data["category"])),
                        subcategory=category_data.get("subcategory", "Tools"),
                        confidence=float(category_data.get("confidence", 75)),
                        reasoning=category_data.get("reasoning", "Automated categorization"),
                        difficulty=category_data.get("difficulty", "Intermediate"),
                        platform_specific=category_data.get("platform_specific", ["Universal"])
                    )
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Claude category response: {content}")
                    return self._get_fallback_category(content_outline.main_topic)
                    
        except Exception as e:
            logger.error(f"Error in category analysis: {e}")
            return self._get_fallback_category(getattr(gemini_analysis.content_outline, 'main_topic', 'Unknown'))
    
    async def evaluate_image_necessity(self, gemini_analysis: GeminiAnalysis, 
                                     category_suggestion: CategorySuggestion) -> ImageEvaluationResult:
        """
        Intelligently evaluate whether visual content would enhance understanding.
        This replaces automatic image generation with cost-effective conditional generation.
        """
        try:
            content_outline = gemini_analysis.content_outline
            video_metadata = gemini_analysis.video_metadata
            
            # Extract key concepts for evaluation
            key_concepts = ', '.join(content_outline.key_concepts[:5])
            subtopics = ', '.join(content_outline.subtopics[:3])
            
            prompt = f"""
            Evaluate whether this content would benefit from visual diagrams, flowcharts, or technical illustrations.
            
            CONTENT DETAILS:
            Title: {video_metadata.title}
            Category: {category_suggestion.category_display}
            Main Topic: {content_outline.main_topic}
            Key Concepts: {key_concepts}
            Subtopics: {subtopics}
            Difficulty: {content_outline.difficulty_level}
            
            EVALUATION CRITERIA:
            - Does this involve system architecture, workflows, or complex processes?
            - Would visual diagrams significantly enhance understanding?
            - Is this practical/technical content vs theoretical/definitional?
            - Does it involve multiple components or relationships?
            
            CONTENT TYPES THAT TYPICALLY NEED IMAGES:
            - System architecture explanations
            - Step-by-step tutorials with UI elements
            - Network diagrams and infrastructure
            - Process flows and workflows
            - Code architecture and patterns
            - Hardware setup and connections
            
            CONTENT TYPES THAT TYPICALLY DON'T NEED IMAGES:
            - Simple definitions or concepts
            - Theoretical discussions
            - Text-based tutorials
            - Pure code explanations
            - Opinion pieces or reviews
            
            Respond with JSON only:
            {{
                "needs_images": true/false,
                "reasoning": "Specific explanation for decision",
                "content_type": "practical|theoretical|architectural|tutorial",
                "complexity_score": 7,
                "image_plans": [
                    {{
                        "image_type": "flowchart",
                        "description": "System workflow diagram",
                        "placement_section": "Implementation",
                        "prompt": "Detailed prompt for image generation",
                        "priority": 3
                    }}
                ]
            }}
            
            Only suggest images if they would genuinely enhance understanding. Prioritize cost efficiency.
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": Config.CLAUDE_MODEL,
                        "messages": [
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "max_tokens": 800,
                        "temperature": 0.2
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Claude image evaluation error: {response.status_code}")
                    return ImageEvaluationResult(needs_images=False, reasoning="API error, defaulting to no images")
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    evaluation_data = json.loads(content.strip())
                    
                    # Parse image plans if they exist
                    image_plans = []
                    for plan_data in evaluation_data.get("image_plans", []):
                        image_plans.append(ImagePlan(
                            image_type=plan_data.get("image_type", "diagram"),
                            description=plan_data.get("description", ""),
                            placement_section=plan_data.get("placement_section", "Overview"),
                            prompt=plan_data.get("prompt", ""),
                            priority=int(plan_data.get("priority", 1))
                        ))
                    
                    return ImageEvaluationResult(
                        needs_images=evaluation_data.get("needs_images", False),
                        image_plans=image_plans,
                        reasoning=evaluation_data.get("reasoning", "No specific reasoning provided"),
                        content_type=evaluation_data.get("content_type", "theoretical"),
                        complexity_score=int(evaluation_data.get("complexity_score", 1))
                    )
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Claude image evaluation: {content}")
                    return ImageEvaluationResult(needs_images=False, reasoning="Failed to parse evaluation")
                    
        except Exception as e:
            logger.error(f"Error in image evaluation: {e}")
            return ImageEvaluationResult(needs_images=False, reasoning=f"Error: {str(e)}")
    
    async def create_enhanced_content(self, gemini_analysis: GeminiAnalysis, 
                                    category_suggestion: CategorySuggestion,
                                    image_evaluation: ImageEvaluationResult) -> str:
        """
        Create comprehensive educational content optimized for the selected category.
        """
        try:
            content_outline = gemini_analysis.content_outline
            video_metadata = gemini_analysis.video_metadata
            
            # Extract transcript text for context
            transcript_text = ""
            if gemini_analysis.transcript:
                transcript_parts = []
                for segment in gemini_analysis.transcript[:10]:  # Limit for context
                    if hasattr(segment, 'text'):
                        transcript_parts.append(segment.text)
                    elif isinstance(segment, dict):
                        transcript_parts.append(segment.get('text', ''))
                transcript_text = " ".join(transcript_parts)[:1000]  # Limit length
            
            # Image placeholders for content structure
            image_placeholders = ""
            if image_evaluation.needs_images:
                for i, plan in enumerate(image_evaluation.image_plans):
                    image_placeholders += f"\n[IMAGE_{i+1}: {plan.description} - Section: {plan.placement_section}]"
            
            prompt = f"""
            Create comprehensive, textbook-quality educational content based on this video analysis.
            
            VIDEO DETAILS:
            Title: {video_metadata.title}
            Platform: {video_metadata.platform}
            Category: {category_suggestion.category_display}
            Subcategory: {category_suggestion.subcategory}
            Difficulty: {category_suggestion.difficulty}
            
            CONTENT ANALYSIS:
            Main Topic: {content_outline.main_topic}
            Key Concepts: {', '.join(content_outline.key_concepts)}
            Learning Objectives: {', '.join(content_outline.learning_objectives)}
            Prerequisites: {', '.join(content_outline.prerequisites)}
            
            TRANSCRIPT CONTEXT:
            {transcript_text}
            
            IMAGE INTEGRATION:
            {image_placeholders if image_evaluation.needs_images else "[No images planned - focus on clear textual explanations]"}
            
            Create a comprehensive {Config.TARGET_CONTENT_LENGTH}-word educational article with:
            
            1. **YAML Frontmatter** with metadata
            2. **Executive Summary** (3-4 sentences)
            3. **Overview** section introducing the topic
            4. **Key Concepts** with detailed explanations
            5. **Practical Implementation** (if applicable)
            6. **Tools and Technologies** mentioned
            7. **Best Practices** and recommendations
            8. **Common Pitfalls** and troubleshooting
            9. **Advanced Considerations** for expert users
            10. **Additional Resources** and references
            
            FORMATTING REQUIREMENTS:
            - Use proper Markdown formatting
            - Include code blocks where appropriate
            - Add clear section headers
            - Use bullet points and numbered lists
            - Include practical examples
            - Reference image placeholders where specified
            
            TARGET WORD COUNT: {Config.TARGET_CONTENT_LENGTH} words
            TONE: Professional, educational, comprehensive
            AUDIENCE: {category_suggestion.difficulty} level practitioners
            
            Begin with YAML frontmatter and create engaging, informative content.
            """
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": Config.CLAUDE_MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": Config.OPENROUTER_MAX_TOKENS,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Claude content creation error: {response.status_code}")
                    return self._create_fallback_content(gemini_analysis, category_suggestion)
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return content.strip()
                
        except Exception as e:
            logger.error(f"Error creating enhanced content: {e}")
            return self._create_fallback_content(gemini_analysis, category_suggestion)
    
    async def extract_notion_metadata(self, content: str, gemini_analysis: GeminiAnalysis,
                                    category_suggestion: CategorySuggestion) -> NotionPayload:
        """
        Extract comprehensive metadata for Notion database integration.
        """
        try:
            # Extract key points from content
            key_points = self._extract_key_points(content)
            
            # Extract tools and tags
            tools_mentioned = self._extract_tools_from_content(content, gemini_analysis)
            tags = self._extract_tags_from_content(content, gemini_analysis)
            
            # Calculate word count
            word_count = len(content.split())
            
            # Extract cross-references
            prerequisites = gemini_analysis.content_outline.prerequisites[:5]
            related_topics = self._extract_related_topics(content)
            advanced_topics = self._extract_advanced_topics(content)
            
            return NotionPayload(
                title=gemini_analysis.video_metadata.title or "Untitled Knowledge Entry",
                category=category_suggestion.category_display,
                subcategory=category_suggestion.subcategory,
                content_quality="⭐⭐ Basic",  # Start with basic, can be upgraded
                difficulty=category_suggestion.difficulty,
                word_count=word_count,
                processing_date=datetime.now().isoformat(),
                source_video=gemini_analysis.video_metadata.url,
                key_points=key_points,
                gemini_confidence=int(category_suggestion.confidence),
                tags=tags,
                tools_mentioned=tools_mentioned,
                platform_specific=category_suggestion.platform_specific,
                prerequisites=prerequisites,
                related_topics=related_topics,
                advanced_topics=advanced_topics,
                auto_created=True,
                verified=False,
                ready_for_script=False,
                ready_for_ebook=False,
                content_blocks=self._content_to_notion_blocks(content)
            )
            
        except Exception as e:
            logger.error(f"Error extracting Notion metadata: {e}")
            # Return minimal viable payload
            return NotionPayload(
                title=getattr(gemini_analysis.video_metadata, 'title', 'Untitled'),
                category=category_suggestion.category_display,
                subcategory="Tools",
                source_video=getattr(gemini_analysis.video_metadata, 'url', ''),
                gemini_confidence=int(category_suggestion.confidence)
            )
    
    def _get_fallback_category(self, main_topic: str) -> CategorySuggestion:
        """Provide fallback category suggestion."""
        # Simple keyword-based fallback
        topic_lower = main_topic.lower()
        
        if any(word in topic_lower for word in ['apple', 'macos', 'ios', 'iphone', 'mac']):
            category = "apple"
        elif any(word in topic_lower for word in ['linux', 'ubuntu', 'terminal', 'command']):
            category = "linux"
        elif any(word in topic_lower for word in ['ai', 'machine learning', 'neural', 'gpt']):
            category = "ai"
        elif any(word in topic_lower for word in ['money', 'business', 'revenue', 'monetize']):
            category = "monetization"
        elif any(word in topic_lower for word in ['cloud', 'aws', 'docker', 'kubernetes']):
            category = "cloud"
        elif any(word in topic_lower for word in ['security', 'privacy', 'encryption', 'hack']):
            category = "security"
        elif any(word in topic_lower for word in ['mobile', 'app', 'android', 'swift']):
            category = "mobile_dev"
        elif any(word in topic_lower for word in ['device', 'hardware', 'iot', 'sensor']):
            category = "external_devices"
        else:
            category = "productivity"
        
        return CategorySuggestion(
            category=category,
            category_display=NotionFieldMappings.get_category_emoji_name(category),
            subcategory="Tools",
            confidence=60.0,
            reasoning="Fallback categorization based on keywords",
            difficulty="Intermediate",
            platform_specific=["Universal"]
        )
    
    def _create_fallback_content(self, gemini_analysis: GeminiAnalysis, 
                               category_suggestion: CategorySuggestion) -> str:
        """Create basic fallback content if Claude fails."""
        title = gemini_analysis.video_metadata.title or "Knowledge Entry"
        main_topic = gemini_analysis.content_outline.main_topic
        
        return f"""---
title: "{title}"
category: {category_suggestion.category}
difficulty: {category_suggestion.difficulty}
date: {datetime.now().isoformat()}
source: {gemini_analysis.video_metadata.url}
---

# {title}

## Overview

This content covers {main_topic} with a focus on practical implementation and best practices.

## Key Concepts

{chr(10).join([f"- {concept}" for concept in gemini_analysis.content_outline.key_concepts[:5]])}

## Learning Objectives

{chr(10).join([f"- {obj}" for obj in gemini_analysis.content_outline.learning_objectives[:3]])}

## Additional Resources

For more information on this topic, refer to the original video source and related documentation.
"""
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key bullet points from markdown content."""
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                point = stripped[2:].strip()
                if len(point) > 10 and len(key_points) < 8:  # Limit to 8 key points
                    key_points.append(point)
        
        return key_points[:8]
    
    def _extract_tools_from_content(self, content: str, gemini_analysis: GeminiAnalysis) -> List[str]:
        """Extract mentioned tools and technologies."""
        tools = set()
        
        # From entities
        for entity in gemini_analysis.entities:
            if entity.type in ['technology', 'tool', 'software']:
                tools.add(entity.name)
        
        # Common tools to look for in content
        common_tools = [
            'Python', 'JavaScript', 'React', 'Node.js', 'Docker', 'Kubernetes',
            'AWS', 'GCP', 'Azure', 'Git', 'GitHub', 'VS Code', 'Xcode',
            'Terminal', 'Bash', 'Linux', 'macOS', 'Windows', 'ChatGPT',
            'Claude', 'Gemini', 'OpenAI', 'TensorFlow', 'PyTorch'
        ]
        
        content_lower = content.lower()
        for tool in common_tools:
            if tool.lower() in content_lower:
                tools.add(tool)
        
        return list(tools)[:10]  # Limit to 10 tools
    
    def _extract_tags_from_content(self, content: str, gemini_analysis: GeminiAnalysis) -> List[str]:
        """Extract relevant tags from content."""
        tags = set()
        
        # Category-based tags
        content_lower = content.lower()
        
        tag_keywords = {
            'tutorial': ['tutorial', 'guide', 'how to', 'step by step'],
            'automation': ['automation', 'script', 'automate', 'automatic'],
            'development': ['development', 'coding', 'programming', 'dev'],
            'beginner': ['beginner', 'getting started', 'introduction', 'basics'],
            'advanced': ['advanced', 'expert', 'professional', 'complex'],
            'productivity': ['productivity', 'workflow', 'efficiency', 'optimization'],
            'security': ['security', 'secure', 'encryption', 'privacy'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'database': ['database', 'sql', 'mongodb', 'postgresql'],
            'frontend': ['frontend', 'ui', 'interface', 'design'],
            'backend': ['backend', 'server', 'infrastructure', 'deployment']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.add(tag)
        
        return list(tags)[:8]  # Limit to 8 tags
    
    def _extract_related_topics(self, content: str) -> List[str]:
        """Extract related topics mentioned in content."""
        # Look for "related", "see also", "similar" sections
        related = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if any(phrase in line.lower() for phrase in ['related', 'see also', 'similar', 'additionally']):
                # Look at next few lines for related topics
                for j in range(i+1, min(i+4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('- '):
                        topic = next_line[2:].strip()
                        if len(topic) > 5 and len(related) < 5:
                            related.append(topic)
        
        return related
    
    def _extract_advanced_topics(self, content: str) -> List[str]:
        """Extract advanced topics for future learning."""
        advanced = []
        lines = content.split('\n')
        
        for line in lines:
            if any(phrase in line.lower() for phrase in ['advanced', 'next steps', 'further', 'deep dive']):
                # Extract potential advanced topics from the line
                if '- ' in line:
                    topic = line.split('- ')[-1].strip()
                    if len(topic) > 5 and len(advanced) < 3:
                        advanced.append(topic)
        
        return advanced
    
    def _content_to_notion_blocks(self, content: str) -> List[Dict]:
        """Convert markdown content to Notion blocks."""
        # For now, return as a single rich text block
        # Can be enhanced to parse markdown into proper Notion blocks
        return [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content[:2000]  # Limit for Notion API
                            }
                        }
                    ]
                }
            }
        ]