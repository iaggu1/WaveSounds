import hashlib
import ipaddress
import logging
import time
from collections import defaultdict, deque
from threading import Lock

from starlette.requests import Request

from backend.core.config import get_settings

logger = logging.getLogger("forma.security")
_trusted_proxy_ips = {ip.strip() for ip in get_settings().trusted_proxy_ips.split(",") if ip.strip()}
_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 5


def ip_digest(ip_address: str) -> str:
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()


def client_ip(request: Request) -> str:
    direct_ip = request.client.host if request.client else "unknown"
    if direct_ip not in _trusted_proxy_ips:
        return direct_ip
    forwarded_ip = request.headers.get("x-forma-client-ip", "")
    try:
        return str(ipaddress.ip_address(forwarded_ip))
    except ValueError:
        return direct_ip


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
