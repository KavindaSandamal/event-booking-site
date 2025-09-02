import time
import redis
import os
from typing import Dict, Optional
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: Optional[str] = None
    ) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., 'login', 'register')
            limit: Maximum number of requests allowed
            window: Time window in seconds
            identifier: Optional identifier (IP, user_id, etc.)
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        try:
            # Create unique key with identifier
            if identifier:
                rate_key = f"rate_limit:{key}:{identifier}"
            else:
                rate_key = f"rate_limit:{key}"
            
            # Get current time
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(rate_key, window)
            
            # Execute pipeline
            results = pipe.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            if current_count >= limit:
                logger.warning(f"Rate limit exceeded for {key}: {current_count}/{limit}")
                return False
            
            logger.debug(f"Rate limit check passed for {key}: {current_count + 1}/{limit}")
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request if rate limiter fails
            return True
    
    async def get_remaining_requests(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: Optional[str] = None
    ) -> int:
        """Get remaining requests for the current window."""
        try:
            if identifier:
                rate_key = f"rate_limit:{key}:{identifier}"
            else:
                rate_key = f"rate_limit:{key}"
            
            current_time = int(time.time())
            window_start = current_time - window
            
            # Remove expired entries and count
            self.redis.zremrangebyscore(rate_key, 0, window_start)
            current_count = self.redis.zcard(rate_key)
            
            return max(0, limit - current_count)
            
        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return limit

# Rate limit configurations
RATE_LIMITS = {
    "login": {"limit": 5, "window": 300},  # 5 attempts per 5 minutes
    "register": {"limit": 3, "window": 3600},  # 3 registrations per hour
    "password_reset": {"limit": 3, "window": 3600},  # 3 password resets per hour
    "api_general": {"limit": 100, "window": 3600},  # 100 requests per hour
    "api_auth": {"limit": 50, "window": 3600},  # 50 auth requests per hour
}

# Global rate limiter instance
rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    global rate_limiter
    if rate_limiter is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        rate_limiter = RateLimiter(redis_client)
    return rate_limiter

async def check_rate_limit(
    request: Request,
    limit_key: str,
    identifier: Optional[str] = None
) -> None:
    """Check rate limit and raise exception if exceeded."""
    limiter = get_rate_limiter()
    
    if limit_key not in RATE_LIMITS:
        logger.warning(f"Unknown rate limit key: {limit_key}")
        return
    
    config = RATE_LIMITS[limit_key]
    
    # Use IP address as identifier if not provided
    if not identifier:
        identifier = request.client.host
    
    is_allowed = await limiter.is_allowed(
        limit_key, 
        config["limit"], 
        config["window"],
        identifier
    )
    
    if not is_allowed:
        remaining = await limiter.get_remaining_requests(
            limit_key,
            config["limit"],
            config["window"],
            identifier
        )
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": config["limit"],
                "window": config["window"],
                "remaining": remaining,
                "retry_after": config["window"]
            }
        )
