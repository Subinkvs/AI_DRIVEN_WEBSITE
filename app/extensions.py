from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

cache = Cache()

limiter = Limiter(
    key_func=get_remote_address,  # defines how to get the client identity
    default_limits=["100 per minute"]
)
