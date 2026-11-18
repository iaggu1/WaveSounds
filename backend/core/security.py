import hashlib
import ipaddress
import logging

from starlette.requests import Request

from backend.core.config import get_settings

logger = logging.getLogger("forma.security")
_trusted_proxy_ips = {ip.strip() for ip in get_settings().trusted_proxy_ips.split(",") if ip.strip()}


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


def log_email_event(message: str, email: str) -> None:
    logger.info("%s recipient=%s", message, masked_email(email))

