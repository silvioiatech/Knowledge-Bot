# � AI Knowledge Bot - Textbook Edition

A powerful Python Telegram bot that transforms TikTok/Instagram videos into **comprehensive, illustrated textbook-quality content**. Uses advanced AI to analyze video content and generate professional reference material with technical diagrams.🤖 AI Knowledge Bot

A powerful Python Telegram bot that transforms TikTok/Instagram videos into organized knowledge entries. Uses AI to analyze video conten## 📦 Storage Modes

### 📝 **Markdown Mode** (Default)
- Simple markdown files in `./knowledge_base/`
- Works with any text editor
- Easy to backup and version control

### 📖 **Book Mode** (Obsidian)
- Beautiful book-like formatting
- Auto-categorization into sections
- Cross-references and navigation
- Perfect for Obsidian users

### 🗄️ **Notion Database Mode** (NEW!)
- Cloud-based Notion database storage
- Automatic categorization with emojis
- Rich properties (tags, difficulty, tools)
- Web access and mobile sync

#### Notion Setup
```bash
# In your .env file
USE_NOTION_STORAGE=true
NOTION_API_KEY=secret_your_integration_key
NOTION_DATABASE_ID=your_database_id_here
```

**Required Database Properties:**
- Title (title)
- Category (select) - Auto-categorized with emojis
- Subcategory (select)
- Tags (multi_select)
- Tools Mentioned (multi_select)
- Difficulty (select) - 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced
- Source Video (url)
- Date Added (date)

To enable Book Mode:
```bash
# In your .env file
STORAGE_MODE=book
OBSIDIAN_VAULT_PATH=./my-knowledge-library
ENABLE_BOOK_STRUCTURE=true
```creates beautiful, searchable knowledge bases.

## ✨ Features

### 🎥 **Smart Video Processing**
- Downloads from TikTok & Instagram URLs
- Handles multiple video formats automatically
- Railway.app integration for reliable downloading

### 🧠 **Advanced AI-Powered Analysis**
- **Google Gemini 1.5 Pro** - Comprehensive video content analysis with 20+ data fields
- **Claude 3.5 Sonnet** - Textbook-quality content generation (2500-4000 words)
- **Gemini 2.5 Flash Image Preview** - AI-generated technical diagrams and illustrations
- Extracts category confidence, visual concepts, code snippets, performance metrics

### 📚 **Professional Reference Material**
- **Textbook-Quality Content**: Comprehensive 3000+ word technical documentation
- **AI-Generated Diagrams**: Up to 3 technical illustrations per entry
- **Advanced Categorization**: Confidence scoring and auto-review flagging
- **Multiple Storage Options**: Notion database, Obsidian books, or markdown files
- **Cost Tracking**: Token usage monitoring and pricing analytics

### 🎨 **New: AI-Generated Technical Diagrams**
- **Gemini 2.5 Flash Image Preview** creates professional technical illustrations
- Automatically detects diagram opportunities in content
- Generates: flowcharts, system architectures, process diagrams, UI mockups
- Embedded directly into textbook-quality content with proper captions

### 📊 **Enhanced Analytics & Quality Control**
- **Category Confidence Scoring**: Auto-flags uncertain classifications for review
- **Content Quality Metrics**: Tracks comprehensive analysis depth (20+ fields)
- **Cost Analytics**: Real-time token usage and pricing with OpenRouter integration
- **Dynamic Category Management**: Learns and adapts categorization over time

### 🔒 **Privacy & Control**
- Interactive approval system - you control what gets saved
- Private repository integration for personal knowledge
- Rate limiting and user management
- Local or cloud storage options

### 📱 **Multi-Platform Access**
- Works with any Markdown editor
- Obsidian mobile app support
- GitHub integration for sync across devices

## 🏗️ Project Structure

```
Knowledge-Bot/
├── 📁 bot/
│   ├── main.py              # aiogram bot initialization
│   └── handlers/
│       └── video_handler.py # Video processing workflow
├── 📁 services/
│   ├── railway_client.py           # Video download service  
│   ├── gemini_service.py           # Comprehensive AI video analysis
│   ├── claude_service.py           # Textbook-quality content generation
│   ├── image_generation_service.py # AI-powered technical diagrams
│   └── git_sync.py                 # GitHub integration
├── 📁 storage/
│   ├── markdown_storage.py  # Simple markdown files
│   ├── book_storage.py      # Obsidian book format
│   └── notion_storage.py    # Notion database integration
├── ⚙️ config.py             # Configuration management
├── 🚀 app.py               # Main application entry
└── 📖 PRIVATE_REPOSITORY_SETUP.md  # Setup guide
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
python app.py
```

The bot will start polling for messages. Send it a TikTok or Instagram URL to begin!

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
| **Core AI Configuration** |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model for analysis | `gemini-1.5-pro` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `OPENROUTER_MODEL` | Claude model for content | `anthropic/claude-3.5-sonnet` |
| **Image Generation** |
| `IMAGE_MODEL` | Gemini model for diagrams | `google/gemini-2.5-flash-image-preview` |
| `ENABLE_IMAGE_GENERATION` | Enable diagram generation | `true` |
| `MAX_IMAGES_PER_ENTRY` | Max diagrams per entry | `3` |
| **Content Quality** |
| `TARGET_CONTENT_LENGTH` | Target word count | `3000` |
| `MIN_CATEGORY_CONFIDENCE` | Category confidence threshold | `0.7` |
| **Storage & Limits** |
| `RAILWAY_API_URL` | Railway yt-dlp service URL | Optional |
| `KNOWLEDGE_BASE_PATH` | Storage directory | `./knowledge_base` |
| `USE_NOTION_STORAGE` | Enable Notion database | `false` |
| `NOTION_API_KEY` | Notion integration token | Optional |
| `NOTION_DATABASE_ID` | Target Notion database | Optional |
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

## � Storage Modes

### 📝 **Markdown Mode** (Default)
- Simple markdown files in `./knowledge_base/`
- Works with any text editor
- Easy to backup and version control

### 📖 **Book Mode** (Obsidian)
- Beautiful book-like formatting
- Auto-categorization into sections
- Cross-references and navigation
- Perfect for Obsidian users

To enable Book Mode:
```bash
# In your .env file
STORAGE_MODE=book
OBSIDIAN_VAULT_PATH=./my-knowledge-library
ENABLE_BOOK_STRUCTURE=true
```

## 🔒 Private Repository Setup

Want to keep your knowledge private while sharing the bot code?

1. **Create a private GitHub repository** for your knowledge
2. **Follow the detailed setup guide**: [PRIVATE_REPOSITORY_SETUP.md](./PRIVATE_REPOSITORY_SETUP.md)
3. **Configure auto-sync** to your private repo

This allows you to:
- ✅ Share the bot code publicly
- ✅ Keep your knowledge private
- ✅ Auto-sync across devices
- ✅ Version control your learning

## 🌟 Community & Contributions

- **⭐ Star this repository** if you find it useful
- **🐛 Report bugs** via GitHub issues
- **💡 Suggest features** for future versions
- **🔧 Contribute code** via pull requests

## 📄 License

MIT License - feel free to use this bot for your own knowledge curation!
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