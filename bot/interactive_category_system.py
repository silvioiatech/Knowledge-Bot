"""
Interactive category selection system for Telegram bot with inline keyboards.
"""

import logging
from typing import List, Dict, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from core.models.content_models import CategorySuggestion, NotionFieldMappings

logger = logging.getLogger(__name__)

class CategoryCallbackData(CallbackData, prefix="cat"):
    """Callback data for category selection."""
    action: str  # "select", "subcategory", "confirm"
    category: str
    subcategory: str = ""

class SubcategoryCallbackData(CallbackData, prefix="sub"):
    """Callback data for subcategory selection."""
    action: str  # "select", "confirm"
    category: str
    subcategory: str

class InteractiveCategorySystem:
    """Manages interactive category selection through Telegram inline keyboards."""
    
    def __init__(self):
        self.pending_selections = {}  # user_id -> selection state
    
    def create_category_selection_message(self, suggestion: CategorySuggestion, 
                                        user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """
        Create the initial category selection message with inline keyboard.
        """
        # Store suggestion for this user
        self.pending_selections[user_id] = {
            "suggestion": suggestion,
            "current_category": suggestion.category,
            "current_subcategory": suggestion.subcategory,
            "step": "category_selection"
        }
        
        message_text = f"""
🤖 **AI Analysis Complete!**

**Suggested Categorization:**
📂 **Category**: {suggestion.category_display}
📋 **Subcategory**: {suggestion.subcategory}
🎯 **Confidence**: {suggestion.confidence:.0f}%
⚡ **Difficulty**: {suggestion.difficulty}
🔗 **Platform**: {', '.join(suggestion.platform_specific)}

**Reasoning**: {suggestion.reasoning}

Please review and confirm the categorization, or select different options:
        """
        
        keyboard = self._create_category_keyboard(suggestion.category)
        
        return message_text.strip(), keyboard
    
    def _create_category_keyboard(self, selected_category: str = "") -> InlineKeyboardMarkup:
        """Create inline keyboard for category selection."""
        keyboard = []
        
        # Create rows of category buttons (2 per row)
        categories = list(NotionFieldMappings.CATEGORIES.items())
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    cat_key, cat_display = categories[i + j]
                    # Add checkmark if this is the selected category
                    button_text = f"✅ {cat_display}" if cat_key == selected_category else cat_display
                    callback_data = CategoryCallbackData(
                        action="select",
                        category=cat_key
                    )
                    row.append(InlineKeyboardButton(
                        text=button_text,
                        callback_data=callback_data.pack()
                    ))
            keyboard.append(row)
        
        # Add confirm button if a category is selected
        if selected_category:
            keyboard.append([
                InlineKeyboardButton(
                    text="➡️ Select Subcategory",
                    callback_data=CategoryCallbackData(
                        action="subcategory",
                        category=selected_category
                    ).pack()
                )
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def _create_subcategory_keyboard(self, category: str, 
                                   selected_subcategory: str = "") -> InlineKeyboardMarkup:
        """Create inline keyboard for subcategory selection."""
        keyboard = []
        
        # Create rows of subcategory buttons (2 per row)
        subcategories = NotionFieldMappings.SUBCATEGORIES
        for i in range(0, len(subcategories), 2):
            row = []
            for j in range(2):
                if i + j < len(subcategories):
                    subcategory = subcategories[i + j]
                    # Add checkmark if this is the selected subcategory
                    button_text = f"✅ {subcategory}" if subcategory == selected_subcategory else subcategory
                    callback_data = SubcategoryCallbackData(
                        action="select",
                        category=category,
                        subcategory=subcategory
                    )
                    row.append(InlineKeyboardButton(
                        text=button_text,
                        callback_data=callback_data.pack()
                    ))
            keyboard.append(row)
        
        # Add navigation buttons
        navigation_row = [
            InlineKeyboardButton(
                text="⬅️ Back to Categories",
                callback_data=CategoryCallbackData(
                    action="select",
                    category=category
                ).pack()
            )
        ]
        
        if selected_subcategory:
            navigation_row.append(
                InlineKeyboardButton(
                    text="✅ Confirm Selection",
                    callback_data=SubcategoryCallbackData(
                        action="confirm",
                        category=category,
                        subcategory=selected_subcategory
                    ).pack()
                )
            )
        
        keyboard.append(navigation_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def handle_category_selection(self, user_id: int, callback_data: str) -> tuple[str, InlineKeyboardMarkup, bool]:
        """
        Handle category selection callback.
        Returns: (message_text, keyboard, is_final_selection)
        """
        try:
            # Parse callback data
            if callback_data.startswith("cat:"):
                data = CategoryCallbackData.unpack(callback_data)
                return await self._handle_category_callback(user_id, data)
            elif callback_data.startswith("sub:"):
                data = SubcategoryCallbackData.unpack(callback_data)
                return await self._handle_subcategory_callback(user_id, data)
            else:
                return "Invalid selection", InlineKeyboardMarkup(inline_keyboard=[]), False
                
        except Exception as e:
            logger.error(f"Error handling category selection: {e}")
            return "Error processing selection", InlineKeyboardMarkup(inline_keyboard=[]), False
    
    async def _handle_category_callback(self, user_id: int, 
                                      data: CategoryCallbackData) -> tuple[str, InlineKeyboardMarkup, bool]:
        """Handle category callback data."""
        if user_id not in self.pending_selections:
            return "Session expired. Please start over.", InlineKeyboardMarkup(inline_keyboard=[]), False
        
        selection = self.pending_selections[user_id]
        
        if data.action == "select":
            # Update selected category
            selection["current_category"] = data.category
            category_display = NotionFieldMappings.get_category_emoji_name(data.category)
            
            message_text = f"""
🤖 **Category Updated**

**Selected Category**: {category_display}

Please choose a subcategory or click "Select Subcategory" to continue:
            """
            
            keyboard = self._create_category_keyboard(data.category)
            return message_text.strip(), keyboard, False
            
        elif data.action == "subcategory":
            # Move to subcategory selection
            selection["step"] = "subcategory_selection"
            category_display = NotionFieldMappings.get_category_emoji_name(data.category)
            
            message_text = f"""
📋 **Subcategory Selection**

**Category**: {category_display}

Please select the most appropriate subcategory:
            """
            
            keyboard = self._create_subcategory_keyboard(data.category, selection["current_subcategory"])
            return message_text.strip(), keyboard, False
        
        return "Unknown action", InlineKeyboardMarkup(inline_keyboard=[]), False
    
    async def _handle_subcategory_callback(self, user_id: int,
                                         data: SubcategoryCallbackData) -> tuple[str, InlineKeyboardMarkup, bool]:
        """Handle subcategory callback data."""
        if user_id not in self.pending_selections:
            return "Session expired. Please start over.", InlineKeyboardMarkup(inline_keyboard=[]), False
        
        selection = self.pending_selections[user_id]
        
        if data.action == "select":
            # Update selected subcategory
            selection["current_subcategory"] = data.subcategory
            category_display = NotionFieldMappings.get_category_emoji_name(data.category)
            
            message_text = f"""
📋 **Subcategory Updated**

**Category**: {category_display}
**Subcategory**: {data.subcategory}

Please confirm your selection or choose a different subcategory:
            """
            
            keyboard = self._create_subcategory_keyboard(data.category, data.subcategory)
            return message_text.strip(), keyboard, False
            
        elif data.action == "confirm":
            # Final confirmation
            category_display = NotionFieldMappings.get_category_emoji_name(data.category)
            
            # Update the suggestion with user's final choice
            selection["suggestion"].category = data.category
            selection["suggestion"].category_display = category_display
            selection["suggestion"].subcategory = data.subcategory
            
            message_text = f"""
✅ **Selection Confirmed!**

**Final Categorization:**
📂 **Category**: {category_display}
📋 **Subcategory**: {data.subcategory}

Processing content with your selected categorization...
            """
            
            return message_text.strip(), InlineKeyboardMarkup(inline_keyboard=[]), True
        
        return "Unknown action", InlineKeyboardMarkup(inline_keyboard=[]), False
    
    def get_final_selection(self, user_id: int) -> Optional[CategorySuggestion]:
        """Get the final category selection for a user."""
        if user_id in self.pending_selections:
            return self.pending_selections[user_id]["suggestion"]
        return None
    
    def clear_selection(self, user_id: int):
        """Clear the selection state for a user."""
        if user_id in self.pending_selections:
            del self.pending_selections[user_id]
    
    def create_processing_result_message(self, notion_payload, railway_url: str = "", 
                                       notion_url: str = "") -> str:
        """
        Create comprehensive result message after successful processing.
        """
        message_parts = [
            "🎉 **Content Successfully Processed!**",
            "",
            f"📖 **Title**: {notion_payload.title}",
            f"📂 **Category**: {notion_payload.category}",
            f"📋 **Subcategory**: {notion_payload.subcategory}",
            f"⭐ **Quality**: {notion_payload.content_quality}",
            f"⚡ **Difficulty**: {notion_payload.difficulty}",
            f"📊 **Word Count**: {notion_payload.word_count:,} words",
            f"🎯 **Confidence**: {notion_payload.gemini_confidence}%",
            ""
        ]
        
        if notion_payload.platform_specific:
            message_parts.extend([
                f"🔗 **Platform**: {', '.join(notion_payload.platform_specific)}",
                ""
            ])
        
        if notion_payload.tools_mentioned:
            tools_display = ', '.join(notion_payload.tools_mentioned[:5])
            if len(notion_payload.tools_mentioned) > 5:
                tools_display += f" (+{len(notion_payload.tools_mentioned) - 5} more)"
            message_parts.extend([
                f"🛠️ **Tools**: {tools_display}",
                ""
            ])
        
        if notion_payload.tags:
            tags_display = ', '.join([f"#{tag}" for tag in notion_payload.tags[:5]])
            if len(notion_payload.tags) > 5:
                tags_display += f" (+{len(notion_payload.tags) - 5} more)"
            message_parts.extend([
                f"🏷️ **Tags**: {tags_display}",
                ""
            ])
        
        # Add key points preview
        if notion_payload.key_points:
            message_parts.append("🔑 **Key Points**:")
            for i, point in enumerate(notion_payload.key_points[:3], 1):
                message_parts.append(f"{i}. {point}")
            if len(notion_payload.key_points) > 3:
                message_parts.append(f"   (+{len(notion_payload.key_points) - 3} more points)")
            message_parts.append("")
        
        # Add access links
        message_parts.append("🔗 **Access Your Content**:")
        
        if railway_url:
            message_parts.append(f"🌐 [View Online]({railway_url})")
            message_parts.append(f"📝 [Raw Markdown]({railway_url.replace('/view/', '/raw/')})")
        
        if notion_url:
            message_parts.append(f"📚 [Notion Database]({notion_url})")
        
        message_parts.extend([
            "",
            "💡 *Your content has been organized and is ready for learning!*"
        ])
        
        return "\n".join(message_parts)

# Global instance for the bot
category_system = InteractiveCategorySystem()