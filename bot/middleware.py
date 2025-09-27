"""Bot middleware for rate limiting and logging."""

import time
from typing import Dict, Any, Awaitable, Callable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent spam."""
    
    def __init__(self, rate_limit: int = 60):  # 1 minute cooldown
        self.rate_limit = rate_limit
        self.user_last_request: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        # Check rate limit for video processing requests
        if isinstance(event, Message) and event.text and ("http" in event.text):
            last_request = self.user_last_request.get(user_id, 0)
            
            if current_time - last_request < self.rate_limit:
                remaining = int(self.rate_limit - (current_time - last_request))
                await event.answer(
                    f"⏰ Rate limit: Please wait {remaining} seconds before sending another video."
                )
                return
            
            self.user_last_request[user_id] = current_time
        
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Enhanced logging middleware."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        username = event.from_user.username or "unknown"
        
        if isinstance(event, Message):
            text_preview = (event.text[:50] + "...") if event.text and len(event.text) > 50 else event.text
            logger.info(f"Message from user {user_id} (@{username}): {text_preview}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Callback from user {user_id} (@{username}): {event.data}")
        
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(f"Handler error for user {user_id}: {e}")
            
            if isinstance(event, Message):
                await event.answer("❌ An error occurred. Please try again later.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ An error occurred. Please try again.")
            
            raise
