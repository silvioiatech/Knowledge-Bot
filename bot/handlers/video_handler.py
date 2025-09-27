"""Video processing handlers with web research and confirmation preview."""

import asyncio
import re
from typing import Dict, Any
from urllib.parse import urlparse

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.filters import Command
from loguru import logger

from services.railway_client import RailwayClient
from services.gemini_service import EnhancedGeminiService
from services.claude_service import ClaudeService
from services.image_generation_service import ImageGenerationService
from storage.markdown_storage import MarkdownStorage
from storage.notion_storage import NotionStorage
from config import Config, ERROR_MESSAGES, PROGRESS_MESSAGES, SUPPORTED_PLATFORMS
from core.pipeline import KnowledgeBotPipeline

# Router for video handlers
router = Router()

# Service instances - initialized lazily
railway_client = None
gemini_service = None
claude_service = None
image_service = None
markdown_storage = None
notion_storage = None
pipeline = None


def get_services():
    """Initialize services lazily."""
    global railway_client, gemini_service, claude_service, image_service
    global markdown_storage, notion_storage, pipeline
    
    if railway_client is None:
        railway_client = RailwayClient()
        gemini_service = EnhancedGeminiService()
        claude_service = ClaudeService()
        image_service = ImageGenerationService()
        markdown_storage = MarkdownStorage()
        notion_storage = NotionStorage()
        pipeline = KnowledgeBotPipeline()
        logger.debug("Services initialized lazily")
    
    return (railway_client, gemini_service, claude_service, image_service,
            markdown_storage, notion_storage, pipeline)

# User sessions to track processing state
user_sessions: Dict[int, Dict[str, Any]] = {}


def is_supported_video_url(url: str) -> str:
    """Check if URL is from supported platforms."""
    for platform, patterns in SUPPORTED_PLATFORMS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    return ""


def create_preview_keyboard(analysis_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for video analysis preview."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Add to Knowledge Base",
                    callback_data=f"approve_{analysis_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"reject_{analysis_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Re-analyze with Different Focus",
                    callback_data=f"reanalyze_{analysis_id}"
                )
            ]
        ]
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    welcome_text = """
🤖 **Knowledge Bot Enhanced**

I can analyze TikTok and Instagram videos to create comprehensive educational content for your knowledge base.

**What I do:**
1. 📥 **Download** your video
2. 🧠 **Analyze** with AI + web research  
3. 📋 **Preview** technical summary for your approval
4. ✨ **Generate** comprehensive educational content
5. 🖼️ **Create** technical diagrams (optional)
6. 💾 **Save** to your knowledge base

Just send me a TikTok or Instagram video URL to get started!

**Supported platforms:** TikTok, Instagram Reels
"""
    await message.answer(welcome_text)


@router.message(F.text.regexp(r'https?://[^\s]+'))
async def process_video_url(message: Message) -> None:
    """Process video URLs with enhanced analysis and preview."""
    url = message.text.strip()
    user_id = message.from_user.id
    
    # Initialize services
    (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
     markdown_storage_inst, notion_storage_inst, pipeline_inst) = get_services()
    
    # Validate URL
    platform = is_supported_video_url(url)
    if not platform:
        await message.answer(ERROR_MESSAGES["invalid_url"])
        return
    
    try:
        # Step 1: Download video
        logger.info(f"Starting video processing for user {user_id}: {url}")
        status_msg = await message.answer(PROGRESS_MESSAGES["downloading"])
        
        # Download via Railway
        video_path = await railway_client_inst.download_video(url)
        logger.info(f"Video downloaded successfully: {video_path}")
        
        # Step 2: Enhanced Gemini analysis with web research
        await status_msg.edit_text(PROGRESS_MESSAGES["analyzing"])
        analysis = await gemini_service_inst.analyze_video_with_research(
            video_path=video_path,
            video_url=url,
            platform=platform
        )
        
        logger.info(f"Video analysis completed for user {user_id}")
        
        # Step 3: Generate technical preview
        await status_msg.edit_text("🔍 Generating technical preview...")
        preview = await _generate_technical_preview(analysis, url)
        
        # Store analysis in user session
        analysis_id = f"{user_id}_{hash(url) % 10000}"
        user_sessions[user_id] = {
            'analysis_id': analysis_id,
            'analysis': analysis,
            'video_url': url,
            'platform': platform,
            'preview': preview
        }
        
        # Step 4: Send technical preview with confirmation buttons
        keyboard = create_preview_keyboard(analysis_id)
        await status_msg.edit_text(
            text=preview,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Analysis failed for user {user_id}: {e}")
        await status_msg.edit_text(ERROR_MESSAGES["analysis_failed"])


async def _generate_technical_preview(analysis, video_url: str) -> str:
    """Generate a comprehensive technical preview of the video analysis."""
    
    # Extract key information from analysis
    title = analysis.video_metadata.title or "Untitled Video"
    author = analysis.video_metadata.author or "Unknown"
    duration = analysis.video_metadata.duration or 0
    
    # Main topic and category
    main_topic = analysis.content_outline.main_topic
    category = analysis.content_outline.category
    difficulty = analysis.content_outline.difficulty_level
    
    # Key concepts and tools
    key_concepts = [entity.name for entity in analysis.entities if entity.type in ['concept', 'technology']][:6]
    tools_mentioned = [entity.name for entity in analysis.entities if entity.type == 'technology'][:5]
    
    # Research findings
    research_topics = analysis.research_queries if hasattr(analysis, 'research_queries') else []
    web_sources = len(analysis.fact_checks) if hasattr(analysis, 'fact_checks') else 0
    
    # Quality metrics
    confidence = analysis.quality_scores.overall
    completeness = analysis.quality_scores.content_completeness
    technical_depth = analysis.quality_scores.technical_depth
    
    # Estimated output
    estimated_words = 2000 + (len(analysis.entities) * 30)
    estimated_sections = len(analysis.content_outline.key_points) + 3
    
    preview = f"""
🎥 <b>Technical Analysis Preview</b>

📹 <b>Video Details:</b>
• Title: {title[:60]}{'...' if len(title) > 60 else ''}
• Author: {author}
• Duration: {duration:.1f}s | Platform: {video_url.split('/')[2].split('.')[0].upper()}

🎯 <b>Content Analysis:</b>
• <b>Main Topic:</b> {main_topic}
• <b>Category:</b> {category}
• <b>Difficulty:</b> {difficulty.title()}
• <b>Confidence:</b> {confidence:.0%}

🔍 <b>Web Research Conducted:</b>
• Research queries: {len(research_topics)}
• Web sources verified: {web_sources}
• Fact-checking: {'✅' if web_sources > 0 else '⚠️'}

🧠 <b>Key Technical Concepts:</b>
{chr(10).join([f"• {concept}" for concept in key_concepts[:4]])}
{f"... and {len(key_concepts)-4} more" if len(key_concepts) > 4 else ""}

🛠️ <b>Tools/Technologies:</b>
{chr(10).join([f"• {tool}" for tool in tools_mentioned[:3]]) if tools_mentioned else "• No specific tools mentioned"}

📊 <b>Quality Metrics:</b>
• Content Completeness: {completeness:.0%}
• Technical Depth: {technical_depth:.0%}
• Overall Quality: {confidence:.0%}

📝 <b>Estimated Output:</b>
• ~{estimated_words:,} words of educational content
• ~{estimated_sections} detailed sections
• Technical diagrams: {"Yes" if Config.ENABLE_IMAGE_GENERATION else "No"}
• Knowledge base storage: {"Notion + Markdown" if Config.USE_NOTION_STORAGE else "Markdown"}

<b>Proceed with full content generation?</b>
"""
    
    return preview.strip()


@router.callback_query(F.data.startswith("approve_"))
async def handle_approval_callback(callback: CallbackQuery) -> None:
    """Handle approval of video analysis."""
    analysis_id = callback.data.replace("approve_", "")
    user_id = callback.from_user.id
    
    # Initialize services
    (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
     markdown_storage_inst, notion_storage_inst, pipeline_inst) = get_services()
    
    if user_id not in user_sessions:
        await callback.answer("❌ Session expired. Please submit the video URL again.")
        return
    
    session = user_sessions[user_id]
    if session['analysis_id'] != analysis_id:
        await callback.answer("❌ Invalid session. Please try again.")
        return
    
    try:
        # Update message to show processing
        await callback.message.edit_text(PROGRESS_MESSAGES["enriching"])
        
        # Step 4: Claude content enrichment
        enriched_content = await claude_service_inst.enrich_content(session['analysis'])
        
        # Step 5: Generate diagrams if enabled
        if Config.ENABLE_IMAGE_GENERATION:
            await callback.message.edit_text(PROGRESS_MESSAGES["generating_diagrams"])
            enriched_content = await image_service_inst.generate_textbook_diagrams(enriched_content)
        
        # Step 6: Save to storage
        await callback.message.edit_text(PROGRESS_MESSAGES["saving"])
        
        # Try Notion first, fallback to Markdown
        storage_success = False
        storage_location = ""
        
        try:
            if Config.USE_NOTION_STORAGE and Config.NOTION_API_KEY:
                notion_url = await notion_storage_inst.save_entry(
                    session['analysis'], 
                    enriched_content,
                    session['video_url']
                )
                storage_location = f"📋 <a href='{notion_url}'>Notion Database</a>"
                storage_success = True
        except Exception as notion_error:
            logger.error(f"Notion storage failed: {notion_error}, falling back to local storage")
        
        # Fallback to Markdown storage
        if not storage_success:
            file_path = await markdown_storage_inst.save_entry(
                session['analysis'],
                enriched_content,
                session['video_url']
            )
            storage_location = f"📁 <code>{file_path}</code>"
        
        # Success message
        success_message = f"""
✅ <b>Knowledge Entry Created Successfully!</b>

📊 <b>Final Metrics:</b>
• Words Generated: ~{len(enriched_content.split()) if isinstance(enriched_content, str) else 'N/A'}
• Processing Time: Complete
• Storage: {storage_location}

🎯 <b>Content Includes:</b>
• Comprehensive analysis from Gemini
• Educational content from Claude  
• Web research validation
• Technical concepts breakdown
{'• AI-generated diagrams' if Config.ENABLE_IMAGE_GENERATION else ''}

The knowledge has been added to your database!
        """
        
        await callback.message.edit_text(
            success_message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        # Clear user session
        del user_sessions[user_id]
        
    except Exception as e:
        logger.error(f"Processing failed for user {user_id}: {e}")
        await callback.message.edit_text("❌ Processing failed. Please try again.")
    
    await callback.answer()


@router.callback_query(F.data.startswith("reject_"))
async def handle_rejection_callback(callback: CallbackQuery) -> None:
    """Handle rejection of video analysis."""
    user_id = callback.from_user.id
    
    # Clear user session
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await callback.message.edit_text(
        "❌ Analysis rejected. Send me another video URL when you're ready!",
        reply_markup=None
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reanalyze_"))
async def handle_reanalyze_callback(callback: CallbackQuery) -> None:
    """Handle request to re-analyze with different focus."""
    analysis_id = callback.data.replace("reanalyze_", "")
    user_id = callback.from_user.id
    
    # Initialize services
    (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
     markdown_storage_inst, notion_storage_inst, pipeline_inst) = get_services()
    
    if user_id not in user_sessions:
        await callback.answer("❌ Session expired. Please submit the video URL again.")
        return
    
    session = user_sessions[user_id]
    
    try:
        await callback.message.edit_text("🔄 Re-analyzing with enhanced focus...")
        
        # Re-run analysis with different parameters
        analysis = await gemini_service_inst.analyze_video_with_research(
            video_path=None,  # Use cached if available
            video_url=session['video_url'],
            platform=session['platform'],
            enhanced_focus=True  # Different analysis approach
        )
        
        # Generate new preview
        preview = await _generate_technical_preview(analysis, session['video_url'])
        
        # Update session
        session['analysis'] = analysis
        session['preview'] = preview
        
        # Send updated preview
        keyboard = create_preview_keyboard(analysis_id)
        await callback.message.edit_text(
            text=preview,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Re-analysis failed for user {user_id}: {e}")
        await callback.message.edit_text("❌ Re-analysis failed. Please try with a new video.")
    
    await callback.answer()


def register_video_handlers(dp) -> None:
    """Register all video handlers."""
    dp.include_router(router)
    logger.info("Video handlers registered")
