"""Configuration module for Knowledge Bot MVP with enhanced textbook generation capabilities."""

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
    
    # Railway yt-dlp API (optional)
    RAILWAY_API_URL: str = os.getenv("RAILWAY_API_URL", "")
    RAILWAY_API_KEY: str = os.getenv("RAILWAY_API_KEY", "")  # Optional - can be empty
    
    # AI Service Configuration - Enhanced for Textbook Quality
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Use gemini-1.5-flash for Google AI Studio
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
    
    # OpenRouter Configuration (for Claude and Image Generation)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")  # Keep Sonnet for quality
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "20000"))  # Massive increase for textbook content
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Image Generation Configuration
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "google/gemini-2.5-flash-image-preview")
    ENABLE_IMAGE_GENERATION: bool = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() == "true"
    MAX_IMAGES_PER_ENTRY: int = int(os.getenv("MAX_IMAGES_PER_ENTRY", "3"))  # Up to 3 diagrams per entry
    
    # Content Quality Configuration
    TARGET_CONTENT_LENGTH: int = int(os.getenv("TARGET_CONTENT_LENGTH", "3000"))  # Target word count
    MIN_CATEGORY_CONFIDENCE: float = float(os.getenv("MIN_CATEGORY_CONFIDENCE", "0.7"))  # Category confidence threshold
    
    # Storage Configuration
    KNOWLEDGE_BASE_PATH: Path = Path(os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base"))
    
    # Book Mode Configuration
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "markdown")  # "book" or "markdown"
    OBSIDIAN_VAULT_PATH: str = os.getenv("OBSIDIAN_VAULT_PATH", "./knowledge_base")
    ENABLE_BOOK_STRUCTURE: bool = os.getenv("ENABLE_BOOK_STRUCTURE", "true").lower() == "true"
    AUTO_GENERATE_INDEX: bool = os.getenv("AUTO_GENERATE_INDEX", "true").lower() == "true"
    
    # Private Repository Configuration (Optional)
    PRIVATE_REPO_PATH: str = os.getenv("PRIVATE_REPO_PATH", "")
    GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")  # Personal Access Token
    AUTO_COMMIT: bool = os.getenv("AUTO_COMMIT", "false").lower() == "true"
    AUTO_PUSH: bool = os.getenv("AUTO_PUSH", "false").lower() == "true"
    
    # Notion Configuration
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    USE_NOTION_STORAGE: bool = os.getenv("USE_NOTION_STORAGE", "false").lower() == "true"
    
    # Limits
    MAX_VIDEO_DURATION_SECONDS: int = _safe_int(os.getenv("MAX_VIDEO_DURATION_SECONDS"), "600")
    RATE_LIMIT_PER_HOUR: int = _safe_int(os.getenv("RATE_LIMIT_PER_HOUR"), "10")
    
    # Timeouts
    RAILWAY_DOWNLOAD_TIMEOUT: int = _safe_int(os.getenv("RAILWAY_DOWNLOAD_TIMEOUT"), "300")
    GEMINI_ANALYSIS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_ANALYSIS_TIMEOUT"), "180")
    GEMINI_VIDEO_PROCESS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_VIDEO_PROCESS_TIMEOUT"), "300")
    CLAUDE_ENRICHMENT_TIMEOUT: int = _safe_int(os.getenv("CLAUDE_ENRICHMENT_TIMEOUT"), "120")
    
    # Cost Tracking Configuration
    ENABLE_COST_TRACKING: bool = os.getenv("ENABLE_COST_TRACKING", "true").lower() == "true"
    LOG_TOKEN_USAGE: bool = os.getenv("LOG_TOKEN_USAGE", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "GEMINI_API_KEY", 
            "OPENROUTER_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Optional validation warnings
        if not cls.RAILWAY_API_URL:
            print("⚠️  Warning: RAILWAY_API_URL not set - video downloads may not work")
        
        if cls.ENABLE_IMAGE_GENERATION and not cls.OPENROUTER_API_KEY:
            print("⚠️  Warning: Image generation enabled but OPENROUTER_API_KEY not set")
        
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
    "image_generation_failed": "⚠️ Diagram generation failed, content saved without images.",
    "category_confidence_low": "⚠️ Auto-categorization confidence low, marked for review.",
}

# Progress messages  
PROGRESS_MESSAGES = {
    "downloading": "🔄 Downloading video...",
    "analyzing": f"🤖 Analyzing with {Config.GEMINI_MODEL.replace('gemini-', 'Gemini ')}...",
    "enriching": f"✨ Creating textbook-quality content with {Config.OPENROUTER_MODEL.split('/')[-1]}...",
    "generating_diagrams": "🎨 Generating technical diagrams...",
    "saving": "💾 Saving comprehensive reference material...",
    "completed": "✅ Successfully created textbook-quality entry!",
}

# URL patterns
SUPPORTED_PLATFORMS = {
    "tiktok": r"https?://(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com)",
    "instagram": r"https?://(?:www\.)?instagram\.com/(?:p|reel)",
}

# Cost tracking (approximate pricing)
PRICING = {
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},  # per 1k tokens
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},  # per 1k tokens  
    "gemini-2.5-flash-image": {"image": 0.039}  # per image
}