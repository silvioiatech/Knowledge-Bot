#!/bin/bash

# Production Verification Script for Knowledge Bot
# This script verifies that the repository is production-ready

echo "🔍 Knowledge Bot - Production Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Directory: $1"
    else
        echo -e "${YELLOW}⚠${NC} Missing directory: $1 (will be auto-created)"
        ((WARNINGS++))
    fi
}

echo "📁 Checking Core Files..."
echo "------------------------"
check_file "main.py"
check_file "config.py"
check_file "requirements.txt"
check_file ".env.example"
check_file "README.md"
echo ""

echo "🤖 Checking Bot Components..."
echo "----------------------------"
check_file "bot/main.py"
check_file "bot/middleware.py"
check_file "bot/handlers/video_handler.py"
check_file "bot/interactive_category_system.py"
echo ""

echo "🧠 Checking AI Services..."
echo "-------------------------"
check_file "services/gemini_service.py"
check_file "services/enhanced_claude_service.py"
check_file "services/gpt_service.py"
check_file "services/railway_client.py"
check_file "services/image_generation_service.py"
echo ""

echo "💾 Checking Storage Systems..."
echo "-----------------------------"
check_file "storage/markdown_storage.py"
check_file "storage/notion_storage.py"
echo ""

echo "📊 Checking Data Models..."
echo "-------------------------"
check_file "core/models/content_models.py"
echo ""

echo "🛠️ Checking Utilities..."
echo "------------------------"
check_file "utils/retry_utils.py"
echo ""

echo "📚 Checking Documentation..."
echo "---------------------------"
check_file "README.md"
check_file "CONTRIBUTING.md"
check_file "LICENSE"
echo ""

echo "🚀 Checking Deployment Files..."
echo "------------------------------"
check_file "Dockerfile"
check_file "Procfile"
check_file "railway.toml"
check_file "runtime.txt"
echo ""

echo "⚙️ Checking Configuration Files..."
echo "---------------------------------"
check_file ".gitignore"
check_file ".gitattributes"
check_file "pyproject.toml"
echo ""

echo "📁 Checking Directories..."
echo "-------------------------"
check_dir "bot"
check_dir "services"
check_dir "storage"
check_dir "core/models"
check_dir "utils"
check_dir "knowledge_base"
check_dir "logs"
echo ""

echo "🔐 Checking Security..."
echo "----------------------"
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} Warning: .env file exists (should not be committed)"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} No .env file in repository (correct)"
fi

if grep -q "your_.*_here" .env.example 2>/dev/null; then
    echo -e "${GREEN}✓${NC} .env.example has placeholder values"
else
    echo -e "${YELLOW}⚠${NC} .env.example might have real API keys"
    ((WARNINGS++))
fi
echo ""

echo "📦 Checking Python Dependencies..."
echo "---------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"

    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python version >= 3.8"
    else
        echo -e "${RED}✗${NC} Python version < 3.8 (required: 3.8+)"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Python not found"
    ((ERRORS++))
fi
echo ""

echo "📊 Repository Statistics..."
echo "--------------------------"
PY_FILES=$(find . -name "*.py" -not -path '*/\.*' | wc -l | tr -d ' ')
MD_FILES=$(find . -name "*.md" -not -path '*/\.*' | wc -l | tr -d ' ')
echo -e "${GREEN}✓${NC} Python files: $PY_FILES"
echo -e "${GREEN}✓${NC} Documentation files: $MD_FILES"
echo ""

echo "=========================================="
echo "📋 Verification Summary"
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ PRODUCTION READY!${NC}"
    echo "All checks passed. Repository is ready for deployment."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ WARNINGS: $WARNINGS${NC}"
    echo "Repository is functional but has warnings."
    exit 0
else
    echo -e "${RED}❌ ERRORS: $ERRORS${NC}"
    echo -e "${YELLOW}⚠ WARNINGS: $WARNINGS${NC}"
    echo "Please fix errors before deployment."
    exit 1
fi
