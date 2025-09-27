"""Enhanced configuration for Knowledge Bot with OpenRouter integration."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

# Load environment variables  
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    """Enhanced Knowledge Bot configuration."""
    
    # Core Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", "")
    
    # Railway Download Service
    RAILWAY_API_URL: str = os.getenv("RAILWAY_API_URL", "https://railway-yt-dlp-service-production.up.railway.app")
    RAILWAY_API_KEY: str = os.getenv("RAILWAY_API_KEY", "")
    
    # AI Services Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    GEMINI_ANALYSIS_TIMEOUT: int = int(os.getenv("GEMINI_ANALYSIS_TIMEOUT", "600"))
    
    # Notion Storage
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    USE_NOTION_STORAGE: bool = os.getenv("USE_NOTION_STORAGE", "true").lower() == "true"
    
    # OpenRouter Configuration (for Claude, GPT, and Image Generation)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Anthropic Direct API (fallback)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration via OpenRouter
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "anthropic/claude-3.5-sonnet")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "openai/gpt-4")
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "black-forest-labs/flux-1.1-pro")  # Image generation via OpenRouter
    
    # Token limits
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "4000"))
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "8000"))
    GPT_MAX_TOKENS: int = int(os.getenv("GPT_MAX_TOKENS", "4000"))
    
    # File Storage Configuration  
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/knowledge_bot"))
    KNOWLEDGE_BASE_PATH: Path = Path(os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base"))
    
    # Processing Configuration
    TARGET_CONTENT_LENGTH: int = int(os.getenv("TARGET_CONTENT_LENGTH", "2500"))
    ENABLE_IMAGE_GENERATION: bool = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() == "true"
    MAX_PROCESSING_TIME: int = int(os.getenv("MAX_PROCESSING_TIME", "1800"))  # 30 minutes
    
    # GitHub Integration (Optional)
    GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    PRIVATE_REPO_PATH: str = os.getenv("PRIVATE_REPO_PATH", "")
    GIT_AUTO_COMMIT: bool = os.getenv("GIT_AUTO_COMMIT", "false").lower() == "true"
    AUTO_COMMIT: bool = os.getenv("AUTO_COMMIT", "false").lower() == "true"
    AUTO_PUSH: bool = os.getenv("AUTO_PUSH", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
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
        
        # Validate optional but recommended settings
        if cls.ENABLE_IMAGE_GENERATION and not cls.OPENROUTER_API_KEY:
            print("⚠️  Warning: Image generation enabled but OPENROUTER_API_KEY not set")
        
        if cls.USE_NOTION_STORAGE and not cls.NOTION_API_KEY:
            print("⚠️  Warning: Notion storage enabled but NOTION_API_KEY not set")
        
        # Create required directories
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)
        
        print("✅ Configuration validated successfully")


# Error messages
ERROR_MESSAGES = {
    "invalid_url": "❌ Please send a valid TikTok or Instagram video URL",
    "download_failed": "❌ Failed to download video. The video might be private or unavailable.",
    "analysis_failed": "❌ Could not analyze video. Please try again later.",
    "processing_failed": "❌ Processing failed. Please try with a different video.",
    "rate_limit": "⏰ Rate limit reached. Try again in 1 hour.",
    "timeout": "⏱️ Processing timeout. Video might be too long or complex.",
}

# Progress messages with dynamic model names
PROGRESS_MESSAGES = {
    "downloading": "📥 Downloading video...",
    "analyzing": f"🤖 Analyzing with {Config.GEMINI_MODEL.replace('gemini-', 'Gemini ')}...",
    "enriching": f"✨ Creating comprehensive guide with {Config.CLAUDE_MODEL.split('/')[-1]}...",
    "generating_diagrams": "🎨 Generating technical diagrams...",
    "saving": "💾 Saving to knowledge base...",
    "completed": "✅ Knowledge entry created successfully!"
}

# Supported platforms with URL patterns
SUPPORTED_PLATFORMS = {
    "tiktok": [
        r"tiktok\.com",
        r"vm\.tiktok\.com",
        r"vt\.tiktok\.com"
    ],
    "instagram": [
        r"instagram\.com/reel",
        r"instagram\.com/p/",
        r"instagr\.am"
    ]
}

# Category mappings for knowledge organization
CATEGORY_MAPPINGS = {
    "🤖 AI": ["ai", "machine learning", "llm", "neural", "gpt", "claude", "artificial intelligence"],
    "🌐 Web Development": ["web", "javascript", "react", "vue", "html", "css", "frontend", "backend"],
    "💻 Programming": ["python", "java", "golang", "rust", "programming", "coding", "software"],
    "⚙️ DevOps": ["devops", "docker", "kubernetes", "cloud", "aws", "deployment", "infrastructure"],
    "📱 Mobile": ["mobile", "ios", "android", "react native", "flutter", "swift", "kotlin"],
    "🛡️ Security": ["security", "cybersecurity", "encryption", "authentication", "vulnerability"],
    "📊 Data": ["data science", "analytics", "database", "sql", "big data", "visualization"]
}

# Export commonly used values for backwards compatibility
TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
RAILWAY_API_URL = Config.RAILWAY_API_URL
RAILWAY_API_KEY = Config.RAILWAY_API_KEY
GEMINI_API_KEY = Config.GEMINI_API_KEY
GEMINI_MODEL = Config.GEMINI_MODEL
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
OPENROUTER_BASE_URL = Config.OPENROUTER_BASE_URL
OPENROUTER_MAX_TOKENS = Config.OPENROUTER_MAX_TOKENS
CLAUDE_MODEL = Config.CLAUDE_MODEL
CLAUDE_MAX_TOKENS = Config.CLAUDE_MAX_TOKENS
GPT_MODEL = Config.GPT_MODEL
GPT_MAX_TOKENS = Config.GPT_MAX_TOKENS
IMAGE_MODEL = Config.IMAGE_MODEL
NOTION_API_KEY = Config.NOTION_API_KEY
NOTION_DATABASE_ID = Config.NOTION_DATABASE_ID
TEMP_DIR = Config.TEMP_DIR
KNOWLEDGE_BASE_PATH = Config.KNOWLEDGE_BASE_PATH
ANTHROPIC_API_KEY = Config.ANTHROPIC_API_KEY
