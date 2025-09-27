"""Knowledge Bot processing pipeline."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger

from core.models.content_models import GeminiAnalysis
from config import Config


class KnowledgeBotPipeline:
    """Main processing pipeline for the Knowledge Bot."""
    
    def __init__(self):
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "last_processed": None
        }
    
    async def process_video_complete(
        self,
        video_url: str,
        analysis: GeminiAnalysis,
        user_id: int
    ) -> Dict[str, Any]:
        """Complete video processing pipeline."""
        
        start_time = datetime.now()
        logger.info(f"Starting complete pipeline for user {user_id}: {video_url}")
        
        try:
            # Import services here to avoid circular imports
            from services.claude_service import ClaudeService
            from services.image_generation_service import ImageGenerationService
            from core.processors.gpt_processor import GPTAssemblyProcessor
            from storage.notion_storage import NotionStorage
            from storage.markdown_storage import MarkdownStorage
            
            # Initialize services
            claude_service = ClaudeService()
            image_service = ImageGenerationService() 
            gpt_processor = GPTAssemblyProcessor()
            notion_storage = NotionStorage()
            markdown_storage = MarkdownStorage()
            
            # Step 1: Claude content enrichment
            logger.info("Step 1: Claude content enrichment")
            enriched_content = await claude_service.enrich_content(analysis)
            
            # Step 2: Generate diagrams if enabled
            if Config.ENABLE_IMAGE_GENERATION and enriched_content.image_plans:
                logger.info("Step 2: Generating technical diagrams")
                enriched_content = await image_service.generate_textbook_diagrams(enriched_content)
            
            # Step 3: GPT final assembly and quality assurance
            logger.info("Step 3: GPT final assembly")
            final_content = await gpt_processor.assemble_final_content(
                analysis=analysis,
                claude_output=enriched_content,
                generated_images=enriched_content.generated_images
            )
            
            # Step 4: Save to storage
            logger.info("Step 4: Saving to storage")
            storage_result = await self._save_to_storage(
                analysis=analysis,
                final_content=final_content,
                video_url=video_url,
                notion_storage=notion_storage,
                markdown_storage=markdown_storage
            )
            
            # Update stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_stats["total_processed"] += 1
            self.processing_stats["successful"] += 1
            self.processing_stats["last_processed"] = datetime.now()
            
            logger.success(f"Pipeline completed successfully in {processing_time:.1f}s")
            
            return {
                "success": True,
                "processing_time": processing_time,
                "final_content": final_content,
                "storage_result": storage_result,
                "quality_score": final_content.get("quality_score", 0),
                "word_count": final_content.get("word_count", 0)
            }
            
        except Exception as e:
            self.processing_stats["failed"] += 1
            logger.error(f"Pipeline failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _save_to_storage(
        self,
        analysis: GeminiAnalysis,
        final_content: Dict[str, Any],
        video_url: str,
        notion_storage,
        markdown_storage
    ) -> Dict[str, Any]:
        """Save content to configured storage systems."""
        
        storage_results = {
            "notion_success": False,
            "markdown_success": False,
            "notion_url": None,
            "markdown_path": None
        }
        
        # Try Notion storage first
        if Config.USE_NOTION_STORAGE and Config.NOTION_API_KEY:
            try:
                notion_url = await notion_storage.save_entry(
                    analysis=analysis,
                    enriched_content=final_content["content"],
                    video_url=video_url
                )
                storage_results["notion_success"] = True
                storage_results["notion_url"] = notion_url
                logger.info(f"Saved to Notion: {notion_url}")
            except Exception as e:
                logger.error(f"Notion storage failed: {e}")
        
        # Always save to Markdown as backup
        try:
            markdown_path = await markdown_storage.save_entry(
                analysis=analysis,
                enriched_content=final_content["content"],
                video_url=video_url
            )
            storage_results["markdown_success"] = True
            storage_results["markdown_path"] = markdown_path
            logger.info(f"Saved to Markdown: {markdown_path}")
        except Exception as e:
            logger.error(f"Markdown storage failed: {e}")
        
        return storage_results
    
    async def validate_prerequisites(self) -> Dict[str, bool]:
        """Validate that all required services and configurations are available."""
        
        validation_results = {
            "config_valid": False,
            "gemini_available": False,
            "claude_available": False,
            "storage_available": False,
            "directories_created": False
        }
        
        try:
            # Validate configuration
            Config.validate()
            validation_results["config_valid"] = True
            
            # Check Gemini
            if Config.GEMINI_API_KEY:
                validation_results["gemini_available"] = True
            
            # Check Claude (via OpenRouter)
            if Config.OPENROUTER_API_KEY:
                validation_results["claude_available"] = True
            
            # Check storage
            if Config.NOTION_API_KEY or Config.KNOWLEDGE_BASE_PATH.exists():
                validation_results["storage_available"] = True
            
            # Ensure directories
            Config.TEMP_DIR.mkdir(parents=True, exist_ok=True)
            Config.KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)
            validation_results["directories_created"] = True
            
        except Exception as e:
            logger.error(f"Pipeline validation failed: {e}")
        
        return validation_results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            **self.processing_stats,
            "success_rate": (
                self.processing_stats["successful"] / max(1, self.processing_stats["total_processed"])
            ) * 100
        }
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up old temporary files."""
        
        if not Config.TEMP_DIR.exists():
            return 0
        
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        try:
            for temp_file in Config.TEMP_DIR.glob("*"):
                if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
                    temp_file.unlink()
                    cleaned_count += 1
                    
            logger.info(f"Cleaned up {cleaned_count} old temporary files")
            
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
        
        return cleaned_count
