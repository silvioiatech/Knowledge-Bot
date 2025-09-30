# 🤖 Knowledge Bot

AI-powered Telegram bot that transforms social media videos into educational content with Notion integration.

## Features

- 🎥 Video analysis with Google Gemini 2.5 Pro
- 🧠 Educational content generation with Claude 3.5 Sonnet
- 🎨 Smart image generation when valuable
- 📊 Automatic Notion database integration
- 🏷️ Interactive category selection
- ⚡ Async, non-blocking architecture

## Quick Start

### Prerequisites

- Python 3.11+
- API Keys: Telegram, Gemini, OpenRouter, Notion

### Installation

```bash
git clone https://github.com/yourusername/Knowledge-Bot.git
cd Knowledge-Bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

## Deployment

### Railway

1. Connect GitHub repo to Railway
2. Set environment variables (see `.env.example`)
3. Deploy automatically on push

### Required Environment Variables

```bash
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-pro
OPENROUTER_API_KEY=your_key
CLAUDE_MODEL=anthropic/claude-3.5-sonnet
IMAGE_MODEL=google/gemini-2.5-flash-image-preview
NOTION_API_KEY=your_key
NOTION_DATABASE_ID=your_id
```

## Usage

1. Start chat with bot on Telegram
2. Send `/start`
3. Share TikTok or Instagram video URL
4. Approve analysis
5. Select category
6. Entry saved to Notion

## Architecture

```
bot/           - Telegram handlers
services/      - AI services (Gemini, Claude)
storage/       - Notion & Markdown storage
core/          - Data models
utils/         - Helper functions
```

## License

MIT License - see LICENSE file

---

Built with ❤️ using Google Gemini, Anthropic Claude, and Notion
