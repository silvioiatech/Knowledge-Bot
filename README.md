# 🤖 Knowledge Bot# 🤖 Knowledge Bot# 🤖 Knowledge Bot# � AI Knowledge Bot - Textbook Edition



A powerful Python Telegram bot that transforms TikTok and Instagram videos into organized knowledge base entries using AI-powered analysis and content generation.



[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)A powerful Python Telegram bot that transforms TikTok and Instagram videos into organized knowledge base entries using AI-powered analysis and content generation.

[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



## ✨ Features[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)Transform TikTok and Instagram videos into comprehensive knowledge base entries using AI-powered analysis and content generation.A powerful Python Telegram bot that transforms TikTok/Instagram videos into **comprehensive, illustrated textbook-quality content**. Uses advanced AI to analyze video content and generate professional reference material with technical diagrams.🤖 AI Knowledge Bot



### 🎥 **Smart Video Processing**[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

- **Automatic Download**: TikTok and Instagram URL support

- **Multiple Formats**: Handles various video formats automatically[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

- **Railway Integration**: Reliable cloud-based video downloading



### 🧠 **AI-Powered Analysis**

- **Google Gemini**: Advanced video content analysis## ✨ Features## ✨ FeaturesA powerful Python Telegram bot that transforms TikTok/Instagram videos into organized knowledge entries. Uses AI to analyze video conten## 📦 Storage Modes

- **Claude 3.5 Sonnet**: Professional content enrichment via OpenRouter

- **Structured Output**: Extracts topics, tools, key points, and resources



### 💾 **Flexible Storage**### 🎥 **Smart Video Processing**

- **Railway Files**: Persistent cloud storage with web browsing

- **Notion Database**: Optional cloud database integration- **Automatic Download**: TikTok and Instagram URL support

- **Markdown Files**: Local storage in organized categories

- **Multiple Formats**: Handles various video formats automatically- **📥 Video Download**: Automatic video download from TikTok and Instagram### 📝 **Markdown Mode** (Default)

### 🎯 **Interactive Workflow**

- **Preview & Approve**: Review analysis before content generation- **Railway Integration**: Reliable cloud-based video downloading

- **Quality Control**: Approve, reject, or re-analyze videos

- **Session Management**: Non-blocking processing for multiple users- **🧠 AI Analysis**: Deep content analysis with Google Gemini- Simple markdown files in `./knowledge_base/`



## 🚀 Quick Start### 🧠 **AI-Powered Analysis**



### 1. **Clone Repository**- **Google Gemini**: Advanced video content analysis- **📝 Content Generation**: Textbook-quality content creation with Claude- Works with any text editor

```bash

git clone https://github.com/silvioiatech/Knowledge-Bot.git- **Claude 3.5 Sonnet**: Professional content enrichment via OpenRouter

cd Knowledge-Bot

pip install -r requirements.txt- **Structured Output**: Extracts topics, tools, key points, and resources- **🖼️ Diagram Generation**: AI-generated technical diagrams- Easy to backup and version control

```



### 2. **Configure Environment**

```bash### 💾 **Flexible Storage**- **💾 Smart Storage**: Markdown files + optional Notion database integration

cp .env.example .env

# Edit .env with your API keys- **Railway Files**: Persistent cloud storage with web browsing

```

- **Notion Database**: Optional cloud database integration- **🎯 Interactive Workflow**: Approve/reject analysis before content generation### 📖 **Book Mode** (Obsidian)

**Required API Keys:**

- **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)- **Markdown Files**: Local storage in organized categories

- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com)

- **OpenRouter API Key**: Get from [OpenRouter](https://openrouter.ai)- Beautiful book-like formatting



### 3. **Run the Bot**### 🎯 **Interactive Workflow**

```bash

python app.py- **Preview & Approve**: Review analysis before content generation## 🚀 Quick Start- Auto-categorization into sections

```

- **Quality Control**: Approve, reject, or re-analyze videos

## 📋 Environment Configuration

- **Session Management**: Non-blocking processing for multiple users- Cross-references and navigation

### Core Settings

```env

# Telegram Bot

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here## 🚀 Quick Start### 1. Clone and Setup- Perfect for Obsidian users



# AI Services

GEMINI_API_KEY=your_gemini_api_key_here

OPENROUTER_API_KEY=your_openrouter_api_key_here### 1. **Clone Repository**



# Railway Deployment```bash

RAILWAY_STATIC_URL=https://your-app.up.railway.app

KNOWLEDGE_BASE_PATH=/app/knowledge_basegit clone https://github.com/silvioiatech/Knowledge-Bot.git```bash### 🗄️ **Notion Database Mode** (NEW!)

```

cd Knowledge-Bot

### Optional Integrations

```envpip install -r requirements.txtgit clone https://github.com/silvioiatech/Knowledge-Bot.git- Cloud-based Notion database storage

# Notion Database (Optional)

USE_NOTION_STORAGE=true```

NOTION_API_KEY=secret_your_notion_integration_key

NOTION_DATABASE_ID=your_database_id_herecd Knowledge-Bot- Automatic categorization with emojis

```

### 2. **Configure Environment**

See [`.env.example`](.env.example) for complete configuration options.

```bashpip install -r requirements.txt- Rich properties (tags, difficulty, tools)

## 🏗️ Architecture

cp .env.example .env

### Core Components

```# Edit .env with your API keys```- Web access and mobile sync

Knowledge-Bot/

├── 🤖 app.py                     # Main entry point (bot + file server)```

├── 🌐 railway_server.py          # FastAPI file server for web browsing

├── ⚙️ config.py                  # Environment configuration

├── 📁 bot/

│   ├── main.py                   # Telegram bot initialization**Required API Keys:**

│   ├── middleware.py             # Rate limiting & session management

│   └── handlers/- **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)### 2. Configure Environment#### Notion Setup

│       └── video_handler.py      # Video processing workflow

├── 🔧 services/- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com)

│   ├── gemini_service.py         # AI video analysis

│   ├── claude_service.py         # Content enrichment- **OpenRouter API Key**: Get from [OpenRouter](https://openrouter.ai)```bash

│   ├── image_generation_service.py # AI-powered technical diagrams

│   └── railway_client.py         # Video download service

├── 💾 storage/

│   ├── railway_storage.py        # Railway persistent files### 3. **Run the Bot**```bash# In your .env file

│   ├── notion_storage.py         # Notion database integration

│   └── markdown_storage.py       # Local markdown storage```bash

└── 🛠️ utils/

    └── retry_utils.py            # Retry logic with exponential backoffpython app.pycp .env.example .envUSE_NOTION_STORAGE=true

```

```

## 🎯 How It Works

# Edit .env with your API keysNOTION_API_KEY=secret_your_integration_key

1. **📱 Send Video URL** → User sends TikTok/Instagram video URL

2. **📥 Download Video** → Railway service downloads the video file## 📋 Environment Configuration

3. **🧠 AI Analysis** → Gemini analyzes content and extracts insights

4. **✅ Preview & Approval** → Interactive preview with approve/reject buttons```NOTION_DATABASE_ID=your_database_id_here

5. **📝 Content Generation** → Claude creates comprehensive educational content

6. **💾 Save Results** → Store in Railway files with web access + optional Notion backup### Core Settings



## 📊 Output Examples```env```



### Markdown Files# Telegram Bot

```markdown

---TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here**Required API Keys:**

title: "Advanced Python AsyncIO Patterns"

date: "2024-01-15T10:30:00"

source_url: "https://tiktok.com/@user/video/123"

platform: "tiktok"# AI Services- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)**Required Database Properties:**

category: "programming"

tools: ["Python", "AsyncIO", "aiohttp"]GEMINI_API_KEY=your_gemini_api_key_here

tags: ["python", "async", "performance"]

quality_score: 85OPENROUTER_API_KEY=your_openrouter_api_key_here- `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/)- Title (title)

---



# Advanced Python AsyncIO Patterns

# Railway Deployment- `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/)- Category (select) - Auto-categorized with emojis

## Overview

Comprehensive guide to modern asynchronous programming in Python...RAILWAY_STATIC_URL=https://your-app.up.railway.app



## Key ConceptsKNOWLEDGE_BASE_PATH=/app/knowledge_base- Subcategory (select)

- Event loops and coroutines

- Error handling in async code```

- Performance optimization techniques

### 3. Run the Bot- Tags (multi_select)

## Tools & Technologies

- **Python AsyncIO**: Core async framework### Optional Integrations

- **aiohttp**: Async HTTP client/server

- **asyncpg**: Async PostgreSQL driver```env- Tools Mentioned (multi_select)



## Practical Examples# Notion Database (Optional)

[Code examples and implementation details...]

USE_NOTION_STORAGE=true```bash- Difficulty (select) - 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced

## Additional Resources

- [Official AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)NOTION_API_KEY=secret_your_notion_integration_key

- [Real Python AsyncIO Guide](https://realpython.com/async-io-python/)

```NOTION_DATABASE_ID=your_database_id_herepython app.py- Source Video (url)



### Railway Web Access```

- **Browse Categories**: `https://your-app.up.railway.app/kb/`

- **View Files**: `https://your-app.up.railway.app/view/programming/asyncio-patterns.md````- Date Added (date)

- **Download Raw**: `https://your-app.up.railway.app/raw/programming/asyncio-patterns.md`

See [`.env.example`](.env.example) for complete configuration options.

## 🚀 Railway Deployment



### 1. **Setup Railway**

```bash## 🏗️ Architecture

# Install Railway CLI

npm install -g @railway/cli## 📋 Environment VariablesTo enable Book Mode:



# Login and deploy### Core Components

railway login

railway link``````bash

railway add volume --name knowledge-base --mount /app/knowledge_base

railway deployKnowledge-Bot/

```

├── 🤖 app.py                     # Main entry point (bot + file server)### Core Configuration# In your .env file

### 2. **Environment Variables**

Set in Railway dashboard:├── 🌐 railway_server.py          # FastAPI file server for web browsing

```env

TELEGRAM_BOT_TOKEN=your_token├── ⚙️ config.py                  # Environment configuration```envSTORAGE_MODE=book

GEMINI_API_KEY=your_key

OPENROUTER_API_KEY=your_key├── 📁 bot/

RAILWAY_STATIC_URL=https://your-app.up.railway.app

PORT=8000│   ├── main.py                   # Telegram bot initializationTELEGRAM_BOT_TOKEN=your_telegram_bot_tokenOBSIDIAN_VAULT_PATH=./my-knowledge-library

```

│   ├── middleware.py             # Rate limiting & session management

### 3. **Access Your Knowledge Base**

- **Web Browser**: `https://your-app.up.railway.app/kb/`│   └── handlers/GEMINI_API_KEY=your_gemini_api_keyENABLE_BOOK_STRUCTURE=true

- **File Viewer**: `https://your-app.up.railway.app/view/category/file.md`

- **API Health**: `https://your-app.up.railway.app/health`│       └── video_handler.py      # Video processing workflow



## 🔧 Supported Platforms├── 🔧 services/OPENROUTER_API_KEY=your_openrouter_api_key```creates beautiful, searchable knowledge bases.



| Platform | URL Format | Status |│   ├── gemini_service.py         # AI video analysis

|----------|------------|--------|

| **TikTok** | `tiktok.com/@user/video/...` | ✅ Supported |│   ├── claude_service.py         # Content enrichment```

| **Instagram** | `instagram.com/p/...` | ✅ Supported |

| **Instagram Reels** | `instagram.com/reel/...` | ✅ Supported |│   └── railway_client.py         # Video download service



## 📱 Usage Workflow├── 💾 storage/## ✨ Features



1. **Start Bot**: Send `/start` to initialize│   ├── railway_storage.py        # Railway persistent files

2. **Send URL**: Share a TikTok or Instagram video URL

3. **Processing**: Bot downloads and analyzes (progress updates shown)│   ├── notion_storage.py         # Notion database integration### Optional Services

4. **Review**: Get analysis summary with quality score

5. **Approve/Reject**: Use ✅ Approve, ❌ Reject, or 🔄 Re-analyze buttons│   └── markdown_storage.py       # Local markdown storage

6. **Access Content**: Get Railway URL for immediate web access

└── 🛠️ utils/```env### 🎥 **Smart Video Processing**

## 🚨 Troubleshooting

    └── retry_utils.py            # Retry logic with exponential backoff

### Common Issues

```# Railway video download service- Downloads from TikTok & Instagram URLs

#### ❌ Gemini API Errors

```

404 Model not found: projects/generativelanguage-ga/...

```## 🎯 How It WorksRAILWAY_API_URL=https://your-railway-service.up.railway.app- Handles multiple video formats automatically

**Solution**: Use correct model names

```env

GEMINI_MODEL=gemini-1.5-flash  # ✅ Correct

GEMINI_MODEL=gemini-1.5-pro    # ✅ Correct1. **📱 Send Video URL** → User sends TikTok/Instagram video URL- Railway.app integration for reliable downloading

```

2. **📥 Download Video** → Railway service downloads the video file

#### ❌ OpenRouter API Errors

**Check**: 3. **🧠 AI Analysis** → Gemini analyzes content and extracts insights# Notion database integration

- API key is valid at [OpenRouter](https://openrouter.ai)

- Account has sufficient credits4. **✅ Preview & Approval** → Interactive preview with approve/reject buttons

- Model name is correct: `anthropic/claude-3.5-sonnet`

5. **📝 Content Generation** → Claude creates comprehensive educational contentNOTION_API_KEY=your_notion_api_key### 🧠 **Advanced AI-Powered Analysis**

#### ❌ Video Download Failures

**TikTok videos may fail initially** - this is normal behavior. The bot automatically retries failed downloads.6. **💾 Save Results** → Store in Railway files with web access + optional Notion backup



#### ❌ Memory IssuesNOTION_DATABASE_ID=your_database_id- **Google Gemini 1.5 Pro** - Comprehensive video content analysis with 20+ data fields

**Fixed in latest version**:

- Session TTL management (30-minute expiration)## 📊 Output Examples

- Background cleanup tasks

- Proper async processingUSE_NOTION_STORAGE=true- **Claude 3.5 Sonnet** - Textbook-quality content generation (2500-4000 words)



## 🔒 Production Features### Markdown Files



### Security & Reliability```markdown- **Gemini 2.5 Flash Image Preview** - AI-generated technical diagrams and illustrations

- ✅ **Rate Limiting**: 10 videos per user per hour

- ✅ **Session Management**: TTL-based cleanup prevents memory leaks---

- ✅ **Retry Logic**: Exponential backoff for API failures

- ✅ **Error Recovery**: Comprehensive error handling and user feedbacktitle: "Advanced Python AsyncIO Patterns"# Image generation- Extracts category confidence, visual concepts, code snippets, performance metrics



### Quality Controldate: "2024-01-15T10:30:00"

- ✅ **Realistic Quality Scores**: Capped at 60-90% range

- ✅ **Content Validation**: Interactive approval workflowsource_url: "https://tiktok.com/@user/video/123"ENABLE_IMAGE_GENERATION=true

- ✅ **Honest Features**: No fake capabilities or impossible metrics

platform: "tiktok"

### Performance

- ✅ **Non-blocking Processing**: Multiple users can process simultaneouslycategory: "programming"IMAGE_MODEL=black-forest-labs/flux-1.1-pro### 📚 **Professional Reference Material**

- ✅ **Service Singleton Pattern**: Efficient resource usage

- ✅ **Persistent Storage**: Railway files survive deploymentstools: ["Python", "AsyncIO", "aiohttp"]



## 📝 Configuration Referencetags: ["python", "async", "performance"]```- **Textbook-Quality Content**: Comprehensive 3000+ word technical documentation



| Variable | Description | Default | Required |quality_score: 85

|----------|-------------|---------|----------|

| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | - | ✅ |---- **AI-Generated Diagrams**: Up to 3 technical illustrations per entry

| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |

| `OPENROUTER_API_KEY` | OpenRouter API key | - | ✅ |

| `CLAUDE_MODEL` | Claude model via OpenRouter | `anthropic/claude-3.5-sonnet` | ❌ |

| `RAILWAY_STATIC_URL` | Railway app URL | - | 🚀 Railway |# Advanced Python AsyncIO Patterns## 🏗️ Project Structure- **Advanced Categorization**: Confidence scoring and auto-review flagging

| `KNOWLEDGE_BASE_PATH` | Storage directory | `/app/knowledge_base` | ❌ |

| `USE_NOTION_STORAGE` | Enable Notion backup | `false` | ❌ |

| `MAX_VIDEOS_PER_HOUR` | Rate limit per user | `10` | ❌ |

| `TARGET_CONTENT_LENGTH` | Target word count | `2500` | ❌ |## Overview- **Multiple Storage Options**: Notion database, Obsidian books, or markdown files



## 🤝 ContributingComprehensive guide to modern asynchronous programming in Python...



1. **Fork** the repository```- **Cost Tracking**: Token usage monitoring and pricing analytics

2. **Create** a feature branch: `git checkout -b feature/amazing-feature`

3. **Commit** changes: `git commit -m 'Add amazing feature'`## Key Concepts

4. **Push** to branch: `git push origin feature/amazing-feature`

5. **Submit** a Pull Request- Event loops and coroutinesKnowledge-Bot/



## 📄 License- Error handling in async code



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.- Performance optimization techniques├── app.py                      # Main entry point### 🎨 **New: AI-Generated Technical Diagrams**



## 🆘 Support



- **🐛 Bug Reports**: [GitHub Issues](https://github.com/silvioiatech/Knowledge-Bot/issues)## Tools & Technologies├── config.py                   # Configuration management- **Gemini 2.5 Flash Image Preview** creates professional technical illustrations

- **💡 Feature Requests**: [GitHub Discussions](https://github.com/silvioiatech/Knowledge-Bot/discussions)

- **📧 Questions**: Check existing issues or start a new discussion- **Python AsyncIO**: Core async framework



## 🌟 Acknowledgments- **aiohttp**: Async HTTP client/server├── requirements.txt            # Dependencies- Automatically detects diagram opportunities in content



- **Google Gemini**: AI video analysis capabilities- **asyncpg**: Async PostgreSQL driver

- **Anthropic Claude**: Content enrichment via OpenRouter

- **Railway**: Reliable cloud deployment and persistent storage├── .env.example               # Environment template- Generates: flowcharts, system architectures, process diagrams, UI mockups

- **aiogram**: Excellent Telegram bot framework

## Practical Examples

---

[Code examples and implementation details...]├── bot/- Embedded directly into textbook-quality content with proper captions

**Star ⭐ this repository if you find it useful!**


## Additional Resources│   ├── main.py                # Bot initialization

- [Official AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

- [Real Python AsyncIO Guide](https://realpython.com/async-io-python/)│   ├── middleware.py          # Rate limiting & logging### 📊 **Enhanced Analytics & Quality Control**

```

│   └── handlers/- **Category Confidence Scoring**: Auto-flags uncertain classifications for review

### Railway Web Access

- **Browse Categories**: `https://your-app.up.railway.app/kb/`│       └── video_handler.py   # Video processing workflow- **Content Quality Metrics**: Tracks comprehensive analysis depth (20+ fields)

- **View Files**: `https://your-app.up.railway.app/view/programming/asyncio-patterns.md`

- **Download Raw**: `https://your-app.up.railway.app/raw/programming/asyncio-patterns.md`├── services/- **Cost Analytics**: Real-time token usage and pricing with OpenRouter integration



## 🚀 Railway Deployment│   ├── railway_client.py      # Video download service- **Dynamic Category Management**: Learns and adapts categorization over time



### 1. **Setup Railway**│   ├── gemini_service.py      # AI video analysis

```bash

# Install Railway CLI│   ├── claude_service.py      # Content enrichment### 🔒 **Privacy & Control**

npm install -g @railway/cli

│   └── image_generation_service.py # Diagram generation- Interactive approval system - you control what gets saved

# Login and deploy

railway login├── storage/- Private repository integration for personal knowledge

railway link

railway add volume --name knowledge-base --mount /app/knowledge_base│   ├── markdown_storage.py    # Markdown file management- Rate limiting and user management

railway deploy

```│   └── notion_storage.py      # Notion database integration- Local or cloud storage options



### 2. **Environment Variables**└── core/models/

Set in Railway dashboard:

```env    └── content_models.py      # Data models### 📱 **Multi-Platform Access**

TELEGRAM_BOT_TOKEN=your_token

GEMINI_API_KEY=your_key```- Works with any Markdown editor

OPENROUTER_API_KEY=your_key

RAILWAY_STATIC_URL=https://your-app.up.railway.app- Obsidian mobile app support

PORT=8000

```## 🎯 How It Works- GitHub integration for sync across devices



### 3. **Access Your Knowledge Base**

- **Web Browser**: `https://your-app.up.railway.app/kb/`

- **File Viewer**: `https://your-app.up.railway.app/view/category/file.md`1. **Send Video URL** → Bot receives TikTok/Instagram video URL## 🏗️ Project Structure

- **API Health**: `https://your-app.up.railway.app/health`

2. **Download Video** → Railway service downloads the video file

## 🔧 Supported Platforms

3. **AI Analysis** → Gemini analyzes video content and extracts insights```

| Platform | URL Format | Status |

|----------|------------|--------|4. **Preview & Approval** → Interactive preview with approve/reject optionsKnowledge-Bot/

| **TikTok** | `tiktok.com/@user/video/...` | ✅ Supported |

| **Instagram** | `instagram.com/p/...` | ✅ Supported |5. **Content Generation** → Claude creates comprehensive educational content├── 📁 bot/

| **Instagram Reels** | `instagram.com/reel/...` | ✅ Supported |

6. **Save Results** → Store in Markdown files and/or Notion database│   ├── main.py              # aiogram bot initialization

## 📱 Usage Workflow

│   └── handlers/

1. **Start Bot**: Send `/start` to initialize

2. **Send URL**: Share a TikTok or Instagram video URL## 🔧 Supported Platforms│       └── video_handler.py # Video processing workflow

3. **Processing**: Bot downloads and analyzes (progress updates shown)

4. **Review**: Get analysis summary with quality score├── 📁 services/

5. **Approve/Reject**: Use ✅ Approve, ❌ Reject, or 🔄 Re-analyze buttons

6. **Access Content**: Get Railway URL for immediate web access- **TikTok**: `tiktok.com/@user/video/...`│   ├── railway_client.py           # Video download service  



## 🚨 Troubleshooting- **Instagram**: `instagram.com/p/...` and `instagram.com/reel/...`│   ├── gemini_service.py           # Comprehensive AI video analysis



### Common Issues│   ├── claude_service.py           # Textbook-quality content generation



#### ❌ Gemini API Errors## 📊 Output Examples│   ├── image_generation_service.py # AI-powered technical diagrams

```

404 Model not found: projects/generativelanguage-ga/...│   └── git_sync.py                 # GitHub integration

```

**Solution**: Use correct model names### Markdown Files├── 📁 storage/

```env

GEMINI_MODEL=gemini-1.5-flash  # ✅ Correct```markdown│   ├── markdown_storage.py  # Simple markdown files

GEMINI_MODEL=gemini-1.5-pro    # ✅ Correct

```# Advanced Python AsyncIO Patterns│   ├── book_storage.py      # Obsidian book format



#### ❌ OpenRouter API Errors│   └── notion_storage.py    # Notion database integration

**Check**: 

- API key is valid at [OpenRouter](https://openrouter.ai)## Overview├── ⚙️ config.py             # Configuration management

- Account has sufficient credits

- Model name is correct: `anthropic/claude-3.5-sonnet`Learn modern asynchronous programming patterns...├── 🚀 app.py               # Main application entry



#### ❌ Video Download Failures└── 📖 PRIVATE_REPOSITORY_SETUP.md  # Setup guide

**TikTok videos may fail initially** - this is normal behavior. The bot automatically retries failed downloads.

## Key Concepts│   └── claude_service.py    # Claude content enrichment

#### ❌ Memory Issues

**Fixed in latest version**:- Event loops and coroutines├── storage/

- Session TTL management (30-minute expiration)

- Background cleanup tasks- Error handling in async code│   └── markdown_storage.py  # Markdown file management

- Proper async processing

- Performance optimization techniques├── config.py                # Configuration & environment

## 🔒 Production Features

├── run_bot.py              # Main entry point

### Security & Reliability

- ✅ **Rate Limiting**: 10 videos per user per hour## Tools & Technologies└── knowledge_base/          # Generated knowledge base

- ✅ **Session Management**: TTL-based cleanup prevents memory leaks

- ✅ **Retry Logic**: Exponential backoff for API failures- Python AsyncIO    ├── artificial-intelligence/

- ✅ **Error Recovery**: Comprehensive error handling and user feedback

- aiohttp    ├── development/

### Quality Control

- ✅ **Realistic Quality Scores**: Capped at 60-90% range- asyncpg    ├── design/

- ✅ **Content Validation**: Interactive approval workflow

- ✅ **Honest Features**: No fake capabilities or impossible metrics```    └── ...



### Performance```

- ✅ **Non-blocking Processing**: Multiple users can process simultaneously

- ✅ **Service Singleton Pattern**: Efficient resource usage### Notion Database

- ✅ **Persistent Storage**: Railway files survive deployments

Automatically creates entries with:## 🚀 Quick Start

## 📝 Configuration Reference

- Title, Category, Tags

| Variable | Description | Default | Required |

|----------|-------------|---------|----------|- Content Quality Score### 1. Installation

| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | - | ✅ |

| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |- Word Count, Processing Date

| `OPENROUTER_API_KEY` | OpenRouter API key | - | ✅ |

| `CLAUDE_MODEL` | Claude model via OpenRouter | `anthropic/claude-3.5-sonnet` | ❌ |- Key Points, Tools Used```bash

| `RAILWAY_STATIC_URL` | Railway app URL | - | 🚀 Railway |

| `KNOWLEDGE_BASE_PATH` | Storage directory | `/app/knowledge_base` | ❌ |- Source URL and Platform# Clone repository

| `USE_NOTION_STORAGE` | Enable Notion backup | `false` | ❌ |

| `MAX_VIDEOS_PER_HOUR` | Rate limit per user | `10` | ❌ |git clone https://github.com/silvioiatech/Knowledge-Bot.git

| `TARGET_CONTENT_LENGTH` | Target word count | `2500` | ❌ |

## 🚨 Troubleshootingcd Knowledge-Bot

## 🤝 Contributing



1. **Fork** the repository

2. **Create** a feature branch: `git checkout -b feature/amazing-feature`### Common Issues# Install dependencies

3. **Commit** changes: `git commit -m 'Add amazing feature'`

4. **Push** to branch: `git push origin feature/amazing-feature`pip install -r requirements.txt

5. **Submit** a Pull Request

**❌ "Gemini API Error: Model not found"**```

## 📄 License

```env

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Use correct model name### 2. Configuration

## 🆘 Support

GEMINI_MODEL=gemini-1.5-flash

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/silvioiatech/Knowledge-Bot/issues)

- **💡 Feature Requests**: [GitHub Discussions](https://github.com/silvioiatech/Knowledge-Bot/discussions)``````bash

- **📧 Questions**: Check existing issues or start a new discussion

# Copy environment template

## 🌟 Acknowledgments

**❌ "OpenRouter API Error"**cp .env.example .env

- **Google Gemini**: AI video analysis capabilities

- **Anthropic Claude**: Content enrichment via OpenRouter- Check your API key at [OpenRouter](https://openrouter.ai)

- **Railway**: Reliable cloud deployment and persistent storage

- **aiogram**: Excellent Telegram bot framework- Verify you have credits available# Edit .env with your API keys



---- Ensure model name is correct (e.g., `anthropic/claude-3.5-sonnet`)nano .env



**Star ⭐ this repository if you find it useful!**```

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