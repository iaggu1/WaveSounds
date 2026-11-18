from redis.asyncio import Redis

from backend.core.config import get_settings

redis_client = Redis.from_url(
    get_settings().redis_url,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
    max_connections=100,
)

