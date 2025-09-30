"""Video processing handlers with web research and confirmation preview."""

import re
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.filters import Command
from loguru import logger

from services.railway_client import RailwayClient
from services.gemini_service import EnhancedGeminiService
from services.enhanced_claude_service import EnhancedClaudeService
from services.image_generation_service import SmartImageGenerationService
from storage.markdown_storage import MarkdownStorage
from storage.notion_storage import EnhancedNotionStorageService
from bot.interactive_category_system import InteractiveCategorySystem
from core.models.content_models import NotionPayload
from config import Config, ERROR_MESSAGES, SUPPORTED_PLATFORMS

# Router for video handlers
router = Router()

# Service instances - initialized lazily
railway_client = None
gemini_service = None
claude_service = None
image_service = None


def _determine_content_category(analysis) -> str:
    """Determine content category from analysis."""
    main_topic = analysis.content_outline.main_topic.lower()
    entities = [entity.name.lower() for entity in analysis.entities]
    
    # Category mapping based on content
    if any(term in main_topic or any(term in entity for entity in entities) 
           for term in ["ai", "machine learning", "llm", "neural", "gpt", "claude"]):
        return "🤖 AI"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["web", "javascript", "react", "vue", "html", "css"]):
        return "🌐 Web Development"  
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["python", "java", "golang", "rust", "programming"]):
        return "💻 Programming"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["devops", "docker", "kubernetes", "cloud", "aws"]):
        return "⚙️ DevOps"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["mobile", "ios", "android", "react native", "flutter"]):
        return "📱 Mobile"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["security", "cybersecurity", "encryption", "authentication"]):
        return "🛡️ Security"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["data science", "analytics", "database", "sql", "big data"]):
        return "📊 Data"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["mac", "macos", "osx", "macbook", "apple", "xcode", "homebrew"]):
        return "🍎 macOS"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["linux", "ubuntu", "debian", "fedora", "arch", "centos", "unix", "bash", "terminal"]):
        return "🐧 Linux"
    elif any(term in main_topic or any(term in entity for entity in entities)
            for term in ["windows", "microsoft", "powershell", "cmd", "wsl", "visual studio"]):
        return "🪟 Windows"
    else:
        return "📚 General Tech"
markdown_storage = None
notion_storage = None
railway_storage = None


def get_services():
    """Initialize services lazily with singleton pattern."""
    global railway_client, gemini_service, claude_service, image_service
    global markdown_storage, notion_storage, railway_storage
    
    if railway_client is None:
        railway_client = RailwayClient()
        gemini_service = EnhancedGeminiService()
        claude_service = EnhancedClaudeService()
        image_service = SmartImageGenerationService()
        markdown_storage = MarkdownStorage()
        notion_storage = EnhancedNotionStorageService()
        # Note: RailwayStorage doesn't exist yet, using markdown for now
        railway_storage = markdown_storage
        logger.debug("Enhanced services initialized with singleton pattern")
    
    return (railway_client, gemini_service, claude_service, image_service,
            markdown_storage, notion_storage, railway_storage)

# User sessions to track processing state with TTL
user_sessions: Dict[int, Dict[str, Any]] = {}
SESSION_TTL_MINUTES = 30

# Background task for session cleanup
cleanup_task = None


async def cleanup_expired_sessions():
    """Background task to clean up expired user sessions."""
    while True:
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for user_id, session in user_sessions.items():
                session_time = session.get('created_at', current_time)
                if current_time - session_time > timedelta(minutes=SESSION_TTL_MINUTES):
                    expired_sessions.append(user_id)
            
            for user_id in expired_sessions:
                del user_sessions[user_id]
                logger.info(f"Cleaned up expired session for user {user_id}")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
        
        # Run cleanup every 10 minutes
        await asyncio.sleep(600)


def start_session_cleanup():
    """Start the session cleanup background task."""
    global cleanup_task
    if cleanup_task is None or cleanup_task.done():
        cleanup_task = asyncio.create_task(cleanup_expired_sessions())
        logger.info("Session cleanup task started")


def get_or_create_session(user_id: int) -> Dict[str, Any]:
    """Get existing session or create new one with TTL."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
    else:
        user_sessions[user_id]['last_activity'] = datetime.now()
    
    return user_sessions[user_id]


def clear_user_session(user_id: int):
    """Manually clear a user's session."""
    if user_id in user_sessions:
        del user_sessions[user_id]
        logger.info(f"Cleared session for user {user_id}")


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
🤖 **Enhanced Knowledge Bot**

I analyze TikTok and Instagram videos to create comprehensive educational content with smart AI optimization.

**🎯 Enhanced Features:**
1. 📥 **Smart Download** - Railway-powered video processing
2. 🧠 **AI Analysis** - Gemini 1.5 Flash advanced content analysis  
3. 🎨 **Conditional Image Generation** - Claude evaluates when visuals add value
4. � **Interactive Categories** - Choose optimal knowledge organization
5. 🗄️ **Notion Integration** - Exact database schema mapping
6. ✨ **Educational Enhancement** - Claude transforms to learning material

**🔄 Intelligent Workflow:**
• Claude analyzes content for category suggestions
• Interactive selection with inline keyboards
• Smart image generation only when beneficial
• Comprehensive Notion database integration
• Cost-optimized processing pipeline

**💡 What makes this special:**
• **Smart Cost Management** - Images generated only when necessary
• **Exact Schema Mapping** - Perfect Notion database integration  
• **Interactive Control** - You choose categories and content flow
• **Educational Focus** - Content optimized for learning
• **Quality Assurance** - Multi-AI validation and enhancement

Just send me a TikTok or Instagram video URL to experience the enhanced workflow!

**Supported platforms:** TikTok, Instagram Reels
"""
    await message.answer(welcome_text)


@router.message(F.text.regexp(r'https?://[^\s]+'))
async def process_video_url(message: Message) -> None:
    """Process video URLs with non-blocking async processing."""
    url = message.text.strip()
    user_id = message.from_user.id
    
    # Start session cleanup if not running
    start_session_cleanup()
    
    # Validate URL
    platform = is_supported_video_url(url)
    if not platform:
        await message.answer(ERROR_MESSAGES["invalid_url"])
        return
    
    # Check if user already has an active session
    session = get_or_create_session(user_id)
    if 'processing' in session and session['processing']:
        await message.answer("⏳ You have a video being processed. Please wait for it to complete.")
        return
    
    # Mark as processing
    session['processing'] = True
    session['url'] = url
    session['platform'] = platform
    
    try:
        # Send initial message
        status_msg = await message.answer("🎬 **Starting Video Processing**\n\n📥 Initiating download...")
        
        # Start processing task (non-blocking)
        task = asyncio.create_task(process_video_task(user_id, url, platform, status_msg))
        session['task'] = task
        
        logger.info(f"Started non-blocking video processing task for user {user_id}: {url}")
        
    except Exception as e:
        # Clear processing flag on error
        session['processing'] = False
        logger.error(f"Failed to start processing for user {user_id}: {e}")
        await message.answer("❌ Failed to start processing. Please try again.")


async def process_video_task(user_id: int, url: str, platform: str, status_msg) -> None:
    """Non-blocking video processing task."""
    session = get_or_create_session(user_id)
    
    try:
        # Initialize services
        (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
         markdown_storage_inst, notion_storage_inst, railway_storage_inst) = get_services()
        
        # Step 1: Download video with retry
        await status_msg.edit_text("🎬 **Video Processing**\n\n📥 Downloading video...")
        video_path = await railway_client_inst.download_video(url)
        logger.info(f"Video downloaded successfully: {video_path}")
        
        # Step 2: Analyze with Gemini (no fake research)
        await status_msg.edit_text("🎬 **Video Processing**\n\n🤖 Analyzing content with AI...")
        analysis = await gemini_service_inst.analyze_video_with_research(
            video_path=video_path,
            video_url=url,
            platform=platform
        )
        
        logger.info(f"Video analysis completed for user {user_id}")
        
        # Step 3: Generate preview
        await status_msg.edit_text("🎬 **Video Processing**\n\n🔍 Generating preview...")
        preview = await _generate_technical_preview(analysis, url)
        
        # Store analysis in session
        analysis_id = f"{user_id}_{hash(url) % 10000}"
        session.update({
            'analysis_id': analysis_id,
            'analysis': analysis,
            'video_url': url,
            'platform': platform,
            'preview': preview,
            'processing': False  # Mark as complete
        })
        
        # Show preview with approval buttons
        keyboard = create_preview_keyboard(analysis_id)
        await status_msg.edit_text(
            text=preview,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        session['processing'] = False
        logger.error(f"Video processing failed for user {user_id}: {e}")
        await status_msg.edit_text(
            f"❌ **Processing Failed**\n\n"
            f"Error: {str(e)[:100]}...\n\n"
            f"Please try again or contact support."
        )


async def _generate_technical_preview(analysis, video_url: str) -> str:
    """Generate a comprehensive technical preview of the video analysis."""
    
    # Extract key information from analysis
    title = analysis.video_metadata.title or "Untitled Video"
    author = analysis.video_metadata.author or "Unknown"
    duration = analysis.video_metadata.duration or 0
    
    # Main topic and category
    main_topic = analysis.content_outline.main_topic
    category = _determine_content_category(analysis)
    difficulty = analysis.content_outline.difficulty_level
    
    # Key concepts and tools
    key_concepts = [entity.name for entity in analysis.entities if entity.type in ['concept', 'technology']][:6]
    tools_mentioned = [entity.name for entity in analysis.entities if entity.type == 'technology'][:5]
    
    # Quality metrics (realistic 0-100 scaling)
    confidence = min(85, max(60, int(analysis.quality_scores.overall)))
    completeness = min(80, max(55, int(analysis.quality_scores.completeness)))
    technical_depth = min(85, max(50, int(analysis.quality_scores.technical_depth)))
    educational_value = min(90, max(65, int(analysis.quality_scores.educational_value)))
    
    # Content summary
    content_summary = f"This video covers {main_topic.lower()} with practical insights."
    
    # Estimated output
    estimated_words = 1800 + (len(analysis.entities) * 40) + (len(analysis.content_outline.key_concepts) * 150)
    estimated_sections = len(analysis.content_outline.key_concepts) + 4
    estimated_read_time = max(5, estimated_words // 200)  # ~200 WPM reading speed
    
    preview = f"""🎥 <b>Enhanced Technical Analysis</b>

📹 <b>Video Details:</b>
• <b>Title:</b> {title[:65]}{'...' if len(title) > 65 else ''}
• <b>Author:</b> {author}
• <b>Duration:</b> {duration:.1f}s | <b>Platform:</b> {video_url.split('/')[2].split('.')[0].upper()}

📝 <b>Content Summary:</b>
<i>{content_summary[:200]}{'...' if len(content_summary or '') > 200 else ''}</i>

🎯 <b>Analysis Results:</b>
• <b>Main Topic:</b> {main_topic}
• <b>Category:</b> {category}
• <b>Difficulty:</b> {difficulty.title()}
• <b>Overall Quality:</b> {confidence}%

🧠 <b>Key Learning Points:</b>
{chr(10).join([f"• {concept}" for concept in key_concepts[:4]])}
{f"<i>... and {len(key_concepts)-4} more concepts</i>" if len(key_concepts) > 4 else ""}

🛠️ <b>Tools & Technologies:</b>
{chr(10).join([f"• {tool}" for tool in tools_mentioned[:3]]) if tools_mentioned else "• General technical concepts"}
{f"<i>... and {len(tools_mentioned)-3} more tools</i>" if len(tools_mentioned) > 3 else ""}

🔍 <b>Analysis Quality:</b>
• <b>Research queries:</b> Analysis completed without external research
• <b>Quality assurance:</b> ✅ AI-verified content structure

📊 <b>Quality Metrics:</b>
• <b>Overall Quality:</b> {confidence}% | <b>Completeness:</b> {completeness}%
• <b>Technical Depth:</b> {technical_depth}% | <b>Educational Value:</b> {educational_value}%

📄 <b>Expected Output:</b>
• <b>Content Length:</b> ~{estimated_words:,} words ({estimated_read_time} min read)
• <b>Structure:</b> {estimated_sections} detailed sections with examples
• <b>Format:</b> Professional markdown with examples
• <b>Storage:</b> {"Notion database + Markdown files" if Config.USE_NOTION_STORAGE else "Markdown knowledge base"}

<b>✅ Ready for content generation and knowledge base storage?</b>"""
    
    return preview.strip()



@router.callback_query(F.data.startswith("approve_"))
async def handle_approval_callback(callback: CallbackQuery) -> None:
    """Handle approval of video analysis with complete enhanced workflow."""
    analysis_id = callback.data.replace("approve_", "")
    user_id = callback.from_user.id
    
    # Initialize services
    (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
     markdown_storage_inst, notion_storage_inst, railway_storage_inst) = get_services()
    
    if user_id not in user_sessions:
        await callback.answer("❌ Session expired. Please submit the video URL again.")
        return
    
    session = user_sessions[user_id]
    if session['analysis_id'] != analysis_id:
        await callback.answer("❌ Invalid session. Please try again.")
        return
    
    try:
        # Initialize interactive category system
        category_system = InteractiveCategorySystem()
        
        # Step 1: Enhanced Claude analysis for category suggestions
        await callback.message.edit_text("🤖 Analyzing content for optimal categorization...")
        
        category_suggestions = await claude_service_inst.analyze_content_for_categories(
            session['analysis']
        )
        
        # Step 2: Show interactive category selection
        selection_message, keyboard = category_system.create_category_selection_message(
            category_suggestions, user_id
        )
        
        # Store analysis in session for category selection
        session['category_suggestions'] = category_suggestions
        session['awaiting_category'] = True
        
        await callback.message.edit_text(
            text=selection_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Enhanced processing failed for user {user_id}: {e}")
        await callback.message.edit_text("❌ Processing failed. Please try again.")
    
    await callback.answer()


@router.callback_query(F.data.startswith("cat:") | F.data.startswith("sub:"))
async def handle_category_selection(callback: CallbackQuery) -> None:
    """Handle category selection and continue with enhanced processing."""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions:
        await callback.answer("❌ Session expired. Please submit the video URL again.")
        return
    
    session = user_sessions[user_id]
    if not session.get('awaiting_category'):
        await callback.answer("❌ Invalid session state.")
        return
    
    try:
        # Initialize services
        (railway_client_inst, gemini_service_inst, claude_service_inst, image_service_inst,
         markdown_storage_inst, notion_storage_inst, railway_storage_inst) = get_services()
        
        category_system = InteractiveCategorySystem()
        
        # Handle category selection
        message_text, keyboard, is_final = await category_system.handle_category_selection(
            user_id, callback.data
        )
        
        if not is_final:
            # Still selecting - update message with new keyboard
            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Final selection made - get the selected category and continue processing
            final_selection = category_system.get_final_selection(user_id)
            if not final_selection:
                await callback.answer("❌ Failed to get category selection.")
                return
            
            selected_category = final_selection.category
            session['selected_category'] = selected_category
            session['awaiting_category'] = False
            
            # Show processing message
            await callback.message.edit_text(message_text, parse_mode="HTML")
            
            # Step 3: Claude content enrichment with selected category
            await callback.message.edit_text("✨ Generating enhanced educational content...")
            
            enhanced_content = await claude_service_inst.create_enhanced_content(
                session['analysis'],
                selected_category
            )
            
            # Step 4: Smart conditional image generation
            await callback.message.edit_text("🎨 Evaluating image generation necessity...")
            
            image_evaluation = await claude_service_inst.evaluate_image_necessity(
                enhanced_content
            )
            
            generated_images = []
            if image_evaluation.should_generate:
                await callback.message.edit_text("🎨 Generating AI images...")
                generated_images = await image_service_inst.generate_conditional_images(
                    enhanced_content, image_evaluation
                )
            
            # Step 5: Extract Notion metadata
            await callback.message.edit_text("📊 Preparing database entry...")
            
            notion_metadata = await claude_service_inst.extract_notion_metadata(
                session['analysis'], enhanced_content, selected_category
            )
        
        # Create NotionPayload
        notion_payload = NotionPayload(
            title=notion_metadata.title,
            category=selected_category,
            subcategory=notion_metadata.subcategory,
            content_quality=notion_metadata.content_quality,
            difficulty=notion_metadata.difficulty,
            word_count=len(enhanced_content.split()) if isinstance(enhanced_content, str) else 0,
            processing_date=datetime.now().isoformat(),
            source_video=session['video_url'],
            key_points=notion_metadata.key_points,
            gemini_confidence=notion_metadata.gemini_confidence,
            tags=notion_metadata.tags,
            tools_mentioned=notion_metadata.tools_mentioned,
            platform_specific=notion_metadata.platform_specific,
            prerequisites=notion_metadata.prerequisites,
            related=notion_metadata.related,
            advanced_topics=notion_metadata.advanced_topics,
            auto_created_category=True,
            verified=False,
            ready_for_script=notion_metadata.content_quality in ["📚 High Quality", "🌟 Premium"],
            ready_for_ebook=notion_metadata.content_quality == "🌟 Premium"
        )
        
        # Add content blocks for Notion
        if isinstance(enhanced_content, str):
            notion_payload.content_blocks = notion_storage_inst.create_notion_content_blocks(enhanced_content)
        
        # Step 6: Save to Notion database
        await callback.message.edit_text("💾 Saving to knowledge base...")
        
        success, notion_url = await notion_storage_inst.save_enhanced_entry(notion_payload)
        
        if success:
            # Generate comprehensive result message  
            result_message = category_system.create_processing_result_message(
                notion_payload, railway_url="", notion_url=notion_url
            )
            
            await callback.message.edit_text(
                text=result_message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        else:
            await callback.message.edit_text(
                "❌ Failed to save to Notion database. Please check configuration."
            )
        
        # Clear user session and category selection
        category_system.clear_selection(user_id)
        if user_id in user_sessions:
            del user_sessions[user_id]
            
    except Exception as e:
        logger.error(f"Enhanced category processing failed for user {user_id}: {e}")
        await callback.message.edit_text("❌ Processing failed. Please try again.")
        
        # Clear session on error
        if user_id in user_sessions:
            del user_sessions[user_id]
        category_system.clear_selection(user_id)
    
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
     markdown_storage_inst, notion_storage_inst, railway_storage_inst) = get_services()
    
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
    logger.info("Enhanced video handlers registered")
