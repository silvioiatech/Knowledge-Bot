#!/usr/bin/env python3
"""
Quick fix script for minor code organization issues in Knowledge Bot
"""

import sys
from pathlib import Path

def fix_video_handler():
    """Fix global variable placement in video_handler.py"""
    
    video_handler_path = Path("bot/handlers/video_handler.py")
    
    if not video_handler_path.exists():
        print("❌ video_handler.py not found")
        return False
    
    print("📝 Reading video_handler.py...")
    content = video_handler_path.read_text()
    lines = content.split('\n')
    
    # Find the service instances section
    service_section_index = None
    for i, line in enumerate(lines):
        if "# Service instances - initialized lazily" in line:
            service_section_index = i
            break
    
    if service_section_index is None:
        print("❌ Could not find service instances section")
        return False
    
    # Check if storage variables are already in the right place
    storage_vars = ["markdown_storage = None", "notion_storage = None", "railway_storage = None"]
    service_section_end = service_section_index + 5
    
    already_fixed = True
    for var in storage_vars:
        found_in_section = any(var in lines[i] for i in range(service_section_index, service_section_end))
        if not found_in_section:
            already_fixed = False
            break
    
    if already_fixed:
        print("✅ Code organization already correct!")
        return True
    
    print("🔧 Fixing global variable placement...")
    
    # Find and remove misplaced storage variables (around line 77)
    lines_to_remove = []
    for i, line in enumerate(lines):
        if any(var.strip() in line for var in storage_vars) and i > service_section_end:
            lines_to_remove.append(i)
    
    # Add storage variables after service instances
    insert_index = service_section_index + 4  # After image_service = None
    
    if "image_service = None" not in lines[insert_index]:
        print("⚠️  Warning: Service section structure unexpected")
    
    # Create new content
    new_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            new_lines.append(line)
        
        # Add storage variables after image_service
        if i == insert_index and not already_fixed:
            new_lines.append("markdown_storage = None")
            new_lines.append("notion_storage = None")
            new_lines.append("railway_storage = None")
    
    # Write back
    new_content = '\n'.join(new_lines)
    video_handler_path.write_text(new_content)
    
    print("✅ Fixed video_handler.py")
    return True


def main():
    """Main function"""
    print("🔧 Knowledge Bot - Quick Fix Script")
    print("=" * 50)
    print()
    
    # Change to project directory
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    success = fix_video_handler()
    
    print()
    print("=" * 50)
    if success:
        print("✅ All fixes applied successfully!")
        print()
        print("Next steps:")
        print("1. Run: ./verify.sh")
        print("2. If all checks pass, run: python3 main.py")
    else:
        print("❌ Some fixes failed - please check manually")
        sys.exit(1)


if __name__ == "__main__":
    main()
