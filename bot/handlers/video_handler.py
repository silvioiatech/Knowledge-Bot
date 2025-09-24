"""Video URL handler for Telegram bot."""

import re
import asyncio
from typing import Dict, Any

try:
    from aiogram import Router, F
    from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.filters import StateFilter
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from loguru import logger
except ImportError:
    Router = F = Message = CallbackQuery = InlineKeyboardMarkup = None
    InlineKeyboardButton = StateFilter = FSMContext = State = StatesGroup = None
    logger = None

from config import Config, ERROR_MESSAGES, PROGRESS_MESSAGES, SUPPORTED_PLATFORMS
from services.railway_client import download_video_from_url, RailwayDownloadError, RailwayClient
from services.gemini_service import analyze_video_content, GeminiAnalysisError
from services.claude_service import enrich_analysis, ClaudeEnrichmentError
from storage.markdown_storage import save_knowledge_entry, MarkdownStorageError


class VideoStates(StatesGroup):
    """FSM states for video processing."""
    waiting_for_approval = State()


def create_approval_keyboard(analysis_data: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Create inline keyboard for analysis approval."""
    if not InlineKeyboardMarkup:
        return None
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Add to Knowledge Base", callback_data="approve"),
            InlineKeyboardButton(text="❌ Reject", callback_data="reject")
        ],
        [
            InlineKeyboardButton(text="🔄 Re-analyze", callback_data="reanalyze")
        ]
    ])
    return keyboard


def format_analysis_message(analysis: Dict[str, Any]) -> str:
    """Format Gemini analysis as readable Telegram message."""
    title = analysis.get("title", "Untitled Video")
    subject = analysis.get("subject", "Unknown")
    summary = analysis.get("summary", "No summary available")
    key_points = analysis.get("key_points", [])
    tools = analysis.get("tools", [])
    difficulty = analysis.get("difficulty_level", "unknown")
    
    message = f"""
🎥 <b>{title}</b>

📂 <b>Category:</b> {subject}
⏱️ <b>Difficulty:</b> {difficulty}

📝 <b>Summary:</b>
{summary}

🔑 <b>Key Points:</b>
"""
    
    for i, point in enumerate(key_points[:5], 1):  # Limit to 5 points
        message += f"{i}. {point}\n"
    
    if tools:
        message += f"\n🛠️ <b>Tools mentioned:</b> {', '.join(tools[:5])}"
    
    message += "\n\n👆 <b>Approve this analysis to add to your knowledge base?</b>"
    
    return message


async def process_video_url(message: Message, state: FSMContext, url: str):
    """Process video URL through the complete pipeline."""
    if not message:
        return
    
    user_id = message.from_user.id if message.from_user else 0
    
    try:
        # Step 1: Download video
        status_msg = await message.answer(PROGRESS_MESSAGES["downloading"])
        
        try:
            download_info, video_path = await download_video_from_url(url)
        except RailwayDownloadError as e:
            # Provide more specific error messages based on error type
            if "url" in str(e).lower() or "not found" in str(e).lower():
                error_msg = "❌ Video not found or unavailable. Please check the URL."
            elif "private" in str(e).lower():
                error_msg = "❌ This video is private and cannot be downloaded."
            elif "service error" in str(e).lower():
                error_msg = "❌ Download service temporarily unavailable. Please try again later."
            else:
                error_msg = ERROR_MESSAGES["download_failed"]
            
            await status_msg.edit_text(error_msg)
            if logger:
                logger.error(f"Download failed for user {user_id}: {e}")
            return
        
        # Step 2: Analyze with Gemini
        await status_msg.edit_text(PROGRESS_MESSAGES["analyzing"])
        
        try:
            analysis = await analyze_video_content(video_path)
            analysis["original_url"] = url
            analysis["download_info"] = download_info
        except GeminiAnalysisError as e:
            await status_msg.edit_text(ERROR_MESSAGES["analysis_failed"])
            if logger:
                logger.error(f"Analysis failed for user {user_id}: {e}")
            return
        finally:
            # Cleanup temp file
            try:
                client = RailwayClient()
                await client.cleanup_temp_file(video_path)
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to cleanup temp file {video_path}: {e}")
                else:
                    print(f"Warning: Failed to cleanup temp file {video_path}: {e}")
        
        # Step 3: Show analysis for approval
        analysis_text = format_analysis_message(analysis)
        keyboard = create_approval_keyboard(analysis)
        
        await status_msg.edit_text(analysis_text, reply_markup=keyboard)
        
        # Set state and store analysis data
        await state.set_state(VideoStates.waiting_for_approval)
        await state.update_data(analysis=analysis, message_id=status_msg.message_id)
        
        if logger:
            logger.info(f"Video analysis completed for user {user_id}")
    
    except Exception as e:
        await message.answer(ERROR_MESSAGES["general_error"])
        if logger:
            logger.error(f"Unexpected error processing video for user {user_id}: {e}")


async def handle_approval_callback(callback: CallbackQuery, state: FSMContext):
    """Handle approval/rejection callbacks."""
    if not callback.data:
        return
    
    user_id = callback.from_user.id if callback.from_user else 0
    data = await state.get_data()
    analysis = data.get("analysis")
    
    if not analysis:
        await callback.answer("❌ Analysis data not found")
        return
    
    try:
        if callback.data == "approve":
            # Enrich and save content
            await callback.message.edit_text(PROGRESS_MESSAGES["enriching"])
            
            try:
                enriched_content = await enrich_analysis(analysis)
            except ClaudeEnrichmentError as e:
                await callback.message.edit_text(ERROR_MESSAGES["enrichment_failed"])
                if logger:
                    logger.error(f"Enrichment failed for user {user_id}: {e}")
                return
            
            # Save to knowledge base
            await callback.message.edit_text(PROGRESS_MESSAGES["saving"])
            
            try:
                file_path = await save_knowledge_entry(enriched_content, analysis)
                success_msg = f"{PROGRESS_MESSAGES['completed']}\n\n📁 Saved to: <code>{file_path}</code>"
                await callback.message.edit_text(success_msg)
            except MarkdownStorageError as e:
                await callback.message.edit_text(ERROR_MESSAGES["storage_failed"])
                if logger:
                    logger.error(f"Storage failed for user {user_id}: {e}")
                return
        
        elif callback.data == "reject":
            await callback.message.edit_text("❌ Analysis rejected. Send another video URL to try again.")
        
        elif callback.data == "reanalyze":
            # Re-process the same URL
            original_url = analysis.get("original_url")
            if original_url:
                await callback.message.edit_text("🔄 Re-analyzing video...")
                # Create a mock message object for re-processing
                class MockMessage:
                    def __init__(self, chat_id, user_id):
                        self.chat = type('obj', (object,), {'id': chat_id})()
                        self.from_user = type('obj', (object,), {'id': user_id})()
                    
                    async def answer(self, text, **kwargs):
                        return await callback.message.edit_text(text, **kwargs)
                
                mock_msg = MockMessage(callback.message.chat.id, user_id)
                await process_video_url(mock_msg, state, original_url)
            else:
                await callback.message.edit_text("❌ Cannot re-analyze: original URL not found")
    
    except Exception as e:
        await callback.message.edit_text(ERROR_MESSAGES["general_error"])
        if logger:
            logger.error(f"Callback handling error for user {user_id}: {e}")
    
    finally:
        # Clear state
        await state.clear()
        await callback.answer()


def register_video_handlers(dp):
    """Register all video-related handlers."""
    if not Router:
        return
    
    router = Router()
    
    # URL detection handler
    @router.message(F.text.regexp(r'https?://(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com|instagram\.com/(?:p|reel))'))
    async def handle_video_url(message: Message, state: FSMContext):
        """Handle video URL messages."""
        url = message.text.strip()
        
        # Validate URL format
        valid_url = False
        for platform, pattern in SUPPORTED_PLATFORMS.items():
            if re.match(pattern, url):
                valid_url = True
                break
        
        if not valid_url:
            await message.answer(ERROR_MESSAGES["invalid_url"])
            return
        
        # Process the video
        await process_video_url(message, state, url)
    
    # Callback handlers
    @router.callback_query(F.data.in_(["approve", "reject", "reanalyze"]))
    async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
        """Handle inline button callbacks."""
        await handle_approval_callback(callback, state)
    
    # Register router with dispatcher
    dp.include_router(router)
    
    if logger:
        logger.info("Video handlers registered")