"""Middleware for Knowledge Bot."""

import time
from collections import defaultdict
from typing import Dict, Any, Callable, Awaitable

try:
    from aiogram import BaseMiddleware
    from aiogram.types import TelegramObject, Message
except ImportError:
    BaseMiddleware = object
    TelegramObject = Message = None

from config import Config, ERROR_MESSAGES


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent spam."""
    
    def __init__(self):
        super().__init__()
        # Store user request timestamps
        self.user_requests: Dict[int, list] = defaultdict(list)
        self.max_requests = Config.RATE_LIMIT_PER_HOUR
        self.window_seconds = 3600  # 1 hour
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process middleware."""
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id if event.from_user else 0
        current_time = time.time()
        
        # Clean old requests
        self._cleanup_old_requests(user_id, current_time)
        
        # Check if user is within rate limit
        if self._is_rate_limited(user_id):
            await event.answer(ERROR_MESSAGES["rate_limit"])
            return
        
        # Add current request
        self.user_requests[user_id].append(current_time)
        
        # Continue to handler
        return await handler(event, data)
    
    def _cleanup_old_requests(self, user_id: int, current_time: float):
        """Remove requests older than the time window."""
        cutoff_time = current_time - self.window_seconds
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if req_time > cutoff_time
        ]
    
    def _is_rate_limited(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit."""
        return len(self.user_requests[user_id]) >= self.max_requests