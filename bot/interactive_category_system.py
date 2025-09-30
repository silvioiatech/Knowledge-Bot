"""Interactive category selection system for Knowledge Bot."""

from typing import Dict, Optional, Tuple
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from core.models.content_models import CategorySuggestion, NotionFieldMappings, NotionPayload


class CategorySelection:
    """Tracks user's category selection process."""
    
    def __init__(self, user_id: int, suggestions: CategorySuggestion):
        self.user_id = user_id
        self.suggestions = suggestions
        self.category: Optional[str] = None
        self.category_display: Optional[str] = None
        self.subcategory: Optional[str] = None
        self.created_at = datetime.now()
        self.completed = False
    
    def is_complete(self) -> bool:
        """Check if selection is complete."""
        return self.category is not None and self.subcategory is not None


class InteractiveCategorySystem:
    """System for interactive category selection with inline keyboards."""
    
    def __init__(self):
        self._selections: Dict[int, CategorySelection] = {}
        logger.info("Interactive Category System initialized")
    
    def create_category_selection_message(
        self, 
        suggestions: CategorySuggestion, 
        user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Create initial category selection message with keyboard.
        Returns: (message_text, keyboard)
        """
        # Store selection state
        self._selections[user_id] = CategorySelection(user_id, suggestions)
        
        # Create message
        message = f"""🎯 **Category Selection**

Based on the content analysis, here's the suggested categorization:

**Recommended Category:** {suggestions.category_display}
**Confidence:** {suggestions.confidence:.0f}%
**Reasoning:** {suggestions.reasoning}

**Suggested Details:**
• Subcategory: {suggestions.subcategory}
• Difficulty: {suggestions.difficulty}
• Platform: {', '.join(suggestions.platform_specific)}

Please select a category:
"""
        
        # Create keyboard with category options
        keyboard = self._create_category_keyboard()
        
        return message, keyboard
    
    def _create_category_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard with all available categories."""
        buttons = []
        
        # Create 2 buttons per row
        row = []
        for key, display in NotionFieldMappings.CATEGORIES.items():
            row.append(InlineKeyboardButton(
                text=display,
                callback_data=f"cat:{key}"
            ))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        
        # Add remaining button if any
        if row:
            buttons.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _create_subcategory_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard with subcategory options."""
        buttons = []
        
        # Create 2 buttons per row
        row = []
        for subcategory in NotionFieldMappings.SUBCATEGORIES:
            row.append(InlineKeyboardButton(
                text=subcategory,
                callback_data=f"sub:{subcategory}"
            ))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        
        # Add remaining button if any
        if row:
            buttons.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def handle_category_selection(
        self, 
        user_id: int, 
        callback_data: str
    ) -> Tuple[str, Optional[InlineKeyboardMarkup], bool]:
        """
        Handle category/subcategory selection.
        Returns: (message_text, keyboard, is_final)
        """
        if user_id not in self._selections:
            return "❌ Session expired. Please start over.", None, False
        
        selection = self._selections[user_id]
        
        # Parse callback data
        if callback_data.startswith("cat:"):
            # Category selected
            category_key = callback_data[4:]
            selection.category = category_key
            selection.category_display = NotionFieldMappings.get_category_emoji_name(category_key)
            
            message = f"""✅ **Category Selected:** {selection.category_display}

Now select a subcategory:
"""
            keyboard = self._create_subcategory_keyboard()
            return message, keyboard, False
            
        elif callback_data.startswith("sub:"):
            # Subcategory selected
            subcategory = callback_data[4:]
            selection.subcategory = subcategory
            selection.completed = True
            
            message = f"""✅ **Selection Complete**

**Category:** {selection.category_display}
**Subcategory:** {subcategory}

Processing your knowledge entry...
"""
            return message, None, True
        
        return "❌ Invalid selection.", None, False
    
    def get_final_selection(self, user_id: int) -> Optional[CategorySelection]:
        """Get the completed selection for a user."""
        if user_id in self._selections:
            selection = self._selections[user_id]
            if selection.is_complete():
                return selection
        return None
    
    def clear_selection(self, user_id: int) -> None:
        """Clear selection state for a user."""
        if user_id in self._selections:
            del self._selections[user_id]
            logger.debug(f"Cleared category selection for user {user_id}")
    
    def create_processing_result_message(
        self,
        payload: NotionPayload,
        railway_url: str,
        notion_url: str
    ) -> str:
        """Create final processing result message."""
        
        message = f"""✅ **Knowledge Entry Created Successfully!**

📋 **Entry Details:**
• **Title:** {payload.title}
• **Category:** {payload.category}
• **Subcategory:** {payload.subcategory}
• **Difficulty:** {payload.difficulty}
• **Quality:** {payload.content_quality}
• **Word Count:** {payload.word_count:,}

🎯 **Classification:**
• **Tags:** {', '.join(payload.tags[:5])}{'...' if len(payload.tags) > 5 else ''}
• **Tools:** {', '.join(payload.tools_mentioned[:5])}{'...' if len(payload.tools_mentioned) > 5 else ''}
• **Platforms:** {', '.join(payload.platform_specific)}

📊 **Analysis:**
• **Gemini Confidence:** {payload.gemini_confidence}%
• **Processing Date:** {payload.processing_date}

🔗 **Links:**
"""
        
        if notion_url:
            message += f"• **Notion:** {notion_url}\n"
        
        if railway_url:
            message += f"• **Railway Storage:** {railway_url}\n"
        
        if payload.source_video:
            message += f"• **Source Video:** {payload.source_video}\n"
        
        message += "\n✨ Entry is ready for review and enhancement!"
        
        return message
