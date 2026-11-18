from redis.asyncio import Redis

from backend.core.security import ip_digest

_WINDOW_SECONDS = 60
_MAX_REQUESTS = 5

_INCREMENT_WITH_EXPIRY = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


async def allow_lead_request(redis: Redis, client_ip: str) -> bool:
    key = f"forma:lead-rate:{ip_digest(client_ip)}"
    count = await redis.eval(_INCREMENT_WITH_EXPIRY, 1, key, _WINDOW_SECONDS)
    return int(count) <= _MAX_REQUESTS

