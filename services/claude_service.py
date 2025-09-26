"""Claude content enrichment service via OpenRouter."""

from typing import Dict, Any

try:
    import httpx
    from loguru import logger
except ImportError:
    httpx = None
    logger = None

from config import Config


class ClaudeEnrichmentError(Exception):
    """Custom exception for Claude enrichment failures."""
    pass


class ClaudeService:
    """Service for enriching content with Claude API via OpenRouter."""
    
    def __init__(self):
        if not httpx:
            raise ClaudeEnrichmentError("httpx not installed")
        
        if not Config.OPENROUTER_API_KEY:
            raise ClaudeEnrichmentError("OPENROUTER_API_KEY not configured")
            
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        self.timeout = Config.CLAUDE_ENRICHMENT_TIMEOUT
    
    async def enrich_content(self, analysis: Dict[str, Any]) -> str:
        """Transform Gemini analysis into educational Markdown content."""
        try:
            if logger:
                logger.info("Starting Claude content enrichment via OpenRouter")
            
            prompt = self._build_enrichment_prompt(analysis)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/Knowledge-Bot",
                "X-Title": "Knowledge Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,  # Reduce from 8192 to avoid cutoffs
                "temperature": 0.3   # Increase from 0.1 for better creativity
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                enriched_content = result["choices"][0]["message"]["content"].strip()
            
            # Check if content was cut off
            if enriched_content.endswith("...]") or "partial response" in enriched_content.lower():
                if logger:
                    logger.warning("Content was truncated, generating summary section")
                enriched_content = self._fix_truncated_content(enriched_content, analysis)
            
            if logger:
                logger.success("Claude enrichment completed via OpenRouter")
            
            return enriched_content
            
        except Exception as e:
            if logger:
                logger.error(f"Claude enrichment error: {e}")
            raise ClaudeEnrichmentError(f"Enrichment failed: {e}")
    
    def _build_enrichment_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build realistic prompt for complete content generation."""
        title = analysis.get('title', 'Technical Guide')
        subject = analysis.get('subject', 'Technology')
        key_points = analysis.get('key_points', [])
        tools = analysis.get('tools', [])
        visual_concepts = analysis.get('visual_concepts', [])
        
        # Format key information
        points_text = '\n'.join([f"- {point}" for point in key_points[:5]])
        tools_text = ', '.join(tools) if tools else 'General tools'
        
        return f"""Create a comprehensive technical guide about: {title}

Key Information:
- Subject: {subject}
- Tools/Technologies: {tools_text}
- Visual concepts identified: {', '.join(visual_concepts[:3]) if visual_concepts else 'None'}

Key Points to Cover:
{points_text}

Generate a complete, well-structured technical guide following this format:

# {title}

## Overview
Write 2-3 paragraphs explaining what this technology/concept is, why it matters, and its practical applications.

## Key Concepts
Expand on the main concepts with clear explanations. Include:
- Core principles and how they work
- Important terminology
- Relationship to other technologies

## Implementation Guide

### Basic Example
```language
# Provide a simple, working code example (20-30 lines)
# Include comments explaining key parts
```

### Practical Application
```language
# Show a more realistic use case (30-50 lines)
# Include error handling and best practices
```

## Tools & Technologies
Detail each tool mentioned:
{chr(10).join([f"- {tool}: [Brief description of its role]" for tool in tools[:5]])}

## Best Practices
- List 5-7 important best practices
- Include security considerations
- Performance optimization tips

## Common Issues & Solutions
Provide 3-4 common problems and their solutions:

**Issue:** [Description]
**Solution:** [How to fix]

## Next Steps
- Suggested learning path
- Related topics to explore
- Additional resources

## Summary
Conclude with key takeaways and practical applications.

IMPORTANT: Generate complete content for ALL sections. Aim for 2000-2500 words total. Focus on practical, actionable information."""

    def _fix_truncated_content(self, content: str, analysis: Dict[str, Any]) -> str:
        """Fix truncated content by adding a proper ending."""
        # Remove truncation message
        content = content.replace("[Note: This is a partial response due to length limits", "")
        content = content.replace("...]", "")
        
        # Add a proper conclusion
        conclusion = f"""

## Summary

This guide covered the essential aspects of {analysis.get('title', 'this technology')}, including:

- Core concepts and implementation patterns
- Practical examples and use cases  
- Best practices and common pitfalls
- Tools and technologies involved

For production use, ensure you've addressed security, performance, and scalability considerations discussed above.

## Tags
{', '.join(['#' + tag for tag in analysis.get('tags', [])])}
"""
        
        return content.strip() + conclusion


async def enrich_analysis(analysis: Dict[str, Any]) -> str:
    """Enrich Gemini analysis with Claude."""
    service = ClaudeService()
    return await service.enrich_content(analysis)