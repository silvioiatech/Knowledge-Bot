# Copilot Instructions for Knowledge Bot MVP

## Project Overview

This is a Python Telegram bot that processes TikTok/Instagram video URLs, downloads videos via a Railway yt-dlp API service, analyzes content with Google Gemini 1.5 Flash, and enriches content with Claude API before saving as Markdown files to build a knowledge base.

## Architecture & Key Components

### Core Service Flow
1. **Video Input** → Telegram bot receives URLs via aiogram 3.5
2. **Download** → Railway yt-dlp API service downloads videos  
3. **Analysis** → Google Gemini 1.5 Flash extracts structured insights
4. **Validation** → User approves/rejects via inline keyboard buttons
5. **Enrichment** → Claude transforms analysis into educational content
6. **Storage** → Save as categorized Markdown files with YAML frontmatter

### Project Structure
```
knowledge-bot/
├── bot/
│   ├── main.py              # aiogram bot initialization & polling
│   └── handlers/
│       └── video_handler.py # URL detection, workflow orchestration
├── services/
│   ├── railway_client.py    # Railway yt-dlp API integration
│   ├── gemini_service.py    # Video analysis with structured output
│   └── claude_service.py    # Content enrichment to educational format
├── storage/
│   └── markdown_storage.py  # Categorized Markdown file management
├── config.py                # Environment configuration
└── knowledge_base/          # Generated Markdown knowledge base
```

## Development Patterns & Conventions

### Async/Await Throughout
- All services use `httpx` for async HTTP calls
- Bot handlers are async functions with proper error handling
- Use `aiofiles` for file operations in storage layer

### Error Handling Strategy
```python
ERROR_MESSAGES = {
    "invalid_url": "❌ Please send a valid TikTok or Instagram video URL",
    "download_failed": "❌ Failed to download video. Try again later.",
    "analysis_failed": "❌ Could not analyze video. Please try again.",
    "rate_limit": "⏰ Rate limit reached. Try again in 1 hour.",
}
```

### Rate Limiting
- Max 10 videos per user per hour via middleware
- Max video duration: 600 seconds
- Railway API calls include retry logic with exponential backoff

### Message Flow Pattern
- Edit existing messages rather than sending new ones
- Progress updates: "🔄 Downloading..." → "🤖 Analyzing..." → Results
- Inline keyboards for user validation (✅ Approve / ❌ Reject / 🔄 Re-analyze)

## Key Service Integrations

### Railway yt-dlp API Client
- Poll `/downloads/{request_id}` until completion
- Handle file downloads to temp directory
- Include proper timeout and retry mechanisms

### Gemini Video Analysis
- Upload video files for analysis
- Extract structured data: subject, tools, key_points, visible_text, resources
- Return JSON format for consistent downstream processing
- Implement caching to avoid re-analyzing identical content

### Claude Content Enrichment
- Transform Gemini analysis into educational chapters
- Generate Markdown with sections: Overview, Key Concepts, Tools, Applications, Resources
- Maintain consistent formatting for knowledge base integration

### Markdown Storage System
- Auto-generate filenames from title + date
- Create category folders based on video subject mapping
- Include YAML frontmatter with metadata (title, date, source_url, tools, tags)
- Save to `KNOWLEDGE_BASE_PATH/category/filename.md`

## Environment Configuration

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Bot authentication
- `RAILWAY_API_URL` / `RAILWAY_API_KEY` - Video download service
- `GEMINI_API_KEY` - Google AI analysis
- `ANTHROPIC_API_KEY` - Claude enrichment  
- `KNOWLEDGE_BASE_PATH` - Storage directory (default: `./knowledge_base`)

## Testing & Validation

### MVP Completion Checklist
- [ ] `/start` command responds correctly
- [ ] TikTok/Instagram URL detection works
- [ ] Railway API downloads videos successfully
- [ ] Gemini analyzes and returns structured data
- [ ] Inline keyboard validation functions
- [ ] Claude enrichment generates educational content
- [ ] Markdown files save with proper categorization

### Development Workflow
1. Test each service independently before integration
2. Verify Railway API connection first
3. Test Gemini with sample video files
4. Validate Claude enrichment output format
5. Ensure Telegram bot handles all error cases gracefully

## Logging & Monitoring

Use `loguru` with daily rotation:
```python
logger.add(
    "logs/bot_{time}.log",
    rotation="1 day", 
    retention="7 days",
    format="{time} | {level} | {message}"
)
```

## Key Dependencies

- `aiogram==3.5.0` - Telegram bot framework
- `httpx==0.27.0` - Async HTTP client
- `google-generativeai==0.3.2` - Gemini AI integration
- `anthropic==0.25.0` - Claude API client
- `loguru==0.7.2` - Structured logging
- `aiofiles==23.2.1` - Async file operations

## AI Service Prompts

### Gemini Analysis Focus
Extract: main topic, tools/apps mentioned, key points (numbered), on-screen text, important URLs/resources

### Claude Enrichment Goals  
Transform summary into educational chapter with context, explanations, practical examples, and maintained Markdown formatting

## File Creation Order
1. `config.py` - Environment setup
2. `services/railway_client.py` - Video download capability
3. `services/gemini_service.py` - Analysis engine
4. `bot/main.py` - Core bot initialization
5. `bot/handlers/video_handler.py` - Business logic orchestration
6. `services/claude_service.py` - Content enrichment
7. `storage/markdown_storage.py` - Knowledge base persistence