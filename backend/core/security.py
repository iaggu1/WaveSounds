import hashlib
import logging
import time
from collections import defaultdict, deque
from threading import Lock

logger = logging.getLogger("forma.security")
_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 5


def ip_digest(ip_address: str) -> str:
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()


def masked_email(email: str) -> str:
    local, separator, domain = email.partition("@")
    if not separator:
        return "[email ocultado]"
    return f"{local[:2]}***@{domain}"


def allow_request(ip_address: str) -> bool:
    now = time.monotonic()
    with _lock:
        bucket = _requests[ip_address]
        while bucket and now - bucket[0] >= _WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= _MAX_REQUESTS:
            return False
        bucket.append(now)
        if len(_requests) > 10_000:
            expired = [key for key, values in _requests.items() if not values or now - values[-1] >= _WINDOW_SECONDS]
            for key in expired:
                _requests.pop(key, None)
        return True


def log_email_event(message: str, email: str) -> None:
    logger.info("%s recipient=%s", message, masked_email(email))
