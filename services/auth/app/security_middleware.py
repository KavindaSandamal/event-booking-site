from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=()"
        )
        
        # Add CORS headers for API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
        
        # Add cache control headers
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        else:
            response.headers["Cache-Control"] = "public, max-age=3600"
        
        # Add server information
        response.headers["Server"] = "EventBooking/1.0"
        
        # Log request
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"IP: {request.client.host}"
        )
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests for security monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"IP: {request.client.host} - "
            f"User-Agent: {request.headers.get('user-agent', 'Unknown')} - "
            f"Referer: {request.headers.get('referer', 'None')}"
        )
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "admin", "login", "password", "sql", "script", "union", "select",
            "drop", "delete", "insert", "update", "exec", "eval", "javascript"
        ]
        
        url_lower = request.url.path.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                logger.warning(
                    f"Suspicious request pattern detected: {pattern} in {request.url.path} - "
                    f"IP: {request.client.host}"
                )
                break
        
        response = await call_next(request)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app, rate_limiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Apply rate limiting based on endpoint
        rate_limit_key = self._get_rate_limit_key(request)
        
        if rate_limit_key:
            try:
                from .rate_limiter import check_rate_limit
                await check_rate_limit(request, rate_limit_key)
            except Exception as e:
                logger.warning(f"Rate limit check failed: {e}")
                # Continue processing if rate limiter fails
        
        response = await call_next(request)
        return response
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Determine rate limit key based on request."""
        path = request.url.path
        
        if path.startswith("/api/auth/login"):
            return "login"
        elif path.startswith("/api/auth/register"):
            return "register"
        elif path.startswith("/api/auth/password-reset"):
            return "password_reset"
        elif path.startswith("/api/auth/"):
            return "api_auth"
        elif path.startswith("/api/"):
            return "api_general"
        
        return None
