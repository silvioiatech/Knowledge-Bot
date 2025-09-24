"""Git automation service for private knowledge repository."""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger
from config import Config


class GitKnowledgeSync:
    """Handles automatic git operations for private knowledge repository."""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path or Config.PRIVATE_REPO_PATH)
        self.github_username = Config.GITHUB_USERNAME
        self.github_token = Config.GITHUB_TOKEN
        self.auto_commit = Config.AUTO_COMMIT
        self.auto_push = Config.AUTO_PUSH
        
    async def setup_repository(self) -> bool:
        """Setup or clone the private knowledge repository."""
        try:
            if self.repo_path.exists() and (self.repo_path / ".git").exists():
                logger.info(f"Repository already exists at {self.repo_path}")
                return await self._ensure_remote_configured()
            
            # Create directory and initialize/clone
            self.repo_path.mkdir(parents=True, exist_ok=True)
            
            if self.github_username and self.github_token:
                # Clone from GitHub
                repo_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/my-private-knowledge.git"
                
                try:
                    await self._run_git_command(["clone", repo_url, str(self.repo_path)])
                    logger.success(f"Cloned repository to {self.repo_path}")
                    return True
                except subprocess.CalledProcessError:
                    logger.warning("Clone failed, initializing new repository")
                    
            # Initialize new repository
            os.chdir(self.repo_path)
            await self._run_git_command(["init"])
            await self._run_git_command(["branch", "-M", "main"])
            
            # Create initial README
            readme_content = """# My Private Knowledge Library

This is my personal knowledge library created by my AI Knowledge Bot.

## 📚 Structure

- Automatically organized by topics
- Beautiful Obsidian vault format
- Cross-referenced and searchable
- Continuously updated by AI

## 🔒 Privacy

This repository is private and contains my personal learning notes.
"""
            
            readme_path = self.repo_path / "README.md"
            readme_path.write_text(readme_content)
            
            await self._run_git_command(["add", "README.md"])
            await self._run_git_command(["commit", "-m", "Initial commit: Setup private knowledge library"])
            
            # Add remote if credentials available
            if self.github_username and self.github_token:
                remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/my-private-knowledge.git"
                try:
                    await self._run_git_command(["remote", "add", "origin", remote_url])
                    await self._run_git_command(["push", "-u", "origin", "main"])
                    logger.success("Repository setup complete with GitHub remote")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to setup remote: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup repository: {e}")
            return False
    
    async def _ensure_remote_configured(self) -> bool:
        """Ensure the remote URL is configured correctly."""
        try:
            os.chdir(self.repo_path)
            
            if not self.github_username or not self.github_token:
                return True
                
            # Check if remote exists
            try:
                await self._run_git_command(["remote", "get-url", "origin"])
            except subprocess.CalledProcessError:
                # Add remote
                remote_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/my-private-knowledge.git"
                await self._run_git_command(["remote", "add", "origin", remote_url])
                logger.info("Added GitHub remote")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure remote: {e}")
            return False
    
    async def commit_and_push(self, message: str, file_paths: Optional[list] = None) -> bool:
        """Commit and push changes to the repository."""
        if not self.auto_commit:
            logger.info("Auto-commit disabled, skipping git operations")
            return True
            
        try:
            os.chdir(self.repo_path)
            
            # Add files
            if file_paths:
                for file_path in file_paths:
                    await self._run_git_command(["add", str(file_path)])
            else:
                await self._run_git_command(["add", "."])
            
            # Check if there are changes to commit
            result = await self._run_git_command(["diff", "--cached", "--quiet"], check=False)
            if result.returncode == 0:
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            await self._run_git_command(["commit", "-m", message])
            logger.success(f"Committed changes: {message}")
            
            # Push if enabled and remote configured
            if self.auto_push and self.github_username and self.github_token:
                try:
                    await self._run_git_command(["push", "origin", "main"])
                    logger.success("Pushed changes to GitHub")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to push: {e}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in git operations: {e}")
            return False
    
    async def _run_git_command(self, args: list, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command asynchronously."""
        cmd = ["git"] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.repo_path
        )
        
        stdout, stderr = await process.communicate()
        
        result = subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr
        )
        
        if check and result.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise subprocess.CalledProcessError(result.returncode, cmd, stderr=error_msg)
        
        return result
    
    async def get_status(self) -> dict:
        """Get repository status information."""
        try:
            os.chdir(self.repo_path)
            
            # Get branch name
            branch_result = await self._run_git_command(["branch", "--show-current"])
            branch = branch_result.stdout.decode().strip()
            
            # Get status
            status_result = await self._run_git_command(["status", "--porcelain"])
            modified_files = len(status_result.stdout.decode().strip().split('\n')) if status_result.stdout else 0
            
            # Get commit count
            try:
                count_result = await self._run_git_command(["rev-list", "--count", "HEAD"])
                commit_count = int(count_result.stdout.decode().strip())
            except subprocess.CalledProcessError:
                commit_count = 0
            
            # Get last commit info
            try:
                log_result = await self._run_git_command(["log", "-1", "--format=%s"])
                last_commit = log_result.stdout.decode().strip()
            except subprocess.CalledProcessError:
                last_commit = "No commits yet"
            
            return {
                "branch": branch,
                "modified_files": modified_files,
                "total_commits": commit_count,
                "last_commit": last_commit,
                "repository_path": str(self.repo_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to get repository status: {e}")
            return {
                "branch": "unknown",
                "modified_files": 0,
                "total_commits": 0,
                "last_commit": "Error getting status",
                "repository_path": str(self.repo_path)
            }


# Integration function for the bot
async def auto_sync_knowledge(file_path: str, title: str) -> bool:
    """Automatically commit and sync a new knowledge entry."""
    try:
        git_sync = GitKnowledgeSync()
        
        # Ensure repository is set up
        await git_sync.setup_repository()
        
        # Commit the new file
        commit_message = f"Add: {title}"
        success = await git_sync.commit_and_push(commit_message, [file_path])
        
        if success:
            logger.success(f"Knowledge entry synced: {title}")
        else:
            logger.warning(f"Failed to sync knowledge entry: {title}")
            
        return success
        
    except Exception as e:
        logger.error(f"Auto-sync failed: {e}")
        return False