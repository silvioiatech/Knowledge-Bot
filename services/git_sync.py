"""Git synchronization service for knowledge base management."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from loguru import logger

from config import Config


class GitSyncError(Exception):
    """Custom exception for Git sync errors."""
    pass


class GitSyncService:
    """Service for synchronizing knowledge base with Git repositories."""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or Config.KNOWLEDGE_BASE_PATH)
        self.git_enabled = Config.GIT_AUTO_COMMIT
        
        if not self.repo_path.exists():
            self.repo_path.mkdir(parents=True, exist_ok=True)
    
    async def initialize_repository(self) -> bool:
        """Initialize Git repository if not exists."""
        try:
            if not self.git_enabled:
                logger.info("Git auto-commit disabled, skipping repository initialization")
                return False
            
            git_dir = self.repo_path / ".git"
            if git_dir.exists():
                logger.info("Git repository already initialized")
                return True
            
            # Initialize repository
            await self._run_git_command(["init"])
            
            # Create initial .gitignore
            gitignore_content = """
# Temporary files
*.tmp
*.temp
.DS_Store

# Environment files
.env
.env.local

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Logs
*.log
logs/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Notion API cache
.notion_cache/
"""
            gitignore_path = self.repo_path / ".gitignore"
            gitignore_path.write_text(gitignore_content.strip())
            
            # Initial commit
            await self._run_git_command(["add", ".gitignore"])
            await self._run_git_command([
                "commit", "-m", "Initial commit: Knowledge Bot repository setup"
            ])
            
            logger.success("Git repository initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Git repository: {e}")
            return False
    
    async def commit_changes(self, 
                           file_paths: Optional[List[str]] = None,
                           message: Optional[str] = None) -> bool:
        """Commit changes to the repository."""
        try:
            if not self.git_enabled:
                logger.debug("Git auto-commit disabled, skipping commit")
                return False
            
            # Check if there are changes to commit
            status = await self._get_git_status()
            if not status.get("has_changes", False):
                logger.debug("No changes to commit")
                return True
            
            # Add files
            if file_paths:
                for file_path in file_paths:
                    relative_path = Path(file_path).relative_to(self.repo_path)
                    await self._run_git_command(["add", str(relative_path)])
            else:
                await self._run_git_command(["add", "."])
            
            # Generate commit message
            if not message:
                message = f"Auto-commit: Knowledge base update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Commit changes
            await self._run_git_command(["commit", "-m", message])
            
            logger.success(f"Successfully committed changes: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return False
    
    async def sync_with_remote(self, 
                             remote_url: Optional[str] = None,
                             branch: str = "main") -> bool:
        """Sync with remote repository."""
        try:
            if not self.git_enabled:
                logger.debug("Git sync disabled")
                return False
            
            # Add remote if provided
            if remote_url:
                try:
                    await self._run_git_command(["remote", "add", "origin", remote_url])
                except GitSyncError:
                    # Remote might already exist
                    await self._run_git_command(["remote", "set-url", "origin", remote_url])
            
            # Check if remote exists
            try:
                await self._run_git_command(["remote", "get-url", "origin"])
            except GitSyncError:
                logger.warning("No remote repository configured")
                return False
            
            # Pull latest changes (if any)
            try:
                await self._run_git_command(["pull", "origin", branch])
            except GitSyncError:
                logger.warning("Failed to pull from remote (might be first push)")
            
            # Push local changes
            await self._run_git_command(["push", "-u", "origin", branch])
            
            logger.success(f"Successfully synced with remote repository")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync with remote: {e}")
            return False
    
    async def create_backup_branch(self, branch_name: Optional[str] = None) -> bool:
        """Create a backup branch with current state."""
        try:
            if not branch_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                branch_name = f"backup_{timestamp}"
            
            # Create and switch to backup branch
            await self._run_git_command(["checkout", "-b", branch_name])
            
            # Commit current state
            await self.commit_changes(message=f"Backup branch: {branch_name}")
            
            # Switch back to main branch
            await self._run_git_command(["checkout", "main"])
            
            logger.success(f"Created backup branch: {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup branch: {e}")
            return False
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            if not self.git_enabled:
                return {"git_enabled": False}
            
            stats = {
                "git_enabled": True,
                "repository_path": str(self.repo_path)
            }
            
            # Get current branch
            try:
                result = await self._run_git_command(["branch", "--show-current"])
                stats["current_branch"] = result.strip()
            except:
                stats["current_branch"] = "unknown"
            
            # Get commit count
            try:
                result = await self._run_git_command(["rev-list", "--count", "HEAD"])
                stats["total_commits"] = int(result.strip())
            except:
                stats["total_commits"] = 0
            
            # Get last commit info
            try:
                result = await self._run_git_command([
                    "log", "-1", "--format=%H|%s|%ai", "HEAD"
                ])
                if result.strip():
                    hash_val, message, date = result.strip().split("|", 2)
                    stats["last_commit"] = {
                        "hash": hash_val[:8],
                        "message": message,
                        "date": date
                    }
            except:
                stats["last_commit"] = None
            
            # Get status
            status = await self._get_git_status()
            stats.update(status)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get repository stats: {e}")
            return {"error": str(e)}
    
    async def _get_git_status(self) -> Dict[str, Any]:
        """Get Git status information."""
        try:
            # Get status
            result = await self._run_git_command(["status", "--porcelain"])
            lines = [line.strip() for line in result.split("\n") if line.strip()]
            
            status = {
                "has_changes": len(lines) > 0,
                "total_changes": len(lines),
                "modified_files": [],
                "new_files": [],
                "deleted_files": []
            }
            
            for line in lines:
                if line.startswith("M "):
                    status["modified_files"].append(line[2:])
                elif line.startswith("A "):
                    status["new_files"].append(line[2:])
                elif line.startswith("D "):
                    status["deleted_files"].append(line[2:])
                elif line.startswith("??"):
                    status["new_files"].append(line[3:])
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get Git status: {e}")
            return {"has_changes": False, "error": str(e)}
    
    async def _run_git_command(self, args: List[str]) -> str:
        """Run Git command and return output."""
        try:
            command = ["git"] + args
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Git command failed: {' '.join(args)} - {error_msg}")
                raise GitSyncError(f"Git command failed: {error_msg}")
            
            return stdout.decode().strip()
            
        except FileNotFoundError:
            raise GitSyncError("Git is not installed or not available in PATH")
        except Exception as e:
            raise GitSyncError(f"Git command execution failed: {e}")
    
    async def auto_commit_file(self, file_path: str, operation: str = "update") -> bool:
        """Auto-commit a single file with descriptive message."""
        try:
            if not self.git_enabled:
                return False
            
            file_name = Path(file_path).name
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"Auto-{operation}: {file_name} - {timestamp}"
            
            return await self.commit_changes(
                file_paths=[file_path],
                message=message
            )
            
        except Exception as e:
            logger.error(f"Failed to auto-commit file {file_path}: {e}")
            return False
