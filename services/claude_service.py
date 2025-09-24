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
        """
        Transform Gemini analysis into educational Markdown content.
        
        Args:
            analysis: Structured analysis from Gemini
            
        Returns:
            Enriched Markdown content
            
        Raises:
            ClaudeEnrichmentError: If enrichment fails
        """
        try:
            if logger:
                logger.info("Starting Claude content enrichment via OpenRouter")
            
            # Build enrichment prompt
            prompt = self._build_enrichment_prompt(analysis)
            
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/Knowledge-Bot",
                "X-Title": "Knowledge Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
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
            
            if logger:
                logger.success("Claude enrichment completed via OpenRouter")
            
            return enriched_content
            
        except Exception as e:
            if logger:
                logger.error(f"Claude enrichment error: {e}")
            raise ClaudeEnrichmentError(f"Enrichment failed: {e}")
    
    def _build_enrichment_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build enrichment prompt for Claude."""
        title = analysis.get("title", "Untitled")
        subject = analysis.get("subject", "Unknown")
        summary = analysis.get("summary", "")
        key_points = analysis.get("key_points", [])
        tools = analysis.get("tools", [])
        visible_text = analysis.get("visible_text", [])
        resources = analysis.get("resources", [])
        difficulty = analysis.get("difficulty_level", "unknown")
        
        # Format key points
        key_points_text = "\n".join([f"- {point}" for point in key_points])
        
        # Format tools
        tools_text = ", ".join(tools) if tools else "None mentioned"
        
        # Format resources
        resources_text = "\n".join([f"- {resource}" for resource in resources]) if resources else "None mentioned"
        
        # Format visible text
        visible_text_formatted = "\n".join([f"- {text}" for text in visible_text]) if visible_text else "None captured"
        
        prompt = f"""
Transform the following video analysis into an educational knowledge base entry. Create comprehensive, well-structured Markdown content that would be valuable for learning and reference.

**Original Analysis:**
Title: {title}
Subject: {subject}
Difficulty: {difficulty}
Summary: {summary}

Key Points:
{key_points_text}

Tools/Software: {tools_text}

Visible Text/Code:
{visible_text_formatted}

Resources:
{resources_text}

**Instructions:**
1. Create an educational chapter with clear sections
2. Expand on the key points with context and explanations
3. Add practical examples where relevant
4. Include step-by-step guidance if applicable
5. Maintain professional, educational tone
6. Use proper Markdown formatting
7. Add relevant subsections for better organization

**Required Structure:**
# [Descriptive Title]

## Overview
[2-3 sentence introduction explaining what this content covers]

## Key Concepts
[Expand key points into detailed explanations]

## Tools & Technologies
[Detail the tools mentioned with context about their use]

## Step-by-Step Guide
[If applicable, create actionable steps]

## Practical Applications
[Real-world use cases and examples]

## Important Notes
[Highlight critical information, tips, or warnings]

## Additional Resources
[Expand on resources with descriptions]

## Tags
[Relevant keywords for categorization]

Write the content in a way that someone could learn from it even without watching the original video. Focus on educational value and practical application.
"""
        
        return prompt


# Convenience function for external use
async def enrich_analysis(analysis: Dict[str, Any]) -> str:
    """
    Enrich Gemini analysis with Claude.
    
    Args:
        analysis: Analysis dictionary from Gemini
        
    Returns:
        Enriched Markdown content
    """
    service = ClaudeService()
    return await service.enrich_content(analysis)