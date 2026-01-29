"""
Rate limiting configuration for Chestia backend using SlowAPI.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize limiter using client IP address
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """
    Set up rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
