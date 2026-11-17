import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.api.v1.endpoints import router
from backend.core.config import get_settings
from backend.core.database import engine
from backend.models.lead import Base
from backend.core.security import allow_request, client_ip

settings = get_settings()
ALLOWED_ORIGINS = {origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
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
        if not allow_request(request_ip):
            limited = JSONResponse(status_code=429, content={"detail": "Limite de tentativas excedido. Aguarde um minuto e tente novamente."})
            origin = request.headers.get("origin")
            if origin in ALLOWED_ORIGINS:
                limited.headers["Access-Control-Allow-Origin"] = origin
                limited.headers["Vary"] = "Origin"
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
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(router, prefix="/api/v1")
