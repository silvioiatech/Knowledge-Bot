# Knowledge Bot MVP

A Python Telegram bot that processes TikTok/Instagram video URLs, analyzes content with AI, and builds a knowledge base from video insights.

## 🎯 Features

- **Video Processing**: Downloads videos from TikTok and Instagram URLs
- **AI Analysis**: Uses Google Gemini 1.5 Flash for video content analysis  
- **Content Enrichment**: Transforms analysis into educational content with Claude
- **Knowledge Base**: Automatically saves content as categorized Markdown files
- **Interactive Approval**: Users can approve/reject analysis before saving
- **Rate Limiting**: Max 10 videos per user per hour

## 🏗️ Architecture

```
knowledge-bot/
├── bot/
│   ├── main.py              # Bot initialization & polling
│   ├── middleware.py        # Rate limiting middleware
│   └── handlers/
│       └── video_handler.py # URL detection & workflow
├── services/
│   ├── railway_client.py    # Railway yt-dlp API integration
│   ├── gemini_service.py    # Google Gemini video analysis
│   └── claude_service.py    # Claude content enrichment
├── storage/
│   └── markdown_storage.py  # Markdown file management
├── config.py                # Configuration & environment
├── run_bot.py              # Main entry point
└── knowledge_base/          # Generated knowledge base
    ├── artificial-intelligence/
    ├── development/
    ├── design/
    └── ...
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/silvioiatech/Knowledge-Bot.git
cd Knowledge-Bot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:
- **Telegram Bot Token**: Create bot with [@BotFather](https://t.me/botfather)
- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com)
- **OpenRouter API Key**: Get from [OpenRouter](https://openrouter.ai)

Optional:
- **Railway API**: Deploy yt-dlp service on Railway (API key not required)

### 3. Launch

```bash
# Run the bot
python run_bot.py

# Or directly
python bot/main.py
```

## 📋 Usage Workflow

1. **Start**: Send `/start` to the bot
2. **Send URL**: Share a TikTok or Instagram video URL
3. **Processing**: Bot downloads and analyzes the video
4. **Review**: Get analysis summary with approval buttons
5. **Approve**: Click ✅ to enrich and save to knowledge base
6. **Access**: Find saved content in `knowledge_base/` directory

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.0-flash-exp` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `OPENROUTER_MODEL` | Claude model via OpenRouter | `anthropic/claude-3.5-sonnet` |
| `RAILWAY_API_URL` | Railway yt-dlp service URL | Optional |
| `RAILWAY_API_KEY` | Railway API authentication | Optional |
| `KNOWLEDGE_BASE_PATH` | Storage directory | `./knowledge_base` |
| `MAX_VIDEO_DURATION_SECONDS` | Video length limit | `600` (10 min) |
| `RATE_LIMIT_PER_HOUR` | Max videos per user | `10` |

## 🎨 Output Format

Each processed video becomes a Markdown file with:

```yaml
---
title: "Video Title"
date: "2024-01-15T10:30:00"
source_url: "https://tiktok.com/..."
platform: "tiktok"
subject: "AI Development"
tools: ["ChatGPT", "Python", "VS Code"]
tags: ["ai", "coding", "tutorial"]
---

# Video Title

## Overview
Brief introduction...

## Key Concepts
Detailed explanations...

## Tools & Technologies
Tool descriptions...

## Additional Resources
Links and references...
```

## 🛠️ Development

### Testing Individual Components

```bash
# Test Railway client
python -c "from services.railway_client import *; import asyncio; asyncio.run(download_video_from_url('URL'))"

# Test Gemini analysis  
python -c "from services.gemini_service import *; import asyncio; asyncio.run(analyze_video_content('video.mp4'))"

# Test Claude enrichment
python -c "from services.claude_service import *; import asyncio; asyncio.run(enrich_analysis({...}))"
```

### MVP Validation Checklist

- [ ] `/start` command responds
- [ ] URL detection works for TikTok/Instagram
- [ ] Railway API downloads videos
- [ ] Gemini analyzes video content
- [ ] Inline keyboard buttons function
- [ ] Claude enriches content
- [ ] Markdown files save with categories

### Logs

Bot logs are saved to `logs/bot_YYYY-MM-DD.log` with 7-day rotation.

## 🔗 Dependencies

- **aiogram 3.5**: Telegram bot framework
- **httpx**: Async HTTP client for API calls and OpenRouter integration
- **google-generativeai 0.7+**: Official Google Gemini AI SDK
- **loguru**: Structured logging
- **aiofiles**: Async file operations
- **pyyaml**: YAML frontmatter processing

**Note**: Removed `anthropic` dependency - now using OpenRouter for Claude API access

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test changes thoroughly
4. Submit pull request

## 📞 Support

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: See `.github/copilot-instructions.md` for AI development guidance