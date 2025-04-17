from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


# Initialize Flask-Caching extension
cache = Cache()

# Initialize Flask-Limiter extension to apply rate limiting
limiter = Limiter(
    key_func=get_remote_address,   # Function to identify clients by their IP address
    default_limits=["100 per minute"]  # Default rate limit: 100 requests per minute per IP
)
