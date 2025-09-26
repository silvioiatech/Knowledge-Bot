"""Utility functions for the Knowledge Bot pipeline."""

import asyncio
import hashlib
import re
import time
from typing import Dict, Any, List, Union
from pathlib import Path
import json
from datetime import datetime

from loguru import logger


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def generate_content_hash(content: str, length: int = 16) -> str:
    """Generate hash for content deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()[:length]


def detect_content_language(text: str) -> str:
    """Simple language detection based on character patterns."""
    # Very basic language detection - could be enhanced with proper library
    
    # Check for common English words
    english_indicators = ['the', 'and', 'or', 'but', 'with', 'for', 'this', 'that']
    text_lower = text.lower()
    
    english_count = sum(1 for word in english_indicators if word in text_lower)
    
    if english_count >= 3:
        return 'en'
    
    # Check for other language patterns (basic)
    if any(char in text for char in 'àáâãäåæçèéêëìíîïñòóôõöøùúûüý'):
        return 'es'  # Spanish/French/etc
    
    if any(char in text for char in 'äöüß'):
        return 'de'  # German
    
    return 'en'  # Default to English


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Estimate reading time in minutes."""
    word_count = len(text.split())
    return max(1, round(word_count / wpm))


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes)}m {seconds:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity based on word overlap."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def extract_technical_terms(text: str) -> List[str]:
    """Extract potential technical terms from text."""
    # Look for capitalized terms, acronyms, and technical patterns
    patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms (2+ uppercase letters)
        r'\b[A-Z][a-z]+[A-Z][a-z]*\b',  # CamelCase
        r'\b\w*[Aa]pi\b',  # API-related terms
        r'\b\w*[Ss]ql\b',  # SQL-related terms
        r'\b\w+\.[a-z]{2,4}\b',  # Domain-like patterns
    ]
    
    terms = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        terms.update(matches)
    
    # Filter terms by length
    technical_terms = [term for term in terms if len(term) > 1]
    
    return list(set(technical_terms))


def validate_url(url: str) -> bool:
    """Validate if URL format is correct."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If space is not too far back
        return truncated[:last_space] + suffix
    else:
        return truncated + suffix


def parse_video_duration(duration_str: str) -> float:
    """Parse duration string (e.g., '5:32', '1:23:45') to seconds."""
    try:
        parts = duration_str.split(':')
        parts = [int(p) for p in parts]
        
        if len(parts) == 2:  # MM:SS
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:  # HH:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        else:
            return float(duration_str)  # Assume seconds
    except (ValueError, AttributeError):
        return 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_slug(text: str, max_length: int = 50) -> str:
    """Create URL-friendly slug from text."""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug[:max_length]


class ProcessingTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type:
            logger.error(f"{self.operation_name} failed after {format_duration(duration)}")
        else:
            logger.info(f"{self.operation_name} completed in {format_duration(duration)}")
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def acquire(self):
        """Acquire rate limit slot."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # Check if we can make a call
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
        
        # Record this call
        self.calls.append(now)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff."""
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse JSON, returning default")
        return default


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence or word boundary
        if end < len(text):
            # Look for sentence boundary
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size * 0.8:
                end = sentence_end + 1
            else:
                # Look for word boundary
                word_end = text.rfind(' ', start, end)
                if word_end > start + chunk_size * 0.8:
                    end = word_end
        
        chunks.append(text[start:end])
        start = max(start + chunk_size - overlap, end)
        
        if start >= len(text):
            break
    
    return chunks


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later ones taking precedence."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def is_video_file(filename: str) -> bool:
    """Check if file is a video based on extension."""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v'}
    return get_file_extension(filename) in video_extensions


def format_timestamp(timestamp: float) -> str:
    """Format timestamp to readable format."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# Export commonly used functions
__all__ = [
    'sanitize_filename',
    'generate_content_hash',
    'detect_content_language',
    'estimate_reading_time',
    'extract_urls',
    'format_duration',
    'calculate_text_similarity',
    'extract_technical_terms',
    'validate_url',
    'truncate_text',
    'parse_video_duration',
    'format_file_size',
    'create_slug',
    'ProcessingTimer',
    'RateLimiter',
    'retry_with_exponential_backoff',
    'safe_json_loads',
    'chunk_text',
    'merge_dictionaries',
    'ensure_directory',
    'get_file_extension',
    'is_video_file',
    'format_timestamp'
]