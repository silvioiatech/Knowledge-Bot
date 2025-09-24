#!/usr/bin/env python3
"""Setup script for private knowledge repository."""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.git_sync import GitKnowledgeSync
from storage.book_storage import BookStorage


async def main():
    """Setup the private knowledge repository."""
    print("🔒 Setting up your private knowledge repository...")
    print()
    
    # Get user information
    github_username = input("📝 Enter your GitHub username: ").strip()
    if not github_username:
        print("❌ GitHub username is required")
        return
    
    print()
    print("🔑 You need a GitHub Personal Access Token:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select scopes: 'repo' (for private repositories)")
    print("4. Copy the generated token")
    print()
    
    github_token = input("🔑 Enter your GitHub Personal Access Token: ").strip()
    if not github_token:
        print("❌ GitHub token is required for private repository sync")
        return
    
    print()
    
    # Update environment variables temporarily
    os.environ["GITHUB_USERNAME"] = github_username
    os.environ["GITHUB_TOKEN"] = github_token
    os.environ["AUTO_COMMIT"] = "true"
    os.environ["AUTO_PUSH"] = "true"
    os.environ["PRIVATE_REPO_PATH"] = "../my-private-knowledge"
    os.environ["OBSIDIAN_VAULT_PATH"] = "../my-private-knowledge"
    
    try:
        # Setup git repository
        print("📂 Setting up repository structure...")
        git_sync = GitKnowledgeSync("../my-private-knowledge")
        success = await git_sync.setup_repository()
        
        if not success:
            print("❌ Failed to setup repository")
            return
        
        # Initialize book structure in the private repo
        print("📚 Creating knowledge library structure...")
        storage = BookStorage()
        await storage.initialize_book_structure()
        
        # Initial commit of the book structure
        print("💾 Committing initial library structure...")
        await git_sync.commit_and_push("Initial setup: Create knowledge library structure")
        
        # Get repository status
        status = await git_sync.get_status()
        
        print()
        print("✅ Private knowledge repository setup complete!")
        print()
        print("📊 Repository Status:")
        print(f"  📁 Location: {status['repository_path']}")
        print(f"  🌿 Branch: {status['branch']}")
        print(f"  💾 Commits: {status['total_commits']}")
        print(f"  📝 Last commit: {status['last_commit']}")
        print()
        
        # Create .env update instructions
        env_content = f"""
# Add these to your .env file:
STORAGE_MODE=book
OBSIDIAN_VAULT_PATH=../my-private-knowledge
PRIVATE_REPO_PATH=../my-private-knowledge
GITHUB_USERNAME={github_username}
GITHUB_TOKEN={github_token}
AUTO_COMMIT=true
AUTO_PUSH=true
"""
        
        env_file = Path("private_repo.env")
        env_file.write_text(env_content.strip())
        
        print("🎯 Next Steps:")
        print(f"1. Copy settings from 'private_repo.env' to your main '.env' file")
        print("2. Download Obsidian from https://obsidian.md")
        print(f"3. Open vault: ../my-private-knowledge")
        print("4. Start your bot and add some videos!")
        print()
        print("🔒 Your private knowledge library is ready!")
        print(f"🌐 GitHub Repository: https://github.com/{github_username}/my-private-knowledge")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())