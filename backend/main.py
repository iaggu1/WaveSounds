import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text

from backend.api.v1.endpoints import router
from backend.core.config import get_settings
from backend.core.database import engine
from backend.core.rate_limit import allow_lead_request
from backend.core.redis_client import redis_client
from backend.core.security import client_ip

settings = get_settings()
ALLOWED_ORIGINS = {origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("forma.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await redis_client.ping()
        yield
    finally:
        await redis_client.aclose()
        await engine.dispose()


app = FastAPI(title="forma. API", version="1.0.0", docs_url="/docs" if settings.app_env == "development" else None, redoc_url=None, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/api/v1/leads":
        request_ip = client_ip(request)
        try:
            allowed = await allow_lead_request(redis_client, request_ip)
        except RedisError as error:
            logger.error("Rate limit indisponível (%s)", type(error).__name__)
            unavailable = JSONResponse(status_code=503, content={"detail": "Serviço temporariamente indisponível."})
            origin = request.headers.get("origin")
            if origin in ALLOWED_ORIGINS:
                unavailable.headers["Access-Control-Allow-Origin"] = origin
                unavailable.headers["Vary"] = "Origin"
            unavailable.headers["Retry-After"] = "10"
            unavailable.headers["X-Content-Type-Options"] = "nosniff"
            unavailable.headers["X-Frame-Options"] = "DENY"
            unavailable.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            unavailable.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
            unavailable.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            return unavailable
        if not allowed:
            limited = JSONResponse(status_code=429, content={"detail": "Limite de tentativas excedido. Aguarde um minuto e tente novamente."})
            origin = request.headers.get("origin")
            if origin in ALLOWED_ORIGINS:
                limited.headers["Access-Control-Allow-Origin"] = origin
                limited.headers["Vary"] = "Origin"
            limited.headers["Retry-After"] = "60"
            limited.headers["X-Content-Type-Options"] = "nosniff"
            limited.headers["X-Frame-Options"] = "DENY"
            limited.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            limited.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
            limited.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            return limited
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "Confira os dados enviados."})


@app.exception_handler(Exception)
async def internal_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("forma.api").error("Erro interno não tratado (%s)", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Não foi possível processar sua solicitação no momento."})


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    await redis_client.ping()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(router, prefix="/api/v1")

