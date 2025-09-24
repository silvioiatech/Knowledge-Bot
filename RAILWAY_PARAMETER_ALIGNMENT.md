# Railway API Parameter Alignment ✅

## Fixed Parameters

### ✅ Correct API Parameters Used

Based on your Railway yt-dlp service README, the Knowledge Bot now correctly uses:

```python
payload = {
    "url": url,                                    # ✅ Required - video URL
    "format": format_selector,                     # ✅ Correct (not "quality")  
    "path": "videos/{safe_title}-{id}.{ext}"      # ✅ Uses your path template system
}
```

### 📋 Railway API Parameter Reference

From your service documentation:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Source URL to download |
| `format` | string | No | yt-dlp format selector (default: "bv*+ba/best") |
| `path` | string | No | File path template (default: "videos/{safe_title}-{id}.{ext}") |
| `webhook` | string | No | Webhook URL for completion notification |
| `timeout_sec` | number | No | Timeout in seconds (default: 1800) |

### 🎯 Format Selectors

Your service supports comprehensive yt-dlp format selectors:

- `"best"` - Best quality available
- `"worst"` - Lowest quality  
- `"bestaudio"` - Audio only
- `"bv*+ba/best"` - Best video + best audio
- `"best[height<=1080]"` - Quality limited formats
- Platform-specific selectors

### 🛠 Path Templates 

Your service supports dynamic path templates with tokens:

- `{id}` - Video ID
- `{title}` - Full title  
- `{safe_title}` - Sanitized title
- `{ext}` - File extension
- `{uploader}` - Uploader name
- `{date}` - Upload date (YYYY-MM-DD)
- `{random}` - Random hex string

### ⚠️ Removed Parameters

- ❌ `"extract_flat": False` - Not in your API specification
- ✅ Replaced with standard parameters

## Result

The Knowledge Bot payload now perfectly matches your Railway yt-dlp service API specification! 🚀