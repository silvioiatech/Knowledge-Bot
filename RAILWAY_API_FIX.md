# Railway API Integration Fix

## Issues Identified

### 1. **Status Values Mismatch**
Your Railway API returns:
- `QUEUED` ✅ (now handled)  
- `RUNNING` ✅ (now handled)
- `DONE` ✅ (now handled - was expecting `completed`)
- `ERROR` ✅ (now handled - was treating as unknown)

**Fixed**: Updated status handling to match your exact API responses.

### 2. **Endpoint Corrections** 
- Health check: Changed from `/health` to `/healthz` to match your API
- Download status: Already correct `/downloads/{request_id}`

### 3. **Authentication**
Your API expects `X-API-Key` header when `REQUIRE_API_KEY=true`. 
Knowledge Bot is configured to send this header when `RAILWAY_API_KEY` is set.

## Environment Variables to Check

Make sure these are set in your deployment:

```bash
# Railway API Configuration
RAILWAY_API_URL=https://your-railway-service.railway.app
RAILWAY_API_KEY=your_api_key  # Only if REQUIRE_API_KEY=true on Railway

# Other required vars
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_openrouter_key  
GEMINI_API_KEY=your_gemini_key
```

## Testing Commands

1. **Test Railway API directly**:
   ```bash
   python debug_railway.py
   ```

2. **Check Railway service health**:
   ```bash
   curl https://your-railway-service.railway.app/healthz
   ```

3. **Test full download flow**:
   ```bash
   curl -X POST https://your-railway-service.railway.app/download \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_key" \
     -d '{"url": "https://www.tiktok.com/@test/video/123"}'
   ```

## Response Format Your API Returns

```json
{
  "status": "DONE",           // ✅ Now handled correctly
  "request_id": "uuid",       // ✅ Already handled
  "file_url": "/files/path",  // ✅ Already handled
  "bytes": 12345,             // ✅ Already handled  
  "duration_sec": 45.2,       // ✅ Already handled
  "created_at": "2025-09-24...", // ✅ Already handled
  "completed_at": "2025-09-24...", // ✅ Already handled
  "deletion_time": "2025-09-24..." // ✅ Auto-deletion after 1 hour
}
```

## What Should Work Now

1. ✅ Bot recognizes `QUEUED` status and continues polling
2. ✅ Bot recognizes `RUNNING` status and continues polling  
3. ✅ Bot recognizes `DONE` status as success
4. ✅ Bot recognizes `ERROR` status as failure and stops polling
5. ✅ Health check uses correct `/healthz` endpoint
6. ✅ Better error logging to debug any remaining issues

## Next Steps

1. **Deploy the updated bot** with the Railway API fixes
2. **Test with a real video URL** to verify the integration works
3. **Check the logs** - much more detailed debugging is now enabled
4. **Verify environment variables** are set correctly

The bot should now properly handle your Railway API responses and successfully download videos!