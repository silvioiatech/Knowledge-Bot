#!/usr/bin/env python3
"""
Automated fix application script for Knowledge Bot.
This script applies safe, automated fixes to the codebase.
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


def backup_file(file_path: Path) -> Path:
    """Create a backup of a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backed up: {file_path} -> {backup_path}")
    return backup_path


def fix_syntax_error_line_282(file_path: Path) -> bool:
    """Fix the extra bracket on line 282."""
    try:
        content = file_path.read_text()
        
        # Fix the specific syntax error
        fixed_content = content.replace(
            "tools_mentioned = [entity.name for entity in analysis.entities if entity.type == 'technology']][:5]",
            "tools_mentioned = [entity.name for entity in analysis.entities if entity.type == 'technology'][:5]"
        )
        
        if content != fixed_content:
            backup_file(file_path)
            file_path.write_text(fixed_content)
            print(f"✅ Fixed syntax error in {file_path}")
            return True
        else:
            print(f"⚠️  No syntax error found in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def add_http_client_cleanup(file_path: Path) -> bool:
    """Add HTTP client cleanup to service classes."""
    try:
        content = file_path.read_text()
        
        # Check if cleanup already exists
        if "async def close(self)" in content:
            print(f"⚠️  HTTP client cleanup already exists in {file_path}")
            return False
        
        # Find the class definition
        if "class " not in content or "AsyncClient" not in content:
            print(f"⚠️  No AsyncClient found in {file_path}")
            return False
        
        # Add cleanup methods at the end of the class (before last line)
        cleanup_code = '''
    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close HTTP client and cleanup resources."""
        if hasattr(self, 'http_client') and self.http_client:
            try:
                await self.http_client.aclose()
                logger.debug(f"{self.__class__.__name__} HTTP client closed")
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
'''
        
        # Insert before the last line (usually class end)
        lines = content.split('\n')
        
        # Find a good insertion point (after __init__ or last method)
        insertion_index = len(lines) - 1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('def ') or lines[i].strip().startswith('async def '):
                # Find the end of this method
                for j in range(i + 1, len(lines)):
                    if lines[j] and not lines[j][0].isspace():
                        insertion_index = j
                        break
                break
        
        # Insert the cleanup code
        lines.insert(insertion_index, cleanup_code)
        fixed_content = '\n'.join(lines)
        
        backup_file(file_path)
        file_path.write_text(fixed_content)
        print(f"✅ Added HTTP client cleanup to {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding cleanup to {file_path}: {e}")
        return False


def fix_quality_scores_scaling(file_path: Path) -> bool:
    """Add min/max clamping to quality scores."""
    try:
        content = file_path.read_text()
        
        # Pattern to find quality score assignments without clamping
        pattern = r'(overall|technical_depth|content_accuracy|completeness|educational_value|source_credibility)\s*=\s*(?!min\()(.*?)(?=,|\))'
        
        def clamp_score(match):
            field = match.group(1)
            expression = match.group(2).strip()
            return f"{field} = min(100, max(0, {expression}))"
        
        fixed_content = re.sub(pattern, clamp_score, content)
        
        if content != fixed_content:
            backup_file(file_path)
            file_path.write_text(fixed_content)
            print(f"✅ Added quality score clamping to {file_path}")
            return True
        else:
            print(f"⚠️  Quality scores already clamped in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing quality scores in {file_path}: {e}")
        return False


def main():
    """Main fix application function."""
    print("🔧 Knowledge Bot - Automated Fix Application")
    print("=" * 50)
    
    project_root = Path("/Users/silvio/Documents/GitHub/Knowledge-Bot")
    
    fixes_applied = 0
    fixes_failed = 0
    
    # Fix 1: Syntax error in video_handler.py
    print("\n1️⃣ Fixing syntax error in video_handler.py...")
    video_handler = project_root / "bot" / "handlers" / "video_handler.py"
    if video_handler.exists():
        if fix_syntax_error_line_282(video_handler):
            fixes_applied += 1
        else:
            fixes_failed += 1
    else:
        print(f"⚠️  File not found: {video_handler}")
        fixes_failed += 1
    
    # Fix 2: Add HTTP client cleanup to service files
    print("\n2️⃣ Adding HTTP client cleanup to service files...")
    service_files = [
        project_root / "services" / "gemini_service.py",
        project_root / "services" / "claude_service.py",
        project_root / "services" / "enhanced_claude_service.py",
        project_root / "services" / "railway_client.py",
    ]
    
    for service_file in service_files:
        if service_file.exists():
            print(f"\n  Processing {service_file.name}...")
            if add_http_client_cleanup(service_file):
                fixes_applied += 1
            else:
                fixes_failed += 1
        else:
            print(f"  ⚠️  File not found: {service_file}")
            fixes_failed += 1
    
    # Fix 3: Quality score scaling in gemini_service.py
    print("\n3️⃣ Fixing quality score scaling...")
    gemini_service = project_root / "services" / "gemini_service.py"
    if gemini_service.exists():
        if fix_quality_scores_scaling(gemini_service):
            fixes_applied += 1
        else:
            fixes_failed += 1
    else:
        print(f"⚠️  File not found: {gemini_service}")
        fixes_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Fixes applied: {fixes_applied}")
    print(f"❌ Fixes failed: {fixes_failed}")
    print("\n📝 Note: All original files have been backed up with timestamp suffixes")
    print("📝 Manual fixes still needed - see FIXES_SUMMARY.md for details")
    print("\n🧪 Next step: Test the application thoroughly!")


if __name__ == "__main__":
    main()
