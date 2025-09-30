# 🔍 Knowledge Bot Verification Guide

## Step-by-Step Testing Instructions

### ✅ STEP 1: Syntax Validation (5 minutes)

Open your terminal and navigate to your project:

```bash
cd /Users/silvio/Documents/GitHub/Knowledge-Bot
```

#### A. Check Python Syntax

```bash
# Test each critical file for syntax errors
python3 -m py_compile bot/handlers/video_handler.py
python3 -m py_compile services/gemini_service.py
python3 -m py_compile services/enhanced_claude_service.py
python3 -m py_compile services/claude_service.py
python3 -m py_compile bot/interactive_category_system.py
python3 -m py_compile config.py
python3 -m py_compile main.py
```

**Expected output:** No output = Success! ✅  
**If errors:** You'll see line numbers and error descriptions

#### B. Quick Code Quality Check (Optional)

```bash
# Install pylint if you don't have it
pip3 install pylint

# Check code quality (you can ignore style warnings for now)
pylint bot/handlers/video_handler.py --disable=C0111,C0103,C0301
```

---

### ✅ STEP 2: Environment Setup (2 minutes)

#### A. Check .env File

Make sure you have a `.env` file with all required variables:

```bash
# View your .env file (sensitive info will be hidden)
cat .env | grep -E "TELEGRAM_BOT_TOKEN|GEMINI_API_KEY|OPENROUTER_API_KEY|NOTION"
```

**Required variables:**
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `GEMINI_API_KEY` - Google Gemini API key
- `OPENROUTER_API_KEY` - OpenRouter API key for Claude
- `NOTION_API_KEY` - Notion integration token
- `NOTION_DATABASE_ID` - Your Notion database ID

#### B. Create .env Template (if needed)

```bash
cat > .env.example << 'EOF'
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CHAT_ID=your_telegram_chat_id

# AI Services
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Notion Storage
NOTION_API_KEY=your_notion_integration_token_here
NOTION_DATABASE_ID=your_database_id_here
USE_NOTION_STORAGE=true

# Railway Download Service (Optional)
RAILWAY_API_URL=https://railway-yt-dlp-service-production.up.railway.app
RAILWAY_API_KEY=your_railway_api_key
RAILWAY_STATIC_URL=https://your-app.up.railway.app

# Model Configuration
GEMINI_MODEL=gemini-2.5-pro
CLAUDE_MODEL=anthropic/claude-3.5-sonnet
GPT_MODEL=openai/gpt-4
IMAGE_MODEL=black-forest-labs/flux-1.1-pro

# Processing Settings
TARGET_CONTENT_LENGTH=2500
ENABLE_IMAGE_GENERATION=true
MAX_PROCESSING_TIME=1800
EOF
```

---

### ✅ STEP 3: Install Dependencies (2 minutes)

```bash
# Make sure all required packages are installed
pip3 install -r requirements.txt

# Or install individually:
pip3 install aiogram loguru httpx python-dotenv google-generativeai python-magic
```

---

### ✅ STEP 4: Test Bot Startup (1 minute)

#### A. Dry Run Test

```bash
# Test if the bot starts without errors
python3 main.py
```

**What to look for:**
- ✅ `✅ Configuration validated successfully`
- ✅ `✅ Bot setup completed successfully`
- ✅ `🤖 Enhanced Knowledge Bot started: @YourBotName`
- ✅ `📡 Starting bot polling...`

**Press Ctrl+C to stop** when you see these messages.

#### B. Check Logs

```bash
# View logs for any errors
cat logs/knowledge_bot.log
```

---

### ✅ STEP 5: End-to-End Testing (10 minutes)

Now let's test the complete workflow:

#### Test Scenario 1: Basic Video Processing

1. **Start your bot:**
   ```bash
   python3 main.py
   ```

2. **Open Telegram** and find your bot

3. **Send the /start command**
   - You should see the welcome message with features listed

4. **Send a TikTok video URL** (example):
   ```
   https://www.tiktok.com/@username/video/1234567890
   ```

5. **Watch the processing stages:**
   - ✅ "📥 Downloading video..."
   - ✅ "🤖 Analyzing content with AI..."
   - ✅ "🔍 Generating preview..."
   - ✅ Should show preview with three buttons:
     - "✅ Add to Knowledge Base"
     - "❌ Reject"
     - "🔄 Re-analyze with Different Focus"

6. **Click "✅ Add to Knowledge Base"**
   - Should show category selection keyboard
   - Choose a category (e.g., "🤖 AI")
   - Choose a subcategory (e.g., "Tools")

7. **Wait for processing:**
   - ✅ "✨ Generating enhanced educational content..."
   - ✅ "🎨 Evaluating image generation necessity..."
   - ✅ "📊 Preparing database entry..."
   - ✅ "💾 Saving to knowledge base..."

8. **Final result:**
   - ✅ Should show complete entry details
   - ✅ Should have a Notion link (if configured)
   - ✅ Entry should appear in your Notion database

#### Test Scenario 2: Session Cleanup

1. **After processing a video**, wait 5 minutes

2. **Send another video URL** - should work fine

3. **Check logs for session cleanup:**
   ```bash
   grep "Cleaned up expired" logs/knowledge_bot.log
   ```

#### Test Scenario 3: Error Handling

1. **Test invalid URL:**
   ```
   https://example.com/invalid-video
   ```
   - Should see: "❌ Please send a valid TikTok or Instagram video URL"

2. **Test private/unavailable video:**
   - Send a private TikTok URL
   - Should see: "❌ Failed to download video..."

---

### ✅ STEP 6: Code Organization Fix (Optional)

I noticed the global variables `markdown_storage`, `notion_storage`, and `railway_storage` are declared at line 77 in `video_handler.py`, but they should be with the other service variables at the top.

**To fix:**

```bash
# Open the file
nano bot/handlers/video_handler.py

# Or use your preferred editor:
code bot/handlers/video_handler.py  # VS Code
vim bot/handlers/video_handler.py   # Vim
```

**Move these lines** (currently around line 77):
```python
markdown_storage = None
notion_storage = None
railway_storage = None
```

**To be with the other service variables** (around line 24):
```python
# Service instances - initialized lazily
railway_client = None
gemini_service = None
claude_service = None
image_service = None
markdown_storage = None  # ← ADD HERE
notion_storage = None     # ← ADD HERE
railway_storage = None    # ← ADD HERE
```

**Then delete the duplicates at line 77**.

---

### 🐛 TROUBLESHOOTING

#### Issue: "ModuleNotFoundError"
```bash
# Solution: Install missing package
pip3 install [package-name]
```

#### Issue: "Configuration validation failed"
```bash
# Solution: Check your .env file has all required variables
cat .env
```

#### Issue: "Failed to download video"
```bash
# Check Railway service is running
# Check RAILWAY_API_URL and RAILWAY_API_KEY are correct
```

#### Issue: "Notion API error"
```bash
# Check NOTION_API_KEY is valid
# Check NOTION_DATABASE_ID matches your database
# Verify integration has access to the database
```

#### Issue: Bot doesn't respond
```bash
# Check bot token is correct
# Check bot is polling (should see "Starting bot polling..." in logs)
# Check Telegram for bot messages
```

---

### 📊 MONITORING CHECKLIST

After deployment, monitor these:

```bash
# Watch logs in real-time
tail -f logs/knowledge_bot.log

# Check session cleanup is running
grep "Session cleanup task started" logs/knowledge_bot.log

# Check for errors
grep "ERROR" logs/knowledge_bot.log

# Check for memory leaks (run this periodically)
ps aux | grep python3 | grep main.py
```

---

### ✅ SUCCESS CRITERIA

Your bot is ready for production when:

- [x] All Python files compile without syntax errors
- [x] Bot starts and connects to Telegram successfully
- [x] Can process a test video end-to-end
- [x] Interactive category selection works
- [x] Entry appears in Notion database
- [x] Session cleanup task is running
- [x] No errors in logs after test run
- [x] Resources are being cleaned up (check logs)

---

### 🚀 PRODUCTION DEPLOYMENT

Once all tests pass:

```bash
# Run in production mode
nohup python3 main.py > bot.log 2>&1 &

# Or use a process manager like systemd, supervisord, or pm2

# Check it's running
ps aux | grep main.py

# View logs
tail -f bot.log
```

---

### 📞 NEED HELP?

If you encounter issues:

1. **Check logs first:** `cat logs/knowledge_bot.log`
2. **Verify config:** `python3 -c "from config import Config; Config.validate()"`
3. **Test individual services:** Create a test script for each service
4. **Enable debug logging:** Set log level to DEBUG in main.py

---

## 🎯 QUICK TEST COMMAND

Run all checks at once:

```bash
#!/bin/bash
echo "🔍 Running Knowledge Bot Verification..."
echo ""

echo "1️⃣ Syntax Check..."
python3 -m py_compile bot/handlers/video_handler.py && echo "✅ video_handler.py" || echo "❌ video_handler.py FAILED"
python3 -m py_compile services/gemini_service.py && echo "✅ gemini_service.py" || echo "❌ gemini_service.py FAILED"
python3 -m py_compile services/enhanced_claude_service.py && echo "✅ enhanced_claude_service.py" || echo "❌ enhanced_claude_service.py FAILED"

echo ""
echo "2️⃣ Config Check..."
python3 -c "from config import Config; Config.validate()" && echo "✅ Configuration valid" || echo "❌ Configuration FAILED"

echo ""
echo "3️⃣ Import Check..."
python3 -c "from main import main; print('✅ All imports successful')" || echo "❌ Import FAILED"

echo ""
echo "✅ Verification complete! If all checks passed, run: python3 main.py"
```

Save this as `verify.sh`, make it executable, and run:

```bash
chmod +x verify.sh
./verify.sh
```

---

**Good luck! Your bot is almost ready to go! 🚀**
