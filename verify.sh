#!/bin/bash

# Knowledge Bot Quick Verification Script
# This script checks if your bot is ready to run

echo "🔍 Knowledge Bot - Quick Verification"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        ((ERRORS++))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Step 1: Check Python version
echo "1️⃣ Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if python3 --version &> /dev/null; then
    print_status 0 "Python 3 installed: $(python3 --version)"
else
    print_status 1 "Python 3 not found"
fi
echo ""

# Step 2: Check syntax of critical files
echo "2️⃣ Checking Python syntax..."
FILES=(
    "bot/handlers/video_handler.py"
    "services/gemini_service.py"
    "services/enhanced_claude_service.py"
    "services/claude_service.py"
    "bot/interactive_category_system.py"
    "config.py"
    "main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            print_status 0 "$(basename $file)"
        else
            print_status 1 "$(basename $file) - SYNTAX ERROR"
        fi
    else
        print_warning "$(basename $file) - FILE NOT FOUND"
    fi
done
echo ""

# Step 3: Check environment variables
echo "3️⃣ Checking environment configuration..."
if [ -f ".env" ]; then
    print_status 0 ".env file exists"
    
    # Check for required variables
    REQUIRED_VARS=(
        "TELEGRAM_BOT_TOKEN"
        "GEMINI_API_KEY"
        "OPENROUTER_API_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env; then
            # Check if not empty
            value=$(grep "^${var}=" .env | cut -d'=' -f2)
            if [ ! -z "$value" ] && [ "$value" != "your_*" ]; then
                print_status 0 "$var is set"
            else
                print_warning "$var is empty or has placeholder value"
            fi
        else
            print_warning "$var not found in .env"
        fi
    done
else
    print_status 1 ".env file not found"
fi
echo ""

# Step 4: Check required dependencies
echo "4️⃣ Checking Python dependencies..."
REQUIRED_PACKAGES=(
    "aiogram"
    "loguru"
    "httpx"
    "google.generativeai"
    "dotenv"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import ${package}" 2>/dev/null; then
        print_status 0 "${package}"
    else
        print_warning "${package} - Not installed (run: pip3 install -r requirements.txt)"
    fi
done
echo ""

# Step 5: Check configuration validation
echo "5️⃣ Testing configuration validation..."
if python3 -c "from config import Config; Config.validate()" 2>/dev/null; then
    print_status 0 "Configuration validation passed"
else
    print_status 1 "Configuration validation failed - check your .env file"
fi
echo ""

# Step 6: Check import chain
echo "6️⃣ Testing import chain..."
if python3 -c "from main import main" 2>/dev/null; then
    print_status 0 "All imports successful"
else
    print_status 1 "Import chain broken - check for missing dependencies"
fi
echo ""

# Step 7: Check directory structure
echo "7️⃣ Checking directory structure..."
REQUIRED_DIRS=(
    "bot"
    "bot/handlers"
    "services"
    "storage"
    "core"
    "core/models"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status 0 "$dir/"
    else
        print_warning "$dir/ - Directory not found"
    fi
done
echo ""

# Final Summary
echo "===================================="
echo "📊 VERIFICATION SUMMARY"
echo "===================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Your bot is ready to run!${NC}"
    echo ""
    echo "To start your bot, run:"
    echo "  python3 main.py"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} warnings found (bot may still work)${NC}"
    echo ""
    echo "You can try running the bot:"
    echo "  python3 main.py"
    echo ""
    echo "Or fix warnings first by checking VERIFICATION_GUIDE.md"
else
    echo -e "${RED}❌ ${ERRORS} errors found - Please fix before running${NC}"
    echo ""
    echo "Fix errors using VERIFICATION_GUIDE.md, then run this script again"
fi

echo ""
echo "For detailed testing instructions, see: VERIFICATION_GUIDE.md"

exit $ERRORS
