#!/bin/bash

echo "🚀 Knowledge Bot - Production Deployment"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "🧹 Step 1: Removing ALL non-essential files..."
echo ""

# Remove ALL documentation except README and LICENSE
rm -f CLEANUP_SUMMARY.md \
      CODE_ANALYSIS_AND_FIXES.md \
      COMPLETE_ANALYSIS_REPORT.md \
      COMPLETE_MODEL_FIXES.md \
      DEPLOYMENT_COMPLETE.md \
      FIXES_COMPLETE_SUMMARY.md \
      FIXES_IMPLEMENTED.md \
      FIXES_SUMMARY.md \
      PRODUCTION_FIX_COMPLETE.md \
      PRODUCTION_READY.md \
      QUICK_START.md \
      VERIFICATION_GUIDE.md \
      VERIFICATION_REPORT.md \
      CONTRIBUTING.md

# Remove ALL scripts and debug files
rm -f app.py \
      app_debug.py \
      apply_automated_fixes.py \
      quick_fix.py \
      verify.sh \
      cleanup_repo.sh \
      production_cleanup.sh \
      final_cleanup.sh \
      railway_server.py \
      .env.corrected

echo "✅ Removed all non-essential files"
echo ""

echo "📦 Step 2: Production files remaining:"
echo ""
ls -1 | grep -E '\.(py|txt|toml|md|gitignore)$|Procfile|Dockerfile|LICENSE'
echo ""
echo "📁 Directories:"
ls -d */ 2>/dev/null | grep -v __pycache__
echo ""

echo "📋 Step 3: Staging changes..."
git add -A
echo "✅ Changes staged"
echo ""

echo "💾 Step 4: Committing..."
git commit -m "production: Clean repository - production ready

✅ Removed all debug files and documentation
✅ Clean minimal README
✅ Simplified .env.example  
✅ Minimal .gitignore
✅ Fixed Railway deployment (main.py)
✅ Fixed syntax errors

Production deployment ready 🚀"

echo ""
echo "✅ Committed!"
echo ""

echo "========================================"
echo "✅ PRODUCTION READY!"
echo "========================================"
echo ""
echo "📌 Final structure:"
echo "   Essential files only:"
echo "   ├── main.py (entry point)"
echo "   ├── config.py"
echo "   ├── requirements.txt"
echo "   ├── Procfile"
echo "   ├── railway.toml"
echo "   ├── Dockerfile"
echo "   ├── README.md"
echo "   ├── LICENSE"
echo "   ├── .env.example"
echo "   ├── .gitignore"
echo "   └── Source code (bot/, services/, storage/, core/)"
echo ""
echo "🚀 Deploy: git push origin main"
echo ""
