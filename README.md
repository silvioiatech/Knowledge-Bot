# 🤖 Knowledge Bot# � AI Knowledge Bot - Textbook Edition



Transform TikTok and Instagram videos into comprehensive knowledge base entries using AI-powered analysis and content generation.A powerful Python Telegram bot that transforms TikTok/Instagram videos into **comprehensive, illustrated textbook-quality content**. Uses advanced AI to analyze video content and generate professional reference material with technical diagrams.🤖 AI Knowledge Bot



## ✨ FeaturesA powerful Python Telegram bot that transforms TikTok/Instagram videos into organized knowledge entries. Uses AI to analyze video conten## 📦 Storage Modes



- **📥 Video Download**: Automatic video download from TikTok and Instagram### 📝 **Markdown Mode** (Default)

- **🧠 AI Analysis**: Deep content analysis with Google Gemini- Simple markdown files in `./knowledge_base/`

- **📝 Content Generation**: Textbook-quality content creation with Claude- Works with any text editor

- **🖼️ Diagram Generation**: AI-generated technical diagrams- Easy to backup and version control

- **💾 Smart Storage**: Markdown files + optional Notion database integration

- **🎯 Interactive Workflow**: Approve/reject analysis before content generation### 📖 **Book Mode** (Obsidian)

- Beautiful book-like formatting

## 🚀 Quick Start- Auto-categorization into sections

- Cross-references and navigation

### 1. Clone and Setup- Perfect for Obsidian users



```bash### 🗄️ **Notion Database Mode** (NEW!)

git clone https://github.com/silvioiatech/Knowledge-Bot.git- Cloud-based Notion database storage

cd Knowledge-Bot- Automatic categorization with emojis

pip install -r requirements.txt- Rich properties (tags, difficulty, tools)

```- Web access and mobile sync



### 2. Configure Environment#### Notion Setup

```bash

```bash# In your .env file

cp .env.example .envUSE_NOTION_STORAGE=true

# Edit .env with your API keysNOTION_API_KEY=secret_your_integration_key

```NOTION_DATABASE_ID=your_database_id_here

```

**Required API Keys:**

- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)**Required Database Properties:**

- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/)- Title (title)

- `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/)- Category (select) - Auto-categorized with emojis

- Subcategory (select)

### 3. Run the Bot- Tags (multi_select)

- Tools Mentioned (multi_select)

```bash- Difficulty (select) - 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced

python app.py- Source Video (url)

```- Date Added (date)



## 📋 Environment VariablesTo enable Book Mode:

```bash

### Core Configuration# In your .env file

```envSTORAGE_MODE=book

TELEGRAM_BOT_TOKEN=your_telegram_bot_tokenOBSIDIAN_VAULT_PATH=./my-knowledge-library

GEMINI_API_KEY=your_gemini_api_keyENABLE_BOOK_STRUCTURE=true

OPENROUTER_API_KEY=your_openrouter_api_key```creates beautiful, searchable knowledge bases.

```

## ✨ Features

### Optional Services

```env### 🎥 **Smart Video Processing**

# Railway video download service- Downloads from TikTok & Instagram URLs

RAILWAY_API_URL=https://your-railway-service.up.railway.app- Handles multiple video formats automatically

- Railway.app integration for reliable downloading

# Notion database integration

NOTION_API_KEY=your_notion_api_key### 🧠 **Advanced AI-Powered Analysis**

NOTION_DATABASE_ID=your_database_id- **Google Gemini 1.5 Pro** - Comprehensive video content analysis with 20+ data fields

USE_NOTION_STORAGE=true- **Claude 3.5 Sonnet** - Textbook-quality content generation (2500-4000 words)

- **Gemini 2.5 Flash Image Preview** - AI-generated technical diagrams and illustrations

# Image generation- Extracts category confidence, visual concepts, code snippets, performance metrics

ENABLE_IMAGE_GENERATION=true

IMAGE_MODEL=black-forest-labs/flux-1.1-pro### 📚 **Professional Reference Material**

```- **Textbook-Quality Content**: Comprehensive 3000+ word technical documentation

- **AI-Generated Diagrams**: Up to 3 technical illustrations per entry

## 🏗️ Project Structure- **Advanced Categorization**: Confidence scoring and auto-review flagging

- **Multiple Storage Options**: Notion database, Obsidian books, or markdown files

```- **Cost Tracking**: Token usage monitoring and pricing analytics

Knowledge-Bot/

├── app.py                      # Main entry point### 🎨 **New: AI-Generated Technical Diagrams**

├── config.py                   # Configuration management- **Gemini 2.5 Flash Image Preview** creates professional technical illustrations

├── requirements.txt            # Dependencies- Automatically detects diagram opportunities in content

├── .env.example               # Environment template- Generates: flowcharts, system architectures, process diagrams, UI mockups

├── bot/- Embedded directly into textbook-quality content with proper captions

│   ├── main.py                # Bot initialization

│   ├── middleware.py          # Rate limiting & logging### 📊 **Enhanced Analytics & Quality Control**

│   └── handlers/- **Category Confidence Scoring**: Auto-flags uncertain classifications for review

│       └── video_handler.py   # Video processing workflow- **Content Quality Metrics**: Tracks comprehensive analysis depth (20+ fields)

├── services/- **Cost Analytics**: Real-time token usage and pricing with OpenRouter integration

│   ├── railway_client.py      # Video download service- **Dynamic Category Management**: Learns and adapts categorization over time

│   ├── gemini_service.py      # AI video analysis

│   ├── claude_service.py      # Content enrichment### 🔒 **Privacy & Control**

│   └── image_generation_service.py # Diagram generation- Interactive approval system - you control what gets saved

├── storage/- Private repository integration for personal knowledge

│   ├── markdown_storage.py    # Markdown file management- Rate limiting and user management

│   └── notion_storage.py      # Notion database integration- Local or cloud storage options

└── core/models/

    └── content_models.py      # Data models### 📱 **Multi-Platform Access**

```- Works with any Markdown editor

- Obsidian mobile app support

## 🎯 How It Works- GitHub integration for sync across devices



1. **Send Video URL** → Bot receives TikTok/Instagram video URL## 🏗️ Project Structure

2. **Download Video** → Railway service downloads the video file

3. **AI Analysis** → Gemini analyzes video content and extracts insights```

4. **Preview & Approval** → Interactive preview with approve/reject optionsKnowledge-Bot/

5. **Content Generation** → Claude creates comprehensive educational content├── 📁 bot/

6. **Save Results** → Store in Markdown files and/or Notion database│   ├── main.py              # aiogram bot initialization

│   └── handlers/

## 🔧 Supported Platforms│       └── video_handler.py # Video processing workflow

├── 📁 services/

- **TikTok**: `tiktok.com/@user/video/...`│   ├── railway_client.py           # Video download service  

- **Instagram**: `instagram.com/p/...` and `instagram.com/reel/...`│   ├── gemini_service.py           # Comprehensive AI video analysis

│   ├── claude_service.py           # Textbook-quality content generation

## 📊 Output Examples│   ├── image_generation_service.py # AI-powered technical diagrams

│   └── git_sync.py                 # GitHub integration

### Markdown Files├── 📁 storage/

```markdown│   ├── markdown_storage.py  # Simple markdown files

# Advanced Python AsyncIO Patterns│   ├── book_storage.py      # Obsidian book format

│   └── notion_storage.py    # Notion database integration

## Overview├── ⚙️ config.py             # Configuration management

Learn modern asynchronous programming patterns...├── 🚀 app.py               # Main application entry

└── 📖 PRIVATE_REPOSITORY_SETUP.md  # Setup guide

## Key Concepts│   └── claude_service.py    # Claude content enrichment

- Event loops and coroutines├── storage/

- Error handling in async code│   └── markdown_storage.py  # Markdown file management

- Performance optimization techniques├── config.py                # Configuration & environment

├── run_bot.py              # Main entry point

## Tools & Technologies└── knowledge_base/          # Generated knowledge base

- Python AsyncIO    ├── artificial-intelligence/

- aiohttp    ├── development/

- asyncpg    ├── design/

```    └── ...

```

### Notion Database

Automatically creates entries with:## 🚀 Quick Start

- Title, Category, Tags

- Content Quality Score### 1. Installation

- Word Count, Processing Date

- Key Points, Tools Used```bash

- Source URL and Platform# Clone repository

git clone https://github.com/silvioiatech/Knowledge-Bot.git

## 🚨 Troubleshootingcd Knowledge-Bot



### Common Issues# Install dependencies

pip install -r requirements.txt

**❌ "Gemini API Error: Model not found"**```

```env

# Use correct model name### 2. Configuration

GEMINI_MODEL=gemini-1.5-flash

``````bash

# Copy environment template

**❌ "OpenRouter API Error"**cp .env.example .env

- Check your API key at [OpenRouter](https://openrouter.ai)

- Verify you have credits available# Edit .env with your API keys

- Ensure model name is correct (e.g., `anthropic/claude-3.5-sonnet`)nano .env

```

**❌ "Railway Download Failed"**

- Verify `RAILWAY_API_URL` is correctly configuredRequired API keys:

- TikTok downloads may fail on first attempt (bot retries automatically)- **Telegram Bot Token**: Create bot with [@BotFather](https://t.me/botfather)

- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com)

**❌ "Notion Integration Error"**- **OpenRouter API Key**: Get from [OpenRouter](https://openrouter.ai)

- Check database ID and API key are correct

- Ensure integration has write permissions to the databaseOptional:

- **Railway API**: Deploy yt-dlp service on Railway (API key not required)

## 📝 License

### 3. Launch

MIT License - feel free to use and modify for your projects.

```bash

## 🤝 Contributing# Run the bot

python app.py

1. Fork the repository```

2. Create a feature branch

3. Make your changesThe bot will start polling for messages. Send it a TikTok or Instagram URL to begin!

4. Submit a pull request

## 📋 Usage Workflow

## 🆘 Support

1. **Start**: Send `/start` to the bot

- Open an [Issue](https://github.com/silvioiatech/Knowledge-Bot/issues) for bug reports2. **Send URL**: Share a TikTok or Instagram video URL

- Check [Discussions](https://github.com/silvioiatech/Knowledge-Bot/discussions) for questions3. **Processing**: Bot downloads and analyzes the video

- Review `.env.example` for configuration help4. **Review**: Get analysis summary with approval buttons
5. **Approve**: Click ✅ to enrich and save to knowledge base
6. **Access**: Find saved content in `knowledge_base/` directory

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| **Core AI Configuration** |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model for analysis | `gemini-1.5-flash` |
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

## 🚨 Troubleshooting

### Common Issues

**❌ Gemini Analysis Failed: Model Not Found**
```
404 Publisher Model `projects/generativelanguage-ga/...` was not found
```
- **Solution**: Use Google AI Studio model names, not Vertex AI names
- **Correct models**: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash-exp`
- **Update**: `GEMINI_MODEL=gemini-1.5-flash` in your `.env` file

**❌ OpenRouter API Errors**
- **Check**: API key is valid and has credits
- **Verify**: Model name is correct (`anthropic/claude-3.5-sonnet`)
- **Solution**: Visit [OpenRouter](https://openrouter.ai) to check usage

**❌ Railway Download Fails**
- **TikTok URLs**: May fail on first attempt (normal behavior), bot will retry automatically
- **Check**: `RAILWAY_API_URL` is correctly set
- **Verify**: Railway service is deployed and running
- **Alternative**: Leave `RAILWAY_API_URL` empty to use fallback methods

**❌ Notion Storage Errors**
- **Check**: Database ID and API key are correct
- **Verify**: Integration has write permissions
- **Required**: Database must have all required properties (see setup guide)

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