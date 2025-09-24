# Configuration Migration Guide

## Summary of Changes

This update introduces several important configuration changes to make the bot more flexible and use OpenRouter instead of direct Anthropic API access.

## 🔄 What Changed

### 1. **Railway API Key Now Optional**
- **Before**: `RAILWAY_API_KEY` was required
- **After**: `RAILWAY_API_KEY` is optional (Railway yt-dlp doesn't require authentication)
- **Migration**: You can leave `RAILWAY_API_KEY` empty in your `.env` file

### 2. **Configurable AI Models** 
- **Before**: Hardcoded model names (`gemini-1.5-flash`, `claude-3-haiku`)
- **After**: Configurable via environment variables
- **New Variables**:
  - `GEMINI_MODEL=gemini-2.0-flash-exp` (default)
  - `OPENROUTER_MODEL=anthropic/claude-3.5-sonnet` (default)

### 3. **OpenRouter Instead of Direct Anthropic**
- **Before**: Direct Anthropic API via `anthropic` package
- **After**: OpenRouter API for Claude access
- **Benefits**: 
  - Access to multiple Claude models
  - Better rate limiting
  - Unified billing
  - No need for separate Anthropic API key

## 📝 Required .env Changes

### Old Configuration:
```bash
# Old .env
TELEGRAM_BOT_TOKEN=your_bot_token
RAILWAY_API_URL=https://your-app.up.railway.app
RAILWAY_API_KEY=your_api_key_here          # Was required
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key       # Replace this
```

### New Configuration:
```bash
# New .env
TELEGRAM_BOT_TOKEN=your_bot_token
RAILWAY_API_URL=https://your-app.up.railway.app
RAILWAY_API_KEY=                           # Optional now
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.0-flash-exp          # New: configurable model
OPENROUTER_API_KEY=your_openrouter_key     # New: replaces ANTHROPIC_API_KEY
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # New: configurable Claude model
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## 🚀 Migration Steps

### 1. Get OpenRouter API Key
1. Go to [OpenRouter](https://openrouter.ai)
2. Create account or sign in
3. Generate API key
4. Add credits to your account

### 2. Update Dependencies
```bash
pip install -r requirements.txt  # anthropic package removed
```

### 3. Update .env File
```bash
# Copy new template
cp .env.example .env.new

# Edit with your values
nano .env.new

# Backup old config and switch
mv .env .env.backup
mv .env.new .env
```

### 4. Test Configuration
```bash
python run_bot.py
```

## 🎛️ Available Models

### Gemini Models
- `gemini-2.0-flash-exp` (default) - Latest experimental model
- `gemini-1.5-pro` - Production ready, more capable
- `gemini-1.5-flash` - Faster, good for most tasks

### Claude Models (via OpenRouter)
- `anthropic/claude-3.5-sonnet` (default) - Best balance
- `anthropic/claude-3-haiku` - Faster, cheaper
- `anthropic/claude-3-opus` - Most capable, expensive
- `anthropic/claude-3.5-haiku` - Latest fast model

## 🔍 Validation Checklist

- [ ] OpenRouter API key added to `.env`
- [ ] `OPENROUTER_MODEL` configured
- [ ] `GEMINI_MODEL` configured (optional)
- [ ] Railway API key removed or left empty
- [ ] Bot starts without errors
- [ ] Video analysis works end-to-end
- [ ] Content enrichment works with chosen Claude model

## 🆘 Troubleshooting

### "OPENROUTER_API_KEY not configured"
- Check your `.env` file has `OPENROUTER_API_KEY=sk-...`
- Restart the bot after adding the key

### "Model not found" errors
- Verify model name spelling in `OPENROUTER_MODEL`
- Check [OpenRouter models](https://openrouter.ai/models) for available options
- Ensure your OpenRouter account has credits

### Railway download issues
- If Railway URL is configured but API key empty, that's OK
- If you get auth errors, add a Railway API key or use alternative download method

## 💰 Cost Implications

### Before (Direct APIs):
- Anthropic API: $15/MTok (Claude 3.5 Sonnet)
- Google AI: $3.5/MTok (Gemini Pro)

### After (OpenRouter):
- Claude 3.5 Sonnet: ~$3/MTok (lower cost!)
- Gemini models: Similar pricing
- **Benefits**: Unified billing, better rate limits

## 🔄 Rollback Plan

If you need to rollback:
1. Restore `.env.backup`
2. Add `anthropic==0.25.0` back to `requirements.txt`
3. Install: `pip install anthropic==0.25.0`
4. Restart bot

The old configuration will continue to work until you're ready to migrate.