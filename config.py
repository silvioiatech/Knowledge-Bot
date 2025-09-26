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
    
    # OpenRouter Configuration (for Claude, GPT, and Image Generation)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Model Configuration via OpenRouter
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "anthropic/claude-3.5-sonnet")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "openai/gpt-4-1106-preview")
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "black-forest-labs/flux-1.1-pro")  # Image generation via OpenRouter
    
    # Token Limits
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "4000"))
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "8000"))
    GPT_MAX_TOKENS: int = int(os.getenv("GPT_MAX_TOKENS", "4000"))
    
    # Web Search Configuration (optional for fact-checking)
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")  # Google Search API
    
    # Enhanced Image Generation Configuration
    ENABLE_IMAGE_GENERATION: bool = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() == "true"
    MAX_IMAGES_PER_ENTRY: int = int(os.getenv("MAX_IMAGES_PER_ENTRY", "5"))  # Up to 5 diagrams per entry
    IMAGE_QUALITY: str = os.getenv("IMAGE_QUALITY", "high")  # high, medium, low
    
    # Legacy API Keys (for direct API access if needed)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")  # Optional fallback
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # Optional fallback
    
    # Content Quality Configuration
    TARGET_CONTENT_LENGTH: int = int(os.getenv("TARGET_CONTENT_LENGTH", "5000"))  # Target word count (realistic for Claude 8K tokens)
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
    
    # Pipeline Configuration
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "./temp"))
    ENABLE_WEB_RESEARCH: bool = os.getenv("ENABLE_WEB_RESEARCH", "false").lower() == "true"
    ENABLE_FACT_CHECKING: bool = os.getenv("ENABLE_FACT_CHECKING", "false").lower() == "true"
    
    # Limits
    MAX_VIDEO_DURATION_SECONDS: int = _safe_int(os.getenv("MAX_VIDEO_DURATION_SECONDS"), "1800")  # 30 minutes
    RATE_LIMIT_PER_HOUR: int = _safe_int(os.getenv("RATE_LIMIT_PER_HOUR"), "10")
    
    # Timeouts (increased for enhanced processing)
    RAILWAY_DOWNLOAD_TIMEOUT: int = _safe_int(os.getenv("RAILWAY_DOWNLOAD_TIMEOUT"), "300")
    GEMINI_ANALYSIS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_ANALYSIS_TIMEOUT"), "300")  # Increased for research
    GEMINI_VIDEO_PROCESS_TIMEOUT: int = _safe_int(os.getenv("GEMINI_VIDEO_PROCESS_TIMEOUT"), "300")
    CLAUDE_ENRICHMENT_TIMEOUT: int = _safe_int(os.getenv("CLAUDE_ENRICHMENT_TIMEOUT"), "180")  # Increased for longer content
    BANANA_IMAGE_TIMEOUT: int = _safe_int(os.getenv("BANANA_IMAGE_TIMEOUT"), "120")
    GPT_ASSEMBLY_TIMEOUT: int = _safe_int(os.getenv("GPT_ASSEMBLY_TIMEOUT"), "120")
    
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
    "enriching": f"✨ Creating comprehensive 5000-word guide with {Config.OPENROUTER_MODEL.split('/')[-1]}...",
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
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1k tokens
    "banana-image": {"image": 0.05}  # per image
}

# Export commonly used configuration values for easy import
TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
RAILWAY_API_URL = Config.RAILWAY_API_URL
RAILWAY_API_KEY = Config.RAILWAY_API_KEY
GEMINI_API_KEY = Config.GEMINI_API_KEY
GEMINI_MODEL = Config.GEMINI_MODEL
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
OPENROUTER_BASE_URL = Config.OPENROUTER_BASE_URL
CLAUDE_MODEL = Config.CLAUDE_MODEL
GPT_MODEL = Config.GPT_MODEL
IMAGE_MODEL = Config.IMAGE_MODEL
SERPER_API_KEY = Config.SERPER_API_KEY
NOTION_API_KEY = Config.NOTION_API_KEY
NOTION_DATABASE_ID = Config.NOTION_DATABASE_ID
KNOWLEDGE_BASE_PATH = Config.KNOWLEDGE_BASE_PATH
TEMP_DIR = Config.TEMP_DIR

# Legacy direct API keys (optional fallbacks)
ANTHROPIC_API_KEY = Config.ANTHROPIC_API_KEY
OPENAI_API_KEY = Config.OPENAI_API_KEY