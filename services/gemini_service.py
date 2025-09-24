"""Google Gemini 1.5 Flash video analysis service."""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    from loguru import logger
except ImportError:
    logger = None
    genai = None

from config import Config


class GeminiAnalysisError(Exception):
    """Custom exception for Gemini analysis failures."""
    pass


class GeminiService:
    """Service for analyzing videos with Google Gemini 1.5 Flash."""
    
    def __init__(self):
        if not genai:
            raise GeminiAnalysisError("google-generativeai not installed")
            
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.timeout = Config.GEMINI_ANALYSIS_TIMEOUT
        
    async def analyze_video(self, video_path: Path) -> Dict[str, Any]:
        """
        Analyze video content and extract structured information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Structured analysis data
            
        Raises:
            GeminiAnalysisError: If analysis fails
        """
        try:
            if logger:
                logger.info(f"Starting Gemini analysis of {video_path}")
            
            # Upload video file
            video_file = genai.upload_file(str(video_path))
            
            # Wait for processing with timeout
            import time
            start_time = time.time()
            max_wait_seconds = Config.GEMINI_VIDEO_PROCESS_TIMEOUT
            
            while video_file.state.name == "PROCESSING":
                # Check timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait_seconds:
                    raise GeminiAnalysisError(
                        f"Video processing timeout: {video_path} exceeded {max_wait_seconds}s limit"
                    )
                
                await asyncio.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise GeminiAnalysisError("Video processing failed")
            
            # Analyze with structured prompt
            prompt = self._get_analysis_prompt()
            response = self.model.generate_content([video_file, prompt])
            
            # Parse response
            analysis = self._parse_response(response.text)
            
            # Cleanup uploaded file
            genai.delete_file(video_file.name)
            
            if logger:
                logger.success(f"Gemini analysis completed for {video_path}")
            
            return analysis
            
        except Exception as e:
            if logger:
                logger.error(f"Gemini analysis error: {e}")
            raise GeminiAnalysisError(f"Analysis failed: {e}")
    
    def _get_analysis_prompt(self) -> str:
        """Get the structured analysis prompt for Gemini."""
        return """
Analyze this video and extract the following information in JSON format:

{
    "subject": "Main topic or category (e.g., 'AI Development', 'Design Tools', 'Programming')",
    "title": "Descriptive title for the content (max 60 characters)",
    "tools": ["List of software, apps, or tools mentioned or shown"],
    "key_points": [
        "First important point or insight",
        "Second key learning or technique", 
        "Third notable information"
    ],
    "visible_text": [
        "Any text visible on screen",
        "UI elements or code snippets",
        "Important labels or titles"
    ],
    "resources": [
        "Any URLs mentioned",
        "Book titles or references",
        "People or companies mentioned"
    ],
    "summary": "Brief 2-3 sentence summary of the video content",
    "difficulty_level": "beginner|intermediate|advanced",
    "estimated_watch_time": "Duration in minutes",
    "tags": ["relevant", "keywords", "for", "categorization"]
}

Focus on educational and practical information. Be precise and specific.
Return only valid JSON without any markdown formatting.
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response and validate structure."""
        try:
            # Clean response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            analysis = json.loads(cleaned_text.strip())
            
            # Validate required fields
            required_fields = ["subject", "title", "tools", "key_points", "summary"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = self._get_default_value(field)
            
            # Ensure lists are actually lists
            list_fields = ["tools", "key_points", "visible_text", "resources", "tags"]
            for field in list_fields:
                if field in analysis and not isinstance(analysis[field], list):
                    analysis[field] = [str(analysis[field])] if analysis[field] else []
            
            return analysis
            
        except json.JSONDecodeError as e:
            if logger:
                logger.error(f"JSON parsing error: {e}\nResponse: {response_text}")
            
            # Return fallback structure
            return {
                "subject": "Unknown",
                "title": "Video Analysis",
                "tools": [],
                "key_points": ["Analysis could not be parsed"],
                "visible_text": [],
                "resources": [],
                "summary": "Video analysis failed to parse properly",
                "difficulty_level": "unknown",
                "estimated_watch_time": "unknown",
                "tags": ["parsing-error"]
            }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields."""
        defaults = {
            "subject": "Unknown",
            "title": "Untitled Video",
            "tools": [],
            "key_points": [],
            "visible_text": [],
            "resources": [],
            "summary": "No summary available",
            "difficulty_level": "unknown",
            "estimated_watch_time": "unknown",
            "tags": []
        }
        return defaults.get(field, "")


# Convenience function for external use
async def analyze_video_content(video_path: Path) -> Dict[str, Any]:
    """
    Analyze video and return structured data.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Analysis dictionary
    """
    service = GeminiService()
    return await service.analyze_video(video_path)