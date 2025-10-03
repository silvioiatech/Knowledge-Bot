#!/bin/bash

# Knowledge Bot - Quick Start Script
# This script helps you set up and run the Knowledge Bot

set -e

echo "🤖 Knowledge Bot - Quick Start"
echo "=============================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo -e "${BLUE}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file with your API keys before continuing${NC}"
    echo ""
    echo "Required API keys:"
    echo "  1. TELEGRAM_BOT_TOKEN - Get from @BotFather on Telegram"
    echo "  2. GEMINI_API_KEY - Get from https://makersuite.google.com/app/apikey"
    echo "  3. OPENROUTER_API_KEY - Get from https://openrouter.ai/"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Check if required directories exist
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p logs
mkdir -p /tmp/knowledge_bot
mkdir -p knowledge_base
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Check if dependencies are installed
echo -e "${BLUE}Checking dependencies...${NC}"
if python3 -c "import aiogram" 2>/dev/null; then
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
else
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    python3 -m pip install -r requirements.txt --user --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi
echo ""

# Validate configuration
echo -e "${BLUE}Validating configuration...${NC}"
if python3 -c "
from config import Config
try:
    Config.validate()
    print('Configuration valid')
    exit(0)
except ValueError as e:
    print(f'Configuration error: {e}')
    exit(1)
" 2>&1 | grep -q "Configuration valid"; then
    echo -e "${GREEN}✅ Configuration validated${NC}"
else
    echo -e "${RED}❌ Configuration validation failed${NC}"
    echo ""
    echo "Please check your .env file and ensure these are set:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - GEMINI_API_KEY"
    echo "  - OPENROUTER_API_KEY"
    exit 1
fi
echo ""

# Test imports
echo -e "${BLUE}Testing imports...${NC}"
if python3 -c "
from bot.main import KnowledgeBot
from services.railway_client import RailwayClient
from services.gemini_service import EnhancedGeminiService
print('Imports successful')
" 2>/dev/null | grep -q "Imports successful"; then
    echo -e "${GREEN}✅ All imports successful${NC}"
else
    echo -e "${RED}❌ Import test failed${NC}"
    echo "Please check the error messages above"
    exit 1
fi
echo ""

# Display configuration summary
echo -e "${BLUE}Configuration Summary:${NC}"
python3 -c "
from config import Config
import os

print(f'  • Bot Token: {'*' * 20}{Config.TELEGRAM_BOT_TOKEN[-4:] if Config.TELEGRAM_BOT_TOKEN else 'Not set'}')
print(f'  • Gemini Model: {Config.GEMINI_MODEL}')
print(f'  • Claude Model: {Config.CLAUDE_MODEL}')
print(f'  • GPT Model: {Config.GPT_MODEL}')
print(f'  • Image Generation: {'Enabled' if Config.ENABLE_IMAGE_GENERATION else 'Disabled'}')
print(f'  • GPT Finalizer: {'Enabled' if Config.USE_GPT_FINALIZER else 'Disabled'}')
print(f'  • Notion Storage: {'Enabled' if Config.USE_NOTION_STORAGE else 'Disabled'}')
print(f'  • Knowledge Base: {Config.KNOWLEDGE_BASE_PATH}')
"
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}Starting Knowledge Bot...${NC}"
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python3 main.py
