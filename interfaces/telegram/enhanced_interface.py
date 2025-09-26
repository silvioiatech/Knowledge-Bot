"""Enhanced Telegram interface with preview cards and rich interactions."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from loguru import logger


class EnhancedTelegramInterface:
    """Enhanced Telegram interface with rich preview cards and interactions."""
    
    def __init__(self):
        self.router = Router()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # user_id -> session data
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup message and callback handlers."""
        self.router.message(Command("start"))(self.handle_start)
        self.router.message(Command("help"))(self.handle_help)
        self.router.message(Command("stats"))(self.handle_stats)
        self.router.message(F.text.regexp(r'https?://(www\.)?(tiktok\.com|instagram\.com|youtu\.be|youtube\.com)'))(self.handle_video_url)
        self.router.callback_query(F.data.startswith("approve:"))(self.handle_approval)
        self.router.callback_query(F.data.startswith("reject:"))(self.handle_rejection)
        self.router.callback_query(F.data.startswith("regenerate:"))(self.handle_regeneration)
        self.router.callback_query(F.data.startswith("edit:"))(self.handle_edit_request)
        self.router.callback_query(F.data.startswith("preview:"))(self.handle_preview_toggle)
    
    async def handle_start(self, message: Message):
        """Handle /start command with rich welcome."""
        welcome_text = """
🚀 **Welcome to Knowledge Bot 2.0!**

I transform educational videos into comprehensive knowledge base entries with:

✨ **Enhanced Features:**
• 🎥 Multi-platform video analysis (TikTok, Instagram, YouTube)
• 🔍 AI-powered fact-checking and web research
• 📚 Professional textbook-quality content generation
• 🖼️ Smart diagram and flowchart creation
• 📊 Quality scoring and validation
• 💾 Automated Notion database integration

📝 **How to use:**
Simply send me any educational video URL and I'll create a complete knowledge entry!

🎯 **Supported platforms:**
• TikTok videos
• Instagram Reels
• YouTube videos/shorts

Try sending me a video URL to get started! 🎬
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 View Sample", callback_data="preview:sample")],
            [InlineKeyboardButton(text="❓ Get Help", callback_data="preview:help")],
            [InlineKeyboardButton(text="📊 My Stats", callback_data="preview:stats")]
        ])
        
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_help(self, message: Message):
        """Handle /help command."""
        help_text = """
🔧 **Knowledge Bot Commands & Features**

**Commands:**
• `/start` - Welcome message and overview
• `/help` - This help message  
• `/stats` - Your processing statistics

**Video Processing:**
1. Send any supported video URL
2. Review the AI analysis preview
3. Approve or request modifications
4. Get final knowledge base entry

**Quality Controls:**
• ✅ Approve - Accept analysis and generate content
• ❌ Reject - Discard this analysis
• 🔄 Regenerate - Re-analyze with different focus
• ✏️ Edit - Request specific modifications

**Supported Formats:**
• TikTok: tiktok.com/@user/video/...
• Instagram: instagram.com/p/... or instagram.com/reel/...
• YouTube: youtube.com/watch?v=... or youtu.be/...

**Pro Tips:**
• Educational/tutorial content works best
• Technical videos get enhanced with diagrams
• Fact-checking happens automatically
• All content is saved to your Notion database

Need more help? Just ask! 💬
        """
        
        await message.answer(help_text, parse_mode="Markdown")
    
    async def handle_stats(self, message: Message):
        """Handle /stats command - show user statistics."""
        # In a real implementation, you'd fetch these from a database
        stats_text = """
📊 **Your Knowledge Bot Statistics**

**Processing Summary:**
• 🎥 Videos analyzed: 0
• ✅ Entries created: 0
• 📚 Total words generated: 0
• ⭐ Average quality score: N/A

**This Month:**
• 🆕 New entries: 0
• 🔄 Regenerations: 0
• ⏱️ Avg processing time: N/A

**Popular Topics:**
• No data yet - start processing videos!

**Quality Breakdown:**
• 🥇 Excellent (90+): 0
• 🥈 Good (70-89): 0  
• 🥉 Fair (50-69): 0
• ⚠️ Needs work (<50): 0

Start analyzing videos to build your statistics! 🚀
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="preview:stats")]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_video_url(self, message: Message):
        """Handle video URL submission with enhanced processing."""
        url = message.text.strip()
        user_id = str(message.from_user.id)
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Processing video URL from user {user_id}: {url}")
        
        # Store session data
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'url': url,
            'start_time': datetime.now(),
            'status': 'processing'
        }
        
        # Send initial processing message
        processing_msg = await message.answer(
            "🎬 **Video Processing Started**\n\n"
            "📥 Downloading video...\n"
            "⏳ This may take 1-2 minutes for longer videos",
            parse_mode="Markdown"
        )
        
        try:
            # Update to analysis phase
            await processing_msg.edit_text(
                "🎬 **Video Processing Started**\n\n"
                "✅ Video downloaded\n"
                "🤖 Analyzing content with AI...\n"
                "⏳ Extracting insights and fact-checking",
                parse_mode="Markdown"
            )
            
            # Here you would call your processing pipeline
            # For now, we'll simulate with a delay and mock data
            await asyncio.sleep(5)  # Simulate processing
            
            # Create mock analysis result
            analysis_preview = self._create_mock_analysis_preview(url)
            
            # Show analysis preview with approval buttons
            await self._show_analysis_preview(message.chat.id, session_id, analysis_preview, processing_msg.message_id)
            
        except Exception as e:
            logger.error(f"Error processing video {url}: {e}")
            await processing_msg.edit_text(
                "❌ **Processing Failed**\n\n"
                f"Error: {str(e)}\n\n"
                "Please try again or contact support if the issue persists.",
                parse_mode="Markdown"
            )
    
    async def _show_analysis_preview(
        self, 
        chat_id: int, 
        session_id: str, 
        analysis: Dict[str, Any],
        original_msg_id: int
    ):
        """Show rich analysis preview with approval options."""
        
        # Create preview text
        preview_text = self._format_analysis_preview(analysis)
        
        # Create approval keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve & Generate", callback_data=f"approve:{session_id}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{session_id}")
            ],
            [
                InlineKeyboardButton(text="🔄 Re-analyze", callback_data=f"regenerate:{session_id}"),
                InlineKeyboardButton(text="✏️ Request Changes", callback_data=f"edit:{session_id}")
            ],
            [
                InlineKeyboardButton(text="👁️ Toggle Preview", callback_data=f"preview:{session_id}")
            ]
        ])
        
        # Edit the original processing message
        await self._edit_message(chat_id, original_msg_id, preview_text, keyboard)
    
    def _format_analysis_preview(self, analysis: Dict[str, Any]) -> str:
        """Format analysis data into a rich preview."""
        quality = analysis.get('quality_score', 75)
        quality_emoji = "🥇" if quality >= 90 else "🥈" if quality >= 70 else "🥉" if quality >= 50 else "⚠️"
        
        preview = f"""
🎯 **Analysis Complete** {quality_emoji}

**📊 Quality Score: {quality}/100**

**📝 Content Overview:**
• **Topic:** {analysis.get('topic', 'Unknown')}
• **Difficulty:** {analysis.get('difficulty', 'Intermediate')} 
• **Duration:** {analysis.get('duration', '0:00')}
• **Language:** {analysis.get('language', 'English')}

**🔍 Key Insights:**
{self._format_key_insights(analysis.get('insights', []))}

**🏷️ Detected Entities:**
{self._format_entities(analysis.get('entities', []))}

**✅ Fact-Check Status:**
• {analysis.get('facts_verified', 0)} claims verified
• {analysis.get('corrections', 0)} corrections needed
• {analysis.get('confidence', 85)}% confidence

**📈 Estimated Output:**
• ~{analysis.get('estimated_words', 2500)} words
• {analysis.get('estimated_sections', 8)} sections
• {analysis.get('estimated_images', 3)} diagrams planned

**What's Next?**
Approve to generate the complete knowledge base entry, or request changes below.
        """
        
        return preview.strip()
    
    def _format_key_insights(self, insights: List[str]) -> str:
        """Format key insights list."""
        if not insights:
            return "• No key insights detected"
        
        formatted = []
        for i, insight in enumerate(insights[:5]):  # Show top 5
            formatted.append(f"• {insight}")
        
        if len(insights) > 5:
            formatted.append(f"• ... and {len(insights) - 5} more")
        
        return "\n".join(formatted)
    
    def _format_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities list."""
        if not entities:
            return "• No entities detected"
        
        entity_counts = {}
        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        formatted = []
        for entity_type, count in entity_counts.items():
            type_emoji = {
                'technology': '💻',
                'person': '👤', 
                'organization': '🏢',
                'concept': '💡',
                'product': '📦'
            }.get(entity_type, '🔹')
            
            formatted.append(f"• {type_emoji} {count} {entity_type}{'s' if count > 1 else ''}")
        
        return "\n".join(formatted[:5])  # Show top 5 types
    
    def _create_mock_analysis_preview(self, url: str) -> Dict[str, Any]:
        """Create mock analysis data for demonstration."""
        return {
            'topic': 'Python Programming Tutorial',
            'difficulty': 'Intermediate',
            'duration': '5:32',
            'language': 'English',
            'quality_score': 87,
            'insights': [
                'Covers list comprehensions and generators',
                'Demonstrates practical coding examples',
                'Explains performance implications',
                'Shows debugging techniques',
                'Includes best practices discussion'
            ],
            'entities': [
                {'name': 'Python', 'type': 'technology'},
                {'name': 'List Comprehension', 'type': 'concept'},
                {'name': 'Generator', 'type': 'concept'},
                {'name': 'VS Code', 'type': 'technology'},
                {'name': 'Django', 'type': 'technology'}
            ],
            'facts_verified': 12,
            'corrections': 1,
            'confidence': 89,
            'estimated_words': 2800,
            'estimated_sections': 9,
            'estimated_images': 4
        }
    
    async def handle_approval(self, callback: CallbackQuery):
        """Handle approval of analysis - proceed to content generation."""
        session_id = callback.data.split(":")[1]
        
        if session_id not in self.active_sessions:
            await callback.answer("❌ Session expired. Please submit the video again.", show_alert=True)
            return
        
        await callback.answer("✅ Generating content...")
        
        # Update message to show generation progress
        generation_text = """
🎯 **Content Generation Started**

✅ Analysis approved
📝 Generating comprehensive guide...
🖼️ Creating diagrams and flowcharts...
🔍 Final quality check...

⏳ This will take 2-3 minutes for high-quality content.
        """
        
        await callback.message.edit_text(generation_text, parse_mode="Markdown")
        
        # Simulate content generation
        await asyncio.sleep(8)  # Simulate generation time
        
        # Show final result
        await self._show_generation_complete(callback.message, session_id)
    
    async def handle_rejection(self, callback: CallbackQuery):
        """Handle rejection of analysis."""
        session_id = callback.data.split(":")[1]
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        await callback.message.edit_text(
            "❌ **Analysis Rejected**\n\n"
            "No content was generated. Feel free to submit another video URL!",
            parse_mode="Markdown"
        )
        
        await callback.answer("Analysis discarded.")
    
    async def handle_regeneration(self, callback: CallbackQuery):
        """Handle regeneration request."""
        session_id = callback.data.split(":")[1]
        
        await callback.answer("🔄 Re-analyzing video...")
        
        await callback.message.edit_text(
            "🔄 **Re-analyzing Video**\n\n"
            "🤖 Running enhanced analysis...\n"
            "📊 Applying different extraction methods...\n"
            "⏳ This may produce different insights",
            parse_mode="Markdown"
        )
        
        # Simulate re-analysis
        await asyncio.sleep(4)
        
        # Show new analysis (could be different)
        new_analysis = self._create_mock_analysis_preview("regenerated")
        new_analysis['quality_score'] = 92  # Simulate improvement
        
        await self._show_analysis_preview(
            callback.message.chat.id, 
            session_id, 
            new_analysis,
            callback.message.message_id
        )
    
    async def handle_edit_request(self, callback: CallbackQuery):
        """Handle edit/modification requests."""
        await callback.answer()
        
        edit_text = """
✏️ **Request Modifications**

What would you like me to adjust in the analysis or final content?

**Common requests:**
• Focus more on specific topics
• Change difficulty level (beginner/advanced)
• Add more technical details
• Include more practical examples
• Adjust content length
• Emphasize certain aspects

**How to request:**
Reply to this message with your specific requirements, for example:
"Focus more on advanced techniques" or "Make it beginner-friendly"
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Analysis", callback_data=f"preview:{callback.data.split(':')[1]}")]
        ])
        
        await callback.message.edit_text(edit_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_preview_toggle(self, callback: CallbackQuery):
        """Handle preview toggle requests."""
        session_id = callback.data.split(":")[1]
        
        # For demo, just show the same preview
        if session_id in self.active_sessions or session_id == "sample":
            analysis = self._create_mock_analysis_preview("sample")
            await self._show_analysis_preview(
                callback.message.chat.id, 
                session_id, 
                analysis,
                callback.message.message_id
            )
        else:
            await callback.answer("Preview not available", show_alert=True)
    
    async def _show_generation_complete(self, message: Message, session_id: str):
        """Show completion message with final result."""
        result_text = """
🎉 **Knowledge Entry Generated!**

✅ **Processing Complete**
• 📝 2,847 words generated
• 🖼️ 4 diagrams created  
• ⭐ Quality score: 94/100
• 💾 Saved to Notion database

**📊 Final Content:**
• 9 comprehensive sections
• 15 key concepts covered
• 23 technical terms explained
• 12 practical examples included
• 4 visual diagrams embedded

**🔗 Access Your Content:**
• [View in Notion Database](#)
• [Download Markdown](#)
• [Share Link](#)

**⏱️ Processing Time:** 3m 42s

Thank you for using Knowledge Bot! Send another video to continue building your knowledge base. 🚀
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Open in Notion", url="https://notion.so/sample"),
                InlineKeyboardButton(text="📥 Download MD", callback_data=f"download:{session_id}")
            ],
            [InlineKeyboardButton(text="🆕 Process Another Video", callback_data="new_session")]
        ])
        
        await message.edit_text(result_text, reply_markup=keyboard, parse_mode="Markdown")
        
        # Clean up session
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def _edit_message(
        self, 
        chat_id: int, 
        message_id: int, 
        text: str, 
        keyboard: Optional[InlineKeyboardMarkup] = None
    ):
        """Safely edit a message with error handling."""
        try:
            # This would be called through the bot instance
            # For now it's a placeholder showing the interface
            pass
        except Exception as e:
            logger.error(f"Failed to edit message {message_id}: {e}")
    
    def get_router(self) -> Router:
        """Get the configured router for use in the bot."""
        return self.router