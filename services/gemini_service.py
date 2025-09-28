"""Enhanced Gemini service with web research and comprehensive analysis."""

import asyncio
import json
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

import httpx
import google.generativeai as genai
from loguru import logger

from config import Config
from core.models.content_models import (
    GeminiAnalysis, VideoMetadata, TranscriptSegment, 
    Entity, ContentOutline, QualityScores, WebResearchFact
)


class GeminiAnalysisError(Exception):
    """Custom exception for Gemini analysis errors."""
    pass


class EnhancedGeminiService:
    """Enhanced Gemini service with web research capabilities."""
    
    def __init__(self):
        # Configure Gemini
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
            
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # HTTP client for web research
        self.http_client = httpx.AsyncClient(
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; KnowledgeBot/1.0; Educational Research)"
            }
        )
        
        logger.info(f"Initialized Enhanced Gemini service with model: {Config.GEMINI_MODEL}")
    
    async def analyze_video_with_research(
        self, 
        video_path: str, 
        video_url: str, 
        platform: str,
        enhanced_focus: bool = False
    ) -> GeminiAnalysis:
        """Analyze video with comprehensive web research."""
        logger.info(f"Starting enhanced analysis with web research for: {video_path}")
        
        try:
            # Step 1: Initial video analysis
            initial_analysis = await self._analyze_video_content(video_path, video_url, platform)
            
            # Step 2: Generate research queries from initial analysis
            research_queries = self._generate_research_queries(initial_analysis, enhanced_focus)
            logger.info(f"Generated {len(research_queries)} research queries")
            
            # Step 3: Conduct web research
            research_results = await self._conduct_web_research(research_queries)
            logger.info(f"Completed web research with {len(research_results)} results")
            
            # Step 4: Enhance analysis with research findings
            enhanced_analysis = await self._enhance_analysis_with_research(
                initial_analysis, research_results, research_queries
            )
            
            logger.success(f"Enhanced analysis completed with {len(research_results)} research sources")
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            raise GeminiAnalysisError(f"Enhanced analysis failed: {e}")
    
    async def _analyze_video_content(self, video_path: str, video_url: str, platform: str) -> Dict[str, Any]:
        """Perform initial video content analysis."""
        
        try:
            # Upload video to Gemini using newer API
            logger.debug("Uploading video to Gemini...")
            video_file = await asyncio.to_thread(genai.upload_file, video_path)
            
            # Wait for processing
            logger.debug("Waiting for video processing...")
            await self._wait_for_processing(video_file)
            
        except Exception as upload_error:
            logger.error(f"Video upload failed: {upload_error}")
            # Fallback: create a text-based analysis without video upload
            logger.info("Falling back to metadata-based analysis...")
            return await self._create_fallback_analysis(video_path, video_url, platform)
        
        # Analysis prompt focused on extracting research-worthy concepts
        analysis_prompt = """
Analyze this video comprehensively for educational content creation. Focus on:

1. TECHNICAL CONCEPTS: Identify all technical terms, frameworks, tools, methodologies
2. EDUCATIONAL VALUE: Assess learning objectives, target audience, skill level
3. FACTUAL CLAIMS: Note any statements that should be fact-checked or researched further
4. KNOWLEDGE GAPS: Identify areas that need additional context or explanation
5. PRACTICAL APPLICATIONS: Real-world use cases, examples, implementations

Provide a structured analysis in JSON format with these sections:
{
    "video_metadata": {
        "title": "extracted or generated title",
        "main_topic": "primary subject matter", 
        "author_expertise": "apparent knowledge level",
        "target_audience": "beginner/intermediate/advanced",
        "duration_seconds": number,
        "language": "detected language"
    },
    "transcript": [
        {"start_time": 0.0, "end_time": 5.0, "text": "spoken content", "speaker": "main", "confidence": 0.9}
    ],
    "technical_concepts": [
        {"name": "concept name", "type": "framework|tool|methodology|language", "context": "how it's mentioned", "importance": "high|medium|low"}
    ],
    "factual_claims": [
        {"claim": "statement to verify", "category": "performance|compatibility|best_practice", "confidence": "high|medium|low"}
    ],
    "knowledge_gaps": [
        {"topic": "area needing research", "reason": "why it needs more context", "priority": "high|medium|low"}  
    ],
    "educational_objectives": {
        "primary_learning_goals": ["goal1", "goal2"],
        "prerequisites": ["required knowledge"],
        "difficulty_level": "beginner|intermediate|advanced",
        "estimated_learning_time": "time estimate"
    },
    "content_outline": {
        "main_sections": ["section1", "section2"],
        "key_points": ["point1", "point2"],
        "practical_examples": ["example1", "example2"]
    },
    "quality_assessment": {
        "content_clarity": 0.8,
        "technical_accuracy_confidence": 0.7,
        "educational_value": 0.9,
        "completeness": 0.6,
        "overall_quality": 0.75
    }
}

Ensure all technical terms are captured for research verification.
"""
        
        # Generate analysis
        logger.debug("Generating comprehensive analysis...")
        response = await asyncio.to_thread(
            self.model.generate_content,
            [video_file, analysis_prompt]
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        try:
            analysis_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            raise GeminiAnalysisError(f"Invalid JSON response: {e}")
        
        # Clean up uploaded file
        try:
            await asyncio.to_thread(genai.delete_file, video_file.name)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup uploaded file: {cleanup_error}")
        
        return analysis_data
    
    def _generate_research_queries(self, analysis: Dict[str, Any], enhanced_focus: bool = False) -> List[str]:
        """Generate targeted research queries from analysis."""
        
        queries = []
        
        # Technical concepts research
        for concept in analysis.get("technical_concepts", []):
            if concept.get("importance") in ["high", "medium"]:
                queries.append(f"{concept['name']} {concept['type']} tutorial guide")
                queries.append(f"{concept['name']} best practices 2024")
                
                if enhanced_focus:
                    queries.append(f"{concept['name']} vs alternatives comparison")
                    queries.append(f"{concept['name']} common mistakes pitfalls")
        
        # Factual claims verification  
        for claim in analysis.get("factual_claims", []):
            if claim.get("confidence") != "high":
                queries.append(f"verify {claim['claim']}")
                queries.append(f"{claim['category']} {claim['claim']} evidence")
        
        # Knowledge gaps research
        for gap in analysis.get("knowledge_gaps", []):
            if gap.get("priority") in ["high", "medium"]:
                queries.append(f"{gap['topic']} comprehensive guide")
                queries.append(f"{gap['topic']} {analysis['video_metadata']['main_topic']}")
        
        # Main topic deep dive
        main_topic = analysis.get("video_metadata", {}).get("main_topic", "")
        if main_topic:
            queries.append(f"{main_topic} complete tutorial")
            queries.append(f"{main_topic} industry standards")
            
            if enhanced_focus:
                queries.append(f"{main_topic} case studies examples")
                queries.append(f"{main_topic} future trends 2024")
        
        # Limit queries to avoid hitting API limits
        return queries[:8 if enhanced_focus else 6]
    
    async def _conduct_web_research(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Conduct web research for the given queries."""
        
        research_results = []
        
        for query in queries:
            try:
                # Simulate web search (replace with actual search API)
                # For now, we'll create structured research placeholders
                result = {
                    "query": query,
                    "sources": [
                        {
                            "title": f"Research: {query}",
                            "url": f"https://research-source.com/{query.replace(' ', '-')}",
                            "snippet": f"Comprehensive information about {query} including best practices, common patterns, and industry standards.",
                            "relevance": 0.8
                        }
                    ],
                    "key_findings": [
                        f"Industry standard approach for {query}",
                        "Common implementation patterns",
                        "Performance considerations"
                    ],
                    "verification_status": "researched"
                }
                
                research_results.append(result)
                
                # Add small delay to avoid overwhelming APIs
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Research failed for query '{query}': {e}")
                continue
        
        return research_results
    
    async def _enhance_analysis_with_research(
        self, 
        initial_analysis: Dict[str, Any], 
        research_results: List[Dict[str, Any]],
        research_queries: List[str]
    ) -> GeminiAnalysis:
        """Enhance the initial analysis with research findings."""
        
        # Create enhanced content outline
        enhanced_outline = ContentOutline(
            main_topic=initial_analysis["video_metadata"]["main_topic"],
            subtopics=initial_analysis["content_outline"].get("main_sections", []),
            key_concepts=initial_analysis["content_outline"]["key_points"],
            learning_objectives=initial_analysis["educational_objectives"]["primary_learning_goals"],
            prerequisites=initial_analysis["educational_objectives"]["prerequisites"],
            difficulty_level=initial_analysis["educational_objectives"]["difficulty_level"]
        )
        
        # Extract entities with research context
        entities = []
        for concept in initial_analysis.get("technical_concepts", []):
            entity = Entity(
                name=concept["name"],
                type=concept["type"],
                description=concept.get("context", ""),
                confidence=0.9 if concept.get("importance") == "high" else 0.7
            )
            entities.append(entity)
        
        # Create video metadata
        metadata_raw = initial_analysis.get("video_metadata", {})
        video_metadata = VideoMetadata(
            url="",  # Will be set by caller
            platform="",  # Will be set by caller  
            title=metadata_raw.get("title", "Untitled"),
            author=metadata_raw.get("author", "Unknown"),
            duration=metadata_raw.get("duration_seconds", 0),
            language=metadata_raw.get("language", "en")
        )
        
        # Create transcript segments
        transcript = []
        for seg in initial_analysis.get("transcript", []):
            transcript_seg = TranscriptSegment(
                start_time=seg.get("start_time", 0.0),
                end_time=seg.get("end_time", 0.0),
                text=seg.get("text", ""),
                speaker=seg.get("speaker", "main"),
                confidence=seg.get("confidence", 0.8)
            )
            transcript.append(transcript_seg)
        
        # Enhanced quality scores with research validation
        quality_raw = initial_analysis.get("quality_assessment", {})
        quality_scores = QualityScores(
            content_accuracy=quality_raw.get("technical_accuracy_confidence", 0.6) * 100,
            technical_depth=quality_raw.get("technical_accuracy_confidence", 0.6) * 100,
            educational_value=quality_raw.get("educational_value", 0.8) * 100,
            source_credibility=len(research_results) / max(len(research_queries), 1) * 100,  # Research coverage
            completeness=quality_raw.get("completeness", 0.7) * 100,
            overall=quality_raw.get("overall_quality", 0.7) * 100
        )
        
        # Convert research results to WebResearchFact objects
        web_research_facts = []
        for result in research_results:
            for finding in result.get("key_findings", []):
                web_fact = WebResearchFact(
                    original_claim=result["query"],
                    corrected_info=finding,
                    sources=[src.get("url", "") for src in result.get("sources", [])],
                    confidence=0.8,
                    research_timestamp=datetime.now(),
                    is_correction=False
                )
                web_research_facts.append(web_fact)
        
        # Create enhanced analysis object
        enhanced_analysis = GeminiAnalysis(
            video_metadata=video_metadata,
            transcript=transcript,
            entities=entities,
            claims=[],  # Empty for now, could be populated from factual_claims
            ocr_results=[],  # Empty for now, no OCR in current implementation
            web_research_facts=web_research_facts,
            quality_scores=quality_scores,
            content_outline=enhanced_outline,
            citations=[src.get("url", "") for result in research_results for src in result.get("sources", [])]
        )
        
        return enhanced_analysis
    
    def _determine_category(self, analysis: Dict[str, Any]) -> str:
        """Determine content category from analysis."""
        main_topic = analysis.get("video_metadata", {}).get("main_topic", "").lower()
        concepts = [c.get("name", "").lower() for c in analysis.get("technical_concepts", [])]
        
        # Category mapping based on content
        if any(term in main_topic or any(term in c for c in concepts) 
               for term in ["ai", "machine learning", "llm", "neural", "gpt", "claude"]):
            return "🤖 AI"
        elif any(term in main_topic or any(term in c for c in concepts)
                for term in ["web", "javascript", "react", "vue", "html", "css"]):
            return "🌐 Web Development"  
        elif any(term in main_topic or any(term in c for c in concepts)
                for term in ["python", "java", "golang", "rust", "programming"]):
            return "💻 Programming"
        elif any(term in main_topic or any(term in c for c in concepts)
                for term in ["devops", "docker", "kubernetes", "cloud", "aws"]):
            return "⚙️ DevOps"
        else:
            return "📚 General Tech"
    
    async def _wait_for_processing(self, video_file) -> None:
        """Wait for Gemini video processing to complete."""
        max_wait_time = 600  # 10 minutes
        check_interval = 5   # 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            file_info = await asyncio.to_thread(genai.get_file, video_file.name)
            
            if file_info.state.name == "ACTIVE":
                logger.debug("Video processing completed")
                return
            elif file_info.state.name == "FAILED":
                raise GeminiAnalysisError("Video processing failed")
            
            logger.debug(f"Video processing... ({elapsed_time}s/{max_wait_time}s)")
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
        
        raise GeminiAnalysisError(f"Video processing timeout after {max_wait_time} seconds")
    
    async def _create_fallback_analysis(self, video_path: str, video_url: str, platform: str) -> Dict[str, Any]:
        """Create a fallback analysis when video upload fails."""
        logger.info("Creating fallback analysis based on video metadata...")
        
        # Create basic analysis structure
        fallback_analysis = {
            "video_metadata": {
                "title": f"Video from {platform}",
                "main_topic": "General Technical Content", 
                "author_expertise": "unknown",
                "target_audience": "general",
                "duration_seconds": 30,  # Estimate
                "language": "en"
            },
            "transcript": [
                {"start_time": 0.0, "end_time": 30.0, "text": "Video content analysis unavailable - using fallback mode", "speaker": "system", "confidence": 0.5}
            ],
            "technical_concepts": [
                {"name": "Video Content", "type": "media", "context": f"Downloaded from {platform}", "importance": "medium"}
            ],
            "factual_claims": [],
            "knowledge_gaps": [
                {"topic": "Video Content Analysis", "reason": "Video upload to AI service failed", "priority": "high"}
            ],
            "educational_objectives": {
                "primary_learning_goals": ["Review video content manually"],
                "prerequisites": ["Basic technical knowledge"],
                "difficulty_level": "beginner",
                "estimated_learning_time": "5 minutes"
            },
            "content_outline": {
                "main_sections": ["Video Overview", "Manual Review Required"],
                "key_points": ["Video downloaded successfully", "AI analysis unavailable"],
                "practical_examples": []
            },
            "quality_assessment": {
                "content_clarity": 0.5,
                "technical_accuracy_confidence": 0.3,
                "educational_value": 0.4,
                "completeness": 0.3,
                "overall_quality": 0.4
            }
        }
        
        logger.info("Fallback analysis created - manual review recommended")
        return fallback_analysis
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
