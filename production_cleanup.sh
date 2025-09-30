#!/bin/bash

# ============================================
# Knowledge Bot - Production Cleanup Script
# ============================================

echo "🧹 Knowledge Bot - Production Cleanup"
echo "======================================"
echo ""

# Change to repo directory
cd "$(dirname "$0")"

echo "📋 Step 1: Removing debug and analysis files..."
echo ""

# Files to delete
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
rm -f app.py
rm -f app_debug.py
rm -f apply_automated_fixes.py
rm -f quick_fix.py
rm -f verify.sh
rm -f railway_server.py
rm -f .env.corrected

echo "✅ Removed debug files"
echo ""

echo "📋 Step 2: Staging production files..."
echo ""

# Stage all changes
git add -A

# Show what will be committed
echo "Files staged for commit:"
git status --short

echo ""
echo "📋 Step 3: Committing changes..."
echo ""

# Commit
git commit -m "production: Clean repository for production deployment

- Remove all debug and analysis files
- Add professional README.md
- Add LICENSE (MIT)
- Add CONTRIBUTING.md
- Update .gitignore
- Update .env.example
- Fix Railway deployment config
- Fix syntax error in enhanced_claude_service.py

Production-ready ✅"

echo ""
echo "✅ Changes committed!"
echo ""

echo "📋 Step 4: Repository structure"
echo ""
echo "Production files:"
tree -L 2 -I '__pycache__|*.pyc|.git|venv|env|logs|knowledge_base' || ls -la

echo ""
echo "======================================"
echo "✅ CLEANUP COMPLETE!"
echo "======================================"
echo ""
echo "📌 Next steps:"
echo "1. Review the commit: git log -1"
echo "2. Push to Railway: git push origin main"
echo "3. Monitor Railway logs after deployment"
echo ""
echo "🚀 Your bot is production-ready!"
