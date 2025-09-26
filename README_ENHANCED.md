# Knowledge Bot 2.0 - 6-Stage AI Pipeline

A comprehensive Telegram bot that transforms educational videos into high-quality knowledge base entries using a sophisticated 6-stage AI workflow.

## 🚀 Architecture Overview

### 6-Stage AI Pipeline

1. **🧠 Gemini Analysis + Web Research**
   - Video download via Railway API
   - Enhanced content analysis with Gemini 1.5 Flash
   - Entity extraction and claim identification
   - Web research for fact-checking
   - Quality scoring and confidence assessment

2. **📱 Telegram User Approval**
   - Rich preview cards with analysis summary
   - Interactive approval/rejection buttons
   - Quality metrics and estimated output
   - Regeneration and modification options

3. **✍️ Claude Textbook Generation**
   - Professional textbook-quality content creation
   - Comprehensive 2500-3500 word guides
   - Structured academic format with 8+ sections
   - Image plan generation for visual aids

4. **🎨 Conditional Banana Image Generation**
   - Smart decision making for diagram necessity
   - Professional educational diagrams
   - Flowcharts, architecture diagrams, sequences
   - Optimized for web delivery

5. **🔧 GPT Assembly & Quality Assurance**
   - Final content integration and polishing
   - Quality review and consistency checks
   - Cross-reference generation
   - Notion payload preparation

6. **📊 Notion Database Storage**
   - Comprehensive database integration
   - Auto-populated metadata fields
   - Rich content blocks with embedded media
   - Quality ratings and cross-references

## 🏗️ Project Structure

```
knowledge-bot/
├── core/                           # Core processing logic
│   ├── models/
│   │   └── content_models.py      # Data models for pipeline
│   ├── processors/
│   │   ├── gemini_processor.py    # Enhanced Gemini analysis
│   │   ├── claude_processor.py    # Textbook generation
│   │   ├── banana_processor.py    # Image generation
│   │   └── gpt_processor.py       # Final assembly
│   └── pipeline.py                # Main orchestration
├── interfaces/
│   └── telegram/
│       └── enhanced_interface.py  # Rich Telegram UI
├── services/                      # External integrations
│   ├── railway_client.py         # Video download
│   ├── gemini_service.py          # Legacy Gemini
│   └── claude_service.py          # Legacy Claude
├── storage/                       # Storage backends
│   ├── notion_storage.py         # Enhanced Notion integration
│   └── markdown_storage.py       # File storage
├── utils/
│   └── helpers.py                # Utility functions
├── bot/                          # Legacy bot structure
├── config.py                     # Enhanced configuration
├── enhanced_main.py              # New main application
└── requirements.txt              # Dependencies
```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Core APIs
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional Services
RAILWAY_API_URL=your_railway_api_url
BANANA_API_KEY=your_banana_api_key
SERPER_API_KEY=your_google_search_api_key

# Notion Integration
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
USE_NOTION_STORAGE=true

# Pipeline Configuration
ENABLE_IMAGE_GENERATION=true
ENABLE_WEB_RESEARCH=true
MAX_IMAGES_PER_ENTRY=5
TARGET_CONTENT_LENGTH=3000
```

### Optional Configuration

```bash
# Model Selection
GEMINI_MODEL=gemini-1.5-flash
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GPT_MODEL=gpt-4-1106-preview

# Limits & Timeouts
MAX_VIDEO_DURATION_SECONDS=1800
RATE_LIMIT_PER_HOUR=10
GEMINI_ANALYSIS_TIMEOUT=300
CLAUDE_ENRICHMENT_TIMEOUT=180

# Storage
TEMP_DIR=./temp
KNOWLEDGE_BASE_PATH=./knowledge_base
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd knowledge-bot

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Database Setup (Notion)

Create a Notion database with these properties:

| Property | Type | Options |
|----------|------|---------|
| Title | Title | - |
| Source URL | URL | - |
| Platform | Select | TikTok, Instagram, YouTube |
| Content Quality | Select | ⭐⭐⭐⭐⭐, ⭐⭐⭐⭐, ⭐⭐⭐, ⭐⭐, ⭐ |
| Difficulty | Select | Beginner, Intermediate, Advanced, Expert |
| Word Count | Number | - |
| Estimated Reading Time | Number | - |
| Tags | Multi-select | - |
| Key Concepts | Rich Text | - |
| Cross References | Rich Text | - |
| Gemini Confidence | Number | - |
| Processing Date | Date | - |

### 3. Run the Enhanced Bot

```bash
# Start the enhanced bot
python enhanced_main.py

# Or use the legacy version
python bot/main.py
```

## 📊 Features Comparison

| Feature | Legacy Bot | Enhanced Bot 2.0 |
|---------|------------|------------------|
| Video Analysis | Basic Gemini | Enhanced + Web Research |
| Content Generation | 1500-2000 words | 2500-3500 words |
| User Interface | Simple messages | Rich preview cards |
| Image Generation | None | Smart conditional diagrams |
| Quality Assurance | Basic | GPT assembly + review |
| Database Integration | Basic fields | Comprehensive metadata |
| Fact Checking | None | Web research + verification |
| Content Structure | Simple | Academic textbook format |

## 🎯 Usage Examples

### Basic Video Processing

1. Send a TikTok/Instagram/YouTube URL to the bot
2. Review the AI-generated analysis preview
3. Approve or request modifications
4. Receive comprehensive knowledge base entry
5. Access via Notion database or download

### Advanced Features

- **Regeneration**: Re-analyze with different focus
- **Custom Modifications**: Request specific changes
- **Quality Control**: Automatic scoring and validation
- **Cross-References**: Auto-generated related topics
- **Visual Aids**: Context-aware diagram generation

## 🔧 Development

### Adding New Processors

1. Create processor class in `core/processors/`
2. Implement required interfaces from `content_models.py`
3. Add to pipeline orchestration in `core/pipeline.py`
4. Update configuration as needed

### Extending Data Models

1. Modify models in `core/models/content_models.py`
2. Update processors to handle new fields
3. Extend Notion storage schema
4. Add validation logic

### Custom Interfaces

1. Create interface in `interfaces/`
2. Implement required handlers
3. Register with main application
4. Configure routing and middleware

## 📈 Monitoring & Logging

### Health Checks

- System component status
- API availability monitoring
- Performance metrics
- Error rate tracking

### Logging Levels

- **DEBUG**: Detailed processing information
- **INFO**: General operation status
- **WARNING**: Non-critical issues
- **ERROR**: Processing failures

### Log Files

- `logs/knowledge_bot_YYYY-MM-DD.log`: Daily operations
- `logs/errors_YYYY-MM-DD.log`: Error tracking
- Automatic rotation and compression

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Verify configuration
   python -c "from config import Config; Config.validate()"
   ```

2. **Video Download Failures**
   - Check Railway API connectivity
   - Verify supported platforms
   - Check video accessibility

3. **Content Generation Issues**
   - Monitor API rate limits
   - Check token usage
   - Verify model availability

4. **Notion Integration Problems**
   - Validate database schema
   - Check API permissions
   - Verify database ID format

### Performance Optimization

- Enable image generation conditionally
- Adjust content length targets
- Configure appropriate timeouts
- Monitor resource usage

## 🚦 Deployment

### Local Development

```bash
# Development mode with hot reload
python enhanced_main.py
```

### Production Deployment

```bash
# Using Docker
docker build -t knowledge-bot .
docker run -d --env-file .env knowledge-bot

# Using systemd service
sudo systemctl enable knowledge-bot
sudo systemctl start knowledge-bot
```

### Environment-Specific Configuration

- **Development**: Lower limits, detailed logging
- **Staging**: Production-like settings, test data
- **Production**: Optimized limits, error-only logging

## 📝 API Documentation

### Pipeline Methods

- `process_video_url(url, preferences)`: Full processing
- `get_processing_preview(url)`: Quick analysis
- `validate_video_url(url)`: URL validation

### Processor Interfaces

Each processor implements:
- `async def process(input_data)`: Main processing
- `async def close()`: Resource cleanup
- Error handling and retry logic

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- GitHub Issues: Bug reports and feature requests
- Documentation: Comprehensive guides and examples
- Community: Discord server for discussions

---

**Enhanced Knowledge Bot 2.0** - Transforming educational content with AI precision 🚀