"""Enhanced Gemini video analysis service for comprehensive textbook-quality content generation."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    from loguru import logger
except ImportError:
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None
    logger = None

from config import Config


class GeminiAnalysisError(Exception):
    """Custom exception for Gemini analysis errors."""
    pass


def init_gemini():
    """Initialize Gemini with API key."""
    if not genai:
        raise GeminiAnalysisError("google-generativeai not installed")
    
    if not Config.GEMINI_API_KEY:
        raise GeminiAnalysisError("GEMINI_API_KEY not configured")
    
    genai.configure(api_key=Config.GEMINI_API_KEY)
    return genai.GenerativeModel(Config.GEMINI_MODEL)


def create_textbook_analysis_prompt() -> str:
    """Create comprehensive analysis prompt for textbook-quality content extraction."""
    return """You are an expert technical analyst extracting comprehensive information from video content for creating professional textbook and reference material.

Analyze this video content with EXHAUSTIVE detail for educational content creation.

**CRITICAL: Return ONLY valid JSON. No additional text, explanations, or formatting.**

Extract information in this EXACT JSON structure:

{
  "title": "Clear, descriptive title suitable for textbook chapter",
  "subject": "Primary technical category (programming, ai, devops, etc.)",
  "category_confidence": 0.85,
  "suggested_new_category": null,
  "visual_concepts": [
    "API request/response flow diagram needed",
    "Database schema visualization", 
    "Component hierarchy chart",
    "Decision tree for algorithm logic"
  ],
  "key_points": [
    "Comprehensive explanation of each major concept",
    "Step-by-step processes and workflows", 
    "Best practices and why they matter",
    "Common pitfalls and how to avoid them"
  ],
  "tools": [
    "All software with exact version numbers if shown",
    "Frameworks, libraries, platforms mentioned",
    "Development environments and configurations"
  ],
  "code_snippets": [
    {
      "code": "def example_function():\\n    return 'complete code block'",
      "language": "python",
      "purpose": "Main implementation example",
      "line_numbers": "5-8"
    }
  ],
  "error_resolutions": [
    {
      "error": "ModuleNotFoundError: No module named 'requests'",
      "solution": "pip install requests",
      "context": "Installation requirement"
    }
  ],
  "performance_notes": [
    "O(n log n) sorting algorithm complexity",
    "Caches API calls for 5 minutes",
    "Uses connection pooling for efficiency"
  ],
  "security_considerations": [
    "SQL injection vulnerability in query building", 
    "Uses JWT tokens for authentication",
    "Input validation on all user data"
  ],
  "production_ready": false,
  "platform_specific": ["macOS", "Linux"],
  "teaching_approach": "tutorial",
  "problem_context": "Why this solution matters in real-world scenarios",
  "prerequisites": ["Basic Python knowledge", "Understanding of REST APIs"],
  "environment_details": "dev",
  "visible_text": [
    "All exact text shown on screen",
    "Terminal commands with full paths",
    "Configuration file contents",
    "Error messages verbatim"
  ],
  "resources": [
    "Documentation URLs mentioned",
    "GitHub repositories referenced", 
    "Books, courses, articles cited"
  ],
  "tags": [
    "Relevant technical keywords",
    "Framework names", 
    "Methodology tags"
  ]
}

**ANALYSIS REQUIREMENTS:**

1. **Category Confidence (0.0-1.0)**: How confident you are in the main category assignment
   - If < 0.7, suggest a new category in "suggested_new_category"

2. **Visual Concepts**: Identify where technical diagrams would enhance understanding
   - System architecture diagrams
   - Data flow visualizations  
   - Process flowcharts
   - Component relationship charts

3. **Code Analysis**: Extract ALL code with context
   - Complete functions/classes shown
   - Configuration snippets
   - Command-line examples
   - Include line numbers if visible

4. **Error Resolution**: Document any troubleshooting shown
   - Exact error messages
   - Solutions provided
   - Why the error occurred

5. **Performance & Security**: Note any mentions of:
   - Algorithm complexity
   - Optimization techniques
   - Security vulnerabilities or best practices
   - Scalability considerations

6. **Environment Context**: Determine if content is:
   - Development/staging/production focused
   - Platform-specific or universal
   - Version-dependent

**Quality Standards:**
- Extract EVERYTHING for comprehensive reference material
- Focus on technical accuracy over brevity  
- Capture exact syntax and terminology
- Note dependencies and requirements
- Identify gaps that need additional explanation

Return only the JSON object, nothing else."""


class GeminiAnalyzer:
    """Enhanced Gemini analyzer for comprehensive video analysis."""
    
    def __init__(self):
        """Initialize the Gemini analyzer."""
        self.model = init_gemini()
        if logger:
            logger.info(f"Initialized Gemini analyzer with model: {Config.GEMINI_MODEL}")
    
    async def analyze_video(self, video_path: Path) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of video content for textbook creation.
        
        Args:
            video_path: Path to the video file to analyze
            
        Returns:
            Dictionary containing comprehensive analysis results
            
        Raises:
            GeminiAnalysisError: If analysis fails
        """
        try:
            if logger:
                logger.info(f"Starting comprehensive textbook analysis of video: {video_path}")
            
            # Upload video file to Gemini
            if logger:
                logger.debug("Uploading video to Gemini...")
            
            video_file = genai.upload_file(str(video_path))
            
            # Wait for processing to complete
            if logger:
                logger.debug("Waiting for video processing...")
            
            await self._wait_for_processing(video_file)
            
            # Create comprehensive analysis prompt
            prompt = create_textbook_analysis_prompt()
            
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generate comprehensive analysis
            if logger:
                logger.debug("Generating comprehensive textbook analysis...")
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model.generate_content,
                    [video_file, prompt],
                    safety_settings=safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=Config.GEMINI_MAX_TOKENS,
                        temperature=0.1,  # Low temperature for consistent analysis
                    )
                ),
                timeout=Config.GEMINI_ANALYSIS_TIMEOUT
            )
            
            if not response or not response.text:
                raise GeminiAnalysisError("Empty response from Gemini")
            
            # Parse JSON response and validate structure
            try:
                # Strip markdown code blocks if present
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                response_text = response_text.strip()
                
                analysis = json.loads(response_text)
                
                # Validate and enrich analysis data
                analysis = self._validate_and_enrich_analysis(analysis)
                
                if logger:
                    logger.success(f"Successfully analyzed video: {analysis.get('title', 'Unknown')}")
                    logger.info(f"Category confidence: {analysis.get('category_confidence', 0):.2f}")
                    logger.info(f"Visual concepts identified: {len(analysis.get('visual_concepts', []))}")
                    logger.info(f"Code snippets extracted: {len(analysis.get('code_snippets', []))}")
                
                return analysis
                
            except json.JSONDecodeError as e:
                if logger:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.debug(f"Raw response: {response.text}")
                raise GeminiAnalysisError(f"Invalid JSON response: {e}")
                
        except asyncio.TimeoutError:
            raise GeminiAnalysisError(f"Analysis timeout after {Config.GEMINI_ANALYSIS_TIMEOUT} seconds")
        except Exception as e:
            if logger:
                logger.error(f"Gemini analysis failed: {e}")
            raise GeminiAnalysisError(f"Analysis failed: {e}")
        finally:
            # Clean up uploaded file
            try:
                if 'video_file' in locals():
                    genai.delete_file(video_file.name)
            except Exception as cleanup_error:
                if logger:
                    logger.warning(f"Failed to cleanup uploaded file: {cleanup_error}")
    
    def _validate_and_enrich_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enrich analysis data with additional fields."""
        
        # Ensure required fields exist
        required_fields = {
            'title': 'Unknown Title',
            'subject': 'programming', 
            'category_confidence': 0.5,
            'visual_concepts': [],
            'key_points': [],
            'tools': [],
            'code_snippets': [],
            'error_resolutions': [],
            'performance_notes': [],
            'security_considerations': [],
            'production_ready': False,
            'platform_specific': [],
            'teaching_approach': 'tutorial',
            'problem_context': '',
            'prerequisites': [],
            'environment_details': 'unknown',
            'visible_text': [],
            'resources': [],
            'tags': []
        }
        
        for field, default in required_fields.items():
            if field not in analysis:
                analysis[field] = default
        
        # Flag low category confidence
        if analysis['category_confidence'] < Config.MIN_CATEGORY_CONFIDENCE:
            analysis['needs_review'] = True
            if logger:
                logger.warning(f"Low category confidence: {analysis['category_confidence']:.2f}")
        
        # Add metadata
        analysis['analysis_timestamp'] = asyncio.get_event_loop().time()
        analysis['gemini_model'] = Config.GEMINI_MODEL
        analysis['content_length_estimate'] = len(' '.join(analysis['key_points'])) * 8  # Rough estimate
        
        return analysis
    
    async def _wait_for_processing(self, video_file) -> None:
        """Wait for video file processing to complete."""
        max_wait_time = Config.GEMINI_VIDEO_PROCESS_TIMEOUT
        wait_interval = 5  # seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            file_info = genai.get_file(video_file.name)
            
            if file_info.state.name == "ACTIVE":
                if logger:
                    logger.debug("Video processing completed")
                return
            elif file_info.state.name == "FAILED":
                raise GeminiAnalysisError("Video processing failed")
            
            if logger:
                logger.debug(f"Video processing... ({elapsed_time}s/{max_wait_time}s)")
            
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        raise GeminiAnalysisError(f"Video processing timeout after {max_wait_time} seconds")


# Main interface function
async def analyze_video_content(video_path: Path) -> Dict[str, Any]:
    """
    Analyze video content using Gemini for comprehensive textbook creation.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Comprehensive analysis results dictionary
        
    Raises:
        GeminiAnalysisError: If analysis fails
    """
    analyzer = GeminiAnalyzer()
    return await analyzer.analyze_video(video_path)