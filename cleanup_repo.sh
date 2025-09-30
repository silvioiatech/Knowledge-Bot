#!/bin/bash
# Production Repository Cleanup Script

echo "🧹 Cleaning up Knowledge Bot repository for production..."
echo ""

# Files to delete (debug and analysis files)
FILES_TO_DELETE=(
    "CLEANUP_SUMMARY.md"
    "CODE_ANALYSIS_AND_FIXES.md"
    "COMPLETE_ANALYSIS_REPORT.md"
    "COMPLETE_MODEL_FIXES.md"
    "DEPLOYMENT_COMPLETE.md"
    "FIXES_COMPLETE_SUMMARY.md"
    "FIXES_IMPLEMENTED.md"
    "FIXES_SUMMARY.md"
    "PRODUCTION_FIX_COMPLETE.md"
    "QUICK_START.md"
    "VERIFICATION_GUIDE.md"
    "VERIFICATION_REPORT.md"
    "app.py"
    "app_debug.py"
    "apply_automated_fixes.py"
    "quick_fix.py"
    "verify.sh"
    "railway_server.py"
    ".env.corrected"
)

# Delete files
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "✅ Deleted: $file"
    fi
done

echo ""
echo "🎉 Repository cleaned! Production-ready files remain."
echo ""
echo "Remaining structure:"
echo "├── main.py (Bot entry point)"
echo "├── config.py (Configuration)"
echo "├── requirements.txt (Dependencies)"
echo "├── Procfile (Railway worker config)"
echo "├── railway.toml (Railway deployment)"
echo "├── Dockerfile (Container config)"
echo "├── README.md (Documentation)"
echo "├── bot/ (Handlers and logic)"
echo "├── services/ (AI services)"
echo "├── storage/ (Data storage)"
echo "├── core/ (Models and utilities)"
echo "└── utils/ (Helper functions)"
