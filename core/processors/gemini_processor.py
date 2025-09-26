"""Enhanced Gemini processor with web research and fact-checking."""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

import google.generativeai as genai
import httpx
from loguru import logger

from config import (
    GEMINI_API_KEY, 
    GEMINI_MODEL
)
from core.models.content_models import (
    GeminiAnalysis, VideoMetadata, TranscriptSegment, Entity,
    Claim, OCRResult, WebResearchFact, QualityScores, ContentOutline
)


class EnhancedGeminiProcessor:
    """Enhanced Gemini processor with web research and fact-checking."""
    
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def analyze_video(
        self,
        video_path: str,
        video_url: str,
        platform: str
    ) -> GeminiAnalysis:
        """Complete video analysis with fact-checking and web research."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting enhanced analysis of {video_url}")
            
            # Upload video for analysis
            video_file = genai.upload_file(
                path=video_path,
                display_name=f"Video for analysis: {video_url}"
            )
            
            # Wait for file to be ready
            await self._wait_for_file_processing(video_file)
            
            # Phase 1: Basic analysis and extraction
            basic_analysis = await self._extract_basic_content(video_file, video_url, platform)
            
            # Phase 2: Fact-checking and web research
            researched_claims = await self._research_and_fact_check(basic_analysis['claims'])
            
            # Phase 3: Quality scoring
            quality_scores = await self._assess_quality(basic_analysis, researched_claims)
            
            # Phase 4: Create structured outline
            content_outline = await self._create_content_outline(basic_analysis, researched_claims)
            
            # Build final analysis object
            analysis = GeminiAnalysis(
                video_metadata=self._parse_video_metadata(basic_analysis['metadata'], video_url, platform),
                transcript=self._parse_transcript(basic_analysis['transcript']),
                entities=self._parse_entities(basic_analysis['entities']),
                claims=self._parse_claims(basic_analysis['claims']),
                ocr_results=self._parse_ocr(basic_analysis['ocr']),
                web_research_facts=researched_claims,
                quality_scores=quality_scores,
                content_outline=content_outline,
                citations=self._extract_citations(researched_claims),
                gemini_model=GEMINI_MODEL,
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Analysis completed in {analysis.processing_time:.1f}s with quality score: {quality_scores.overall}")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed for {video_url}: {e}")
            raise
        finally:
            if 'video_file' in locals():
                genai.delete_file(video_file.name)
    
    async def _extract_basic_content(
        self, 
        video_file: Any, 
        video_url: str, 
        platform: str
    ) -> Dict[str, Any]:
        """Extract basic content using Gemini's multimodal capabilities."""
        
        prompt = f"""
        Analyze this video comprehensively. Extract and return a JSON response with the following structure:
        
        {{
            "metadata": {{
                "title": "Video title or main subject",
                "author": "Creator/channel name if visible",
                "duration": 0.0,
                "language": "detected language",
                "hashtags": ["list", "of", "hashtags"],
                "description": "Brief description of the video content"
            }},
            "transcript": [
                {{
                    "start_time": 0.0,
                    "end_time": 5.0,
                    "text": "Transcribed speech",
                    "speaker": "speaker name if identifiable",
                    "confidence": 0.95
                }}
            ],
            "entities": [
                {{
                    "name": "Entity name",
                    "type": "person|organization|technology|concept|location|product",
                    "mentions": [
                        {{
                            "text": "how it was mentioned",
                            "timestamp": 15.0,
                            "context": "surrounding context"
                        }}
                    ],
                    "description": "Brief description of the entity"
                }}
            ],
            "claims": [
                {{
                    "text": "Factual claim made in the video",
                    "timestamp": 30.0,
                    "confidence": 0.8,
                    "context": "surrounding context",
                    "is_factual": true
                }}
            ],
            "ocr": [
                {{
                    "text": "Text visible on screen",
                    "timestamp": 45.0,
                    "confidence": 0.9,
                    "context": "description of where/how text appears"
                }}
            ]
        }}
        
        Focus on:
        1. Complete transcription with timestamps
        2. All visible text (UI elements, captions, graphics)
        3. Technical terms, tools, and concepts mentioned
        4. Factual claims that can be verified
        5. People, companies, products referenced
        6. Step-by-step processes or tutorials shown
        
        Platform context: {platform}
        Video URL: {video_url}
        """
        
        response = await asyncio.to_thread(
            self.model.generate_content,
            [video_file, prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8000
            )
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown formatting)
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            # Fallback: use structured prompt to get better format
            return await self._retry_with_structured_prompt(video_file, video_url, platform)
    
    async def _research_and_fact_check(self, claims: List[Dict[str, Any]]) -> List[WebResearchFact]:
        """Research and fact-check claims using web search and fact-check databases."""
        researched_facts = []
        
        # Limit to most important claims (top 10)
        important_claims = sorted(claims, key=lambda x: x.get('confidence', 0), reverse=True)[:10]
        
        for claim_data in important_claims:
            claim_text = claim_data['text']
            
            try:
                # Search for supporting/contradicting information
                search_results = await self._web_search(claim_text)
                
                # Check fact-check databases
                fact_check_results = await self._check_fact_databases(claim_text)
                
                # Analyze results with Gemini
                research_summary = await self._analyze_research_results(
                    claim_text, 
                    search_results, 
                    fact_check_results
                )
                
                if research_summary:
                    researched_facts.append(research_summary)
                
            except Exception as e:
                logger.warning(f"Failed to research claim '{claim_text[:50]}...': {e}")
                continue
        
        return researched_facts
    
    async def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """Search the web for information about a claim."""
        # For MVP, return empty - can be enhanced with search API later
        return []
    
    async def _check_fact_databases(self, claim: str) -> List[Dict[str, Any]]:
        """Check claim against fact-checking databases."""
        # Placeholder for fact-check API integration
        # Could integrate with PolitiFact, Snopes, FactCheck.org APIs
        return []
    
    async def _analyze_research_results(
        self,
        original_claim: str,
        search_results: List[Dict[str, Any]],
        fact_checks: List[Dict[str, Any]]
    ) -> Optional[WebResearchFact]:
        """Analyze research results to create a WebResearchFact."""
        
        if not search_results and not fact_checks:
            return None
        
        # Prepare context for Gemini analysis
        context = f"Original claim: {original_claim}\n\n"
        
        if search_results:
            context += "Web search results:\n"
            for i, result in enumerate(search_results):
                context += f"{i+1}. {result['title']} ({result['source']})\n"
                context += f"   {result['snippet']}\n\n"
        
        if fact_checks:
            context += "Fact-check results:\n"
            for i, check in enumerate(fact_checks):
                context += f"{i+1}. {check.get('title', 'Unknown source')}\n"
                context += f"   {check.get('summary', 'No summary available')}\n\n"
        
        prompt = f"""
        Analyze the following claim and research results. Provide a JSON response:
        
        {{
            "corrected_info": "Accurate information based on research (or same as original if accurate)",
            "sources": ["list", "of", "source", "urls"],
            "confidence": 0.85,
            "is_correction": false
        }}
        
        {context}
        
        Determine:
        1. Is the original claim accurate based on the research?
        2. If not, what is the correct information?
        3. What sources support this conclusion?
        4. How confident are you in this assessment (0-1)?
        5. Does this constitute a correction to misinformation?
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            
            # Parse response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            result_data = json.loads(text)
            
            return WebResearchFact(
                original_claim=original_claim,
                corrected_info=result_data['corrected_info'],
                sources=result_data.get('sources', []),
                confidence=result_data.get('confidence', 0.5),
                research_timestamp=datetime.now(),
                is_correction=result_data.get('is_correction', False)
            )
            
        except Exception as e:
            logger.warning(f"Failed to analyze research results for claim: {e}")
            return None
    
    async def _assess_quality(
        self,
        basic_analysis: Dict[str, Any],
        researched_facts: List[WebResearchFact]
    ) -> QualityScores:
        """Assess content quality based on analysis and research."""
        
        # Calculate accuracy based on fact-checking
        corrections = [f for f in researched_facts if f.is_correction]
        accuracy = max(0, 100 - (len(corrections) / max(len(researched_facts), 1)) * 50)
        
        # Technical depth based on entities and technical terms
        tech_entities = [e for e in basic_analysis.get('entities', []) 
                        if e.get('type') in ['technology', 'concept', 'product']]
        technical_depth = min(100, len(tech_entities) * 10)
        
        # Educational value based on structured content
        claims_count = len(basic_analysis.get('claims', []))
        transcript_length = sum(len(t.get('text', '')) for t in basic_analysis.get('transcript', []))
        educational_value = min(100, (claims_count * 5) + (transcript_length / 100))
        
        # Source credibility based on research quality
        avg_research_confidence = sum(f.confidence for f in researched_facts) / max(len(researched_facts), 1) * 100
        
        # Completeness based on content structure
        has_transcript = len(basic_analysis.get('transcript', [])) > 0
        has_entities = len(basic_analysis.get('entities', [])) > 0
        has_claims = len(basic_analysis.get('claims', [])) > 0
        completeness = (has_transcript + has_entities + has_claims) / 3 * 100
        
        # Overall score
        overall = (accuracy + technical_depth + educational_value + avg_research_confidence + completeness) / 5
        
        return QualityScores(
            content_accuracy=accuracy,
            technical_depth=technical_depth,
            educational_value=educational_value,
            source_credibility=avg_research_confidence,
            completeness=completeness,
            overall=overall
        )
    
    async def _create_content_outline(
        self,
        basic_analysis: Dict[str, Any],
        researched_facts: List[WebResearchFact]
    ) -> ContentOutline:
        """Create a structured content outline."""
        
        entities = basic_analysis.get('entities', [])
        claims = basic_analysis.get('claims', [])
        
        # Extract main topic from most mentioned entities
        entity_counts = {}
        for entity in entities:
            entity_counts[entity['name']] = len(entity.get('mentions', []))
        
        main_topic = max(entity_counts.keys(), default="Unknown Topic") if entity_counts else "Unknown Topic"
        
        # Generate subtopics from entity types and claims
        subtopics = []
        tech_entities = [e['name'] for e in entities if e.get('type') == 'technology']
        concept_entities = [e['name'] for e in entities if e.get('type') == 'concept']
        
        if tech_entities:
            subtopics.extend(tech_entities[:5])
        if concept_entities:
            subtopics.extend(concept_entities[:3])
        
        # Key concepts from high-confidence entities
        key_concepts = [e['name'] for e in entities if len(e.get('mentions', [])) >= 2][:10]
        
        # Learning objectives from claims
        learning_objectives = [f"Understand {claim['text'][:100]}..." for claim in claims[:5]]
        
        # Difficulty assessment
        tech_complexity = len([e for e in entities if e.get('type') == 'technology'])
        if tech_complexity >= 5:
            difficulty = "advanced"
        elif tech_complexity >= 3:
            difficulty = "intermediate" 
        else:
            difficulty = "beginner"
        
        return ContentOutline(
            main_topic=main_topic,
            subtopics=subtopics,
            key_concepts=key_concepts,
            learning_objectives=learning_objectives,
            prerequisites=[],  # Could be enhanced with domain knowledge
            difficulty_level=difficulty
        )
    
    def _extract_citations(self, researched_facts: List[WebResearchFact]) -> List[str]:
        """Extract unique citations from research."""
        citations = set()
        for fact in researched_facts:
            citations.update(fact.sources)
        return list(citations)
    
    # Helper methods for parsing Gemini response into structured objects
    def _parse_video_metadata(self, metadata: Dict[str, Any], url: str, platform: str) -> VideoMetadata:
        return VideoMetadata(
            url=url,
            platform=platform,
            title=metadata.get('title', ''),
            author=metadata.get('author', ''),
            duration=metadata.get('duration', 0.0),
            language=metadata.get('language', 'en'),
            hashtags=metadata.get('hashtags', [])
        )
    
    def _parse_transcript(self, transcript: List[Dict[str, Any]]) -> List[TranscriptSegment]:
        segments = []
        for seg in transcript:
            segments.append(TranscriptSegment(
                start_time=seg.get('start_time', 0.0),
                end_time=seg.get('end_time', 0.0),
                text=seg.get('text', ''),
                speaker=seg.get('speaker'),
                confidence=seg.get('confidence', 1.0)
            ))
        return segments
    
    def _parse_entities(self, entities: List[Dict[str, Any]]) -> List[Entity]:
        parsed_entities = []
        for ent in entities:
            parsed_entities.append(Entity(
                name=ent.get('name', ''),
                type=ent.get('type', 'concept'),
                mentions=ent.get('mentions', []),
                description=ent.get('description')
            ))
        return parsed_entities
    
    def _parse_claims(self, claims: List[Dict[str, Any]]) -> List[Claim]:
        parsed_claims = []
        for claim in claims:
            parsed_claims.append(Claim(
                text=claim.get('text', ''),
                timestamp=claim.get('timestamp', 0.0),
                confidence=claim.get('confidence', 1.0),
                context=claim.get('context', ''),
                is_factual=claim.get('is_factual')
            ))
        return parsed_claims
    
    def _parse_ocr(self, ocr_results: List[Dict[str, Any]]) -> List[OCRResult]:
        parsed_ocr = []
        for ocr in ocr_results:
            parsed_ocr.append(OCRResult(
                text=ocr.get('text', ''),
                timestamp=ocr.get('timestamp', 0.0),
                confidence=ocr.get('confidence', 1.0),
                context=ocr.get('context', '')
            ))
        return parsed_ocr
    
    async def _wait_for_file_processing(self, file: Any) -> None:
        """Wait for uploaded file to be processed."""
        while file.state.name == "PROCESSING":
            logger.info("Waiting for file processing...")
            await asyncio.sleep(2)
            file = genai.get_file(file.name)
        
        if file.state.name == "FAILED":
            raise ValueError(f"Video file processing failed: {file.state}")
    
    async def _retry_with_structured_prompt(self, video_file: Any, url: str, platform: str) -> Dict[str, Any]:
        """Retry analysis with more structured prompt if JSON parsing fails."""
        logger.warning("Retrying analysis with structured format")
        
        prompt = """
        Please analyze this video and provide the information in this exact format:

        METADATA:
        Title: [video title]
        Author: [creator name]
        Duration: [duration in seconds]
        Language: [language code]
        Hashtags: [comma separated hashtags]

        TRANSCRIPT:
        [timestamp] Speaker: [transcribed text]
        [continue for all speech]

        ENTITIES:
        [entity name] (type): [description] - mentioned at [timestamps]
        [continue for all entities]

        CLAIMS:
        [timestamp]: [factual claim] (confidence: [0-1])
        [continue for all claims]

        OCR_TEXT:
        [timestamp]: [visible text] - [context description]
        [continue for all visible text]
        """
        
        response = await asyncio.to_thread(
            self.model.generate_content,
            [video_file, prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8000
            )
        )
        
        # Parse the structured response manually
        return self._parse_structured_response(response.text)
    
    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Parse structured text response into JSON format."""
        # This is a fallback parser - implement basic parsing logic
        # For the MVP, return minimal structure
        return {
            "metadata": {
                "title": "Video Analysis",
                "author": "Unknown",
                "duration": 0.0,
                "language": "en",
                "hashtags": []
            },
            "transcript": [],
            "entities": [],
            "claims": [],
            "ocr": []
        }
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()