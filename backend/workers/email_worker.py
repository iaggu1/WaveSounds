import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from sqlalchemy import and_, delete, or_, select, update

from backend.core.config import get_settings
from backend.core.database import SessionLocal, engine
from backend.core.security import log_email_event
from backend.models.lead import Lead
from backend.models.outbox import EmailOutbox

logger = logging.getLogger("forma.email_worker")
MAX_ATTEMPTS = 5
RETRY_BASE_SECONDS = 30
LEASE_SECONDS = 60
POLL_SECONDS = 2


async def claim_next_job() -> tuple[UUID, UUID, int] | None:
    now = datetime.now(timezone.utc)
    try:
        async with SessionLocal() as session:
            await session.execute(
                update(EmailOutbox)
                .where(
                    EmailOutbox.status == "processing",
                    EmailOutbox.locked_until < now,
                    EmailOutbox.attempts >= MAX_ATTEMPTS,
                )
                .values(status="failed", locked_until=None, last_error_code="max_attempts_exceeded")
            )
            due_job = await session.scalar(
                select(EmailOutbox)
                .where(
                    EmailOutbox.event_type == "welcome",
                    EmailOutbox.attempts < MAX_ATTEMPTS,
                    or_(
                        and_(EmailOutbox.status == "pending", EmailOutbox.available_at <= now),
                        and_(EmailOutbox.status == "processing", EmailOutbox.locked_until < now),
                    ),
                )
                .order_by(EmailOutbox.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if due_job is None:
                await session.commit()
                return None

            due_job.status = "processing"
            due_job.attempts += 1
            due_job.locked_until = now + timedelta(seconds=LEASE_SECONDS)
            await session.flush()
            result = (due_job.id, due_job.lead_id, due_job.attempts)
            await session.commit()
            return result
    except Exception as error:
        logger.error("Falha ao reservar envio de e-mail (%s)", type(error).__name__)
        return None


async def mark_job_failed(job_id: UUID, attempts: int, error_code: str) -> None:
    now = datetime.now(timezone.utc)
    if attempts >= MAX_ATTEMPTS:
        values = {"status": "failed", "locked_until": None, "last_error_code": error_code[:64]}
    else:
        delay = min(RETRY_BASE_SECONDS * (2 ** (attempts - 1)), 3600)
        values = {
            "status": "pending",
            "available_at": now + timedelta(seconds=delay),
            "locked_until": None,
            "last_error_code": error_code[:64],
        }
    try:
        async with SessionLocal() as session:
            await session.execute(update(EmailOutbox).where(EmailOutbox.id == job_id).values(**values))
            await session.commit()
    except Exception as error:
        logger.error("Falha ao registrar resultado do e-mail (%s)", type(error).__name__)


async def deliver(job_id: UUID, lead_id: UUID, attempts: int) -> None:
    settings = get_settings()
    try:
        async with SessionLocal() as session, session.begin():
            # Keep erasure from racing an in-flight provider request; the HTTP timeout bounds this lock.
            lead = await session.scalar(
                select(Lead).where(Lead.id == lead_id).with_for_update(read=True)
            )
            if lead is None:
                return
            email = lead.email
            payload = {
                "from": settings.email_from,
                "to": [email],
                "subject": "Seu acesso à forma. está liberado",
                "html": f"<p>Seu acesso à forma. está liberado.</p><p>Plano selecionado: {lead.plan_interest}.</p>",
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                        "Idempotency-Key": f"welcome/{job_id}",
                    },
                    json=payload,
                )
                response.raise_for_status()
            await session.execute(delete(EmailOutbox).where(EmailOutbox.id == job_id))
        log_email_event("E-mail de boas-vindas enviado", email)
    except httpx.HTTPStatusError as error:
        await mark_job_failed(job_id, attempts, f"provider_http_{error.response.status_code}")
        log_email_event("Falha ao enviar e-mail de boas-vindas", email)
    except httpx.HTTPError as error:
        await mark_job_failed(job_id, attempts, f"provider_{type(error).__name__}")
        log_email_event("Falha ao enviar e-mail de boas-vindas", email)
    except Exception as error:
        await mark_job_failed(job_id, attempts, f"worker_{type(error).__name__}")
        logger.error("Falha inesperada no envio de e-mail (%s)", type(error).__name__)


async def run_worker() -> None:
    settings = get_settings()
    if not settings.resend_api_key:
        logger.info("Integração de e-mail não configurada; envios permanecem na fila")
    try:
        while True:
            if not settings.resend_api_key:
                await asyncio.sleep(POLL_SECONDS)
                continue
            job = await claim_next_job()
            if job is None:
                await asyncio.sleep(POLL_SECONDS)
                continue
            await deliver(*job)
    finally:
        await engine.dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker de e-mail encerrado")


if __name__ == "__main__":
    main()

