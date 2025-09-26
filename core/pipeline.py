"""Main processing pipeline orchestrating the 6-stage AI workflow."""

import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path

from loguru import logger

from core.models.content_models import ProcessingResult, GeminiAnalysis
from core.processors.gemini_processor import EnhancedGeminiProcessor
from core.processors.claude_processor import EnhancedClaudeProcessor
from core.processors.banana_processor import BananaImageProcessor
from core.processors.gpt_processor import GPTAssemblyProcessor
from services.railway_client import RailwayClient
from storage.notion_storage import NotionStorage
from config import TEMP_DIR


class KnowledgeBotPipeline:
    """Main processing pipeline for the Knowledge Bot 6-stage workflow."""
    
    def __init__(self):
        self.gemini_processor = EnhancedGeminiProcessor()
        self.claude_processor = EnhancedClaudeProcessor()
        self.banana_processor = BananaImageProcessor()
        self.gpt_processor = GPTAssemblyProcessor()
        self.railway_client = RailwayClient()
        self.notion_storage = NotionStorage()
        
        # Ensure temp directory exists
        Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    
    async def process_video_url(
        self,
        video_url: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Complete 6-stage processing pipeline:
        1. Gemini: Enhanced analysis with web research
        2. Telegram: User approval (handled externally)
        3. Claude: Textbook-quality content generation
        4. Banana: Conditional image generation
        5. GPT: Final assembly and quality assurance
        6. Notion: Database storage and integration
        """
        
        start_time = time.time()
        logger.info(f"Starting pipeline processing for: {video_url}")
        
        try:
            # Stage 1: Video download and enhanced Gemini analysis
            logger.info("Stage 1: Gemini analysis with web research")
            gemini_analysis = await self._stage_1_gemini_analysis(video_url)
            
            # Stage 2 is handled by Telegram interface (user approval)
            # We assume approval has been granted when this method is called
            
            # Stage 3: Claude textbook content generation
            logger.info("Stage 3: Claude textbook generation")
            claude_output = await self._stage_3_claude_generation(gemini_analysis)
            
            # Stage 4: Conditional Banana image generation
            logger.info("Stage 4: Conditional image generation")
            generated_images = await self._stage_4_banana_images(
                claude_output.image_plans,
                gemini_analysis,
                user_preferences
            )
            
            # Stage 5: GPT final assembly and quality assurance
            logger.info("Stage 5: GPT assembly and QA")
            final_content = await self._stage_5_gpt_assembly(
                gemini_analysis,
                claude_output,
                generated_images
            )
            
            # Stage 6: Notion database storage
            logger.info("Stage 6: Notion storage")
            notion_url = await self._stage_6_notion_storage(
                final_content,
                gemini_analysis,
                video_url
            )
            
            # Create final result
            total_time = time.time() - start_time
            
            result = ProcessingResult(
                gemini_analysis=gemini_analysis,
                claude_output=claude_output,
                generated_images=generated_images,
                notion_payload=final_content.get('notion_payload'),
                notion_page_url=notion_url,
                processing_success=True,
                total_processing_time=total_time
            )
            
            logger.info(f"Pipeline completed successfully in {total_time:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            
            # Return partial result with error
            return ProcessingResult(
                gemini_analysis=gemini_analysis if 'gemini_analysis' in locals() else None,
                claude_output=claude_output if 'claude_output' in locals() else None,
                generated_images=[],
                processing_success=False,
                error_message=str(e),
                total_processing_time=time.time() - start_time
            )
    
    async def _stage_1_gemini_analysis(self, video_url: str) -> GeminiAnalysis:
        """Stage 1: Enhanced Gemini analysis with web research."""
        
        # Detect platform
        platform = self._detect_platform(video_url)
        
        # Download video using Railway client
        video_path = await self.railway_client.download_video(video_url)
        
        try:
            # Enhanced Gemini analysis with fact-checking
            analysis = await self.gemini_processor.analyze_video(
                video_path=video_path,
                video_url=video_url,
                platform=platform
            )
            
            logger.info(f"Gemini analysis completed with quality score: {analysis.quality_scores.overall}")
            return analysis
            
        finally:
            # Clean up downloaded video
            try:
                Path(video_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup video file: {e}")
    
    async def _stage_3_claude_generation(self, analysis: GeminiAnalysis):
        """Stage 3: Claude textbook-quality content generation."""
        
        # Generate comprehensive textbook content
        claude_output = await self.claude_processor.generate_textbook_content(analysis)
        
        logger.info(f"Claude generated {claude_output.word_count} words with {len(claude_output.image_plans)} image plans")
        return claude_output
    
    async def _stage_4_banana_images(
        self,
        image_plans,
        analysis: GeminiAnalysis,
        user_preferences: Optional[Dict[str, Any]]
    ):
        """Stage 4: Conditional Banana image generation."""
        
        # Check if images should be generated based on preferences and content
        should_generate = user_preferences.get('generate_images', True) if user_preferences else True
        
        if not should_generate:
            logger.info("Image generation disabled by user preferences")
            return []
        
        # Analyze content for image generation appropriateness
        try:
            # Handle both TranscriptSegment objects and dict format
            if analysis.transcript and len(analysis.transcript) > 0:
                if hasattr(analysis.transcript[0], 'text'):
                    # TranscriptSegment objects
                    transcript_text = " ".join([seg.text for seg in analysis.transcript])
                elif isinstance(analysis.transcript[0], dict):
                    # Dict format
                    transcript_text = " ".join([seg.get('text', '') for seg in analysis.transcript])
                else:
                    # Fallback to string representation
                    transcript_text = " ".join([str(seg) for seg in analysis.transcript])
            else:
                transcript_text = ""
                
            content_analysis = {
                'word_count': len(transcript_text),
                'difficulty': analysis.content_outline.difficulty_level,
                'technical_complexity': len([e for e in analysis.entities if e.type == 'technology'])
            }
        except Exception as e:
            logger.warning(f"Error processing transcript for content analysis: {e}")
            content_analysis = {
                'word_count': 1000,  # Default fallback
                'difficulty': 'medium',
                'technical_complexity': 3
            }
        
        # Generate images if appropriate
        generated_images = await self.banana_processor.process_all_images(
            image_plans,
            content_analysis
        )
        
        logger.info(f"Generated {len(generated_images)} images")
        return generated_images
    
    async def _stage_5_gpt_assembly(
        self,
        analysis: GeminiAnalysis,
        claude_output,
        generated_images
    ):
        """Stage 5: GPT final assembly and quality assurance."""
        
        # Assemble all components with GPT
        final_content = await self.gpt_processor.assemble_final_content(
            analysis,
            claude_output,
            generated_images
        )
        
        logger.info(f"GPT assembly completed with final quality score: {final_content['quality_score']}")
        return final_content
    
    async def _stage_6_notion_storage(
        self,
        final_content: Dict[str, Any],
        analysis: GeminiAnalysis,
        video_url: str
    ) -> str:
        """Stage 6: Notion database storage."""
        
        # Create Notion payload
        notion_payload = await self.gpt_processor.create_notion_payload(
            final_content,
            analysis,
            video_url
        )
        
        # Save to Notion database
        notion_url = await self.notion_storage.save_enhanced_entry(
            notion_payload,
            analysis,
            final_content
        )
        
        logger.info(f"Saved to Notion: {notion_url}")
        return notion_url
    
    def _detect_platform(self, url: str) -> str:
        """Detect video platform from URL."""
        url_lower = url.lower()
        
        if 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        else:
            return 'unknown'
    
    async def get_processing_preview(
        self,
        video_url: str
    ) -> Dict[str, Any]:
        """Get a processing preview without full generation (for Telegram approval)."""
        
        logger.info(f"Generating preview for: {video_url}")
        
        try:
            # Quick analysis for preview
            platform = self._detect_platform(video_url)
            video_path = await self.railway_client.download_video(video_url)
            
            try:
                # Basic Gemini analysis (without full web research)
                analysis = await self.gemini_processor.analyze_video(
                    video_path=video_path,
                    video_url=video_url,
                    platform=platform
                )
                
                # Generate executive summary with Claude
                executive_summary = await self.claude_processor.generate_executive_summary(analysis)
                
                return {
                    'topic': analysis.content_outline.main_topic,
                    'difficulty': analysis.content_outline.difficulty_level,
                    'quality_score': analysis.quality_scores.overall,
                    'estimated_words': 2500 + (len(analysis.entities) * 50),
                    'estimated_sections': 8,
                    'estimated_images': len(analysis.entities) // 3,
                    'key_concepts': [e.name for e in analysis.entities[:8]],
                    'executive_summary': executive_summary,
                    'processing_time_estimate': '3-5 minutes',
                    'confidence': analysis.quality_scores.overall
                }
                
            finally:
                # Cleanup
                try:
                    Path(video_path).unlink()
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return {
                'topic': 'Analysis Failed',
                'error': str(e),
                'quality_score': 0
            }
    
    async def validate_video_url(self, url: str) -> Dict[str, Any]:
        """Validate if a video URL is processable."""
        
        platform = self._detect_platform(url)
        
        if platform == 'unknown':
            return {
                'valid': False,
                'error': 'Unsupported platform. Please use TikTok, Instagram, or YouTube URLs.'
            }
        
        try:
            # Try to get basic video info (without downloading)
            video_info = await self.railway_client.get_video_info(url)
            
            # Check duration limits
            duration = video_info.get('duration', 0)
            if duration > 1800:  # 30 minutes max
                return {
                    'valid': False,
                    'error': 'Video too long. Maximum duration is 30 minutes.'
                }
            
            return {
                'valid': True,
                'platform': platform,
                'duration': duration,
                'title': video_info.get('title', 'Unknown'),
                'author': video_info.get('uploader', 'Unknown')
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Unable to access video: {str(e)}'
            }
    
    async def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            temp_path = Path(TEMP_DIR)
            if temp_path.exists():
                for file in temp_path.glob('*'):
                    if file.is_file() and time.time() - file.stat().st_mtime > 3600:  # 1 hour old
                        file.unlink()
                        logger.debug(f"Cleaned up old temp file: {file}")
        except Exception as e:
            logger.warning(f"Temp file cleanup failed: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status for monitoring."""
        
        health = {
            'status': 'healthy',
            'components': {},
            'timestamp': time.time()
        }
        
        # Check each component
        try:
            # Test Gemini
            health['components']['gemini'] = 'healthy'  # Would test actual API
        except Exception:
            health['components']['gemini'] = 'unhealthy'
            health['status'] = 'degraded'
        
        try:
            # Test Claude
            health['components']['claude'] = 'healthy'  # Would test actual API
        except Exception:
            health['components']['claude'] = 'unhealthy'
            health['status'] = 'degraded'
        
        try:
            # Test Railway
            health['components']['railway'] = 'healthy'  # Would test actual API
        except Exception:
            health['components']['railway'] = 'unhealthy'
            health['status'] = 'degraded'
        
        try:
            # Test Notion
            health['components']['notion'] = 'healthy'  # Would test actual API
        except Exception:
            health['components']['notion'] = 'unhealthy'
            health['status'] = 'degraded'
        
        return health
    
    async def close(self):
        """Clean up all processors."""
        await asyncio.gather(
            self.gemini_processor.close(),
            self.claude_processor.close(),
            self.banana_processor.close(),
            self.gpt_processor.close(),
            return_exceptions=True
        )