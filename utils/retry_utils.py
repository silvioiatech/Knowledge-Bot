"""Retry utilities for reliable API calls."""

import asyncio
import random
from typing import Callable, Any, Optional
from loguru import logger


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


async def retry_async(
    func: Callable,
    config: RetryConfig = RetryConfig(),
    exceptions: tuple = (Exception,),
    context: str = "operation"
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        config: Retry configuration
        exceptions: Tuple of exceptions to catch and retry
        context: Description for logging
    
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            result = await func()
            if attempt > 0:
                logger.success(f"{context} succeeded on attempt {attempt + 1}")
            return result
            
        except exceptions as e:
            last_exception = e
            attempt_num = attempt + 1
            
            if attempt_num == config.max_attempts:
                logger.error(f"{context} failed after {config.max_attempts} attempts: {e}")
                break
                
            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            
            # Add jitter to prevent thundering herd
            if config.jitter:
                delay = delay * (0.5 + random.random() * 0.5)
            
            logger.warning(f"{context} attempt {attempt_num} failed: {e}. Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)
    
    # All retries exhausted
    raise last_exception


def with_retry(
    config: RetryConfig = RetryConfig(),
    exceptions: tuple = (Exception,),
    context: str = "operation"
):
    """
    Decorator to add retry behavior to async functions.
    
    Usage:
        @with_retry(context="API call")
        async def my_api_call():
            # Your API call here
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async def retry_func():
                return await func(*args, **kwargs)
            
            return await retry_async(
                retry_func,
                config=config,
                exceptions=exceptions,
                context=context or func.__name__
            )
        return wrapper
    return decorator


# Pre-configured retry decorators for common scenarios
api_retry = with_retry(
    config=RetryConfig(max_attempts=3, base_delay=1.0),
    exceptions=(Exception,),
    context="API call"
)

download_retry = with_retry(
    config=RetryConfig(max_attempts=2, base_delay=2.0),
    exceptions=(Exception,),
    context="Download"
)

ai_service_retry = with_retry(
    config=RetryConfig(max_attempts=3, base_delay=2.0, max_delay=30.0),
    exceptions=(Exception,),
    context="AI service"
)