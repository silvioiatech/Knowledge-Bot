"""Configuration module for Knowledge Bot MVP."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

# Load environment variables
load_dotenv()

def _safe_int(env_value: str, default: str) -> int:
    """
    Safely convert environment variable to integer.
    
    Args:
        env_value: Raw environment variable value (may be None)
        default: Default value as string
        
    Returns:
        Integer value, falling back to default on conversion errors
    """
    try:
        if env_value is not None and env_value.strip():
            return int(env_value.strip())
        else:
            return int(default)
    except (ValueError, TypeError):
        return int(default)

class Config:
    """Configuration settings loaded from environment variables."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Railway yt-dlp API
    RAILWAY_API_URL: str = os.getenv("RAILWAY_API_URL", "")
    RAILWAY_API_KEY: str = os.getenv("RAILWAY_API_KEY", "")
    
    # AI Services
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Storage
    KNOWLEDGE_BASE_PATH: Path = Path(os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base"))
    
    # Limits
    MAX_VIDEO_DURATION_SECONDS: int = _safe_int(os.getenv("MAX_VIDEO_DURATION_SECONDS"), "600")
    RATE_LIMIT_PER_HOUR: int = _safe_int(os.getenv("RATE_LIMIT_PER_HOUR"), "10")
    
    # Timeouts
    RAILWAY_DOWNLOAD_TIMEOUT: int = _safe_int(os.getenv("RAILWAY_DOWNLOAD_TIMEOUT"), "300")
    GEMINI_ANALYSIS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_ANALYSIS_TIMEOUT"), "180")
    GEMINI_VIDEO_PROCESS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_VIDEO_PROCESS_TIMEOUT"), "300")
    CLAUDE_ENRICHMENT_TIMEOUT: int = _safe_int(os.getenv("CLAUDE_ENRICHMENT_TIMEOUT"), "120")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "RAILWAY_API_URL", 
            "RAILWAY_API_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Error messages
ERROR_MESSAGES = {
    "invalid_url": "❌ Please send a valid TikTok or Instagram video URL",
    "download_failed": "❌ Failed to download video. Try again later.",
    "analysis_failed": "❌ Could not analyze video. Please try again.",
    "rate_limit": "⏰ Rate limit reached. Try again in 1 hour.",
    "video_too_long": "❌ Video too long. Max 10 minutes.",
    "enrichment_failed": "❌ Content enrichment failed. Please try again.",
    "storage_failed": "❌ Failed to save content. Please try again.",
    "general_error": "❌ An error occurred. Please try again later.",
}

# Progress messages
PROGRESS_MESSAGES = {
    "downloading": "🔄 Downloading video...",
    "analyzing": "🤖 Analyzing with Gemini...",
    "enriching": "✨ Enriching content with Claude...",
    "saving": "💾 Saving to knowledge base...",
    "completed": "✅ Successfully added to knowledge base!",
}

# URL patterns
SUPPORTED_PLATFORMS = {
    "tiktok": r"https?://(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com)",
    "instagram": r"https?://(?:www\.)?instagram\.com/(?:p|reel)",
}