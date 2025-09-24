# TikTok Format Debugging

The error shows:
```
ERROR: [TikTok] 7543023019048848662: Requested format is not available. Use --list-formats for a list of available formats
```

This happens because TikTok videos have specific format IDs that don't always match standard height-based selectors.

## Format Selector Hierarchy (Updated)

1. **`best/worst`** - Most reliable, gets best quality available or fallback to worst
2. **`bv*+ba/b`** - Best video + best audio, fallback to single file
3. **`mp4/best`** - Prefer mp4 container, fallback to best
4. **Platform-specific selectors** for different video platforms

## TikTok Typical Formats
TikTok usually provides:
- Direct mp4 files with embedded audio
- Various quality levels (360p, 540p, 720p, 1080p)
- Some videos only have specific format IDs

## Testing Commands

```bash
# Test format availability for a TikTok URL
yt-dlp --list-formats "https://vm.tiktok.com/ZNdskpvcW/"

# Test with different selectors
yt-dlp -f "best" "https://vm.tiktok.com/ZNdskpvcW/"
yt-dlp -f "worst" "https://vm.tiktok.com/ZNdskpvcW/"
yt-dlp -f "mp4/best" "https://vm.tiktok.com/ZNdskpvcW/"
```

The updated bot now uses `best/worst` which should work with any video that yt-dlp can process.