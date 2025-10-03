# 🤖 Knowledge Bot

> Transform TikTok & Instagram videos into comprehensive educational content with multi-AI pipeline

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway Deploy](https://img.shields.io/badge/Railway-Deploy-purple.svg)](https://railway.app)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](https://github.com/silvioiatech/Knowledge-Bot)

**Knowledge Bot** is a production-ready Telegram bot that automatically downloads, analyzes, and transforms social media videos into structured educational content using cutting-edge AI models (Gemini, Claude, GPT).

## ✨ Features

- 🎥 **Multi-Platform Support** - TikTok, Instagram Reels
- 🤖 **Advanced AI Pipeline**
  - Gemini 2.0 Flash for video analysis
  - Claude 3.5 Sonnet for content enrichment
  - GPT-4 for final course formatting
- 🎯 **Interactive Category System** - Smart categorization with user selection
- 📊 **Dual Storage** - Markdown files + Notion database integration
- 🎨 **Conditional AI Images** - Generate diagrams only when beneficial
- ⚡ **Async Processing** - Non-blocking, efficient workflow
- 🔒 **Rate Limiting** - Built-in spam protection
- 📝 **Quality Metrics** - Confidence scores and quality assessment

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Telegram Bot Token ([Get from @BotFather](https://t.me/botfather))
- Google Gemini API Key ([Get here](https://makersuite.google.com/app/apikey))
- OpenRouter API Key ([Get here](https://openrouter.ai/))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/silvioiatech/Knowledge-Bot.git
cd Knowledge-Bot

# Install dependencies
python3 -m pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configuration

Edit `.env` file:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional
USE_NOTION_STORAGE=true
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

### 4. Run

```bash
# Option 1: Quick start script
./start.sh

# Option 2: Direct run
python3 main.py

# Option 3: Test first
python3 test_bot.py
```

## 📖 How It Works

### Processing Pipeline

```
1. 📥 User sends video URL
   ↓
2. 🔄 Railway API downloads video
   ↓
3. 🤖 Gemini analyzes content
   ↓
4. 📊 Preview & user approval
   ↓
5. 🎯 Interactive category selection
   ↓
6. ✨ Claude enriches content
   ↓
7. 📚 GPT formats as course
   ↓
8. 💾 Save to Notion + Markdown
   ↓
9. ✅ User receives final links
```

### Category System

The bot intelligently categorizes content:

- 🍎 **APPLE** - macOS, iOS ecosystem
- 🐧 **LINUX** - Linux systems, CLI
- 🤖 **AI** - Machine learning, AI tools
- 💰 **MONETIZATION** - Business, marketing
- 🔌 **EXTERNAL_DEVICES** - Hardware, IoT
- 📱 **MOBILE_DEV** - App development
- ☁️ **CLOUD** - Cloud services, SaaS
- 🔒 **SECURITY** - Cybersecurity, privacy
- 📈 **PRODUCTIVITY** - Workflows, tools

## 🎮 Usage

### Basic Commands

- `/start` - Initialize bot and see welcome message
- Send any TikTok or Instagram Reel URL to process

### Supported URLs

```
✅ https://www.tiktok.com/@user/video/123456
✅ https://vm.tiktok.com/XXX
✅ https://www.instagram.com/reel/XXX
✅ https://www.instagram.com/p/XXX
```

### Example Workflow

1. Send video URL to bot
2. Wait for download & analysis (~30-60 seconds)
3. Review AI-generated preview
4. Click ✅ **Approve** to continue
5. Select category from suggestions
6. Choose subcategory
7. Receive Notion link + Markdown file

## 📁 Project Structure

```
Knowledge-Bot/
├── bot/                           # Bot components
│   ├── main.py                    # Bot initialization
│   ├── middleware.py              # Rate limiting
│   ├── interactive_category_system.py  # Category UI
│   └── handlers/
│       └── video_handler.py       # Main processing logic
├── services/                      # AI & API services
│   ├── railway_client.py          # Video downloads
│   ├── gemini_service.py          # Gemini analysis
│   ├── enhanced_claude_service.py # Claude enrichment
│   ├── gpt_service.py             # GPT finalization
│   └── image_generation_service.py # Image generation
├── storage/                       # Storage backends
│   ├── markdown_storage.py        # Local files
│   └── notion_storage.py          # Notion integration
├── core/models/                   # Data models
│   └── content_models.py          # Pydantic models
├── utils/                         # Utilities
│   └── retry_utils.py             # Retry logic
├── config.py                      # Configuration
├── main.py                        # Entry point
├── test_bot.py                    # Test suite
└── start.sh                       # Quick start script
```

## 🔧 Configuration Options

### Model Selection

```bash
# Gemini
GEMINI_MODEL=gemini-2.0-flash-exp  # Fast & cost-effective
# GEMINI_MODEL=gemini-2.5-pro      # More powerful

# Claude (via OpenRouter)
CLAUDE_MODEL=anthropic/claude-3.5-sonnet

# GPT (via OpenRouter)
GPT_MODEL=openai/gpt-4o-mini       # Recommended
# GPT_MODEL=openai/gpt-4           # More powerful
```

### Feature Flags

```bash
ENABLE_IMAGE_GENERATION=false      # AI diagrams (costs extra)
USE_GPT_FINALIZER=true             # GPT formatting (recommended)
ENABLE_WEB_RESEARCH=false          # Web research (experimental)
USE_NOTION_STORAGE=true            # Notion integration
```

### Processing Limits

```bash
MAX_PROCESSING_TIME=1800           # 30 minutes max
TARGET_CONTENT_LENGTH=2500         # Target word count
SESSION_TTL_MINUTES=30             # Session timeout
```

## 📊 Output Format

### Markdown Files

Saved to `./knowledge_base/{category}/YYYYMMDD-title.md`:

```markdown
---
title: 'Video Title'
date: 2025-10-03
source_url: 'https://tiktok.com/...'
platform: tiktok
category: '🤖 AI'
difficulty: Intermediate
tools: [Tool1, Tool2]
tags: [tag1, tag2]
---

# Video Title

## Course Overview

...

## Learning Objectives

...

## Key Concepts

...

## Step-by-Step Labs

...

## Assessment

...

## Resources

...
```

### Notion Database

Structured database entry with:

- Title, Category, Subcategory
- Content Quality, Difficulty
- Word Count, Processing Date
- Source Video URL
- Key Points, Tags, Tools
- Platform Specific
- Quality Checkboxes

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_bot.py
```

Tests include:

- ✅ File structure validation
- ✅ Dependency checks
- ✅ Import verification
- ✅ Configuration validation
- ✅ Data model tests
- ✅ Handler functionality

## 🐛 Troubleshooting

### Common Issues

**"Configuration validation failed"**

```bash
# Ensure all required keys are set
TELEGRAM_BOT_TOKEN=xxx
GEMINI_API_KEY=xxx
OPENROUTER_API_KEY=xxx
```

**"Railway download failed"**

- Video might be private or unavailable
- Try a different video URL
- Check Railway API status

**"Rate limit reached"**

- Wait 60 seconds between video submissions
- Default: 1 video per minute per user

**"Notion save failed"**

- Verify Notion API key is valid
- Check database ID is correct
- Ensure integration has database access
- Verify all required properties exist

### Debug Mode

```bash
# Run with debug logging
python3 -c "
from bot.main import KnowledgeBot
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)
bot = KnowledgeBot()
asyncio.run(bot.start_polling())
"
```

## 🚀 Deployment

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click "Deploy on Railway"
2. Add environment variables
3. Deploy!

### Docker

```bash
# Build
docker build -t knowledge-bot .

# Run
docker run -d \
  --env-file .env \
  --name knowledge-bot \
  knowledge-bot
```

### Heroku

```bash
# Login and create app
heroku login
heroku create your-knowledge-bot

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=xxx
heroku config:set GEMINI_API_KEY=xxx
heroku config:set OPENROUTER_API_KEY=xxx

# Deploy
git push heroku main
```

## 💡 Best Practices

### Cost Optimization

1. **Start with minimal features**

   ```bash
   ENABLE_IMAGE_GENERATION=false
   USE_GPT_FINALIZER=true
   ENABLE_WEB_RESEARCH=false
   ```

2. **Use cost-effective models**

   ```bash
   GEMINI_MODEL=gemini-2.0-flash-exp
   GPT_MODEL=openai/gpt-4o-mini
   ```

3. **Monitor API usage**
   - Check OpenRouter dashboard
   - Monitor Gemini quota
   - Track processing costs

### Quality Control

1. Always review AI-generated content
2. Use "Re-analyze" if results are poor
3. Verify category selections
4. Check Notion entries for accuracy

### Storage Strategy

- Enable both Markdown (backup) and Notion (organization)
- Markdown files are always created locally
- Notion provides better searchability
- Keep knowledge_base/ in version control

## 📈 Roadmap

- [ ] Support for YouTube videos
- [ ] Multi-language content support
- [ ] Custom category creation
- [ ] Batch processing
- [ ] Export to PDF/ePub
- [ ] Web dashboard
- [ ] Analytics & insights

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [Google Gemini](https://ai.google.dev/) - Video analysis AI
- [Anthropic Claude](https://www.anthropic.com/) - Content enrichment
- [OpenRouter](https://openrouter.ai/) - Unified AI API access
- [Railway](https://railway.app/) - Video download service

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/silvioiatech/Knowledge-Bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/silvioiatech/Knowledge-Bot/discussions)
- **Documentation**: This README contains all setup and usage information

---

**Built with ❤️ for knowledge seekers and content creators**

⭐ **Star this repo if you find it useful!**

_Transform videos into knowledge with AI-powered course generation_
