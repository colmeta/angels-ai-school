"""
Rate Limiting Middleware
Prevents API abuse and DDoS attacks

Limits:
- Free tier: 100 requests/hour
- Pro tier: 1,000 requests/hour
- Admin: Unlimited
"""
from fastapi import Request, HTTPException, status
from typing import Dict, Optional
import time
from collections import defaultdict
import asyncio


class RateLimiter:
    """In-memory rate limiter (use Redis in production for distributed systems)"""
    
    def __init__(self):
        # Store: {identifier: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_task = None
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from auth (if implemented)
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get('x-forwarded-for')
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"
    
    def _get_user_tier(self, request: Request) -> str:
        """Determine user tier (free, pro, admin)"""
        # Check if user is admin (from auth)
        role = getattr(request.state, 'user_role', None)
        if role == 'admin':
            return 'admin'
        
        # Check if pro tier (from database or subscription)
        is_pro = getattr(request.state, 'is_pro', False)
        if is_pro:
            return 'pro'
        
        return 'free'
    
    def _get_limit(self, tier: str) -> tuple[int, int]:
        """Get rate limit and window for tier"""
        limits = {
            'admin': (999999, 3600),  # Unlimited (high number)
            'pro': (1000, 3600),       # 1,000/hour
            'free': (100, 3600),       # 100/hour
        }
        return limits.get(tier, limits['free'])
    
    def _cleanup_old_requests(self, identifier: str, window: int):
        """Remove old requests outside the time window"""
        current_time = time.time()
        self.requests[identifier] = [
            (ts, count) for ts, count in self.requests[identifier]
            if current_time - ts < window
        ]
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limit
        
        Returns:
            True if allowed, raises HTTPException if rate limit exceeded
        """
        identifier = self._get_identifier(request)
        tier = self._get_user_tier(request)
        limit, window = self._get_limit(tier)
        
        # Clean up old requests
        self._cleanup_old_requests(identifier, window)
        
        # Count requests in current window
        current_time = time.time()
        request_count = sum(count for ts, count in self.requests[identifier])
        
        if request_count >= limit:
            # Rate limit exceeded
            retry_after = window
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "window": f"{window} seconds",
                    "retry_after": retry_after,
                    "tier": tier,
                    "message": f"You have exceeded the {tier} tier limit of {limit} requests per hour. Please try again later."
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Add current request
        self.requests[identifier].append((current_time, 1))
        
        # Add rate limit headers
        remaining = limit - (request_count + 1)
        reset_time = int(current_time + window)
        
        request.state.rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time
        }
        
        return True
    
    async def start_background_cleanup(self):
        """Start background task to periodically clean up old requests"""
        while True:
            await asyncio.sleep(300)  # Clean up every 5 minutes
            current_time = time.time()
            
            # Remove identifiers with no recent requests
            identifiers_to_remove = []
            for identifier, requests in self.requests.items():
                # Remove requests older than 2 hours
                recent_requests = [
                    (ts, count) for ts, count in requests
                    if current_time - ts < 7200
                ]
                
                if not recent_requests:
                    identifiers_to_remove.append(identifier)
                else:
                    self.requests[identifier] = recent_requests
            
            for identifier in identifiers_to_remove:
                del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limiting"""
    
    # Skip rate limiting for health check
    if request.url.path == "/api/health":
        response = await call_next(request)
        return response
    
    # Check rate limit
    try:
        await rate_limiter.check_rate_limit(request)
    except HTTPException as e:
        # Rate limit exceeded, return 429
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=e.status_code,
            content=e.detail,
            headers=e.headers
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to response
    if hasattr(request.state, 'rate_limit_info'):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
    
    return response
