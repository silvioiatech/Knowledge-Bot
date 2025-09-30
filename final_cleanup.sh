#!/bin/bash

echo "🧹 FINAL PRODUCTION CLEANUP - Removing ALL non-essential files"
echo "=============================================================="
echo ""

cd "$(dirname "$0")"

# Delete ALL markdown documentation except README
echo "📄 Cleaning documentation..."
rm -f CLEANUP_SUMMARY.md
rm -f CODE_ANALYSIS_AND_FIXES.md
rm -f COMPLETE_ANALYSIS_REPORT.md
rm -f COMPLETE_MODEL_FIXES.md
rm -f DEPLOYMENT_COMPLETE.md
rm -f FIXES_COMPLETE_SUMMARY.md
rm -f FIXES_IMPLEMENTED.md
rm -f FIXES_SUMMARY.md
rm -f PRODUCTION_FIX_COMPLETE.md
rm -f QUICK_START.md
rm -f VERIFICATION_GUIDE.md
rm -f VERIFICATION_REPORT.md
rm -f PRODUCTION_READY.md
rm -f CONTRIBUTING.md

# Delete ALL scripts and debug files
echo "🗑️  Removing scripts and debug files..."
rm -f app.py
rm -f app_debug.py
rm -f apply_automated_fixes.py
rm -f quick_fix.py
rm -f verify.sh
rm -f cleanup_repo.sh
rm -f production_cleanup.sh
rm -f railway_server.py
rm -f .env.corrected

# Delete this script itself after execution
rm -f final_cleanup.sh

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📦 Production files remaining:"
echo "├── main.py"
echo "├── config.py"
echo "├── requirements.txt"
echo "├── Procfile"
echo "├── railway.toml"
echo "├── Dockerfile"
echo "├── README.md"
echo "├── LICENSE"
echo "├── .env.example"
echo "├── .gitignore"
echo "├── bot/"
echo "├── services/"
echo "├── storage/"
echo "├── core/"
echo "└── utils/"
echo ""
echo "🚀 Ready to commit and deploy!"
