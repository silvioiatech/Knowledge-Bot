# 🚀 Production Deployment Checklist

## ✅ **Pre-Deployment Verification**

### 1. **Environment Setup**
- [ ] Copy `.env.example` to `.env`
- [ ] Configure all required API keys
- [ ] Verify API quotas and billing setup
- [ ] Test local environment with `python -m config`

### 2. **Required API Keys**
- [ ] **Telegram Bot Token**: Create with [@BotFather](https://t.me/botfather)
- [ ] **Google Gemini API**: Get from [Google AI Studio](https://aistudio.google.com)
- [ ] **OpenRouter API**: Get from [OpenRouter](https://openrouter.ai) for Claude + Image Generation
- [ ] **Notion API** (Optional): Setup integration at [Notion Developers](https://developers.notion.com)

### 3. **Storage Configuration**
- [ ] Choose storage mode: `markdown`, `book`, or `notion`
- [ ] Configure knowledge base path
- [ ] Setup Obsidian vault (if using book mode)
- [ ] Create Notion database with required properties (if using Notion)

### 4. **Railway yt-dlp Service** (Recommended)
- [ ] Deploy yt-dlp service to Railway
- [ ] Configure `RAILWAY_API_URL` in environment
- [ ] Test video download functionality

### 5. **Dependencies**
```bash
# Install production dependencies
pip install -r requirements.txt

# Verify all services are importable
python -c "from services import *; print('✅ All services imported successfully')"
```

## 🏭 **Deployment Options**

### Option 1: Railway Deployment (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy to Railway
railway login
railway init
railway up
```

### Option 2: Docker Deployment
```bash
# Build Docker image
docker build -t knowledge-bot .

# Run with environment variables
docker run -d --env-file .env knowledge-bot
```

### Option 3: VPS/Server Deployment
```bash
# Setup systemd service (Linux)
sudo cp deployment/knowledge-bot.service /etc/systemd/system/
sudo systemctl enable knowledge-bot
sudo systemctl start knowledge-bot
```

## 🔧 **Production Configuration**

### Essential Settings
```bash
# High-quality content generation
TARGET_CONTENT_LENGTH=3000
MIN_CATEGORY_CONFIDENCE=0.7
ENABLE_IMAGE_GENERATION=true

# Rate limiting for production
RATE_LIMIT_PER_HOUR=10
MAX_VIDEO_DURATION_SECONDS=600

# Cost control
ENABLE_COST_TRACKING=true
LOG_TOKEN_USAGE=true
```

### Performance Tuning
```bash
# Adjust timeouts based on your server
RAILWAY_DOWNLOAD_TIMEOUT=300
GEMINI_ANALYSIS_TIMEOUT=180
CLAUDE_ENRICHMENT_TIMEOUT=120

# Memory optimization for VPS
GEMINI_MAX_TOKENS=8192
OPENROUTER_MAX_TOKENS=4000
```

## 📊 **Monitoring & Maintenance**

### Health Checks
- [ ] Setup log monitoring (`logs/bot_*.log`)
- [ ] Configure uptime monitoring
- [ ] Monitor API quota usage
- [ ] Track cost analytics

### Regular Maintenance
- [ ] Review and clean old log files
- [ ] Backup knowledge base regularly
- [ ] Update dependencies monthly
- [ ] Monitor error rates and patterns

## 🔒 **Security Best Practices**

### Environment Security
- [ ] Never commit `.env` files
- [ ] Use strong, unique API keys
- [ ] Rotate API keys regularly
- [ ] Setup IP restrictions where possible

### Bot Security
- [ ] Enable rate limiting
- [ ] Monitor for abuse patterns
- [ ] Setup webhook security (if using webhooks)
- [ ] Regular security updates

## 🚨 **Troubleshooting**

### Common Issues
- **Import Errors**: Check `requirements.txt` and Python version
- **API Failures**: Verify API keys and quotas
- **Gemini Model Errors**: Use Google AI Studio model names (`gemini-1.5-flash`, not Vertex AI names)
- **Memory Issues**: Adjust token limits and video duration
- **Storage Errors**: Check permissions and disk space

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python app.py
```

## 📈 **Scaling Considerations**

### For High Volume
- [ ] Use webhook mode instead of polling
- [ ] Setup Redis for state management
- [ ] Consider load balancing
- [ ] Implement queue system for video processing

### Cost Optimization
- [ ] Monitor token usage patterns
- [ ] Adjust content length targets
- [ ] Optimize image generation frequency
- [ ] Implement smart caching

---

## 🎯 **Quick Start Commands**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
nano .env  # Configure your API keys

# 3. Test configuration
python -c "from config import Config; Config.validate(); print('✅ Configuration valid')"

# 4. Run bot
python app.py
```

## 📞 **Support**

- **Documentation**: Check README.md for detailed setup
- **Issues**: Use GitHub Issues for bugs and feature requests
- **API Keys**: Follow provider documentation for setup
- **Performance**: Monitor logs and adjust timeouts as needed