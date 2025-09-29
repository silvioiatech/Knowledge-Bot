"""Railway file server for persistent knowledge base storage."""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from config import Config


class RailwayFileServer:
    """File server for Railway persistent storage."""
    
    def __init__(self):
        self.app = FastAPI(title="Knowledge Bot File Server")
        self.knowledge_base_path = Path("/app/knowledge_base")
        self.images_path = self.knowledge_base_path / "images"
        
        # Ensure directories exist
        self._create_directory_structure()
        
        # Setup routes
        self._setup_routes()
        
    def _create_directory_structure(self):
        """Create the knowledge base directory structure."""
        categories = [
            "ai", "web-development", "programming", "devops", 
            "mobile", "security", "data", "macos", "linux", "windows", "general"
        ]
        
        # Create main directories
        self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        # Create category directories
        for category in categories:
            (self.knowledge_base_path / category).mkdir(exist_ok=True)
            
        logger.info(f"Created directory structure at {self.knowledge_base_path}")
    
    def _setup_routes(self):
        """Setup FastAPI routes for file serving."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Root directory browser."""
            return self._generate_directory_listing("/")
        
        @self.app.get("/kb/", response_class=HTMLResponse)
        async def knowledge_base_root():
            """Knowledge base directory browser."""
            return self._generate_directory_listing("/kb/")
        
        @self.app.get("/kb/{category}/", response_class=HTMLResponse)
        async def category_listing(category: str):
            """List files in a specific category."""
            category_path = self.knowledge_base_path / category
            if not category_path.exists():
                raise HTTPException(status_code=404, detail="Category not found")
            
            return self._generate_category_listing(category)
        
        @self.app.get("/raw/{category}/{filename}")
        async def raw_file(category: str, filename: str):
            """Serve raw markdown file."""
            file_path = self.knowledge_base_path / category / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            return FileResponse(
                file_path,
                media_type="text/markdown",
                headers={"Content-Disposition": f"inline; filename={filename}"}
            )
        
        @self.app.get("/view/{category}/{filename}", response_class=HTMLResponse)
        async def view_file(category: str, filename: str):
            """Serve rendered HTML version of markdown file."""
            file_path = self.knowledge_base_path / category / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            return self._render_markdown_as_html(file_path, category)
        
        @self.app.get("/images/{filename}")
        async def serve_image(filename: str):
            """Serve image files."""
            image_path = self.images_path / filename
            if not image_path.exists():
                raise HTTPException(status_code=404, detail="Image not found")
            
            return FileResponse(image_path)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    def _generate_directory_listing(self, path: str) -> str:
        """Generate HTML directory listing."""
        categories = [d.name for d in self.knowledge_base_path.iterdir() if d.is_dir() and d.name != "images"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Knowledge Bot - File Browser</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }}
                .header {{ border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                .category {{ 
                    display: block; 
                    padding: 12px 16px; 
                    margin: 8px 0; 
                    text-decoration: none; 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    color: #333;
                    border-left: 4px solid #007bff;
                }}
                .category:hover {{ background: #e9ecef; }}
                .stats {{ color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Knowledge Bot File Browser</h1>
                <p>Browse your AI-generated knowledge base entries</p>
            </div>
            
            <h2>📂 Categories</h2>
        """
        
        for category in sorted(categories):
            file_count = len(list((self.knowledge_base_path / category).glob("*.md")))
            emoji = self._get_category_emoji(category)
            html += f"""
            <a href="/kb/{category}/" class="category">
                {emoji} {category.replace('-', ' ').title()} ({file_count} files)
            </a>
            """
        
        total_files = len(list(self.knowledge_base_path.glob("*/*.md")))
        html += f"""
            <div class="stats">
                📊 Total knowledge entries: {total_files}<br>
                🖼️ Images stored: {len(list(self.images_path.glob("*")))}<br>
                📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_category_listing(self, category: str) -> str:
        """Generate HTML listing for a specific category."""
        category_path = self.knowledge_base_path / category
        files = sorted(category_path.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        
        emoji = self._get_category_emoji(category)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{category.title()} - Knowledge Bot</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }}
                .header {{ border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                .file {{ 
                    display: block; 
                    padding: 16px; 
                    margin: 12px 0; 
                    text-decoration: none; 
                    background: #fff; 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    color: #333;
                }}
                .file:hover {{ background: #f8f9fa; border-color: #007bff; }}
                .file-title {{ font-weight: 600; font-size: 16px; margin-bottom: 4px; }}
                .file-meta {{ color: #666; font-size: 14px; }}
                .back-link {{ color: #007bff; text-decoration: none; }}
                .back-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="header">
                <a href="/kb/" class="back-link">← Back to Categories</a>
                <h1>{emoji} {category.replace('-', ' ').title()}</h1>
                <p>{len(files)} knowledge entries</p>
            </div>
        """
        
        if not files:
            html += "<p>No files in this category yet.</p>"
        else:
            for file_path in files:
                file_stats = file_path.stat()
                file_size = file_stats.st_size
                modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                
                # Extract title from filename
                title = file_path.stem.replace('-', ' ').title()
                if title.startswith(modified_time.strftime('%Y%m%d')):
                    title = title[9:]  # Remove date prefix
                
                html += f"""
                <a href="/view/{category}/{file_path.name}" class="file">
                    <div class="file-title">📄 {title}</div>
                    <div class="file-meta">
                        📅 {modified_time.strftime('%Y-%m-%d %H:%M')} • 
                        📊 {file_size // 1024}KB • 
                        <a href="/raw/{category}/{file_path.name}" style="color: #007bff;">Raw</a>
                    </div>
                </a>
                """
        
        html += """
        </body>
        </html>
        """
        return html
    
    def _render_markdown_as_html(self, file_path: Path, category: str) -> str:
        """Render markdown file as HTML."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple markdown to HTML conversion (basic)
            html_content = content
            html_content = html_content.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
            html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
            html_content = html_content.replace('- ', '<li>').replace('\n\n', '</p><p>')
            html_content = f"<p>{html_content}</p>"
            
            # Fix image paths
            html_content = html_content.replace('](../images/', '](/images/')
            
            title = file_path.stem.replace('-', ' ').title()
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title} - Knowledge Bot</title>
                <meta charset="utf-8">
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 40px 20px; 
                        line-height: 1.6;
                    }}
                    .header {{ border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                    .back-link {{ color: #007bff; text-decoration: none; }}
                    .back-link:hover {{ text-decoration: underline; }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }}
                    pre {{ background: #f8f9fa; padding: 16px; border-radius: 8px; overflow-x: auto; }}
                    img {{ max-width: 100%; height: auto; border-radius: 8px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <a href="/kb/{category}/" class="back-link">← Back to {category.title()}</a>
                    <a href="/raw/{category}/{file_path.name}" style="float: right; color: #007bff;">View Raw</a>
                </div>
                
                {html_content}
            </body>
            </html>
            """
            
        except Exception as e:
            logger.error(f"Error rendering markdown: {e}")
            return f"<html><body><h1>Error</h1><p>Could not render file: {e}</p></body></html>"
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emojis = {
            "ai": "🤖",
            "web-development": "🌐", 
            "programming": "💻",
            "devops": "⚙️",
            "mobile": "📱",
            "security": "🛡️",
            "data": "📊",
            "macos": "🍎",
            "linux": "🐧", 
            "windows": "🪟",
            "general": "📚"
        }
        return emojis.get(category, "📁")
    
    async def save_knowledge_entry(
        self, 
        title: str, 
        category: str, 
        content: str, 
        source_url: str
    ) -> str:
        """Save a new knowledge entry and return the URL."""
        # Generate filename
        date_str = datetime.now().strftime('%Y%m%d')
        clean_title = "".join(c for c in title if c.isalnum() or c in ' -').strip()
        clean_title = clean_title.replace(' ', '-').lower()[:50]
        filename = f"{date_str}-{clean_title}.md"
        
        # Determine category folder
        category_folder = category.lower().replace(' ', '-').replace('🤖', 'ai').replace('🌐', 'web-development')
        category_path = self.knowledge_base_path / category_folder
        category_path.mkdir(exist_ok=True)
        
        # Save file
        file_path = category_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved knowledge entry: {file_path}")
        
        # Return Railway URL
        base_url = os.getenv('RAILWAY_STATIC_URL', 'https://your-app.up.railway.app')
        return f"{base_url}/view/{category_folder}/{filename}"


# Global file server instance
file_server = RailwayFileServer()

# FastAPI app for Railway
app = file_server.app